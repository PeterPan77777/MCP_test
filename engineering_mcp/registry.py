"""
Tool-Registry und Discovery-System für Engineering MCP

Registriert Engineering-Tools DYNAMISCH nach Discovery bei MCP.
Tools sind beim Handshake versteckt, werden aber nach Discovery direkt verfügbar.
"""

import re
import pkgutil
import importlib
from typing import Dict, List, Optional, Any, Callable
import asyncio


# Globaler Registry-Cache für intern verfügbare Tools
_engineering_tools_registry: Dict[str, Dict] = {}
_mcp_instance = None


async def discover_engineering_tools(mcp_instance: Any) -> int:
    """
    Entdeckt Engineering-Tools und speichert sie INTERN für dynamische Registrierung.
    Tools werden NICHT beim Handshake gezeigt, aber nach Discovery bei MCP registriert.
    
    Args:
        mcp_instance: FastMCP Instanz
        
    Returns:
        int: Anzahl der entdeckten Engineering-Tools
    """
    global _engineering_tools_registry, _mcp_instance
    _mcp_instance = mcp_instance
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
                                # Tool-Tags für Discovery erweitern
                                tool_id = metadata.get('name', tool_func.__name__)
                                tags = metadata.get('tags', [])
                                category = category_name.split('.')[-1]
                                if category not in tags:
                                    tags.append(category)
                                tags.append('engineering')
                                
                                # Speichere Tool in INTERNER Registry für dynamische Registrierung
                                _engineering_tools_registry[tool_id] = {
                                    **metadata,
                                    'category': category,
                                    'tags': tags,
                                    'is_registered': False  # Noch nicht bei MCP registriert
                                }
                                
                                tools_count += 1
                                print(f"🔧 Engineering-Tool bereit: {tool_id} in Kategorie {category}")
                                
                    except Exception as e:
                        print(f"❌ Fehler beim Laden von {tool_name}: {e}")
                        
    except ImportError:
        print("ℹ️ Keine Engineering-Tools gefunden (tools/ Verzeichnis fehlt)")
        return 0
    
    print(f"✅ {tools_count} Engineering-Tools bereit für dynamische Registrierung")
    return tools_count


def register_tool_with_mcp(tool_name: str) -> bool:
    """
    Registriert ein Engineering-Tool dynamisch bei MCP (nach Discovery).
    
    Args:
        tool_name: Name des Tools
        
    Returns:
        bool: True wenn erfolgreich registriert
    """
    global _engineering_tools_registry, _mcp_instance
    
    if not _mcp_instance:
        print(f"❌ MCP-Instanz nicht verfügbar für Tool: {tool_name}")
        return False
    
    if tool_name not in _engineering_tools_registry:
        print(f"❌ Tool nicht gefunden: {tool_name}")
        return False
    
    tool_data = _engineering_tools_registry[tool_name]
    
    # Prüfe ob bereits registriert
    if tool_data.get('is_registered', False):
        print(f"✅ Tool bereits registriert: {tool_name}")
        return True
    
    try:
        # Registriere Tool bei MCP
        tool_func = tool_data.get('function')
        if tool_func and callable(tool_func):
            # Bei MCP registrieren
            _mcp_instance.tool(
                name=tool_name,
                description=tool_data.get('short_description', tool_data.get('description', '')),
                tags=tool_data.get('tags', [])
            )(tool_func)
            
            # Markiere als registriert
            _engineering_tools_registry[tool_name]['is_registered'] = True
            print(f"🎯 Tool dynamisch registriert: {tool_name}")
            return True
            
    except Exception as e:
        print(f"❌ Fehler bei Tool-Registrierung {tool_name}: {e}")
        return False
    
    return False


def register_all_tools_with_mcp() -> int:
    """
    Registriert ALLE Engineering-Tools dynamisch bei MCP.
    
    Returns:
        int: Anzahl der erfolgreich registrierten Tools
    """
    global _engineering_tools_registry
    registered_count = 0
    
    for tool_name in _engineering_tools_registry.keys():
        if register_tool_with_mcp(tool_name):
            registered_count += 1
    
    print(f"🚀 {registered_count} Tools dynamisch bei MCP registriert")
    return registered_count


def register_category_tools_with_mcp(category: str) -> int:
    """
    Registriert alle Tools einer Kategorie dynamisch bei MCP.
    
    Args:
        category: Kategorie-Name
        
    Returns:
        int: Anzahl der registrierten Tools
    """
    global _engineering_tools_registry
    registered_count = 0
    
    for tool_name, tool_data in _engineering_tools_registry.items():
        if tool_data.get('category') == category:
            if register_tool_with_mcp(tool_name):
                registered_count += 1
    
    print(f"🚀 {registered_count} Tools aus Kategorie '{category}' registriert")
    return registered_count


def get_tool_info_for_llm(mcp_instance: Any) -> List[Dict]:
    """
    Erstellt strukturierte Tool-Informationen aus der internen Registry.
    
    Args:
        mcp_instance: FastMCP Instanz
        
    Returns:
        List[Dict]: Tool-Informationen mit solvable_variables
    """
    global _engineering_tools_registry
    tool_info = []
    
    # Durchlaufe alle intern registrierten Tools
    for tool_name, tool_data in _engineering_tools_registry.items():
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
            "is_registered": tool_data.get('is_registered', False),
            "source": "dynamic_registry"
        })
    
    return tool_info


async def get_tool_details_from_mcp(tool_name: str, mcp_instance: Any) -> Dict:
    """
    Liefert vollständige Dokumentation für ein intern registriertes Tool.
    Registriert das Tool automatisch bei MCP falls noch nicht geschehen.
    
    Args:
        tool_name: Name des Tools
        mcp_instance: FastMCP Instanz
        
    Returns:
        Dict: Ausführliche Tool-Dokumentation
        
    Raises:
        ValueError: Bei unbekanntem Tool
    """
    global _engineering_tools_registry
    
    if tool_name not in _engineering_tools_registry:
        available_tools = list(_engineering_tools_registry.keys())
        raise ValueError(f"Unbekanntes Tool: {tool_name}. Verfügbare Tools: {available_tools}")
    
    tool_data = _engineering_tools_registry[tool_name]
    
    # Automatische Registrierung bei MCP wenn Details abgerufen werden
    if not tool_data.get('is_registered', False):
        register_tool_with_mcp(tool_name)
    
    # Basis-Informationen
    details = {
        "name": tool_name,
        "category": tool_data.get('category', 'unknown'),
        "tags": tool_data.get('tags', []),
        "short_description": tool_data.get('short_description', tool_data['description'].split('.')[0]),
        "full_description": tool_data.get('description', ''),
        "solvable_variables": extract_solvable_variables(tool_data.get('description', '')),
        "is_registered": tool_data.get('is_registered', False)
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
        
        # Hinweis auf dynamische Registrierung
        if tool_data.get('is_registered', False):
            details['call_status'] = "✅ Tool ist jetzt direkt verfügbar"
        else:
            details['call_status'] = "🔄 Tool wird beim nächsten Aufruf registriert"
    
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


def get_available_tools_list() -> List[str]:
    """
    Gibt eine Liste aller verfügbaren Engineering-Tool-Namen zurück.
    
    Returns:
        List[str]: Tool-Namen
    """
    global _engineering_tools_registry
    return list(_engineering_tools_registry.keys())


def get_registered_tools_list() -> List[str]:
    """
    Gibt eine Liste aller bei MCP registrierten Tools zurück.
    
    Returns:
        List[str]: Registrierte Tool-Namen
    """
    global _engineering_tools_registry
    return [name for name, data in _engineering_tools_registry.items() 
            if data.get('is_registered', False)]


def get_tools_by_category() -> Dict[str, List[str]]:
    """
    Gibt Tools nach Kategorien gruppiert zurück.
    
    Returns:
        Dict[str, List[str]]: Kategorien -> Tool-Namen
    """
    global _engineering_tools_registry
    categories = {}
    
    for tool_name, tool_data in _engineering_tools_registry.items():
        category = tool_data.get('category', 'unknown')
        if category not in categories:
            categories[category] = []
        categories[category].append(tool_name)
    
    return categories 