from fastmcp import FastMCP, Context
import datetime
import json
import re
import ast
from typing import Optional, Dict, List, Literal, Any, Union
from pydantic import BaseModel, ValidationError
from engineering_mcp.registry import (
    get_tool_info_for_llm, 
    get_symbolic_tools_summary,
    call_engineering_tool,
    discover_engineering_tools,
    get_tool_details as get_tool_details_from_registry
)
from tools.tag_definitions import get_tag_definitions

# Session State für sicheres Whitelisting
_session_state = {
    "viewed_categories": set(),      # Angesehene Kategorien
    "viewed_functions": set(),       # Angesehene Funktionen  
    "whitelisted_tools": set(),      # Freigeschaltete Tools (nach get_tool_details)
    "call_count": {}                 # Rate-Limiting Counter
}

# MCP Server mit ausführlichen Instructions für LLMs
mcp = FastMCP(
    name="EngineersCalc", 
    instructions="""
Engineering Calculation Server - Berechnungstools und Informationen für Ingenieure

Dieser Server bietet Zugriff auf eine Sammlung von Engineering-Tools, die Formeln 
symbolisch nach verschiedenen Variablen auflösen können und diese numerisch auswerten können.

WICHTIGER WORKFLOW:
1. Nutze IMMER zuerst 'get_available_categories' um verfügbare Kategorien zu sehen
2. Dann 'list_engineering_tools' mit einer spezifischen Kategorie ODER mit tags=["all"] für alle Tools
3. Verwende immer 'get_tool_details' für ausführliche Tool-Dokumentation, bevor du eine Berechnung mittels call_tool durchführst
4. Schließlich verwende 'call_tool' zur Ausführung.

💡 SCHNELLSTART-OPTION:
• Für vollständige Übersicht: list_engineering_tools(tags=["all"])
• Für spezifische Kategorie: list_engineering_tools(tags=["elementar"])

Bevor du eine Berechnung mittels calculate_engineering durchführst, verwende IMMER das tool get_tool_details:
1. um das tool zu aktivieren (ohne get_tool_details bleibt das tool deaktiviert)
2. um genau Informationen zu erhalten, wie du das tool mit calculate_engineering aufrufen musst.

Die Tools verwenden SymPy für symbolische Mathematik und können Formeln nach 
beliebigen Variablen auflösen und im Anschluss numerisch lösen. 
Gib immer genau n-1 Parameter an, wenn ein Tool n lösbare Variablen hat.

Beispiel: Kesselformel mit 4 Variablen [sigma, p, d, s] - gib 3 an, berechne die 4.

🔧 FEHLERTOLERANTE TOOL-AUSFÜHRUNG:
Das call_tool Tool unterstützt tolerante Parameter-Eingabe:
- Normale JSON: {"param": value}
- Python-dict-Syntax: {param=value, other=True}
- Code-Fence-wrapped: ```json {"param": value} ```
- Automatische Bool/None/String-Reparatur
"""
)

@mcp.tool()
def clock() -> str:
    "Aktuelle UTC-Zeit zurückgeben"
    return datetime.datetime.utcnow().isoformat() + "Z"

# ===== TOLERANTE PARAMETER-REPARATUR (für call_tool) =====

class CalculateToolSchema(BaseModel):
    """Schema für tolerante Tool-Ausführung"""
    tool_name: str
    parameters: dict

def _strip_codefence(txt: str) -> str:
    """Entfernt Code-Fence-Markierungen (```json, ``` etc.)"""
    txt = txt.strip()
    # Entferne Anfangs-Fence
    if txt.startswith("```"):
        lines = txt.splitlines()
        # Erstes und letztes Element entfernen
        if len(lines) >= 2 and lines[-1].strip() == "```":
            txt = "\n".join(lines[1:-1])
        else:
            txt = "\n".join(lines[1:])
    # Entferne End-Fence falls übrig
    if txt.endswith("```"):
        txt = txt[:-3].strip()
    return txt

def _repair_arguments(raw: Any) -> dict:
    """
    Repariert typische LLM-Fehler in Tool-Argumenten:
    - Entfernt Code-Fences
    - Python-dict-Syntax → JSON
    - Einfache → doppelte Anführungszeichen  
    - Python-bool/None → JSON-bool/null
    - Versucht ast.literal_eval als Fallback
    - ⭐ NEU: Erkennt und extrahiert aus n8n/Workflow-JSON-Strukturen
    """
    # ===== SPEZIAL-BEHANDLUNG: n8n/WORKFLOW-JSON ERKENNUNG =====
    if isinstance(raw, dict):
        # Prüfe ob es sich um n8n-Workflow-JSON handelt
        if "nodes" in raw and "connections" in raw and "meta" in raw:
            print("🔧 n8n-Workflow-JSON erkannt - extrahiere Engineering-Parameter...")
            
            # Extrahiere System-Message aus erstem AI-Agent-Node
            nodes = raw.get("nodes", [])
            for node in nodes:
                if node.get("type") == "@n8n/n8n-nodes-langchain.agent":
                    options = node.get("parameters", {}).get("options", {})
                    system_msg = options.get("systemMessage", "")
                    
                    # Durchsuche System-Message nach Engineering-Keywords
                    if any(keyword in system_msg.lower() for keyword in ["calculation", "mcp", "tool", "engineering"]):
                        print(f"📋 System-Message gefunden: {system_msg[:100]}...")
                        
                        # Versuche Parameter aus anderen Teilen der Struktur zu extrahieren
                        # Fallback: Leere Parameter für manuelle Eingabe-Aufforderung
                        return {
                            "detected_format": "n8n_workflow",
                            "extraction_hint": "n8n-Workflow erkannt - bitte Tool-Parameter separat angeben",
                            "system_message": system_msg,
                            "example_format": {
                                "pressure": "100 bar",
                                "wall_thickness": "50 mm", 
                                "allowable_stress": "200 MPa"
                            }
                        }
            
            # Kein AI-Agent gefunden
            return {
                "detected_format": "n8n_workflow_without_agent",
                "error": "n8n-Workflow ohne AI-Agent-Node gefunden",
                "hint": "Bitte Engineering-Parameter im Format {'param': 'value'} angeben"
            }
        
        # Prüfe ob es verschachtelte Engineering-Parameter gibt
        if "parameters" in raw and isinstance(raw["parameters"], dict):
            # Direkte Parameter-Extraktion
            return raw["parameters"]
        
        # Durchsuche nach Engineering-relevanten Schlüsseln
        engineering_keys = ["pressure", "wall_thickness", "diameter", "allowable_stress", 
                          "radius", "area", "volume", "height", "width", "length", 
                          "side_a", "side_c", "base"]
        
        found_params = {}
        for key, value in raw.items():
            if key.lower() in [k.lower() for k in engineering_keys]:
                found_params[key] = value
        
        if found_params:
            print(f"🔧 Engineering-Parameter in JSON gefunden: {list(found_params.keys())}")
            return found_params
    
    # Fall 1: String-Input → JSON parsen
    if isinstance(raw, str):
        raw = _strip_codefence(raw)
        
        # ⭐ NEUE PRÜFUNG: n8n-ähnliche JSON-String
        if "nodes" in raw and "connections" in raw:
            try:
                parsed_json = json.loads(raw)
                return _repair_arguments(parsed_json)  # Rekursiver Aufruf für n8n-Behandlung
            except json.JSONDecodeError:
                pass
        
        # Erweiterte Python-dict → JSON Reparatur
        py_like = raw
        
        # 1. Ersetze key= durch "key": (Python assignment style)
        py_like = re.sub(r"([A-Za-z_][A-Za-z0-9_]*)\s*=", r'"\1":', py_like)
        
        # 2. Ersetze unquoted keys → quoted keys (z.B. {key: value} → {"key": value})
        py_like = re.sub(r"([A-Za-z_][A-Za-z0-9_]*)\s*:", r'"\1":', py_like)
        
        # 3. Einfache → doppelte Anführungszeichen
        py_like = py_like.replace("'", '"')
        
        # 4. Python-bool/None → JSON-bool/null
        py_like = py_like.replace("True", "true").replace("False", "false").replace("None", "null")
        
        try:
            # Versuche JSON-Parsing
            raw = json.loads(py_like)
        except json.JSONDecodeError:
            try:
                # Fallback: Python literal_eval (funktioniert oft mit dict-Literals)
                # Erst wieder auf Original-Format zurück für literal_eval
                py_eval = raw.replace("true", "True").replace("false", "False").replace("null", "None")
                raw = ast.literal_eval(py_eval)
            except (ValueError, SyntaxError):
                try:
                    # Letzter Versuch: Noch aggressivere Regex-Reparatur
                    # Entferne extra Leerzeichen und normalisiere
                    cleaned = re.sub(r'\s+', ' ', raw.strip())
                    # Versuche als dict-literal zu interpretieren
                    if cleaned.startswith('{') and cleaned.endswith('}'):
                        # Minimaler dict-Parser für einfache Fälle
                        content = cleaned[1:-1].strip()
                        pairs = re.findall(r'([A-Za-z_][A-Za-z0-9_]*)\s*[:=]\s*([^,}]+)', content)
                        raw = {}
                        for key, value in pairs:
                            # Versuche Wert zu konvertieren
                            value = value.strip()
                            if value.isdigit():
                                raw[key] = int(value)
                            elif re.match(r'^\d+\.\d+$', value):
                                raw[key] = float(value)
                            elif value in ['True', 'true']:
                                raw[key] = True
                            elif value in ['False', 'false']:
                                raw[key] = False
                            elif value in ['None', 'null']:
                                raw[key] = None
                            else:
                                # Als String behandeln, Anführungszeichen entfernen
                                raw[key] = value.strip('"\'')
                    else:
                        # Als letzter Ausweg: leeres dict
                        print(f"⚠️ Konnte String nicht parsen: {raw[:100]}...")
                        raw = {}
                except Exception:
                    print(f"⚠️ Konnte String nicht parsen: {raw[:100]}...")
                    raw = {}
    
    # Fall 2: Dict-Input → Werte reparieren
    elif isinstance(raw, dict):
        # Nested JSON-Strings in Values reparieren
        for k, v in list(raw.items()):
            if isinstance(v, str) and v.strip().startswith("{"):
                try:
                    raw[k] = json.loads(v)
                except json.JSONDecodeError:
                    pass  # Lasse String-Value unverändert
            # Python-bool in dict reparieren
            elif v is True:
                raw[k] = True  # Bleibt Python-bool (JSON-kompatibel)
            elif v is False:
                raw[k] = False
            elif v is None:
                raw[k] = None
    
    # Fall 3: Liste von 2 Elementen [tool_name, params_as_string]
    elif isinstance(raw, (list, tuple)) and len(raw) == 2:
        tool_name, params_str = raw
        if isinstance(params_str, str):
            repaired_params = _repair_arguments(params_str)
            raw = {"tool_name": tool_name, "parameters": repaired_params}
        else:
            raw = {"tool_name": tool_name, "parameters": params_str}
    
    # Sicherstellen, dass es ein Dict ist
    if not isinstance(raw, dict):
        print(f"⚠️ Raw input konnte nicht zu dict konvertiert werden: {type(raw)}")
        raw = {}
    
    return raw

# ===== Meta-Tools für mehrstufige Discovery =====

@mcp.tool(
    name="get_available_categories",
    description="Gibt alle verfügbaren Engineering-Tool-Tags (Kategorien) mit Beschreibungen zurück. Wird benötigt um die Kategorie für list_engineering_tools zu bestimmen.IMMER ZUERST AUFRUFEN!",
    tags=["meta"]
)
async def get_available_categories(
    ctx: Context = None
) -> Dict:
    """
    Listet alle verfügbaren Tag-Kategorien von Engineering-Tools auf.
    
    Args:
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Tag-Kategorien mit Tool-Anzahl und Beschreibungen
    """
    global _session_state
    
    if ctx:
        await ctx.info("📋 Sammle verfügbare Tool-Tags...")
    
    # Hole Tag-Schema aus separater Datei
    tag_definitions = get_tag_definitions()
    
    # Hole Engineering-Tools aus Registry
    tool_info = get_tool_info_for_llm(include_engineering=True)
    
    # Gruppiere Tools nach Tags
    for tool in tool_info:
        tool_tags = tool.get("tags", [])
        
        for tag in tool_tags:
            if tag in tag_definitions:
                tag_definitions[tag]["tools"].append(tool["name"])
                tag_definitions[tag]["tool_count"] += 1
    
    # Meta-Tools hinzufügen (aktuell verfügbare MCP-Tools)
    meta_tools = ["get_available_categories", "list_engineering_tools", "get_tool_details", "call_tool"]
    tag_definitions["meta"]["tools"].extend(meta_tools)
    tag_definitions["meta"]["tool_count"] = len(meta_tools)
    
    # Session-Tracking
    _session_state["viewed_categories"].update(tag_definitions.keys())
    
    if ctx:
        await ctx.info(f"Gefunden: {len(tag_definitions)} Tag-Kategorien")
    
    return {
        "step": 1,
        "available_tags": list(tag_definitions.keys()),
        "tag_categories": tag_definitions,
        "total_categories": len(tag_definitions),
        "usage_hint": "Verwende diese Tags mit list_engineering_tools(tags=['...'])",
        "next_step": "2️⃣ list_engineering_tools(tags=['...'])",
        "workflow": "1️⃣ ✓ categories → 2️⃣ list_tools → 3️⃣ get_details → 4️⃣ calculate"
    }

@mcp.tool(
    name="list_engineering_tools",
    description="""Listet Engineering-Tools auf - entweder nach spezifischen Tags oder alle verfügbaren Tools

📋 VERWENDUNGSMÖGLICHKEITEN:
1. Mit spezifischen Tags: list_engineering_tools(tags=["elementar"]) 
2. Alle Tools anzeigen: list_engineering_tools(tags=["all"])

🏷️ Verfügbare Tag-Filter:
• ["elementar"] - Grundlegende geometrische Berechnungen (Flächen, Volumen, Umfang)
• ["mechanik"] - Mechanische Berechnungen (Kesselformel, Spannungen)
• ["Fläche"] - Nur Flächenberechnungen
• ["Volumen"] - Nur Volumenberechnungen  
• ["Umfang"] - Nur Umfangsberechnungen
• ["all"] - Alle verfügbaren Tools anzeigen

💡 EMPFEHLUNG: Nutze ["all"] um eine vollständige Übersicht zu erhalten!""",
    tags=["meta"]
)
async def list_engineering_tools(
    tags: List[str],
    ctx: Context = None
) -> List[Dict]:
    """
    Listet alle verfügbaren Engineering-Tools mit spezifischen Tags auf oder alle Tools.
    
    Args:
        tags: Tag-Filter (z.B. ["elementar"], ["mechanik"] oder ["all"] für alle Tools) - PFLICHTPARAMETER
        ctx: FastMCP Context für Logging
        
    Returns:
        List[Dict]: Tools mit Namen, Kurzbeschreibung und lösbaren Variablen
    """
    global _session_state
    
    # Spezielle Behandlung für "all" Tag
    show_all = "all" in tags
    
    if ctx:
        if show_all:
            await ctx.info(f"📂 Sammle ALLE verfügbaren Engineering-Tools")
        else:
            await ctx.info(f"📂 Sammle Engineering-Tools für Tags: {tags}")
    
    # Hole Engineering-Tools aus separater Registry
    tool_info = get_tool_info_for_llm(include_engineering=True)
    
    # Filter nach Tags oder zeige alle
    if show_all:
        # Zeige alle Tools
        filtered_tools = tool_info
    else:
        # Filter nach Tags (Tool muss mindestens einen der angegebenen Tags haben)
        filtered_tools = []
        for tool in tool_info:
            tool_tags = tool.get("tags", [])
            if any(tag in tool_tags for tag in tags):
                filtered_tools.append(tool)
    
    # Kompakte Darstellung für Discovery
    compact_tools = []
    for tool in filtered_tools:
        compact_tools.append({
            "name": tool["name"],
            "short_description": tool.get("short_description", tool["description"].split(".")[0]),
            "solvable_variables": tool["solvable_variables"],
            "tags": tool["tags"],
            "category": tool["category"]
        })
    
    # Sortiere Tools nach Kategorie und Name für bessere Übersicht
    compact_tools.sort(key=lambda x: (x["category"], x["name"]))
    
    # Session-Tracking
    tool_names = [tool["name"] for tool in compact_tools]
    _session_state["viewed_functions"].update(tool_names)
    
    if ctx:
        if show_all:
            await ctx.info(f"✅ Alle Tools gefunden: {len(compact_tools)} Engineering-Tools verfügbar")
        else:
            await ctx.info(f"Gefunden: {len(compact_tools)} Tools mit Tags {tags}")
    
    # Erweiterte Antwort für "all" Tag
    if show_all:
        # Gruppiere nach Kategorien für bessere Übersicht
        categories = {}
        for tool in compact_tools:
            cat = tool["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(tool)
        
        return {
            "step": 2,
            "mode": "all_tools",
            "total_tools": len(compact_tools),
            "categories": categories,
            "category_summary": {cat: len(tools) for cat, tools in categories.items()},
            "all_tools": compact_tools,
            "next_step": "3️⃣ get_tool_details(tool_name='...')",
            "workflow": "1️⃣ ✓ → 2️⃣ ✓ list_tools(all) → 3️⃣ get_details → 4️⃣ calculate",
            "hint": "Wähle einen tool_name aus der vollständigen Liste für get_tool_details()",
            "tip": "📋 Die Tools sind nach Kategorien gruppiert für bessere Übersicht"
        }
    else:
        # Standard-Antwort für spezifische Tags
        return {
            "step": 2,
            "requested_tags": tags,
            "tools": compact_tools,
            "tool_count": len(compact_tools),
            "next_step": "3️⃣ get_tool_details(tool_name='...')",
            "workflow": "1️⃣ ✓ → 2️⃣ ✓ list_tools → 3️⃣ get_details → 4️⃣ calculate",
            "hint": "Wähle einen tool_name aus der Liste für get_tool_details()"
        }

@mcp.tool(
    name="get_tool_details",
    description="Ruft detaillierte Informationen zu einem spezifischen Tool ab und schaltet es für die Ausführung frei. Verwende dieses Tool IMMER bevor Du das Tool call_tool aufrufst",
    tags=["meta"]
)
async def get_tool_details(
    tool_name: str,
    ctx: Context = None
) -> Dict:
    """
    Liefert vollständige Dokumentation eines Engineering-Tools.
    WICHTIG: Schaltet das Tool nach diesem Schritt für call_tool frei!
    
    Args:
        tool_name: Name des Tools (z.B. "solve_kesselformel")
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Ausführliche Tool-Dokumentation mit Parametern, Beispielen und Schema
    """
    global _session_state
    
    if ctx:
        await ctx.info(f"🔍 Hole Details für Tool: {tool_name}")
    
    # Rate-Limiting Check
    current_minute = datetime.datetime.utcnow().strftime("%Y%m%d%H%M")
    rate_key = f"get_details_{current_minute}"
    _session_state["call_count"][rate_key] = _session_state["call_count"].get(rate_key, 0) + 1
    
    if _session_state["call_count"][rate_key] > 10:
        return {
            "error": "Rate-Limit erreicht",
            "message": "Maximal 10 get_tool_details Aufrufe pro Minute",
            "retry_after": "1 minute"
        }
    
    try:
        details = await get_tool_details_from_registry(tool_name)
        
        # ⚡ WHITELIST TOOL FÜR call_tool
        _session_state["whitelisted_tools"].add(tool_name)
        _session_state["viewed_functions"].add(tool_name)
        
        # Erweitere Details um Whitelisting-Info
        details.update({
            "whitelisted": True,
            "execution_unlocked": True,
            "next_step": f"Verwende call_tool(tool_name='{tool_name}', parameters={{...}}) zur Ausführung",
            "session_info": f"Tool ist jetzt für diese Session freigeschaltet"
        })
        
        if ctx:
            await ctx.info(f"✅ Tool '{tool_name}' für Ausführung freigeschaltet")
        
        return details
        
    except ValueError as e:
        if ctx:
            await ctx.error(f"Tool nicht gefunden: {tool_name}")
        
        # Hilfreiche Fehlermeldung mit verfügbaren Tools
        available_tools = list(get_tool_info_for_llm(include_engineering=True))
        tool_names = [tool["name"] for tool in available_tools]
        
        return {
            "error": str(e),
            "available_tools": tool_names[:10],  # Erste 10 Tools
            "hint": "Nutze list_engineering_tools(tags=['...']) um verfügbare Tools zu sehen",
            "workflow_reminder": "1️⃣ get_available_categories → 2️⃣ list_engineering_tools → 3️⃣ get_tool_details → 4️⃣ call_tool"
        }

@mcp.tool(
    name="call_tool",
    description="""🔧 ULTRA-TOLERANTE Tool-Ausführung - Führt Engineering-Tools aus und repariert automatisch alle LLM-Syntax-Fehler

⚡ AKZEPTIERTE PARAMETER-FORMATE:
1. Standard JSON: {"pressure": "100 bar", "wall_thickness": "50 mm"}
2. Python-Dict: {pressure="100 bar", wall_thickness="50 mm"}  
3. String-Parameter: 'pressure="100 bar", wall_thickness="50 mm"'
4. Code-Fence: ```json {"pressure": "100 bar"} ```
5. n8n-Workflow-JSON (automatische Extraktion)
6. Verschachtelte JSON-Strukturen (automatische Suche)

✅ KORREKTE BEISPIELE:
• call_tool(tool_name="solve_kesselformel", parameters={"pressure": "100 bar", "wall_thickness": "50 mm", "allowable_stress": "200 MPa"})
• call_tool(tool_name="solve_circle_area", parameters={"radius": "25 mm"})
• call_tool(tool_name="solve_rechteck", parameters={"length": "10 cm", "width": "5 cm"})

🎯 WICHTIG: Alle Engineering-Parameter benötigen EINHEITEN!
• ✅ "100 bar" ✅ "50 mm" ✅ "200 MPa" 
• ❌ 100 ❌ 50 ❌ 200 (ohne Einheiten)""",
    tags=["meta"]
)
async def call_tool(
    tool_name: str,
    parameters: Union[Dict[str, Any], str],  # Erweitert: auch String akzeptieren
    ctx: Context = None
) -> Dict:
    """
    TOLERANTE Tool-Ausführung mit automatischer LLM-Fehler-Reparatur.
    
    Unterstützt alle Standard-JSON-Parameter sowie:
    - Python-dict-Syntax: {param=value, other=True}
    - Code-Fence-wrapped JSON: ```json {"param": value} ```
    - String-Parameter: Parameter als JSON-String
    - Automatische Bool/None/String-Konvertierung
    
    Args:
        tool_name: Name des Engineering-Tools
        parameters: Tool-Parameter (dict oder JSON-String)
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Berechnungsergebnis oder detaillierte Fehlerinformationen
    """
    if ctx:
        await ctx.info(f"🚀 Starte tolerante Tool-Ausführung: {tool_name}")
    
    # ===== LAYER 1: STRENGE VALIDIERUNG =====
    try:
        # Normale Parameter-Verarbeitung (wenn dict)
        if isinstance(parameters, dict):
            parsed_params = parameters
        else:
            # String-Parameter → dict konvertieren
            parsed_params = _repair_arguments(parameters)
        
        # Schema-Validierung mit Pydantic
        validated = CalculateToolSchema(tool_name=tool_name, parameters=parsed_params)
        
    except (ValidationError, TypeError, ValueError) as e:
        # ===== LAYER 2: HEURISTISCHE REPARATUR =====
        if ctx:
            await ctx.info(f"🔧 Repariere LLM-Syntax-Fehler: {str(e)[:100]}...")
        
        try:
            # Reparaturversuch
            raw_input = {"tool_name": tool_name, "parameters": parameters}
            repaired = _repair_arguments(raw_input)
            
            # Erneute Validierung nach Reparatur
            validated = CalculateToolSchema(**repaired)
            
            if ctx:
                await ctx.info(f"✅ LLM-Fehler erfolgreich repariert")
                
        except ValidationError as repair_error:
            # ===== LAYER 3: KONTROLLIERTE FEHLANTWORT =====
            
            # Spezial-Behandlung für n8n-Workflow-JSON-Erkennungen
            if isinstance(parameters, dict) and parameters.get("detected_format") == "n8n_workflow":
                return {
                    "info": "n8n-Workflow-JSON erkannt",
                    "detected_format": "n8n_workflow", 
                    "system_message": parameters.get("system_message", ""),
                    "next_step": "Bitte geben Sie Engineering-Parameter separat an",
                    "format_examples": [
                        '{"pressure": "100 bar", "wall_thickness": "50 mm", "allowable_stress": "200 MPa"}',
                        '{"radius": "25 mm"}',
                        '{"length": "10 cm", "width": "5 cm"}'
                    ],
                    "wichtig": "Alle Parameter benötigen Einheiten (z.B. 'mm', 'bar', 'MPa')",
                    "status": "workflow_detected"
                }
            
            return {
                "error": "Schema-Validierung fehlgeschlagen",
                "original_error": str(e),
                "repair_error": str(repair_error),
                "received_tool_name": tool_name,
                "received_parameters": str(parameters)[:200],
                "expected_format": {
                    "tool_name": "string (z.B. 'solve_kesselformel')",
                    "parameters": "dict (z.B. {'pressure': '100 bar', 'wall_thickness': '50 mm'})"
                },
                "format_examples": [
                    'call_tool(tool_name="solve_kesselformel", parameters={"pressure": "100 bar", "wall_thickness": "50 mm", "allowable_stress": "200 MPa"})',
                    'call_tool(tool_name="solve_circle_area", parameters={"radius": "25 mm"})'
                ],
                "hint": "Alle Engineering-Parameter benötigen EINHEITEN! Format: 'Wert Einheit' (z.B. '100 bar')",
                "status": "error"
            }
    
    # ===== NORMALE TOOL-AUSFÜHRUNG =====
    # Verwende validierte Parameter
    tool_name = validated.tool_name
    parameters = validated.parameters
    
    # 🔒 SICHERHEITS-CHECK: Whitelist-Validierung
    if tool_name not in _session_state["whitelisted_tools"]:
        return {
            "error": f"Tool '{tool_name}' ist nicht für die Ausführung freigeschaltet",
            "security_info": "Tools müssen zuerst über get_tool_details() freigeschaltet werden",
            "whitelisted_tools": list(_session_state["whitelisted_tools"]),
            "required_workflow": [
                "1️⃣ get_available_categories()",
                "2️⃣ list_engineering_tools(tags=['...'])", 
                "3️⃣ get_tool_details(tool_name='...')",
                "4️⃣ call_tool(tool_name='...', parameters={...})"
            ],
            "status": "security_error"
        }
    
    try:
        result = await call_engineering_tool(tool_name, parameters)
        
        if ctx:
            await ctx.info(f"✅ Tool '{tool_name}' erfolgreich ausgeführt")
        
        # Zusätzliche Metadaten zur Antwort hinzufügen
        if isinstance(result, dict):
            result.update({
                "execution_status": "success",
                "tolerant_parsing": True,
                "tool_executed": tool_name,
                "security_validated": True
            })
        
        return {
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result,
            "status": "success"
        }
        
    except Exception as execution_error:
        error_msg = f"Fehler bei Engineering-Berechnung '{tool_name}': {execution_error}"
        if ctx:
            await ctx.error(error_msg)
        
        return {
            "tool_name": tool_name,
            "parameters": parameters,
            "error": str(execution_error),
            "error_type": type(execution_error).__name__,
            "status": "error",
            "hint": "Prüfe Parameter-Typen und -Werte. Nutze get_tool_details() für detaillierte Parameter-Info."
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
    print(f"   4. call_tool")
    return tools_count 