from fastmcp import FastMCP, Context
import datetime
from typing import Optional, Dict, List
from engineering_mcp.registry import (
    get_tool_info_for_llm, 
    discover_engineering_tools,
    get_tool_details_from_mcp
)

# MCP Server mit ausführlichen Instructions für LLMs
mcp = FastMCP(
    name="EngineersCalc", 
    instructions="""
🔧 Engineering Calculation Server - Symbolische Ingenieurberechnungen

📋 ÜBERSICHT:
Dieser Server bietet Zugriff auf eine Sammlung von Engineering-Tools, die Formeln 
symbolisch nach verschiedenen Variablen auflösen können. Alle Tools verwenden SymPy
für exakte mathematische Berechnungen.

🎯 WICHTIGER WORKFLOW (IMMER IN DIESER REIHENFOLGE):
1️⃣ get_available_categories() - Zeigt verfügbare Tool-Kategorien
2️⃣ list_engineering_tools(category="...") - Listet Tools einer Kategorie  
3️⃣ get_tool_details(tool_name="...") - Optional: Detaillierte Tool-Info
4️⃣ TOOL_DIREKT_AUFRUFEN - z.B. solve_kesselformel(p=10, d=100, sigma=160)

⚙️ KERNKONZEPT - Symbolische Variablen-Auflösung:
- Jedes Tool implementiert EINE Formel mit mehreren Variablen
- Du gibst n-1 Variablen an, das Tool berechnet die fehlende Variable
- Beispiel: Kesselformel σ = p·d/(2·s) hat 4 Variablen [sigma, p, d, s]
  → Gib 3 Werte an: solve_kesselformel(p=10, d=100, sigma=160)
  → Tool berechnet die 4. Variable (hier: s=3.125)

📂 VERFÜGBARE KATEGORIEN:
- pressure: Druckbehälter, Kesselformeln
- geometry: Flächen, Volumen, geometrische Berechnungen
- materials: Werkstoffkennwerte, Festigkeitsberechnungen
- (weitere Kategorien über get_available_categories() erkunden)

💡 TIPPS:
- Starte IMMER mit get_available_categories()
- Nutze get_tool_details() wenn Parameter unklar sind
- Alle physikalischen Werte müssen positiv sein
- Achte auf Einheiten (werden in Tool-Details angegeben)
- Nach Discovery: Rufe Tools DIREKT auf (z.B. solve_circle_area(radius=10))

🔍 BEISPIEL-WORKFLOW:
1. categories = get_available_categories()
2. tools = list_engineering_tools(category="pressure")
3. details = get_tool_details(tool_name="solve_kesselformel")  # Optional
4. result = solve_kesselformel(p=10, d=100, sigma=160)  # DIREKT!
"""
)

@mcp.tool()
def clock() -> str:
    "Aktuelle UTC-Zeit zurückgeben"
    return datetime.datetime.utcnow().isoformat() + "Z"

# ===== Meta-Tools für Discovery (Handshake sichtbar) =====

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
    
    # Hole Engineering-Tools direkt von MCP
    tool_info = get_tool_info_for_llm(mcp_instance=mcp)
    
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
    
    # Hole Engineering-Tools direkt von MCP
    tool_info = get_tool_info_for_llm(mcp_instance=mcp)
    
    # Filter nach Kategorie
    filtered_tools = [tool for tool in tool_info if category in tool.get("tags", []) or category == tool.get("category")]
    
    # Kompakte Darstellung für Discovery
    compact_tools = []
    for tool in filtered_tools:
        compact_tools.append({
            "name": tool["name"],
            "short_description": tool.get("short_description", tool["description"].split(".")[0]),
            "solvable_variables": tool["solvable_variables"],
            "tags": tool["tags"],
            "call_example": f"{tool['name']}(...)"
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
        details = await get_tool_details_from_mcp(tool_name, mcp_instance=mcp)
        
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

# Initialisierung beim Server-Start
async def init_engineering_tools():
    """Lädt und registriert Engineering-Tools direkt bei MCP"""
    tools_count = await discover_engineering_tools(mcp_instance=mcp)
    print(f"✅ {tools_count} Engineering-Tools direkt bei MCP registriert")
    print(f"✅ 3 Discovery-Tools + 1 Utility-Tool (clock) bereit")
    print(f"🎯 Hybrid-Discovery aktiviert:")
    print(f"   1. get_available_categories")
    print(f"   2. list_engineering_tools")  
    print(f"   3. get_tool_details")
    print(f"   4. DIREKTE Tool-Aufrufe (z.B. solve_kesselformel(...))")
    return tools_count 