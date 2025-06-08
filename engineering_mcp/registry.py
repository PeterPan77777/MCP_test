"""
Tool-Registry und Discovery-System für Engineering MCP

Verwaltet die separate Registry für Engineering-Tools und 
bietet Discovery-Funktionen für LLM-Orchestrierung.

⚡ TARGET-SYSTEM: Alle Tools verwenden das neue Target-Parameter-System!
- Alle Parameter sind REQUIRED  
- Ein Parameter wird als "target" markiert (zu berechnen)
- Andere Parameter haben Werte mit Einheiten
"""

import re
import pkgutil
import importlib
from typing import Dict, List, Optional, Any, Callable
import asyncio


# Globale Engineering-Tool-Registry (NICHT bei MCP registriert!)
_ENGINEERING_TOOLS_REGISTRY: Dict[str, Dict] = {}


async def discover_engineering_tools() -> int:
    """
    Entdeckt Engineering-Tools im tools/ Verzeichnis und speichert sie in separater Registry.
    REGISTRIERT NICHT bei MCP - nur interne Speicherung!
    
    ⚡ NUR NEUE TOOL-STRUKTUR: Erwartet get_metadata() und calculate() Funktionen
    
    Returns:
        int: Anzahl der entdeckten Engineering-Tools
    """
    global _ENGINEERING_TOOLS_REGISTRY
    _ENGINEERING_TOOLS_REGISTRY.clear()
    
    # Warning-System für Probleme beim Serverstart
    warnings = []
    
    # Prüfe tag_definitions.py Verfügbarkeit (interne Utility)
    try:
        from engineering_mcp.tag_definitions import get_tag_definitions
        get_tag_definitions()
    except Exception as e:
        warnings.append(f"ERROR: tag_definitions.py: Internal Utility not available -> Tools will get 'unknown' Tag ({str(e)})")
    
    def discover_tools_recursive(module_path, module_name_prefix, category_override=None):
        """Rekursive Funktion zum Durchsuchen von Unterordnern"""
        discovered_count = 0
        
        try:
            for finder, name, ispkg in pkgutil.iter_modules(module_path, module_name_prefix + "."):
                if ispkg:
                    # Unterordner gefunden - rekursiv durchsuchen
                    try:
                        submodule = importlib.import_module(name)
                        # Für geometry.Flaechen etc. - verwende 'geometry' als Kategorie
                        subcategory = category_override if category_override else name.split('.')[-1]
                        discovered_count += discover_tools_recursive(
                            submodule.__path__, 
                            name, 
                            subcategory
                        )
                    except Exception as e:
                        print(f"ERROR: Failed to load submodule {name}: {e}")
                else:
                    # Tool-Modul gefunden - NUR NEUE STRUKTUR!
                    try:
                        # Importiere das Tool-Modul
                        tool_module = importlib.import_module(name)
                        
                        # NUR NEUE STRUKTUR: get_metadata() und calculate() Funktionen
                        if hasattr(tool_module, 'get_metadata') and hasattr(tool_module, 'calculate'):
                            try:
                                metadata = tool_module.get_metadata()
                                calculate_func = tool_module.calculate
                                
                                if calculate_func and callable(calculate_func):
                                    # Speichere in separater Registry
                                    tool_id = metadata.get('tool_name', name.split('.')[-1])
                                    category = category_override if category_override else name.split('.')[-2]
                                    
                                    # Prüfe auf fehlende Tags - unterstütze sowohl "tags" als auch "tool_tags"
                                    tool_tags = metadata.get('tags', []) or metadata.get('tool_tags', [])
                                    if not tool_tags:
                                        tool_tags = ['unknown']
                                        warnings.append(f"ERROR: {tool_id}: No tags defined -> 'unknown' assigned")
                                    
                                    _ENGINEERING_TOOLS_REGISTRY[tool_id] = {
                                        'name': tool_id,
                                        'description': metadata.get('description', ''),
                                        'short_description': metadata.get('short_description', ''),
                                        'tags': tool_tags,
                                        'function': calculate_func,
                                        'category': category,
                                        'module': tool_module,
                                        'metadata': metadata,
                
                                        'has_solving': metadata.get('has_solving', 'symbolic')
                                    }
                                    print(f"SUCCESS: Discovered {tool_id} in {category}")
                                    discovered_count += 1
                            except Exception as e:
                                print(f"ERROR: Failed to load metadata from {name}: {e}")
                        else:
                            print(f"WARNING: Tool {name} ignored: No get_metadata() or calculate() function (old structure not supported)")
                            
                    except Exception as e:
                        print(f"ERROR: Failed to load {name}: {e}")
        except Exception as e:
            print(f"ERROR: Failed to search {module_name_prefix}: {e}")
        
        return discovered_count
    
    try:
        # Dynamischer Import aller Tool-Module
        import tools
        
        # Starte rekursive Suche ab tools/
        total_discovered = discover_tools_recursive(tools.__path__, tools.__name__)
        
    except ImportError:
        print("INFO: No Engineering tools found (tools/ directory missing)")
        return 0
    
    # Ausgabe der Warnings beim Serverstart
    if warnings:
        print(f"\nWARNING: {len(warnings)} tools with issues detected:")
        for warning in warnings:
            print(f"   {warning}")
        print()
    
    return len(_ENGINEERING_TOOLS_REGISTRY)


def get_tool_info_for_llm(include_engineering: bool = True) -> List[Dict]:
    """
    Erstellt strukturierte Tool-Informationen für LLM-Discovery.
    
    ⚡ TARGET-SYSTEM: Alle Tools verwenden target-Parameter-System
    
    Args:
        include_engineering: Engineering-Tools einbeziehen
        
    Returns:
        List[Dict]: Tool-Informationen mit target_parameters
    """
    tool_info = []
    
    if include_engineering:
        for tool_name, tool_data in _ENGINEERING_TOOLS_REGISTRY.items():
            # ⚡ NUR NEUE TOOL-STRUKTUR: Metadaten aus get_metadata()
            target_parameters = []
            if 'metadata' in tool_data and 'parameters' in tool_data['metadata']:
                # Neue Struktur: Parameters in Metadaten
                target_parameters = list(tool_data['metadata']['parameters'].keys())
            else:
                print(f"WARNING: Tool {tool_name}: No metadata found - will be skipped")
                continue
            
            tool_info.append({
                "name": tool_name,
                "description": tool_data.get('description', ''),
                "short_description": tool_data.get('short_description', tool_data.get('description', '').split('.')[0]),
                "tags": tool_data.get('tags', []),
                "target_parameters": target_parameters,  # ⚡ Neue Namensgebung!
                "has_solving": tool_data.get('has_solving', 'symbolic'),  # ⚡ NEUE PARAMETER-STRUKTUR
                "target_parameters_info": tool_data['metadata'].get('target_parameters_info', {}),  # ⚡ Detaillierte Parameter-Info

                "source": "engineering_registry"
            })
    
    # Meta-Tools hinzufügen (ohne Fallback!)
    meta_tools_loaded = 0
    try:
        # Lade Meta-Tool-Definitionen direkt aus den Dateien
        import os
        import importlib.util
        
        meta_tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "Meta")
        
        if os.path.exists(meta_tools_dir):
            for filename in os.listdir(meta_tools_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    try:
                        # Dynamisches Import der Meta-Tool-Module
                        spec = importlib.util.spec_from_file_location(
                            f"meta_tool_{filename[:-3]}", 
                            os.path.join(meta_tools_dir, filename)
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Hole TOOL_METADATA wenn verfügbar
                        if hasattr(module, 'TOOL_METADATA'):
                            meta_data = module.TOOL_METADATA
                            tool_info.append({
                                "name": meta_data.get("name", filename[:-3]),
                                "description": meta_data.get("description", "Meta-Tool zur Tool-Discovery"),
                                "short_description": meta_data.get("description", "").split('\n')[0][:100] + "..." if len(meta_data.get("description", "")) > 100 else meta_data.get("description", "").split('\n')[0],
                                "tags": meta_data.get("tags", ["meta"]),
                                "target_parameters": [],  # Meta-Tools haben keine target-Parameter
                                "has_solving": "none",  # ⚡ NEUE PARAMETER-STRUKTUR

                                "source": f"meta_tools_directory:{filename}"
                            })
                            meta_tools_loaded += 1
                    except Exception as e:
                        print(f"WARNING: Failed to load {filename}: {e}")
                        continue
    except Exception as e:
        print(f"ERROR: Failed to dynamically load Meta-Tools: {e}")
    
    print(f"INFO: {meta_tools_loaded} Meta-Tools loaded")
    
    return tool_info


def get_symbolic_tools_summary() -> Dict:
    """
    Erstellt eine kategorisierte Übersicht aller target-basierten Tools.
    
    Returns:
        Dict: Strukturierte Übersicht mit Formeln und target-Parametern
    """
    summary = {
        "total_tools": 0,
        "categories": {},
        "target_based_tools": []
    }
    
    for tool_name, tool_data in _ENGINEERING_TOOLS_REGISTRY.items():
        if tool_data.get('has_solving', 'symbolic') != 'none':
            category = tool_data.get('category', 'unknown')
            
            # Kategorie initialisieren falls noch nicht vorhanden
            if category not in summary["categories"]:
                summary["categories"][category] = {
                    "tools": [],
                    "description": get_category_description(category)
                }
            
            # Tool-Info sammeln
            target_params = []
            if 'metadata' in tool_data and 'parameters' in tool_data['metadata']:
                target_params = list(tool_data['metadata']['parameters'].keys())
                
            tool_info = {
                "name": tool_name,
                "description": tool_data.get('description', ''),
                "target_parameters": target_params,
                "has_solving": tool_data.get('has_solving', 'symbolic'),  # ⚡ NEUE PARAMETER-STRUKTUR
            }
            
            summary["categories"][category]["tools"].append(tool_info)
            summary["target_based_tools"].append(tool_info)
    
    summary["total_tools"] = len(summary["target_based_tools"])
    return summary


async def call_engineering_tool(tool_name: str, parameters: Dict) -> Any:
    """
    Führt ein Engineering-Tool aus der Registry aus.
    
    Args:
        tool_name: Name des Tools
        parameters: Tool-Parameter (mit target-Parameter)
        
    Returns:
        Any: Tool-Ergebnis
        
    Raises:
        ValueError: Bei unbekanntem Tool
    """
    if tool_name not in _ENGINEERING_TOOLS_REGISTRY:
        available_tools = list(_ENGINEERING_TOOLS_REGISTRY.keys())
        raise ValueError(f"Unknown tool: {tool_name}. Available tools: {available_tools}")
    
    tool_data = _ENGINEERING_TOOLS_REGISTRY[tool_name]
    tool_func = tool_data.get('function')
    
    if not tool_func:
        raise ValueError(f"Tool {tool_name} has no executable function")
    
    # Führe Tool aus (async wenn möglich)
    if asyncio.iscoroutinefunction(tool_func):
        return await tool_func(**parameters)
    else:
        return tool_func(**parameters)


def get_category_description(category: str) -> str:
    """
    Gibt Beschreibung für Tool-Kategorie zurück.
    
    Args:
        category: Kategorie-Name
        
    Returns:
        str: Kategorie-Beschreibung
    """
    descriptions = {
        "pressure": "Druckbehälter, Kesselformeln, Druckberechnungen",
        "geometry": "Flächenberechnungen, Volumen, geometrische Formeln",
        "materials": "Werkstoffkennwerte, Festigkeitsberechnungen",
        "thermodynamics": "Wärmeübertragung, Zustandsänderungen",
        "statics": "Statik, Kräfte, Momente, Balkenberechnung"
    }
    return descriptions.get(category, f"{category.title()}-bezogene Engineering-Tools")


async def discover_tools(mcp_instance: Any) -> int:
    """
    Alias für discover_engineering_tools() zur Kompatibilität.
    
    Args:
        mcp_instance: FastMCP Instanz (wird ignoriert)
        
    Returns:
        int: Anzahl der entdeckten Tools
    """
    return await discover_engineering_tools()


async def get_tool_details(tool_name: str) -> Dict:
    """
    Liefert vollständige Dokumentation für ein spezifisches Tool.
    
    ⚡ TARGET-SYSTEM: Generiert Schema für alle-Parameter-required mit target-Unterstützung
    
    Args:
        tool_name: Name des Tools
        
    Returns:
        Dict: Ausführliche Tool-Dokumentation
        
    Raises:
        ValueError: Bei unbekanntem Tool
    """
    if tool_name not in _ENGINEERING_TOOLS_REGISTRY:
        available_tools = list(_ENGINEERING_TOOLS_REGISTRY.keys())
        raise ValueError(f"Unknown tool: {tool_name}. The tool name is incorrect. Use list_engineering_tools(tags=['all']) to see all available tools, or call the tool list_engineering_tools with a corresponding tag.")
    
    tool_data = _ENGINEERING_TOOLS_REGISTRY[tool_name]
    
    # Basis-Informationen
    details = {
        "tool_name": tool_name,
        "name": tool_name,
        "tags": tool_data.get('tags', []),
        "short_description": tool_data.get('short_description', tool_data.get('description', '').split('.')[0]),
        "full_description": tool_data.get('description', ''),

        "has_solving": tool_data.get('has_solving', 'symbolic')  # ⚡ NEUE PARAMETER-STRUKTUR
    }
    
    # ⚡ NUR NEUE STRUKTUR: Parameters aus Metadaten
    if 'metadata' in tool_data and 'parameters' in tool_data['metadata']:
        # Neue Struktur: Parameters in Metadaten
        details['target_parameters'] = list(tool_data['metadata']['parameters'].keys())
        
        # Weitere Metadaten aus neuer Struktur
        metadata = tool_data['metadata']
        if 'examples' in metadata:
            details['examples'] = metadata['examples']
        if 'parameters' in metadata:
            details['parameters'] = metadata['parameters']
        if 'output' in metadata:
            details['output'] = metadata['output']
    else:
        raise ValueError(f"Tool {tool_name} has no metadata - old structure not supported!")
    
    # ⚡ TARGET-BASIERTES INPUT SCHEMA: Alle Parameter required!
    if details.get('target_parameters') and tool_data.get('has_solving', 'symbolic') != 'none':
        # Target-basiertes Schema: Alle Parameter sind required
        schema_properties = {}
        for var in details['target_parameters']:
            # Prüfe ob Parameter Batch-Support hat
            param_info = details.get('parameters', {}).get(var, {})
            param_type = param_info.get('type', 'string')
            
            if 'array' in param_type:
                # Batch-fähiger Parameter
                schema_properties[var] = {
                    "oneOf": [
                        {
                            "type": "string",
                            "description": f"Einzelwert für {var} mit Einheit (z.B. '100 mm') oder 'target' für Berechnung"
                        },
                        {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": f"Batch-Modus: Liste von Werten für {var} - ALLE Parameter müssen Listen gleicher Länge sein"
                        }
                    ]
                }
            else:
                # Standard Parameter
                schema_properties[var] = {
                    "type": "string",
                    "description": f"Wert für {var} mit Einheit (z.B. '100 mm') oder 'target' für Berechnung"
                }
        
        details['input_schema'] = {
            "type": "object",
            "properties": schema_properties,
            "required": details['target_parameters'],  # ⚡ ALLE Parameter sind required!
            "additionalProperties": False,
            "description": f"Alle {len(details['target_parameters'])} Parameter müssen angegeben werden. Ein Parameter als 'target', die anderen mit Einheiten. 🔄 BATCH-MODUS: ALLE Parameter als Listen gleicher Länge für Massenberechnungen."
        }
        
        details['output_schema'] = {
            "oneOf": [
                {
                    "type": "object",
                    "title": "Einzelberechnung",
                    "properties": {
                        "target_parameter": {"type": "string", "description": "Der berechnete Parameter"},
                        "ergebnis": {"type": "object", "description": "Berechnungsergebnis mit Einheit"},
                        "gegebene_werte": {"type": "object", "description": "Die angegebenen Eingabewerte"},
                        "formel": {"type": "string", "description": "Die verwendete Formel"},
                        "hinweise": {"type": "array", "description": "Zusätzliche Berechnungshinweise"}
                    }
                },
                {
                    "type": "object",
                    "title": "Batch-Berechnung",
                    "properties": {
                        "batch_mode": {"type": "boolean", "description": "Immer true für Batch-Berechnungen"},
                        "total_calculations": {"type": "integer", "description": "Gesamtanzahl der durchgeführten Berechnungen"},
                        "successful": {"type": "integer", "description": "Anzahl erfolgreich abgeschlossener Berechnungen"},
                        "failed": {"type": "integer", "description": "Anzahl fehlgeschlagener Berechnungen"},
                        "results": {
                            "type": "array",
                            "description": "Liste aller Ergebnisse mit batch_index und input_combination",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "batch_index": {"type": "integer", "description": "Index des Parametersatzes"},
                                    "input_combination": {"type": "object", "description": "Verwendete Eingabeparameter"},
                                    "target_parameter": {"type": "string", "description": "Der berechnete Parameter"},
                                    "ergebnis": {"type": "object", "description": "Berechnungsergebnis mit Einheit"},
                                    "error": {"type": "string", "description": "Fehlermeldung bei fehlgeschlagener Berechnung"}
                                }
                            }
                        }
                    }
                }
            ]
        }
        
        # ⚡ TARGET-BASIERTE Verwendungshinweise
        details['usage_hints'] = []
        
        # Einzelberechnung-Hinweise
        for var in details['target_parameters']:
            other_vars = [v for v in details['target_parameters'] if v != var]
            example_params = {var: "'target'"}
            for other_var in other_vars[:2]:  # Maximal 2 Beispiele
                example_params[other_var] = f"'Beispielwert einheit'"
            
            details['usage_hints'].append(
                f"Einzelberechnung {var}: {example_params}"
            )
        
        # Batch-Beispiel hinzufügen
        batch_examples = {}
        if 'parameters' in details:
            for param_name, param_info in details['parameters'].items():
                if isinstance(param_info, dict) and 'batch_example' in param_info:
                    batch_examples[param_name] = param_info['batch_example']
        
        if batch_examples:
            details['usage_hints'].append(
                f"🔄 Batch-Berechnung (alle Parameter als Listen): {batch_examples}"
            )
    else:
        # Alle anderen Tools: Standard-Schema aus Metadaten
        if 'parameters' in details:
            details['input_schema'] = {
                "type": "object", 
                "properties": details['parameters'],
                "required": list(details['parameters'].keys()),
                "additionalProperties": False
            }
    
            # Usage hints für alle Tools
            details['usage_hints'] = [
                f"Tool mit {len(details['parameters'])} Parametern",
                "Alle Parameter sind erforderlich",
                "Parameter-Schema aus Metadaten generiert"
            ]
    
    # TARGET-PARAMETER-FORMAT-HINWEIS
    if tool_data.get('has_solving', 'symbolic') != 'none':
        details['parameter_format'] = {
            "system": "TARGET-PARAMETER-SYSTEM",
            "important": "Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!",
            "target_examples": [
                "'target'", "'TARGET'", "'Target'"
            ],
            "value_examples": [
                '"100 bar"', '"50 mm"', '"200 MPa"', '"5 cm"', '"25.5 cm²"', '"523 cm³"'
            ],
            "invalid_examples": [
                "null (leer)", "100 (ohne Einheit)", "fehlender Parameter"
            ]
        }
        
        # 🔄 BATCH-MODE INFORMATIONEN
        details['batch_mode'] = {
            "supported": True,
            "description": "Unterstützt Listen von Parametern für Massenberechnungen",
            "rules": [
                "ALLE Parameter müssen Listen gleicher Länge sein",
                "Jeder Index repräsentiert einen vollständigen Parametersatz",
                "Keine Mischung von Listen und einzelnen Werten erlaubt"
            ],
            "advantages": [
                "Unbegrenzte Anzahl von Berechnungen in einem Aufruf",
                "Vollständige Nachverfolgbarkeit mit batch_index",
                "Strukturierte Batch-Antworten mit Erfolgsstatistiken"
            ]
        }
        
        # Sammle Batch-Beispiele aus Parameter-Metadaten
        batch_examples = {}
        if 'parameters' in details:
            for param_name, param_info in details['parameters'].items():
                if isinstance(param_info, dict) and 'batch_example' in param_info:
                    batch_examples[param_name] = param_info['batch_example']
        
        if batch_examples:
            details['batch_mode']['example_call'] = {
                "description": f"Batch-Aufruf für {tool_name} mit {len(next(iter(batch_examples.values())))} Parametersätzen",
                "input": batch_examples,
                "result": f"Liste von {len(next(iter(batch_examples.values())))} Ergebnissen mit batch_index und input_combination"
            }
        
        # Generiere spezifisches TARGET-Beispiel
        if details.get('target_parameters') and len(details['target_parameters']) >= 2:
            example_params = {}
            example_units = {
                'pressure': '"100 bar"',
                'wall_thickness': '"50 mm"', 
                'diameter': '"500 mm"',
                'allowable_stress': '"200 MPa"',
                'radius': '"25 mm"',
                'area': '"25.5 cm²"',
                'volume': '"523 cm³"',
                'height': '"10 cm"',
                'width': '"5 cm"',
                'length': '"10 cm"',
                'side_a': '"8 cm"',
                'side_c': '"12 cm"',
                'base': '"6 cm"'
            }
            
            # Erstes Parameter = target, andere = Werte
            target_param = details['target_parameters'][0]
            other_params = details['target_parameters'][1:]
            
            example_params[target_param] = '"target"'
            for param in other_params:
                example_params[param] = example_units.get(param, '"10 unit"')
            
            details['parameter_format']['example_call'] = f'call_tool(tool_name="{tool_name}", parameters={example_params})'
    else:
        # Für nicht-symbolische Tools (wie Tabellen-Lookup)
        details['parameter_format'] = {
            "system": "TABLE-TOOL",
            "important": "Geben Sie exakte Parameterwerte an",
            "note": "Keine target-Parameter - alle Werte direkt angeben"
        }
    
    return details 