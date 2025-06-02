from fastmcp import FastMCP, Context
import datetime
from typing import Optional, Dict, List
from engineering_mcp.registry import (
    get_tool_info_for_llm, 
    discover_engineering_tools,
    get_tool_details_from_mcp
)

# MCP Server mit Progressive Tool Disclosure
mcp = FastMCP(
    name="EngineersCalc", 
    instructions="""
🔧 Engineering Calculation Server - Progressive Tool Disclosure

📋 ÜBERSICHT:
Dieser Server nutzt Progressive Tool Disclosure - beim Handshake siehst du nur 3 Discovery-Tools.
Engineering-Tools werden erst nach Detailabfrage sichtbar und aufrufbar.

🎯 PROGRESSIVE DISCOVERY WORKFLOW:
1️⃣ get_available_categories() - Zeigt verfügbare Tool-Kategorien
2️⃣ list_engineering_tools(category="...") - Listet Tools einer Kategorie  
3️⃣ get_tool_details(tool_name="...") - ⚡ SCHALTET TOOL FREI für direkten Aufruf
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

💡 WICHTIG - Progressive Disclosure:
- Beim Handshake siehst du nur 3 Discovery-Tools
- Engineering-Tools sind registriert aber VERSTECKT
- get_tool_details(tool_name) schaltet spezifisches Tool frei
- Danach ist das Tool in ListTools sichtbar und aufrufbar

🔍 BEISPIEL-WORKFLOW:
1. categories = get_available_categories()
2. tools = list_engineering_tools(category="pressure")
3. details = get_tool_details(tool_name="solve_kesselformel")  # ⚡ SCHALTET FREI
4. result = solve_kesselformel(p=10, d=100, sigma=160)  # JETZT VERFÜGBAR!
"""
)

# Session State für Progressive Disclosure
_session_allowed_tools = set()

@mcp.tool()
def clock() -> str:
    "Aktuelle UTC-Zeit zurückgeben"
    return datetime.datetime.utcnow().isoformat() + "Z"

# ===== Discovery Tools (IMMER sichtbar) =====

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
    
    # Hole Engineering-Tools aus versteckter Registry
    tool_info = get_tool_info_for_llm(mcp_instance=mcp, hidden_registry=True)
    
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
        "usage_hint": "Verwende diese Kategorien mit list_engineering_tools(category='...')",
        "progressive_disclosure_status": {
            "hidden_tools_available": len(tool_info),
            "currently_unlocked": len(_session_allowed_tools),
            "next_step": "Verwende list_engineering_tools(category='...') um Tools zu erkunden"
        }
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
    
    # Hole Engineering-Tools aus versteckter Registry
    tool_info = get_tool_info_for_llm(mcp_instance=mcp, hidden_registry=True)
    
    # Filter nach Kategorie
    filtered_tools = [tool for tool in tool_info if category in tool.get("tags", []) or category == tool.get("category")]
    
    # Kompakte Darstellung für Discovery
    compact_tools = []
    for tool in filtered_tools:
        is_unlocked = tool["name"] in _session_allowed_tools
        
        compact_tools.append({
            "name": tool["name"],
            "short_description": tool.get("short_description", tool["description"].split(".")[0]),
            "solvable_variables": tool["solvable_variables"],
            "tags": tool["tags"],
            "call_example": f"{tool['name']}(...)" if is_unlocked else f"get_tool_details('{tool['name']}')",
            "status": "🔓 UNLOCKED - Ready to call" if is_unlocked else "🔒 LOCKED - Call get_tool_details() to unlock",
            "unlock_hint": f"Nutze get_tool_details('{tool['name']}') um das Tool freizuschalten" if not is_unlocked else "Tool bereits freigeschaltet!"
        })
    
    if ctx:
        await ctx.info(f"Gefunden: {len(compact_tools)} Tools in Kategorie {category}")
    
    unlocked_count = sum(1 for tool in compact_tools if tool["name"] in _session_allowed_tools)
    
    return {
        "tools": compact_tools,
        "category": category,
        "total_tools": len(compact_tools),
        "unlocked_tools": unlocked_count,
        "locked_tools": len(compact_tools) - unlocked_count,
        "progressive_disclosure_hint": "Verwende get_tool_details(tool_name) um Tools freizuschalten"
    }

@mcp.tool(
    name="get_tool_details",
    description="Ruft detaillierte Informationen zu einem Tool ab und SCHALTET ES FREI für direkten Aufruf",
    tags=["discovery", "engineering", "documentation", "meta", "unlock"]
)
async def get_tool_details(
    tool_name: str,
    ctx: Context = None
) -> Dict:
    """
    Liefert vollständige Dokumentation eines Engineering-Tools und schaltet es für direkten Aufruf frei.
    
    Args:
        tool_name: Name des Tools (z.B. "solve_kesselformel")
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Tool-Dokumentation + Freischaltung-Bestätigung
    """
    global _session_allowed_tools
    
    if ctx:
        await ctx.info(f"Hole Details für Tool: {tool_name} und schalte es frei...")
    
    try:
        details = await get_tool_details_from_mcp(tool_name, mcp_instance=mcp, hidden_registry=True)
        
        # ⚡ PROGRESSIVE DISCLOSURE: Tool in Session-Whitelist hinzufügen
        _session_allowed_tools.add(tool_name)
        
        # Registriere das Tool jetzt DYNAMISCH bei FastMCP
        await register_engineering_tool_dynamically(tool_name)
        
        if ctx:
            await ctx.info(f"✅ Tool {tool_name} freigeschaltet und bei MCP registriert")
        
        # Erweiterte Antwort mit Freischaltung-Info
        details["unlock_status"] = {
            "unlocked": True,
            "tool_name": tool_name,
            "session_tools_unlocked": len(_session_allowed_tools),
            "direct_call_available": True,
            "message": f"✅ {tool_name} ist jetzt für direkten Aufruf verfügbar!",
            "next_step": f"Du kannst jetzt {tool_name}(parameter=...) direkt aufrufen"
        }
        
        return details
        
    except ValueError as e:
        if ctx:
            await ctx.error(f"Tool nicht gefunden: {tool_name}")
        
        return {
            "error": str(e),
            "available_tools": "Nutze list_engineering_tools() um verfügbare Tools zu sehen",
            "unlock_status": {
                "unlocked": False,
                "error": f"Tool {tool_name} nicht gefunden"
            }
        }

async def register_engineering_tool_dynamically(tool_name: str):
    """
    Registriert ein Engineering-Tool dynamisch bei FastMCP nach der Freischaltung.
    """
    from engineering_mcp.registry import _HIDDEN_ENGINEERING_TOOLS
    
    if tool_name in _HIDDEN_ENGINEERING_TOOLS:
        tool_metadata = _HIDDEN_ENGINEERING_TOOLS[tool_name]
        tool_func = tool_metadata.get('function')
        
        if tool_func and callable(tool_func):
            # Dynamische Registrierung bei FastMCP
            mcp.tool(
                name=tool_name,
                description=tool_metadata.get('short_description', tool_metadata.get('description', '')),
                tags=tool_metadata.get('tags', [])
            )(tool_func)
            
            print(f"🔓 Dynamisch registriert: {tool_name} bei FastMCP")

# Initialisierung beim Server-Start
async def init_engineering_tools():
    """Lädt Engineering-Tools und registriert sie VERSTECKT (nur in Registry)"""
    global _session_allowed_tools
    _session_allowed_tools = set()  # Reset session state
    
    # Lade Tools in versteckte Registry (NICHT bei MCP registrieren!)
    tools_count = await discover_engineering_tools(mcp_instance=mcp, register_hidden=True)
    print(f"🔐 {tools_count} Engineering-Tools in versteckter Registry geladen")
    print(f"✅ 4 Discovery-Tools (immer sichtbar) bereit")
    print(f"🎯 Progressive Tool Disclosure aktiviert:")
    print(f"   ├─ Handshake: Nur 4 Tools sichtbar (clock + 3 Discovery)")
    print(f"   ├─ Discovery: list_categories → list_tools → get_details")
    print(f"   ├─ Freischaltung: get_tool_details() → Session-Whitelist + Dynamische MCP-Registrierung")
    print(f"   └─ Direkter Aufruf: Tools nach Freischaltung verfügbar")
    return tools_count 