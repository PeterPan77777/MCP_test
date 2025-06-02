from fastmcp import FastMCP, Context
import datetime
from typing import Optional, Dict, List, Literal, Any

# MCP Server mit hierarchischem Tool-Schema
mcp = FastMCP(
    name="EngineersCalc", 
    instructions="""
🔧 Engineering Calculation Server - Hierarchisches Tool-Schema

📋 ÜBERSICHT:
Dieser Server nutzt ein hierarchisches Tool-Schema mit einem Dispatcher.
Beim Handshake siehst du nur 3 Tools: clock, dispatch_engineering und execute_tool.
Nach Domain-Auswahl kannst du Tools über execute_tool ausführen.

🎯 HIERARCHISCHER WORKFLOW:
1️⃣ dispatch_engineering(domain="...", action="...") - Wähle Domain und Aktion
2️⃣ execute_tool(tool_name="...", parameters={...}) - Führe Domain-Tool aus

📂 VERFÜGBARE DOMAINS:
- pressure: Druckbehälter, Kesselformeln
- geometry: Flächen, Volumen, geometrische Berechnungen
- materials: Werkstoffkennwerte, Festigkeitsberechnungen

💡 BEISPIEL-WORKFLOW:
1. dispatch_engineering(domain="pressure", action="activate")
2. execute_tool(tool_name="pressure.solve_kesselformel", parameters={"p": 10, "d": 100, "sigma": 160})

⚙️ KERNKONZEPT:
- Minimaler Handshake (nur 3 Tools)
- Domain-basierte Tool-Aktivierung
- Indirekte Tool-Ausführung über execute_tool
"""
)

# Session State für aktive Domain
_session_state = {
    "active_domain": None,
    "allowed_tools": set()
}

# Registry für versteckte Engineering-Tools (NICHT bei MCP registriert!)
_ENGINEERING_TOOLS = {}

@mcp.tool()
def clock() -> str:
    """Aktuelle UTC-Zeit zurückgeben"""
    return datetime.datetime.utcnow().isoformat() + "Z"

# ===== DISPATCHER TOOL (immer sichtbar) =====

@mcp.tool(
    name="dispatch_engineering",
    description="Wählt eine Engineering-Domain und aktiviert deren Tools. Domains: pressure, geometry, materials",
    tags=["dispatcher", "meta"]
)
async def dispatch_engineering(
    domain: Literal["pressure", "geometry", "materials"],
    action: Literal["list", "activate", "info"] = "activate",
    ctx: Context = None
) -> Dict:
    """
    Dispatcher für hierarchische Tool-Aktivierung.
    
    Args:
        domain: Engineering-Domain (pressure, geometry, materials)
        action: Aktion (list=Tools anzeigen, activate=Domain aktivieren, info=Domain-Info)
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Aktivierte Domain und verfügbare Tools
    """
    global _session_state
    
    if ctx:
        await ctx.info(f"Dispatcher: Domain '{domain}', Action '{action}'")
    
    # Domain-spezifische Tool-Listen
    domain_tools = {
        "pressure": ["pressure.solve_kesselformel"],
        "geometry": ["geometry.solve_circle_area"], 
        "materials": []  # Noch keine Tools implementiert
    }
    
    domain_descriptions = {
        "pressure": "Druckbehälter, Kesselformeln, Druckberechnungen",
        "geometry": "Flächenberechnungen, Volumen, geometrische Formeln",
        "materials": "Werkstoffkennwerte, Festigkeitsberechnungen (in Entwicklung)"
    }
    
    if action == "info":
        # Informationen über alle Domains
        return {
            "available_domains": list(domain_tools.keys()),
            "domain_details": {
                d: {
                    "description": domain_descriptions[d],
                    "tool_count": len(domain_tools[d]),
                    "status": "active" if domain_tools[d] else "in_development"
                }
                for d in domain_tools
            },
            "current_domain": _session_state.get("active_domain"),
            "hint": "Verwende action='activate' um eine Domain zu aktivieren"
        }
    
    elif action == "list":
        # Liste Tools der gewählten Domain
        tools = domain_tools.get(domain, [])
        tool_details = []
        for tool_name in tools:
            if tool_name in _ENGINEERING_TOOLS:
                tool_details.append({
                    "name": tool_name,
                    "description": _ENGINEERING_TOOLS[tool_name]["description"],
                    "parameters": _ENGINEERING_TOOLS[tool_name]["parameters"]
                })
        
        return {
            "domain": domain,
            "description": domain_descriptions.get(domain),
            "tools": tool_details,
            "tool_count": len(tools),
            "hint": f"Verwende execute_tool(tool_name='...', parameters={{...}}) nach Aktivierung"
        }
    
    elif action == "activate":
        # Aktiviere Domain
        _session_state["active_domain"] = domain
        _session_state["allowed_tools"] = set(domain_tools.get(domain, []))
        
        if ctx:
            await ctx.info(f"✅ Domain '{domain}' aktiviert mit {len(domain_tools.get(domain, []))} Tools")
        
        return {
            "domain_activated": domain,
            "description": domain_descriptions.get(domain),
            "tools_available": list(_session_state["allowed_tools"]),
            "message": f"✅ {domain.title()}-Tools sind jetzt über execute_tool verfügbar!",
            "examples": get_domain_examples(domain)
        }

def get_domain_examples(domain: str) -> List[str]:
    """Gibt Beispiel-Aufrufe für Domain-Tools zurück"""
    examples = {
        "pressure": [
            'execute_tool(tool_name="pressure.solve_kesselformel", parameters={"p": 10, "d": 100, "sigma": 160})',
            'execute_tool(tool_name="pressure.solve_kesselformel", parameters={"p": 10, "d": 100, "s": 5})'
        ],
        "geometry": [
            'execute_tool(tool_name="geometry.solve_circle_area", parameters={"radius": 10})',
            'execute_tool(tool_name="geometry.solve_circle_area", parameters={"area": 314.159})'
        ],
        "materials": []
    }
    return examples.get(domain, [])

# ===== EXECUTE TOOL (führt versteckte Tools aus) =====

@mcp.tool(
    name="execute_tool",
    description="Führt ein aktiviertes Engineering-Tool mit den gegebenen Parametern aus",
    tags=["executor", "engineering"]
)
async def execute_tool(
    tool_name: str,
    parameters: Dict[str, Any],
    ctx: Context = None
) -> Dict:
    """
    Führt ein Engineering-Tool aus der aktiven Domain aus.
    
    Args:
        tool_name: Name des Tools (z.B. "pressure.solve_kesselformel")
        parameters: Dictionary mit Tool-Parametern
        ctx: FastMCP Context
        
    Returns:
        Dict: Ergebnis der Tool-Ausführung
    """
    global _session_state, _ENGINEERING_TOOLS
    
    # Prüfe ob Tool erlaubt ist
    if tool_name not in _session_state["allowed_tools"]:
        return {
            "error": f"Tool '{tool_name}' ist nicht aktiviert",
            "hint": "Aktiviere zuerst die passende Domain mit dispatch_engineering()",
            "allowed_tools": list(_session_state["allowed_tools"])
        }
    
    # Prüfe ob Tool existiert
    if tool_name not in _ENGINEERING_TOOLS:
        return {
            "error": f"Tool '{tool_name}' nicht gefunden",
            "available_tools": list(_ENGINEERING_TOOLS.keys())
        }
    
    # Führe Tool aus
    try:
        tool_func = _ENGINEERING_TOOLS[tool_name]["function"]
        result = await tool_func(**parameters, ctx=ctx)
        return result
    except Exception as e:
        return {
            "error": f"Fehler bei Tool-Ausführung: {str(e)}",
            "tool": tool_name,
            "parameters": parameters
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
        "active_domain": None,
        "allowed_tools": set()
    }
    
    print(f"🎯 Hierarchisches Tool-Schema mit Tool-Hiding aktiviert:")
    print(f"   ├─ Handshake: 3 Tools sichtbar (clock, dispatcher, executor)")
    print(f"   ├─ Domains: pressure, geometry, materials")
    print(f"   ├─ Workflow: dispatch → execute_tool")
    print(f"   └─ {len(_ENGINEERING_TOOLS)} Engineering-Tools versteckt")
    
    return 3  # clock, dispatch_engineering, execute_tool

# Beim Import initialisieren
init_hierarchical_tools() 