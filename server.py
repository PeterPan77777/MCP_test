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
import json

# MCP Server mit ausführlichen Instructions für LLMs
mcp = FastMCP(
    name="EngineersCalc", 
    instructions="""
🔧 Engineering Calculation Server - Symbolische Ingenieurberechnungen

📋 ÜBERSICHT:
Dieser Server bietet Zugriff auf eine Sammlung von Engineering-Tools, die Formeln 
symbolisch nach verschiedenen Variablen auflösen können. Alle Tools verwenden SymPy
für exakte mathematische Berechnungen.

🎯 WICHTIGER WORKFLOW (IMMER IN DIESER REIHENFOLGE ausführen):
1️⃣ get_available_categories() - Zeigt verfügbare Tool-Kategorien
2️⃣ list_engineering_tools(category="...") - Listet alle Tools einer Kategorie auf
3️⃣ get_tool_details(tool_name="...") - Beziehe Detaillierte Tool-Info, wie Du dieses Tool genau benutzten musst.
4️⃣ calculate_engineering(tool_name="...", parameters={...}) - Tool ausführen
   ODER execute_engineering_tool(request={...}) - Alternative mit einem Parameter

⚙️ KERNKONZEPT - Symbolische Variablen-Auflösung:
- Jedes Tool implementiert EINE Formel mit mehreren Variablen
- Du gibst n-1 Variablen an, das Tool berechnet die fehlende Variable
- Beispiel: Kesselformel σ = p·d/(2·s) hat 4 Variablen [sigma, p, d, s]
  → Gib 3 Werte an (z.B. p=10, d=100, sigma=160)
  → Tool berechnet die 4. Variable (hier: s=3.125)

📂 VERFÜGBARE KATEGORIEN:
- über get_available_categories() erkunden

💡 TIPPS:
- Starte IMMER mit get_available_categories()
- Nutze get_tool_details() wenn Parameter unklar sind
- Alle physikalischen Werte müssen positiv sein
- Achte auf Einheiten (werden in Tool-Details angegeben)
- Parameter müssen als Dictionary übergeben werden: {"variable": wert}

🔍 BEISPIEL-WORKFLOWS:

1. Kesselformel-Berechnung:
   categories = get_available_categories()
   tools = list_engineering_tools(category="pressure")
   details = get_tool_details(tool_name="solve_kesselformel")  
   result = calculate_engineering(
     tool_name="solve_kesselformel",
     parameters={"p": 10, "d": 100, "sigma": 160}
   )

2. Kreisflächen-Berechnung:
   tools = list_engineering_tools(category="geometry")
   # Fläche aus Radius berechnen:
   result = calculate_engineering(
     tool_name="solve_circle_area",
     parameters={"radius": 10}
   )
   # ODER mit execute_engineering_tool:
   result = execute_engineering_tool(
     request={
       "tool_name": "solve_circle_area",
       "parameters": {"radius": 10}
     }
   )

⚠️ WICHTIG: Zwei Möglichkeiten zur Tool-Ausführung
Option A - Zwei separate Parameter:
  calculate_engineering(tool_name="...", parameters={...})
  
Option B - Ein Dictionary-Parameter:
  execute_engineering_tool(request={"tool_name": "...", "parameters": {...}})

⚠️ WICHTIG: Parameter-Format
- RICHTIG: parameters={"radius": 10}
- FALSCH: parameters="radius=10" oder parameters=[10]
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
    # Enhanced Logging für n8n Debugging
    print(f"\n🔧 CALCULATE_ENGINEERING CALLED")
    print(f"Tool: {tool_name}")
    print(f"Parameters Type: {type(parameters)}")
    print(f"Parameters: {json.dumps(parameters, indent=2) if isinstance(parameters, dict) else parameters}")
    
    if ctx:
        await ctx.info(f"Führe Engineering-Berechnung aus: {tool_name}")
        await ctx.info(f"Parameter: {parameters}")
    
    try:
        result = await call_engineering_tool(tool_name, parameters)
        
        print(f"✅ Calculation successful for {tool_name}")
        print(f"Result: {json.dumps(result, indent=2)}")
        
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
        print(f"❌ ERROR: {error_msg}")
        
        if ctx:
            await ctx.error(error_msg)
        
        # Hilfreiche Fehlerinformationen
        error_response = {
            "tool_name": tool_name,
            "parameters": parameters,
            "error": str(e),
            "status": "error"
        }
        
        # Zusätzliche Hilfe bei bekannten Fehlern
        if "genau" in str(e).lower() and "parameter" in str(e).lower():
            error_response["hint"] = "Für symbolische Tools müssen genau n-1 von n Parametern angegeben werden"
            error_response["help"] = "Nutze get_tool_details() um die erforderlichen Parameter zu sehen"
        
        return error_response

@mcp.tool(
    name="execute_engineering_tool",
    description="Alternative Schnittstelle für Engineering-Tool-Ausführung mit einem einzigen Parameter-Objekt",
    tags=["engineering", "execution", "gateway", "alternative"]
)
async def execute_engineering_tool(
    request: Dict,
    ctx: Context = None
) -> Dict:
    """
    Alternative Gateway-Funktion, die ein einzelnes Dictionary mit tool_name und parameters akzeptiert.
    
    Args:
        request: Dictionary mit 'tool_name' und 'parameters' Feldern
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Berechnungsergebnis
        
    Example:
        request = {
            "tool_name": "solve_circle_area",
            "parameters": {"radius": 10}
        }
    """
    # Enhanced Logging für n8n Debugging
    print(f"\n🔧 EXECUTE_ENGINEERING_TOOL CALLED")
    print(f"Request Type: {type(request)}")
    print(f"Request: {json.dumps(request, indent=2) if isinstance(request, dict) else request}")
    
    if ctx:
        await ctx.info(f"Execute engineering tool mit request: {request}")
    
    # Validiere Request-Struktur
    if not isinstance(request, dict):
        return {
            "error": "Request muss ein Dictionary sein",
            "received_type": str(type(request)),
            "expected_format": '{"tool_name": "...", "parameters": {...}}',
            "status": "error"
        }
    
    if "tool_name" not in request:
        return {
            "error": "Feld 'tool_name' fehlt im Request",
            "received": request,
            "expected_format": '{"tool_name": "...", "parameters": {...}}',
            "status": "error"
        }
    
    if "parameters" not in request:
        return {
            "error": "Feld 'parameters' fehlt im Request",
            "received": request,
            "expected_format": '{"tool_name": "...", "parameters": {...}}',
            "status": "error"
        }
    
    # Delegiere an die ursprüngliche Funktion
    return await calculate_engineering(
        tool_name=request["tool_name"],
        parameters=request["parameters"],
        ctx=ctx
    )

# Initialisierung beim Server-Start
async def init_engineering_tools():
    """Lädt Engineering-Tools beim Server-Start"""
    tools_count = await discover_engineering_tools()
    print(f"✅ {tools_count} Engineering-Tools entdeckt")
    print(f"✅ 5 Meta-Tools + 1 Utility-Tool (clock) bereit")
    print(f"🎯 Mehrstufige Discovery aktiviert:")
    print(f"   1. get_available_categories")
    print(f"   2. list_engineering_tools")  
    print(f"   3. get_tool_details")
    print(f"   4. calculate_engineering (2 Parameter)")
    print(f"   5. execute_engineering_tool (1 Parameter)")
    return tools_count 