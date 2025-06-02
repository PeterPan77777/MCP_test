"""
Tool-Registry und Discovery-System für Engineering MCP

Verwaltet die separate Registry für Engineering-Tools und 
bietet Discovery-Funktionen für LLM-Orchestrierung.
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
    
    Returns:
        int: Anzahl der entdeckten Engineering-Tools
    """
    global _ENGINEERING_TOOLS_REGISTRY
    _ENGINEERING_TOOLS_REGISTRY.clear()
    
    try:
        # Dynamischer Import aller Tool-Module
        import tools
        
        # Iteriere durch alle Submodule in tools/
        for category_finder, category_name, ispkg in pkgutil.iter_modules(tools.__path__, tools.__name__ + "."):
            if ispkg:
                # Importiere Kategorie-Modul (z.B. tools.pressure)
                category_module = importlib.import_module(category_name)
                
                # Iteriere durch alle Tool-Module in der Kategorie
                for tool_finder, tool_name, _ in pkgutil.iter_modules(
                    category_module.__path__, 
                    category_name + "."
                ):
                    try:
                        # Importiere das Tool-Modul
                        tool_module = importlib.import_module(tool_name)
                        
                        # Suche nach TOOL_METADATA
                        if hasattr(tool_module, 'TOOL_METADATA'):
                            metadata = tool_module.TOOL_METADATA
                            tool_func = metadata.get('function')
                            
                            if tool_func and callable(tool_func):
                                # Speichere in separater Registry
                                tool_id = metadata.get('name', tool_func.__name__)
                                _ENGINEERING_TOOLS_REGISTRY[tool_id] = {
                                    **metadata,
                                    'category': category_name.split('.')[-1],
                                    'module': tool_module
                                }
                                print(f"✅ Entdeckt: {tool_id} in {category_name.split('.')[-1]}")
                    except Exception as e:
                        print(f"❌ Fehler beim Laden von {tool_name}: {e}")
                        
    except ImportError:
        print("ℹ️ Keine Engineering-Tools gefunden (tools/ Verzeichnis fehlt)")
        return 0
    
    return len(_ENGINEERING_TOOLS_REGISTRY)


def get_tool_info_for_llm(include_engineering: bool = True) -> List[Dict]:
    """
    Erstellt strukturierte Tool-Informationen für LLM-Discovery.
    
    Args:
        include_engineering: Engineering-Tools einbeziehen
        
    Returns:
        List[Dict]: Tool-Informationen mit solvable_variables
    """
    tool_info = []
    
    if include_engineering:
        for tool_name, tool_data in _ENGINEERING_TOOLS_REGISTRY.items():
            # Extrahiere lösbare Variablen aus der Beschreibung
            solvable_vars = []
            description = tool_data.get('description', '')
            
            # Parse: "Lösbare Variablen: [var1, var2, var3]"
            match = re.search(r'Lösbare Variablen:\s*\[([^\]]+)\]', description)
            if match:
                vars_str = match.group(1)
                solvable_vars = [var.strip() for var in vars_str.split(',')]
            
            tool_info.append({
                "name": tool_name,
                "description": description,
                "tags": tool_data.get('tags', []),
                "category": tool_data.get('category', 'unknown'),
                "solvable_variables": solvable_vars,
                "is_symbolic": "symbolic" in tool_data.get('tags', []),
                "source": "engineering_registry"
            })
    
    return tool_info


def get_symbolic_tools_summary() -> Dict:
    """
    Erstellt eine kategorisierte Übersicht aller symbolischen Tools.
    
    Returns:
        Dict: Strukturierte Übersicht mit Formeln und lösbaren Variablen
    """
    summary = {
        "total_tools": 0,
        "categories": {},
        "symbolic_tools": []
    }
    
    for tool_name, tool_data in _ENGINEERING_TOOLS_REGISTRY.items():
        if "symbolic" in tool_data.get('tags', []):
            category = tool_data.get('category', 'unknown')
            
            # Kategorie initialisieren falls noch nicht vorhanden
            if category not in summary["categories"]:
                summary["categories"][category] = {
                    "tools": [],
                    "description": get_category_description(category)
                }
            
            # Tool-Info sammeln
            tool_info = {
                "name": tool_name,
                "description": tool_data.get('description', ''),
                "solvable_variables": extract_solvable_variables(tool_data.get('description', ''))
            }
            
            summary["categories"][category]["tools"].append(tool_info)
            summary["symbolic_tools"].append(tool_info)
    
    summary["total_tools"] = len(summary["symbolic_tools"])
    return summary


async def call_engineering_tool(tool_name: str, parameters: Dict) -> Any:
    """
    Führt ein Engineering-Tool aus der Registry aus.
    
    Args:
        tool_name: Name des Tools
        parameters: Tool-Parameter
        
    Returns:
        Any: Tool-Ergebnis
        
    Raises:
        ValueError: Bei unbekanntem Tool
    """
    if tool_name not in _ENGINEERING_TOOLS_REGISTRY:
        available_tools = list(_ENGINEERING_TOOLS_REGISTRY.keys())
        raise ValueError(f"Unbekanntes Tool: {tool_name}. Verfügbare Tools: {available_tools}")
    
    tool_data = _ENGINEERING_TOOLS_REGISTRY[tool_name]
    tool_func = tool_data.get('function')
    
    if not tool_func:
        raise ValueError(f"Tool {tool_name} hat keine ausführbare Funktion")
    
    # Führe Tool aus (async wenn möglich)
    if asyncio.iscoroutinefunction(tool_func):
        return await tool_func(**parameters)
    else:
        return tool_func(**parameters)


def extract_solvable_variables(description: str) -> List[str]:
    """
    Extrahiert lösbare Variablen aus Tool-Beschreibung.
    
    Unterstützt verschiedene Formate:
    - "Lösbare Variablen: [var1, var2, var3]"
    - "Lösbare Variablen: var1, var2, var3"
    
    Args:
        description: Tool-Beschreibung
        
    Returns:
        List[str]: Liste der lösbaren Variablen
    """
    # Format 1: Mit eckigen Klammern [var1, var2, var3]
    match = re.search(r'Lösbare Variablen:\s*\[([^\]]+)\]', description)
    if match:
        vars_str = match.group(1)
        return [var.strip() for var in vars_str.split(',')]
    
    # Format 2: Ohne eckige Klammern, aber mit Kommas var1, var2, var3
    match = re.search(r'Lösbare Variablen:\s*([^\n\r]+)', description)
    if match:
        vars_line = match.group(1).strip()
        # Entferne mögliche nachgestellte Texte nach dem ersten Punkt oder Absatz
        vars_line = vars_line.split('.')[0].split('\n')[0].strip()
        return [var.strip() for var in vars_line.split(',')]
    
    return []


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
    
    Args:
        tool_name: Name des Tools
        
    Returns:
        Dict: Ausführliche Tool-Dokumentation
        
    Raises:
        ValueError: Bei unbekanntem Tool
    """
    if tool_name not in _ENGINEERING_TOOLS_REGISTRY:
        available_tools = list(_ENGINEERING_TOOLS_REGISTRY.keys())
        raise ValueError(f"Unbekanntes Tool: {tool_name}. Verfügbare Tools: {available_tools}")
    
    tool_data = _ENGINEERING_TOOLS_REGISTRY[tool_name]
    
    # Basis-Informationen
    details = {
        "name": tool_name,
        "category": tool_data.get('category', 'unknown'),
        "tags": tool_data.get('tags', []),
        "short_description": tool_data.get('short_description', tool_data['description'].split('.')[0]),
        "full_description": tool_data.get('description', ''),
        "solvable_variables": extract_solvable_variables(tool_data.get('description', ''))
    }
    
    # Erweiterte Informationen falls vorhanden
    if 'examples' in tool_data:
        details['examples'] = tool_data['examples']
    
    if 'input_schema' in tool_data:
        details['input_schema'] = tool_data['input_schema']
    
    if 'output_schema' in tool_data:
        details['output_schema'] = tool_data['output_schema']
    
    # Standard Input/Output Schema basierend auf lösbaren Variablen
    if 'input_schema' not in details and details['solvable_variables']:
        details['input_schema'] = {
            "type": "object",
            "properties": {
                var: {
                    "type": "number",
                    "description": f"Wert für {var} (optional)"
                } for var in details['solvable_variables']
            },
            "additionalProperties": False,
            "minProperties": len(details['solvable_variables']) - 1,
            "maxProperties": len(details['solvable_variables']) - 1,
            "description": f"Genau {len(details['solvable_variables']) - 1} von {len(details['solvable_variables'])} Parametern müssen angegeben werden"
        }
    
    if 'output_schema' not in details:
        details['output_schema'] = {
            "type": "object",
            "properties": {
                "unknown_variable": {"type": "string", "description": "Die berechnete Variable"},
                "result": {"type": "number", "description": "Der berechnete Wert"},
                "unit": {"type": "string", "description": "Einheit des Ergebnisses"},
                "formula": {"type": "string", "description": "Die verwendete Formel"},
                "solution_expression": {"type": "string", "description": "Die Lösungsformel"},
                "calculation_steps": {"type": "string", "description": "Berechnungsschritte"}
            }
        }
    
    # Verwendungshinweise generieren
    if details['solvable_variables']:
        details['usage_hints'] = []
        for i, var in enumerate(details['solvable_variables']):
            other_vars = [v for v in details['solvable_variables'] if v != var]
            details['usage_hints'].append(
                f"Um {var} zu berechnen: Gib {', '.join(other_vars)} an"
            )
    
    # ⭐ PARAMETER-FORMAT-HINWEIS hinzufügen
    details['parameter_format'] = {
        "wichtig": "🎯 Alle Parameter benötigen EINHEITEN! Format: 'Wert Einheit'",
        "korrekte_beispiele": [
            '"100 bar"', '"50 mm"', '"200 MPa"', '"5 cm"', '"25.5 cm²"', '"523 cm³"'
        ],
        "falsche_beispiele": [
            "100 (ohne Einheit)", "50.0 (ohne Einheit)", "null (leer)"
        ],
        "tolerante_eingabe": "Der Server kann verschiedene Formate reparieren, aber korrekte JSON-Syntax ist am sichersten"
    }
    
    # Generiere spezifisches Beispiel basierend auf lösbaren Variablen
    if details['solvable_variables'] and len(details['solvable_variables']) >= 2:
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
        
        # Verwende die ersten n-1 Variablen für das Beispiel
        example_vars = details['solvable_variables'][:-1]
        for var in example_vars:
            # Finde passende Einheit oder verwende Fallback
            example_params[var] = example_units.get(var, '"10 unit"')
        
        details['parameter_format']['korrekte_aufruf_syntax'] = f'call_tool(tool_name="{tool_name}", parameters={example_params})'
    
    return details 