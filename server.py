from fastmcp import FastMCP, Context
import datetime
from typing import Optional, Dict, List, Any
from engineering_mcp.registry import (
    get_tool_info_for_llm, 
    discover_engineering_tools,
    get_tool_details_from_mcp,
    get_available_tools_list,
    get_registered_tools_list,
    get_tools_by_category,
    register_tool_with_mcp,
    register_all_tools_with_mcp,
    register_category_tools_with_mcp
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

🎯 WICHTIGER WORKFLOW (DISCOVERY UND DIREKTE NUTZUNG):
1️⃣ get_available_categories() - Zeigt verfügbare Tool-Kategorien
2️⃣ list_engineering_tools(category="...") - Listet Tools einer Kategorie  
3️⃣ get_tool_details(tool_name="...") - Lädt Tool-Details UND registriert Tool automatisch
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
- Nutze get_tool_details() um Tools zu laden UND Parameter-Info zu erhalten
- Alle physikalischen Werte müssen positiv sein
- Achte auf Einheiten (werden in Tool-Details angegeben)
- Nach get_tool_details() sind Tools DIREKT aufrufbar (z.B. solve_circle_area(radius=10))

🔍 BEISPIEL-WORKFLOW:
1. categories = get_available_categories()
2. tools = list_engineering_tools(category="pressure")
3. details = get_tool_details(tool_name="solve_kesselformel")  # Tool wird automatisch geladen!
4. result = solve_kesselformel(p=10, d=100, sigma=160)  # DIREKT verfügbar!

🚀 DYNAMISCHES TOOL-LOADING:
- Tools sind beim Handshake NICHT sichtbar (kompakter Handshake)
- Tools werden automatisch registriert sobald Details abgerufen werden
- Einmal registrierte Tools bleiben für die Session verfügbar
- Discovery-Tools sind immer verfügbar, Engineering-Tools nur nach Bedarf
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
    
    # Hole Engineering-Tools aus interner Registry
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
                "registered_count": 0,
                "description": ""
            }
        
        categories_info[category]["tools"].append(tool["name"])
        categories_info[category]["tool_count"] += 1
        
        if tool.get("is_registered", False):
            categories_info[category]["registered_count"] += 1
    
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
        "total_tools": sum(info["tool_count"] for info in categories_info.values()),
        "registered_tools": sum(info["registered_count"] for info in categories_info.values()),
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
    
    # Hole Engineering-Tools aus interner Registry
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
            "is_registered": tool.get("is_registered", False),
            "status": "✅ Verfügbar" if tool.get("is_registered", False) else "🔄 Wird bei Details geladen",
            "next_step": f"get_tool_details(tool_name='{tool['name']}') um zu laden und nutzen"
        })
    
    if ctx:
        await ctx.info(f"Gefunden: {len(compact_tools)} Tools in Kategorie {category}")
    
    return compact_tools

@mcp.tool(
    name="get_tool_details",
    description="Ruft detaillierte Informationen zu einem Tool ab UND registriert es automatisch für direkten Aufruf",
    tags=["discovery", "engineering", "documentation", "loader", "meta"]
)
async def get_tool_details(
    tool_name: str,
    ctx: Context = None
) -> Dict:
    """
    Liefert vollständige Dokumentation eines Engineering-Tools UND registriert es automatisch.
    Nach diesem Aufruf ist das Tool direkt verfügbar (z.B. solve_kesselformel(...))
    
    Args:
        tool_name: Name des Tools (z.B. "solve_kesselformel")
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Ausführliche Tool-Dokumentation mit Registrierungsstatus
    """
    if ctx:
        await ctx.info(f"Hole Details und registriere Tool: {tool_name}")
    
    try:
        # Dies registriert das Tool automatisch bei MCP
        details = await get_tool_details_from_mcp(tool_name, mcp_instance=mcp)
        
        if ctx:
            if details.get('is_registered', False):
                await ctx.info(f"✅ Tool erfolgreich registriert und verfügbar: {tool_name}")
            else:
                await ctx.warn(f"⚠️ Tool-Details abgerufen, aber Registrierung fehlgeschlagen: {tool_name}")
        
        return details
        
    except ValueError as e:
        if ctx:
            await ctx.error(f"Tool nicht gefunden: {tool_name}")
        
        return {
            "error": str(e),
            "available_tools": "Nutze list_engineering_tools() um verfügbare Tools zu sehen"
        }

# ===== Bulk-Loader-Tools für Effizienz (Handshake sichtbar) =====

@mcp.tool(
    name="register_category_tools",
    description="Registriert ALLE Tools einer Kategorie auf einmal für direkten Aufruf",
    tags=["loader", "bulk", "efficiency", "meta"]
)
async def register_category_tools(
    category: str,
    ctx: Context = None
) -> Dict:
    """
    Registriert alle Tools einer Kategorie bei MCP für direkten Aufruf.
    Effizient für Workflows mit mehreren Tools derselben Kategorie.
    
    Args:
        category: Kategorie-Name (z.B. "pressure", "geometry")
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Registrierungsergebnis
    """
    if ctx:
        await ctx.info(f"Registriere alle Tools der Kategorie: {category}")
    
    try:
        registered_count = register_category_tools_with_mcp(category)
        registered_tools = get_registered_tools_list()
        
        # Filter für Tools dieser Kategorie
        category_tools = get_tools_by_category().get(category, [])
        registered_in_category = [tool for tool in registered_tools if tool in category_tools]
        
        if ctx:
            await ctx.info(f"✅ {registered_count} Tools aus Kategorie '{category}' registriert")
        
        return {
            "category": category,
            "registered_count": registered_count,
            "registered_tools": registered_in_category,
            "total_registered": len(registered_tools),
            "status": f"✅ {registered_count} Tools aus '{category}' jetzt direkt verfügbar",
            "usage": f"Du kannst jetzt alle Tools direkt aufrufen, z.B. {registered_in_category[0] if registered_in_category else 'tool_name'}(...)"
        }
        
    except Exception as e:
        if ctx:
            await ctx.error(f"Fehler bei Bulk-Registrierung für Kategorie {category}: {str(e)}")
        
        return {
            "error": str(e),
            "category": category
        }

@mcp.tool(
    name="register_all_tools",
    description="Registriert ALLE Engineering-Tools auf einmal für direkten Aufruf (Vorsicht: viele Tools)",
    tags=["loader", "bulk", "all", "meta"]
)
async def register_all_tools(
    ctx: Context = None
) -> Dict:
    """
    Registriert ALLE verfügbaren Engineering-Tools bei MCP.
    Nutze dies nur wenn du viele verschiedene Tools benötigst.
    
    Args:
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Registrierungsergebnis aller Tools
    """
    if ctx:
        await ctx.info("Registriere ALLE Engineering-Tools...")
    
    try:
        registered_count = register_all_tools_with_mcp()
        registered_tools = get_registered_tools_list()
        
        if ctx:
            await ctx.info(f"✅ {registered_count} Tools insgesamt registriert")
        
        return {
            "registered_count": registered_count,
            "registered_tools": registered_tools,
            "status": f"✅ Alle {registered_count} Engineering-Tools sind jetzt direkt verfügbar",
            "usage": "Du kannst jetzt alle Tools direkt aufrufen, z.B. solve_kesselformel(p=10, d=100, sigma=160)",
            "categories": get_tools_by_category()
        }
        
    except Exception as e:
        if ctx:
            await ctx.error(f"Fehler bei vollständiger Registrierung: {str(e)}")
        
        return {
            "error": str(e)
        }

# Initialisierung beim Server-Start
async def init_engineering_tools():
    """Lädt und speichert Engineering-Tools für dynamische Registrierung"""
    tools_count = await discover_engineering_tools(mcp_instance=mcp)
    print(f"✅ {tools_count} Engineering-Tools bereit für dynamische Registrierung")
    print(f"✅ 5 Discovery/Loader-Tools + 1 Utility-Tool (clock) beim Handshake sichtbar")
    print(f"🎯 Dynamisches Tool-Loading aktiviert:")
    print(f"   1. get_available_categories")
    print(f"   2. list_engineering_tools")  
    print(f"   3. get_tool_details (lädt Tool automatisch)")
    print(f"   4. register_category_tools (Bulk-Loader)")
    print(f"   5. register_all_tools (Alle-Tools-Loader)")
    print(f"")
    print(f"📋 LLM sieht beim Handshake NUR:")
    print(f"   ✅ clock, get_available_categories, list_engineering_tools")
    print(f"   ✅ get_tool_details, register_category_tools, register_all_tools")
    print(f"   ❌ KEINE Engineering-Tools (solve_*, calculate_*)")
    print(f"")
    print(f"🚀 Engineering-Tools werden automatisch registriert bei:")
    print(f"   - get_tool_details(tool_name): Einzelnes Tool")
    print(f"   - register_category_tools(category): Alle Tools einer Kategorie")
    print(f"   - register_all_tools(): Alle verfügbaren Tools")
    return tools_count 

if __name__ == "__main__":
    import asyncio
    
    async def start_server():
        # Engineering-Tools initialisieren
        tools_count = await init_engineering_tools()
        
        # Server starten
        await mcp.run()
    
    # Server starten
    asyncio.run(start_server()) 