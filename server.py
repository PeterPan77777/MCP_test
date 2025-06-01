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

🔍 BEISPIEL-WORKFLOW:
1. categories = get_available_categories()
2. tools = list_engineering_tools(category="pressure")
3. details = get_tool_details(tool_name="solve_kesselformel")  
4. result = calculate_engineering(
     tool_name="solve_kesselformel",
     parameters={"p": 10, "d": 100, "sigma": 160}
   )
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
    Gateway-Funktion für Engineering-Tool-Ausführung mit detaillierter Fehleranalyse.
    
    Args:
        tool_name: Name des Engineering-Tools
        parameters: Tool-Parameter als Dictionary
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Berechnungsergebnis oder detaillierte Fehleranalyse
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
        error_msg = str(e)
        
        # Detaillierte Fehleranalyse
        error_analysis = await _analyze_calculation_error(tool_name, parameters, error_msg)
        
        if ctx:
            await ctx.error(f"Berechnung fehlgeschlagen: {error_msg}")
            await ctx.info(f"Fehleranalyse erstellt mit {len(error_analysis.get('solutions', []))} Lösungsvorschlägen")
        
        return {
            "tool_name": tool_name,
            "parameters": parameters,
            "error": error_msg,
            "status": "error",
            "error_analysis": error_analysis
        }

async def _analyze_calculation_error(tool_name: str, parameters: Dict, error_msg: str) -> Dict:
    """
    Analysiert Berechnungsfehler und gibt detaillierte Lösungsvorschläge.
    
    Args:
        tool_name: Name des fehlgeschlagenen Tools
        parameters: Übergebene Parameter
        error_msg: Originale Fehlermeldung
        
    Returns:
        Dict: Detaillierte Fehleranalyse mit Lösungsvorschlägen
    """
    analysis = {
        "error_type": "unknown",
        "problem_description": "",
        "solutions": [],
        "corrected_examples": [],
        "parameter_analysis": {}
    }
    
    # 1. Parameter-Analyse
    analysis["parameter_analysis"] = {
        "received_count": len(parameters),
        "parameter_types": {k: type(v).__name__ for k, v in parameters.items()},
        "parameter_values": parameters,
        "negative_values": [k for k, v in parameters.items() if isinstance(v, (int, float)) and v <= 0],
        "string_values": [k for k, v in parameters.items() if isinstance(v, str)]
    }
    
    # 2. Tool-spezifische Analyse
    try:
        from engineering_mcp.registry import get_tool_details
        tool_details = await get_tool_details(tool_name)
        expected_vars = tool_details.get("solvable_variables", [])
        analysis["expected_variables"] = expected_vars
        analysis["expected_count"] = len(expected_vars) - 1 if expected_vars else "unknown"
    except:
        analysis["expected_variables"] = "unknown"
        analysis["expected_count"] = "unknown"
    
    # 3. Fehlertyp-spezifische Analyse
    if "Tool" in error_msg and "nicht gefunden" in error_msg:
        analysis.update(_analyze_tool_not_found_error(tool_name, parameters))
    elif "parameter" in error_msg.lower() and ("3 von 4" in error_msg or "genau" in error_msg.lower()):
        analysis.update(_analyze_parameter_count_error(tool_name, parameters, analysis["expected_count"]))
    elif "positiv" in error_msg.lower() or "positive" in error_msg.lower():
        analysis.update(_analyze_negative_value_error(tool_name, parameters))
    elif "schema" in error_msg.lower():
        analysis.update(_analyze_schema_error(tool_name, parameters))
    elif isinstance(parameters, dict) and analysis["parameter_analysis"]["string_values"]:
        analysis.update(_analyze_datatype_error(tool_name, parameters))
    else:
        analysis.update(_analyze_generic_error(tool_name, parameters, error_msg))
    
    return analysis

def _analyze_tool_not_found_error(tool_name: str, parameters: Dict) -> Dict:
    """Analysiert 'Tool nicht gefunden' Fehler"""
    return {
        "error_type": "tool_not_found",
        "problem_description": f"Das Tool '{tool_name}' existiert nicht in der Registry.",
        "solutions": [
            "1. Nutze list_engineering_tools() um verfügbare Tools zu sehen",
            "2. Überprüfe die Schreibweise des Tool-Namens (case-sensitive)",
            "3. Nutze get_available_categories() um Kategorien zu erkunden",
            "4. Tool-Namen beginnen meist mit 'solve_' (z.B. 'solve_kesselformel')"
        ],
        "corrected_examples": [
            {
                "description": "Korrekte Tool-Discovery",
                "steps": [
                    "categories = get_available_categories()",
                    "tools = list_engineering_tools(category='pressure')",
                    "result = calculate_engineering(tool_name='solve_kesselformel', parameters={...})"
                ]
            }
        ]
    }

def _analyze_parameter_count_error(tool_name: str, parameters: Dict, expected_count) -> Dict:
    """Analysiert Parameteranzahl-Fehler"""
    received_count = len(parameters)
    
    return {
        "error_type": "parameter_count_mismatch",
        "problem_description": f"Falsche Anzahl Parameter: {received_count} erhalten, {expected_count} erwartet.",
        "solutions": [
            f"1. Gib genau {expected_count} Parameter an (nicht {received_count})",
            "2. Prüfe mit get_tool_details() welche Parameter das Tool erwartet",
            "3. Ein Tool mit n Variablen benötigt n-1 Input-Parameter",
            "4. Die fehlende Variable wird automatisch berechnet"
        ],
        "corrected_examples": [
            {
                "description": "Kesselformel (4 Variablen → 3 Parameter)",
                "wrong": {"p": 10, "d": 100, "sigma": 160, "s": 5},
                "correct": {"p": 10, "d": 100, "sigma": 160},
                "explanation": "Entferne einen Parameter - das Tool berechnet ihn automatisch"
            }
        ]
    }

def _analyze_negative_value_error(tool_name: str, parameters: Dict) -> Dict:
    """Analysiert negative Werte Fehler"""
    negative_params = [k for k, v in parameters.items() if isinstance(v, (int, float)) and v <= 0]
    
    return {
        "error_type": "negative_values",
        "problem_description": f"Negative oder Null-Werte nicht erlaubt: {negative_params}",
        "solutions": [
            "1. Alle physikalischen Größen müssen positiv sein (> 0)",
            f"2. Ändere diese Parameter: {negative_params}",
            "3. Prüfe die Einheiten - vielleicht ist eine Umrechnung nötig",
            "4. Verwende realistische Ingenieurswerte"
        ],
        "corrected_examples": [
            {
                "description": "Positive Werte verwenden",
                "wrong": {k: v for k, v in parameters.items()},
                "correct": {k: abs(v) if isinstance(v, (int, float)) and v <= 0 else v for k, v in parameters.items()},
                "explanation": "Alle Werte müssen positiv sein"
            }
        ]
    }

def _analyze_schema_error(tool_name: str, parameters: Dict) -> Dict:
    """Analysiert Schema-Validierung-Fehler"""
    return {
        "error_type": "schema_validation",
        "problem_description": "Parameter entsprechen nicht dem erwarteten Schema.",
        "solutions": [
            "1. Verwende get_tool_details() um das exakte Schema zu sehen",
            "2. Prüfe Parameter-Namen (case-sensitive)",
            "3. Stelle sicher, dass alle Werte Numbers sind (nicht Strings)",
            "4. Verwende die exakten Variablennamen aus solvable_variables"
        ],
        "corrected_examples": [
            {
                "description": "Schema-konforme Parameter",
                "steps": [
                    "details = get_tool_details(tool_name='" + tool_name + "')",
                    "# Verwende die Namen aus details['solvable_variables']",
                    "# Stelle sicher: Numbers nicht Strings"
                ]
            }
        ]
    }

def _analyze_datatype_error(tool_name: str, parameters: Dict) -> Dict:
    """Analysiert Datentyp-Fehler (String statt Number)"""
    string_params = [k for k, v in parameters.items() if isinstance(v, str)]
    
    corrected_params = {}
    for k, v in parameters.items():
        if isinstance(v, str):
            try:
                corrected_params[k] = float(v)
            except:
                corrected_params[k] = v
        else:
            corrected_params[k] = v
    
    return {
        "error_type": "wrong_datatypes",
        "problem_description": f"String-Werte statt Numbers: {string_params}",
        "solutions": [
            "1. Alle numerischen Parameter müssen Numbers sein, nicht Strings",
            f"2. Konvertiere diese Parameter von String zu Number: {string_params}",
            "3. In n8n: Verwende Number() oder parseFloat() Funktionen",
            "4. JSON: Verwende 10 statt '10', 3.14 statt '3.14'"
        ],
        "corrected_examples": [
            {
                "description": "Datentyp-Korrektur",
                "wrong": parameters,
                "correct": corrected_params,
                "explanation": "Numbers verwenden statt Strings"
            }
        ]
    }

def _analyze_generic_error(tool_name: str, parameters: Dict, error_msg: str) -> Dict:
    """Analysiert allgemeine Fehler"""
    return {
        "error_type": "generic",
        "problem_description": f"Unbekannter Fehler: {error_msg}",
        "solutions": [
            "1. Nutze get_tool_details() für detaillierte Parameter-Info",
            "2. Prüfe die Tool-Dokumentation auf spezielle Anforderungen",
            "3. Verwende list_engineering_tools() um ähnliche Tools zu finden",
            "4. Stelle sicher, dass alle Werte realistic sind"
        ],
        "corrected_examples": [
            {
                "description": "Systematisches Debugging",
                "steps": [
                    "1. details = get_tool_details(tool_name='" + tool_name + "')",
                    "2. Prüfe details['solvable_variables']",
                    "3. Prüfe details['examples'] für korrekte Nutzung",
                    "4. Verwende exakt die gezeigten Parameter-Formate"
                ]
            }
        ]
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