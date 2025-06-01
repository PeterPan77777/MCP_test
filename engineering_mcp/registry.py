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


async def discover_tools(mcp_instance: Any) -> int:
    """
    Alias für discover_engineering_tools() zur Kompatibilität.
    
    Args:
        mcp_instance: FastMCP Instanz (wird ignoriert)
        
    Returns:
        int: Anzahl der entdeckten Tools
    """
    return await discover_engineering_tools() 