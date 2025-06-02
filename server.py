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
# Import der Engineering-Tools für direkte Registrierung
from tools.pressure.kesselformel import solve_kesselformel
from tools.geometry.circle_area import solve_circle_area

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
4️⃣ calculate_engineering(tool_name="...", parameters={...}) - Tool ausführen

⚙️ KERNKONZEPT - Symbolische Variablen-Auflösung:
- Jedes Tool implementiert EINE Formel mit mehreren Variablen
- Du gibst n-1 Variablen an, das Tool berechnet die fehlende Variable
- Beispiel: Kesselformel σ = p·d/(2·s) hat 4 Variablen [sigma, p, d, s]
  → Gib 3 Werte an (z.B. p=10, d=100, sigma=160)
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

🔍 BEISPIEL-WORKFLOW:
1. categories = get_available_categories()
2. tools = list_engineering_tools(category="pressure")
3. details = get_tool_details(tool_name="solve_kesselformel")  # Optional
4. result = calculate_engineering(
     tool_name="solve_kesselformel",
     parameters={"p": 10, "d": 100, "sigma": 160}
   )

📊 DIREKT VERFÜGBARE TOOLS:
Zusätzlich zu den Meta-Tools sind folgende Engineering-Tools direkt verfügbar:
- solve_kesselformel: Kesselformel σ = p·d/(2·s) für Druckbehälter
- solve_circle_area: Kreisfläche A = π·r² für geometrische Berechnungen
"""
)

@mcp.tool()
def clock() -> str:
    "Aktuelle UTC-Zeit zurückgeben"
    return datetime.datetime.utcnow().isoformat() + "Z"

# ===== Direkt verfügbare Engineering-Tools =====

@mcp.tool(
    name="solve_kesselformel",
    description="Löst die Kesselformel σ = p·d/(2·s) nach verschiedenen Variablen auf. Lösbare Variablen: [sigma, p, d, s]. Druckbehälterberechnung für dünnwandige zylindrische Druckbehälter.",
    tags=["pressure", "engineering", "symbolic", "vessels"]
)
async def kesselformel_direct(
    p: Optional[float] = None,
    d: Optional[float] = None,
    s: Optional[float] = None,
    sigma: Optional[float] = None,
    ctx: Context = None
) -> Dict:
    """
    Löst die Kesselformel σ = p·d/(2·s) symbolisch nach der unbekannten Variable.
    
    Args:
        p: Innendruck [N/mm²]
        d: Außendurchmesser [mm]  
        s: Wanddicke [mm]
        sigma: Zulässige Spannung [N/mm²]
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Berechnungsergebnis mit Lösung und Metadaten
    """
    return await solve_kesselformel(p=p, d=d, s=s, sigma=sigma, ctx=ctx)

@mcp.tool(
    name="solve_circle_area", 
    description="Löst die Kreisflächenformel A = π·r² nach verschiedenen Variablen auf. Lösbare Variablen: [area, radius]. Berechnung von Kreisfläche oder Radius.",
    tags=["geometry", "engineering", "symbolic", "area"]
)
async def circle_area_direct(
    area: Optional[float] = None,
    radius: Optional[float] = None,
    ctx: Context = None
) -> Dict:
    """
    Löst die Kreisflächenformel A = π·r² symbolisch nach der unbekannten Variable.
    
    Args:
        area: Kreisfläche [mm²]
        radius: Radius [mm]
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Berechnungsergebnis mit Lösung und Metadaten
    """
    return await solve_circle_area(area=area, radius=radius, ctx=ctx)

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
        "usage_hint": "Verwende diese Kategorien mit list_engineering_tools(category='...')",
        "note": "Zusätzlich sind solve_kesselformel und solve_circle_area direkt verfügbar"
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
            "tags": tool["tags"],
            "note": "Auch direkt als MCP Tool verfügbar" if tool["name"] in ["solve_kesselformel", "solve_circle_area"] else ""
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
    print(f"✅ 6 Meta-Tools + 2 direkte Engineering-Tools + 1 Utility-Tool (clock) bereit")
    print(f"🎯 Mehrstufige Discovery aktiviert:")
    print(f"   Meta: get_available_categories, list_engineering_tools, get_tool_details, calculate_engineering")
    print(f"   Direkt: solve_kesselformel, solve_circle_area")
    return tools_count 