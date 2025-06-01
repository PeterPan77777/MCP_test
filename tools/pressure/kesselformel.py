"""
Kesselformel Tool für MCP Engineering Server

Löst die Formel σ = p·d/(2·s) nach verschiedenen Variablen auf.
Lösbare Variablen: [sigma, p, d, s]
"""

from typing import Dict, Optional
from fastmcp import Context
from sympy import symbols, Eq, solve, N
from pydantic import BaseModel, field_validator


class KesselformelInput(BaseModel):
    """Input-Validierung für Kesselformel-Parameter"""
    p: Optional[float] = None       # Innendruck [N/mm²]
    d: Optional[float] = None       # Außendurchmesser [mm]
    s: Optional[float] = None       # Wanddicke [mm]
    sigma: Optional[float] = None   # Zulässige Spannung [N/mm²]
    
    @field_validator('p', 'd', 's', 'sigma')
    @classmethod
    def must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Alle Werte müssen positiv sein")
        return v


async def solve_kesselformel(
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
    # 1. Context-Logging
    if ctx:
        await ctx.info("Starte Kesselformel-Berechnung...")
    
    # 2. Input-Validierung
    inputs = KesselformelInput(p=p, d=d, s=s, sigma=sigma)
    provided_params = {k: v for k, v in inputs.model_dump().items() if v is not None}
    solvable_vars = ['sigma', 'p', 'd', 's']
    
    if len(provided_params) != 3:
        raise ValueError("Genau 3 von 4 Parametern müssen angegeben werden")
    
    # 3. SymPy-Symbole definieren
    p_sym, d_sym, s_sym, sigma_sym = symbols('p d s sigma', positive=True)
    formula = Eq(sigma_sym, (p_sym * d_sym) / (2 * s_sym))
    
    # 4. Unbekannte Variable identifizieren
    unknown_var = next(k for k in solvable_vars if k not in provided_params)
    target_symbol = {
        'p': p_sym, 
        'd': d_sym, 
        's': s_sym, 
        'sigma': sigma_sym
    }[unknown_var]
    
    # 5. Symbolische Lösung
    solution_expr = solve(formula, target_symbol)[0]
    
    # 6. Robuste Substitution mit Symbol-Mapping
    symbol_mapping = {
        p_sym: provided_params.get('p'),
        d_sym: provided_params.get('d'),
        s_sym: provided_params.get('s'), 
        sigma_sym: provided_params.get('sigma')
    }
    symbol_mapping = {k: v for k, v in symbol_mapping.items() if v is not None}
    
    # 7. Numerische Auswertung
    substituted_expr = solution_expr.subs(symbol_mapping)
    result_value = float(N(substituted_expr))
    
    # 8. Einheit bestimmen
    unit = "N/mm²" if unknown_var in ['p', 'sigma'] else "mm"
    
    # 9. Strukturierte Rückgabe
    return {
        "unknown_variable": unknown_var,
        "result": result_value,
        "unit": unit,
        "formula": str(formula),
        "solution_expression": str(solution_expr),
        "input_parameters": provided_params,
        "solvable_variables": solvable_vars,
        "calculation_steps": f"σ = p·d/(2·s) → {unknown_var} = {solution_expr}"
    }


# Tool-Metadaten für Registry
TOOL_METADATA = {
    "name": "solve_kesselformel",
    "description": "Löst die Kesselformel σ = p·d/(2·s) nach verschiedenen Variablen auf. Lösbare Variablen: [sigma, p, d, s]",
    "tags": ["pressure", "engineering", "symbolic", "vessels"],
    "function": solve_kesselformel
} 