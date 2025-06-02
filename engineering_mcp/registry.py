"""
Tool-Registry und Discovery-System für Engineering MCP

Registriert Engineering-Tools direkt bei MCP und bietet Discovery-Funktionen.
"""

import re
import pkgutil
import importlib
from typing import Dict, List, Optional, Any, Callable
import asyncio


async def discover_engineering_tools(mcp_instance: Any) -> int:
    """
    Entdeckt Engineering-Tools und registriert sie DIREKT bei MCP.
    
    Args:
        mcp_instance: FastMCP Instanz
        
    Returns:
        int: Anzahl der registrierten Engineering-Tools
    """
    tools_count = 0
    
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
                                # Registriere Tool DIREKT bei MCP
                                tool_id = metadata.get('name', tool_func.__name__)
                                
                                # Tool-Tags für Discovery erweitern
                                tags = metadata.get('tags', [])
                                category = category_name.split('.')[-1]
                                if category not in tags:
                                    tags.append(category)
                                tags.append('engineering')
                                
                                # Bei MCP registrieren mit discovery-Tags
                                mcp_instance.tool(
                                    name=tool_id,
                                    description=metadata.get('short_description', metadata.get('description', '')),
                                    tags=tags
                                )(tool_func)
                                
                                # Store metadata for discovery
                                if not hasattr(mcp_instance, '_engineering_metadata'):
                                    mcp_instance._engineering_metadata = {}
                                
                                mcp_instance._engineering_metadata[tool_id] = {
                                    **metadata,
                                    'category': category
                                }
                                
                                tools_count += 1
                                print(f"✅ Registriert: {tool_id} in Kategorie {category}")
                                
                    except Exception as e:
                        print(f"❌ Fehler beim Laden von {tool_name}: {e}")
                        
    except ImportError:
        print("ℹ️ Keine Engineering-Tools gefunden (tools/ Verzeichnis fehlt)")
        return 0
    
    return tools_count


def get_tool_info_for_llm(mcp_instance: Any) -> List[Dict]:
    """
    Erstellt strukturierte Tool-Informationen aus direkt bei MCP registrierten Tools.
    
    Args:
        mcp_instance: FastMCP Instanz
        
    Returns:
        List[Dict]: Tool-Informationen mit solvable_variables
    """
    tool_info = []
    
    # Hole Engineering-Metadaten falls vorhanden
    engineering_metadata = getattr(mcp_instance, '_engineering_metadata', {})
    
    # Durchlaufe alle bei MCP registrierten Tools
    for tool_name, tool_data in engineering_metadata.items():
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
            "short_description": tool_data.get('short_description', description.split('.')[0]),
            "description": description,
            "tags": tool_data.get('tags', []),
            "category": tool_data.get('category', 'unknown'),
            "solvable_variables": solvable_vars,
            "is_symbolic": "symbolic" in tool_data.get('tags', []),
            "source": "mcp_direct"
        })
    
    return tool_info


async def get_tool_details_from_mcp(tool_name: str, mcp_instance: Any) -> Dict:
    """
    Liefert vollständige Dokumentation für ein bei MCP registriertes Tool.
    
    Args:
        tool_name: Name des Tools
        mcp_instance: FastMCP Instanz
        
    Returns:
        Dict: Ausführliche Tool-Dokumentation
        
    Raises:
        ValueError: Bei unbekanntem Tool
    """
    # Hole Engineering-Metadaten
    engineering_metadata = getattr(mcp_instance, '_engineering_metadata', {})
    
    if tool_name not in engineering_metadata:
        available_tools = list(engineering_metadata.keys())
        raise ValueError(f"Unbekanntes Tool: {tool_name}. Verfügbare Tools: {available_tools}")
    
    tool_data = engineering_metadata[tool_name]
    
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
                f"Um {var} zu berechnen: {tool_name}({', '.join([f'{v}=...' for v in other_vars])})"
            )
    
    # Direkt-Aufruf Beispiel
    if details['solvable_variables']:
        example_vars = details['solvable_variables'][:-1]  # Alle außer der letzten
        example_call = f"{tool_name}({', '.join([f'{v}=...' for v in example_vars])})"
        details['direct_call_example'] = example_call
    
    return details


def extract_solvable_variables(description: str) -> List[str]:
    """
    Extrahiert lösbare Variablen aus Tool-Beschreibung.
    
    Args:
        description: Tool-Beschreibung
        
    Returns:
        List[str]: Liste der lösbaren Variablen
    """
    match = re.search(r'Lösbare Variablen:\s*\[([^\]]+)\]', description)
    if match:
        vars_str = match.group(1)
        return [var.strip() for var in vars_str.split(',')]
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