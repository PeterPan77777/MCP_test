from fastmcp import FastMCP, Context
import datetime
from typing import Optional, Dict, List
from engineering_mcp.registry import (
    get_tool_info_for_llm, 
    get_symbolic_tools_summary,
    call_engineering_tool,
    discover_engineering_tools,
    get_tool_details as get_tool_details_from_registry
)

# MCP Server mit ausführlichen Instructions für LLMs
mcp = FastMCP(
    name="EngineersCalc", 
    instructions="""
Engineering Calculation Server - Symbolische Ingenieurberechnungen

Dieser Server bietet Zugriff auf eine Sammlung von Engineering-Tools, die Formeln 
symbolisch nach verschiedenen Variablen auflösen können.

WICHTIGER WORKFLOW:
1. Nutze IMMER zuerst 'get_available_categories' um verfügbare Kategorien zu sehen
2. Dann 'list_engineering_tools' mit einer spezifischen Kategorie
3. Optional 'get_tool_details' für ausführliche Tool-Dokumentation
4. Schließlich 'calculate_engineering' zur Ausführung

Die Tools verwenden SymPy für symbolische Mathematik und können Formeln nach 
beliebigen Variablen auflösen. Gib immer genau n-1 Parameter an, wenn ein Tool 
n lösbare Variablen hat.

Beispiel: Kesselformel mit 4 Variablen [sigma, p, d, s] - gib 3 an, berechne die 4.
"""
)

@mcp.tool()
def clock() -> str:
    "Aktuelle UTC-Zeit zurückgeben"
    return datetime.datetime.utcnow().isoformat() + "Z"

# ===== Meta-Tools für mehrstufige Discovery =====

@mcp.tool(
    name="get_available_categories",
    description="Gibt alle verfügbaren Engineering-Tool-Kategorien zurück. IMMER ZUERST AUFRUFEN!",
    tags=["discovery", "categories", "meta"]
)
async def get_available_categories(
    ctx: Context = None
) -> Dict:
    """
    Listet alle verfügbaren Kategorien von Engineering-Tools auf.
    
    Args:
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Kategorien mit Tool-Anzahl und Beschreibungen
    """
    if ctx:
        await ctx.info("Sammle verfügbare Tool-Kategorien...")
    
    # Hole Engineering-Tools aus Registry
    tool_info = get_tool_info_for_llm(include_engineering=True)
    
    # Gruppiere nach Kategorien
    categories_info = {}
    
    for tool in tool_info:
        category = tool.get("category", "unknown")
        
        if category not in categories_info:
            categories_info[category] = {
                "name": category,
                "tools": [],
                "tool_count": 0,
                "description": ""
            }
        
        categories_info[category]["tools"].append(tool["name"])
        categories_info[category]["tool_count"] += 1
    
    # Kategorie-Beschreibungen hinzufügen
    from engineering_mcp.registry import get_category_description
    for category, info in categories_info.items():
        info["description"] = get_category_description(category)
    
    if ctx:
        await ctx.info(f"Gefunden: {len(categories_info)} Kategorien")
    
    return {
        "available_categories": list(categories_info.keys()),
        "category_details": categories_info,
        "total_categories": len(categories_info),
        "usage_hint": "Verwende diese Kategorien mit list_engineering_tools(category='...')"
    }

@mcp.tool(
    name="list_engineering_tools",
    description="Listet alle Tools einer spezifischen Kategorie mit Kurzbeschreibungen auf",
    tags=["discovery", "engineering", "meta"]
)
async def list_engineering_tools(
    category: str,
    ctx: Context = None
) -> List[Dict]:
    """
    Listet alle verfügbaren Engineering-Tools einer Kategorie mit Kurzbeschreibungen auf.
    
    Args:
        category: Kategorie-Filter (z.B. "pressure", "geometry") - PFLICHTPARAMETER
        ctx: FastMCP Context für Logging
        
    Returns:
        List[Dict]: Tools mit Namen, Kurzbeschreibung und lösbaren Variablen
    """
    if ctx:
        await ctx.info(f"Sammle Engineering-Tools für Kategorie: {category}")
    
    # Hole Engineering-Tools aus separater Registry
    tool_info = get_tool_info_for_llm(include_engineering=True)
    
    # Filter nach Kategorie
    filtered_tools = [tool for tool in tool_info if category in tool.get("tags", []) or category == tool.get("category")]
    
    # Kompakte Darstellung für Discovery
    compact_tools = []
    for tool in filtered_tools:
        compact_tools.append({
            "name": tool["name"],
            "short_description": tool.get("short_description", tool["description"].split(".")[0]),
            "solvable_variables": tool["solvable_variables"],
            "tags": tool["tags"]
        })
    
    if ctx:
        await ctx.info(f"Gefunden: {len(compact_tools)} Tools in Kategorie {category}")
    
    return compact_tools

@mcp.tool(
    name="get_tool_details",
    description="Ruft detaillierte Informationen zu einem spezifischen Tool ab",
    tags=["discovery", "engineering", "documentation", "meta"]
)
async def get_tool_details(
    tool_name: str,
    ctx: Context = None
) -> Dict:
    """
    Liefert vollständige Dokumentation eines Engineering-Tools.
    
    Args:
        tool_name: Name des Tools (z.B. "solve_kesselformel")
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Ausführliche Tool-Dokumentation mit Parametern, Beispielen und Schema
    """
    if ctx:
        await ctx.info(f"Hole Details für Tool: {tool_name}")
    
    try:
        details = await get_tool_details_from_registry(tool_name)
        
        if ctx:
            await ctx.info(f"Details erfolgreich abgerufen für: {tool_name}")
        
        return details
        
    except ValueError as e:
        if ctx:
            await ctx.error(f"Tool nicht gefunden: {tool_name}")
        
        return {
            "error": str(e),
            "available_tools": "Nutze list_engineering_tools() um verfügbare Tools zu sehen"
        }

@mcp.tool(
    name="calculate_engineering",
    description="Führt ein Engineering-Tool mit den angegebenen Parametern aus",
    tags=["engineering", "execution", "gateway"]
)
async def calculate_engineering(
    tool_name: str,
    parameters: Dict,
    ctx: Context = None
) -> Dict:
    """
    Gateway-Funktion für Engineering-Tool-Ausführung.
    
    Args:
        tool_name: Name des Engineering-Tools
        parameters: Tool-Parameter als Dictionary
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Berechnungsergebnis
        
    Raises:
        ValueError: Bei ungültigen Tools oder Parametern
    """
    if ctx:
        await ctx.info(f"Führe Engineering-Berechnung aus: {tool_name}")
        await ctx.info(f"Parameter: {parameters}")
    
    try:
        result = await call_engineering_tool(tool_name, parameters)
        
        if ctx:
            await ctx.info(f"Berechnung erfolgreich abgeschlossen")
        
        return {
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result,
            "status": "success"
        }
        
    except Exception as e:
        error_msg = f"Fehler bei Engineering-Berechnung '{tool_name}': {e}"
        if ctx:
            await ctx.error(error_msg)
        
        return {
            "tool_name": tool_name,
            "parameters": parameters,
            "error": str(e),
            "status": "error"
        }

# Initialisierung beim Server-Start
async def init_engineering_tools():
    """Lädt Engineering-Tools beim Server-Start"""
    tools_count = await discover_engineering_tools()
    print(f"✅ {tools_count} Engineering-Tools entdeckt")
    print(f"✅ 4 Meta-Tools + 1 Utility-Tool (clock) bereit")
    print(f"🎯 Mehrstufige Discovery aktiviert:")
    print(f"   1. get_available_categories")
    print(f"   2. list_engineering_tools")  
    print(f"   3. get_tool_details")
    print(f"   4. calculate_engineering")
    return tools_count 