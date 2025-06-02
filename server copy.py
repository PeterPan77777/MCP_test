from fastmcp import FastMCP, Context
import datetime
import json
import re
import ast
from typing import Optional, Dict, List, Literal, Any, Union
from pydantic import BaseModel, ValidationError

# MCP Server mit 4-Stufen Tool-Discovery Schema
mcp = FastMCP(
    name="EngineersCalc", 
    instructions="""
🔧 Engineering Calculation Server - 4-Stufen Tool-Discovery

📋 ÜBERSICHT:
Dieser Server nutzt ein robustes 4-Stufen-Schema für Tool-Discovery.
Beim Handshake siehst du nur 5 minimale Tools.

🎯 4-STUFEN WORKFLOW:
1️⃣ list_categories() → Zeigt verfügbare Kategorien
2️⃣ list_functions_in_category(category="...") → Listet Funktionen einer Kategorie
3️⃣ get_function_details(function_name="...") → Holt Schema & Beispiele
4️⃣ call_tool(tool_name="...", parameters={...}) → Führt Tool aus (fehlertolerant!)

📂 VERFÜGBARE KATEGORIEN:
- pressure: Druckbehälter, Kesselformeln
- geometry: Flächen, Volumen, geometrische Berechnungen
- materials: Werkstoffkennwerte, Festigkeitsberechnungen

💡 BEISPIEL-WORKFLOW:
1. categories = list_categories()
2. functions = list_functions_in_category(category="pressure") 
3. details = get_function_details(function_name="pressure.solve_kesselformel")
4. result = call_tool(tool_name="pressure.solve_kesselformel", parameters={"p": 10, "d": 100, "sigma": 160})

⚙️ KERNKONZEPT:
- Minimaler Handshake (nur 5 Tools)
- Schrittweise Kontext-Anreicherung
- Whitelist-basierte Sicherheit (nur nach get_function_details aufrufbar)
- Fehlertolerante Tool-Ausführung (repariert LLM-Syntax-Fehler automatisch!)
"""
)

# Session State mit erweitertem Whitelisting
_session_state = {
    "viewed_categories": set(),      # Angesehene Kategorien
    "viewed_functions": set(),       # Angesehene Funktionen
    "whitelisted_tools": set(),      # Freigeschaltete Tools (nach get_function_details)
    "call_count": {}                 # Rate-Limiting Counter
}

# Registry für versteckte Engineering-Tools (NICHT bei MCP registriert!)
_ENGINEERING_TOOLS = {}

# Kategorie-Definitionen
_CATEGORIES = {
    "pressure": {
        "name": "Pressure & Vessels",
        "description": "Druckbehälter, Kesselformeln, Druckberechnungen nach AD2000",
        "icon": "🔧"
    },
    "geometry": {
        "name": "Geometry & Areas", 
        "description": "Flächenberechnungen, Volumen, geometrische Formeln",
        "icon": "📐"
    },
    "materials": {
        "name": "Materials & Strength",
        "description": "Werkstoffkennwerte, Festigkeitsberechnungen (in Entwicklung)",
        "icon": "🛡️"
    }
}

# Tool-zu-Kategorie Mapping
_TOOL_CATEGORIES = {
    "pressure": ["pressure.solve_kesselformel"],
    "geometry": ["geometry.solve_circle_area"],
    "materials": []  # Noch keine Tools implementiert
}

@mcp.tool()
def clock() -> str:
    """Aktuelle UTC-Zeit zurückgeben"""
    return datetime.datetime.utcnow().isoformat() + "Z"

# ===== STUFE 1: KATEGORIEN AUFLISTEN =====

@mcp.tool(
    name="list_categories",
    description="Listet alle verfügbaren Tool-Kategorien auf. Erster Schritt im 4-Stufen-Workflow.",
    tags=["discovery", "step1"]
)
async def list_categories(ctx: Context = None) -> Dict:
    """
    Stufe 1: Zeigt verfügbare Tool-Kategorien.
    
    Returns:
        Dict mit Kategorien und deren Beschreibungen
    """
    global _session_state
    
    if ctx:
        await ctx.info("📋 Stufe 1: Kategorien werden aufgelistet")
    
    categories = []
    for cat_id, cat_info in _CATEGORIES.items():
        tool_count = len(_TOOL_CATEGORIES.get(cat_id, []))
        categories.append({
            "id": cat_id,
            "name": cat_info["name"],
            "description": cat_info["description"],
            "icon": cat_info["icon"],
            "tool_count": tool_count,
            "status": "active" if tool_count > 0 else "in_development"
        })
    
    _session_state["viewed_categories"].update(_CATEGORIES.keys())
    
    return {
        "step": 1,
        "categories": categories,
        "total_categories": len(categories),
        "next_step": "Verwende list_functions_in_category(category='...') für Details",
        "workflow": "1️⃣ list_categories → 2️⃣ list_functions → 3️⃣ get_details → 4️⃣ call_tool"
    }

# ===== STUFE 2: FUNKTIONEN IN KATEGORIE AUFLISTEN =====

@mcp.tool(
    name="list_functions_in_category",
    description="Listet alle Funktionen einer bestimmten Kategorie auf. Zweiter Schritt im 4-Stufen-Workflow.",
    tags=["discovery", "step2"]
)
async def list_functions_in_category(
    category: str,
    ctx: Context = None
) -> Dict:
    """
    Stufe 2: Zeigt Funktionen einer spezifischen Kategorie.
    
    Args:
        category: Kategorie-ID (z.B. "pressure", "geometry")
        
    Returns:
        Dict mit Funktionsliste der Kategorie
    """
    global _session_state
    
    if ctx:
        await ctx.info(f"📂 Stufe 2: Funktionen in Kategorie '{category}' werden aufgelistet")
    
    # Validiere Kategorie
    if category not in _CATEGORIES:
        return {
            "error": f"Kategorie '{category}' nicht gefunden",
            "available_categories": list(_CATEGORIES.keys()),
            "hint": "Verwende list_categories() um gültige Kategorien zu sehen"
        }
    
    # Hole Tools der Kategorie
    tool_names = _TOOL_CATEGORIES.get(category, [])
    functions = []
    
    for tool_name in tool_names:
        if tool_name in _ENGINEERING_TOOLS:
            tool_info = _ENGINEERING_TOOLS[tool_name]
            functions.append({
                "name": tool_name,
                "description": tool_info["description"],
                "parameter_count": len(tool_info["parameters"]),
                "category": category
            })
    
    _session_state["viewed_functions"].update(tool_names)
    
    return {
        "step": 2,
        "category": category,
        "category_info": _CATEGORIES[category],
        "functions": functions,
        "function_count": len(functions),
        "next_step": "Verwende get_function_details(function_name='...') für Schema & Beispiele",
        "workflow": "1️⃣ ✓ → 2️⃣ list_functions → 3️⃣ get_details → 4️⃣ call_tool"
    }

# ===== STUFE 3: FUNKTIONS-DETAILS ABRUFEN =====

@mcp.tool(
    name="get_function_details",
    description="Holt detaillierte Informationen zu einer Funktion inkl. Schema und Beispielen. Dritter Schritt im 4-Stufen-Workflow.",
    tags=["discovery", "step3"]
)
async def get_function_details(
    function_name: str,
    ctx: Context = None
) -> Dict:
    """
    Stufe 3: Liefert detailliertes Schema und Beispiele für eine Funktion.
    Nach diesem Schritt ist die Funktion für call_tool freigeschaltet!
    
    Args:
        function_name: Vollständiger Funktionsname (z.B. "pressure.solve_kesselformel")
        
    Returns:
        Dict mit Schema, Parametern und Beispiel-Aufrufen
    """
    global _session_state
    
    if ctx:
        await ctx.info(f"🔍 Stufe 3: Details für Funktion '{function_name}' werden abgerufen")
    
    # Rate-Limiting Check
    current_minute = datetime.datetime.utcnow().strftime("%Y%m%d%H%M")
    rate_key = f"get_details_{current_minute}"
    _session_state["call_count"][rate_key] = _session_state["call_count"].get(rate_key, 0) + 1
    
    if _session_state["call_count"][rate_key] > 10:
        return {
            "error": "Rate-Limit erreicht",
            "message": "Maximal 10 get_function_details Aufrufe pro Minute",
            "retry_after": "1 minute"
        }
    
    # Validiere Funktion
    if function_name not in _ENGINEERING_TOOLS:
        # Hilfreiche Fehlermeldung mit ähnlichen Funktionen
        available = list(_ENGINEERING_TOOLS.keys())
        suggestions = [f for f in available if any(part in f for part in function_name.split("."))]
        
        return {
            "error": f"Funktion '{function_name}' nicht gefunden",
            "available_functions": available,
            "suggestions": suggestions if suggestions else None,
            "hint": "Verwende list_functions_in_category() um gültige Funktionen zu sehen"
        }
    
    # Hole Tool-Info
    tool_info = _ENGINEERING_TOOLS[function_name]
    
    # Whitelist Tool für call_tool
    _session_state["whitelisted_tools"].add(function_name)
    
    # Generiere Beispiele basierend auf Tool
    examples = []
    if "kesselformel" in function_name:
        examples = [
            {
                "description": "Berechne Wandstärke bei gegebenem Druck, Durchmesser und Spannung",
                "call": 'call_tool(tool_name="pressure.solve_kesselformel", parameters={"p": 10, "d": 100, "sigma": 160})',
                "expected_result": {"unknown_variable": "s", "result": 3.125, "unit": "mm"}
            },
            {
                "description": "Berechne zulässige Spannung bei gegebenen Abmessungen",
                "call": 'call_tool(tool_name="pressure.solve_kesselformel", parameters={"p": 10, "d": 100, "s": 5})',
                "expected_result": {"unknown_variable": "sigma", "result": 100.0, "unit": "N/mm²"}
            }
        ]
    elif "circle_area" in function_name:
        examples = [
            {
                "description": "Berechne Fläche aus Radius",
                "call": 'call_tool(tool_name="geometry.solve_circle_area", parameters={"radius": 10})',
                "expected_result": {"unknown_variable": "area", "result": 314.159, "unit": "m²"}
            },
            {
                "description": "Berechne Radius aus Fläche",
                "call": 'call_tool(tool_name="geometry.solve_circle_area", parameters={"area": 314.159})',
                "expected_result": {"unknown_variable": "radius", "result": 10.0, "unit": "m"}
            }
        ]
    
    # Erstelle Parameter-Schema
    param_schema = {}
    for param_name, param_desc in tool_info["parameters"].items():
        param_schema[param_name] = {
            "type": "number",
            "description": param_desc,
            "required": False  # Alle Parameter optional bei n-1 Pattern
        }
    
    return {
        "step": 3,
        "function_name": function_name,
        "description": tool_info["description"],
        "whitelisted": True,
        "schema": {
            "type": "object",
            "properties": param_schema,
            "additionalProperties": False
        },
        "parameters": tool_info["parameters"],
        "examples": examples,
        "next_step": "Verwende call_tool(tool_name='...', parameters={...}) zur Ausführung",
        "workflow": "1️⃣ ✓ → 2️⃣ ✓ → 3️⃣ get_details → 4️⃣ call_tool",
        "hint": "⚡ Diese Funktion ist jetzt für call_tool freigeschaltet!"
    }

# ===== TOLERANTE CALL-TOOL SCHEMAS UND HILFSFUNKTIONEN (BEIBEHALTEN!) =====

class CallToolSchema(BaseModel):
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
    """
    # Fall 1: String-Input → JSON parsen
    if isinstance(raw, str):
        raw = _strip_codefence(raw)
        
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

# ===== STUFE 4: TOLERANTE TOOL-AUSFÜHRUNG (MIT LLM-FEHLER-REPARATUR!) =====

@mcp.tool(
    name="call_tool",
    description="🔧 Fehlertolerante Tool-Ausführung - Führt ein freigeschaltetes Tool aus und repariert automatisch LLM-Syntax-Fehler. Vierter Schritt im 4-Stufen-Workflow.",
    tags=["execution", "step4", "tolerant"]
)
async def call_tool(
    tool_name: str,
    parameters: Union[Dict[str, Any], str],  # Erweitert: auch String akzeptieren
    ctx: Context = None
) -> Dict:
    """
    Stufe 4: TOLERANTE Tool-Ausführung mit automatischer LLM-Fehler-Reparatur.
    Tool muss vorher über get_function_details freigeschaltet worden sein!
    
    Unterstützt:
    - Normale JSON-Parameter: {"param": "value"}
    - Python-dict-Syntax: {param="value", other=True}
    - Code-Fence-wrapped JSON: ```json {"param": "value"} ```
    - String-Parameter: Parameter als JSON-String
    - Automatische Bool/None-Konvertierung
    
    Args:
        tool_name: Name des Tools (z.B. "pressure.solve_kesselformel")
        parameters: Tool-Parameter (dict oder JSON-String)
        ctx: FastMCP Context
        
    Returns:
        Dict: Ergebnis der Tool-Ausführung oder Fehlerdetails
    """
    global _session_state, _ENGINEERING_TOOLS
    
    if ctx:
        await ctx.info(f"🚀 Stufe 4: Tool '{tool_name}' wird ausgeführt")
    
    # ===== LAYER 1: STRENGE VALIDIERUNG =====
    try:
        # Normale Parameter-Verarbeitung (wenn dict)
        if isinstance(parameters, dict):
            parsed_params = parameters
        else:
            # String-Parameter → dict konvertieren
            parsed_params = _repair_arguments(parameters)
        
        # Schema-Validierung mit Pydantic
        validated = CallToolSchema(tool_name=tool_name, parameters=parsed_params)
        
    except (ValidationError, TypeError, ValueError) as e:
        # ===== LAYER 2: HEURISTISCHE REPARATUR =====
        if ctx:
            await ctx.info(f"🔧 Repariere LLM-Syntax-Fehler: {str(e)[:100]}...")
        
        try:
            # Reparaturversuch
            raw_input = {"tool_name": tool_name, "parameters": parameters}
            repaired = _repair_arguments(raw_input)
            
            # Erneute Validierung nach Reparatur
            validated = CallToolSchema(**repaired)
            
            if ctx:
                await ctx.info(f"✅ LLM-Fehler erfolgreich repariert")
                
        except ValidationError as repair_error:
            # ===== LAYER 3: KONTROLLIERTE FEHLANTWORT =====
            return {
                "error": "Schema-Validierung fehlgeschlagen",
                "original_error": str(e),
                "repair_error": str(repair_error),
                "received_tool_name": tool_name,
                "received_parameters": str(parameters)[:200],
                "expected_format": {
                    "tool_name": "string (z.B. 'pressure.solve_kesselformel')",
                    "parameters": "dict (z.B. {'p': 10, 'd': 100, 'sigma': 160})"
                },
                "hint": "Verwende format: call_tool(tool_name='...', parameters={'key': value})"
            }
    
    # ===== NORMALE TOOL-AUSFÜHRUNG =====
    # Verwende validierte Parameter
    tool_name = validated.tool_name
    parameters = validated.parameters
    
    # Prüfe Whitelist (Sicherheit!)
    if tool_name not in _session_state["whitelisted_tools"]:
        return {
            "error": f"Tool '{tool_name}' ist nicht freigeschaltet",
            "hint": "Verwende zuerst get_function_details(function_name='...') um das Tool freizuschalten",
            "whitelisted_tools": list(_session_state["whitelisted_tools"]),
            "workflow": "Du musst dem 4-Stufen-Workflow folgen: 1→2→3→4"
        }
    
    # Prüfe ob Tool existiert
    if tool_name not in _ENGINEERING_TOOLS:
        return {
            "error": f"Tool '{tool_name}' nicht gefunden", 
            "available_tools": list(_ENGINEERING_TOOLS.keys()),
            "hint": "Verwende list_functions_in_category() um gültige Tools zu sehen"
        }
    
    # Führe Tool aus
    try:
        tool_func = _ENGINEERING_TOOLS[tool_name]["function"]
        result = await tool_func(**parameters, ctx=ctx)
        
        # Erfolgsmeldung mit Reparatur-Info
        if ctx:
            await ctx.info(f"✅ Tool '{tool_name}' erfolgreich ausgeführt")
        
        # Zusätzliche Metadaten zur Antwort hinzufügen
        result.update({
            "execution_status": "success",
            "tolerant_parsing": True,
            "tool_executed": tool_name,
            "workflow_complete": True
        })
        
        return result
        
    except Exception as execution_error:
        return {
            "error": f"Fehler bei Tool-Ausführung: {str(execution_error)}",
            "tool": tool_name,
            "parameters": parameters,
            "error_type": type(execution_error).__name__,
            "hint": "Prüfe Parameter-Typen und -Werte"
        }

# ===== VERSTECKTE ENGINEERING TOOLS (nicht bei MCP registriert!) =====

async def _solve_kesselformel(
    sigma: Optional[float] = None,
    p: Optional[float] = None,
    d: Optional[float] = None,
    s: Optional[float] = None,
    ctx: Context = None
) -> Dict:
    """Interne Kesselformel-Berechnung"""
    from sympy import symbols, Eq, solve, N
    
    # Validierung
    provided = {k: v for k, v in {"sigma": sigma, "p": p, "d": d, "s": s}.items() if v is not None}
    if len(provided) != 3:
        raise ValueError("Genau 3 von 4 Parametern müssen angegeben werden")
    
    # SymPy Berechnung
    sigma_sym, p_sym, d_sym, s_sym = symbols('sigma p d s', positive=True)
    formula = Eq(sigma_sym, p_sym * d_sym / (2 * s_sym))
    
    # Finde unbekannte Variable
    unknown_var = next(k for k in ["sigma", "p", "d", "s"] if k not in provided)
    target_symbol = {"sigma": sigma_sym, "p": p_sym, "d": d_sym, "s": s_sym}[unknown_var]
    
    # Löse nach unbekannter Variable
    solution_expr = solve(formula, target_symbol)[0]
    
    # Substitution
    subs_dict = {
        sigma_sym: sigma, p_sym: p, d_sym: d, s_sym: s
    }
    subs_dict = {k: v for k, v in subs_dict.items() if v is not None}
    
    result_value = float(N(solution_expr.subs(subs_dict)))
    
    # Einheit
    units = {"sigma": "N/mm²", "p": "bar", "d": "mm", "s": "mm"}
    
    return {
        "domain": "pressure",
        "tool": "kesselformel",
        "unknown_variable": unknown_var,
        "result": result_value,
        "unit": units[unknown_var],
        "formula": "σ = p·d/(2·s)",
        "input_parameters": provided
    }

async def _solve_circle_area(
    area: Optional[float] = None,
    radius: Optional[float] = None,
    ctx: Context = None
) -> Dict:
    """Interne Kreisflächen-Berechnung"""
    from sympy import symbols, Eq, solve, pi, N
    
    # Validierung
    if (area is None) == (radius is None):
        raise ValueError("Genau einer der Parameter (area oder radius) muss angegeben werden")
    
    # SymPy Berechnung
    A, r = symbols('A r', positive=True)
    formula = Eq(A, pi * r**2)
    
    if radius is not None:
        # Berechne Fläche
        result = float(N(pi * radius**2))
        return {
            "domain": "geometry", 
            "tool": "circle_area",
            "unknown_variable": "area",
            "result": result,
            "unit": "m²",
            "formula": "A = π·r²",
            "input_parameters": {"radius": radius}
        }
    else:
        # Berechne Radius
        solution = solve(formula.subs(A, area), r)[0]
        result = float(N(solution))
        return {
            "domain": "geometry",
            "tool": "circle_area", 
            "unknown_variable": "radius",
            "result": result,
            "unit": "m",
            "formula": "A = π·r² → r = √(A/π)",
            "input_parameters": {"area": area}
        }

# Registriere versteckte Tools
_ENGINEERING_TOOLS = {
    "pressure.solve_kesselformel": {
        "function": _solve_kesselformel,
        "description": "Kesselformel σ = p·d/(2·s) - Löst nach einer der 4 Variablen auf",
        "parameters": {
            "sigma": "Spannung [N/mm²] (optional)",
            "p": "Innendruck [bar] (optional)",
            "d": "Innendurchmesser [mm] (optional)",
            "s": "Wandstärke [mm] (optional)"
        }
    },
    "geometry.solve_circle_area": {
        "function": _solve_circle_area,
        "description": "Kreisfläche A = π·r² - Berechnet Fläche aus Radius oder umgekehrt",
        "parameters": {
            "area": "Kreisfläche [m²] (optional)",
            "radius": "Kreisradius [m] (optional)"
        }
    }
}

# Initialisierung
def init_hierarchical_tools():
    """Initialisiert das hierarchische Tool-System"""
    global _session_state
    _session_state = {
        "viewed_categories": set(),
        "viewed_functions": set(),
        "whitelisted_tools": set(),
        "call_count": {}
    }
    
    print(f"🎯 Hierarchisches Tool-Schema mit Tool-Hiding aktiviert:")
    print(f"   ├─ Handshake: 5 Tools sichtbar (clock, list_categories, list_functions, get_details, call_tool)")
    print(f"   ├─ Kategorien: pressure, geometry, materials")
    print(f"   ├─ Workflow: list_categories → list_functions → get_details → call_tool")
    print(f"   └─ {len(_ENGINEERING_TOOLS)} Engineering-Tools versteckt")
    
    return 5  # clock, list_categories, list_functions, get_details, call_tool

# Beim Import initialisieren
init_hierarchical_tools() 