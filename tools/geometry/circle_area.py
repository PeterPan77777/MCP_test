"""
Circle Area Tool für MCP Engineering Server

Löst die Formel A = π·r² nach verschiedenen Variablen auf.
Lösbare Variablen: [area, radius]
"""

from typing import Dict, Optional
from fastmcp import Context
from sympy import symbols, Eq, solve, pi, N
from pydantic import BaseModel, field_validator


class CircleAreaInput(BaseModel):
    """Input-Validierung für Kreisflächenberechnung"""
    area: Optional[float] = None    # Kreisfläche [mm²]
    radius: Optional[float] = None  # Radius [mm]
    
    @field_validator('area', 'radius')
    @classmethod
    def must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Alle Werte müssen positiv sein")
        return v


async def solve_circle_area(
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
    # 1. Context-Logging
    if ctx:
        await ctx.info("Starte Kreisflächenberechnung...")
    
    # 2. Input-Validierung
    inputs = CircleAreaInput(area=area, radius=radius)
    provided_params = {k: v for k, v in inputs.model_dump().items() if v is not None}
    solvable_vars = ['area', 'radius']
    
    if len(provided_params) != 1:
        raise ValueError("Genau 1 von 2 Parametern muss angegeben werden")
    
    # 3. SymPy-Symbole definieren
    area_sym, radius_sym = symbols('area radius', positive=True)
    formula = Eq(area_sym, pi * radius_sym**2)
    
    # 4. Unbekannte Variable identifizieren
    unknown_var = next(k for k in solvable_vars if k not in provided_params)
    target_symbol = {
        'area': area_sym, 
        'radius': radius_sym
    }[unknown_var]
    
    # 5. Symbolische Lösung
    solutions = solve(formula, target_symbol)
    # Bei radius nehmen wir die positive Lösung
    solution_expr = solutions[0] if len(solutions) == 1 else max(solutions)
    
    # 6. Robuste Substitution mit Symbol-Mapping
    symbol_mapping = {
        area_sym: provided_params.get('area'),
        radius_sym: provided_params.get('radius')
    }
    symbol_mapping = {k: v for k, v in symbol_mapping.items() if v is not None}
    
    # 7. Numerische Auswertung
    substituted_expr = solution_expr.subs(symbol_mapping)
    result_value = float(N(substituted_expr))
    
    # 8. Einheit bestimmen
    unit = "mm²" if unknown_var == 'area' else "mm"
    
    # 9. Strukturierte Rückgabe
    return {
        "unknown_variable": unknown_var,
        "result": result_value,
        "unit": unit,
        "formula": str(formula),
        "solution_expression": str(solution_expr),
        "input_parameters": provided_params,
        "solvable_variables": solvable_vars,
        "calculation_steps": f"A = π·r² → {unknown_var} = {solution_expr}"
    }


# Tool-Metadaten für Registry
TOOL_METADATA = {
    "name": "solve_circle_area",
    "short_description": "Kreisfläche A = π·r² - Berechnung von Fläche oder Radius",
    "description": """Löst die Kreisflächenformel A = π·r² nach verschiedenen Variablen auf. Lösbare Variablen: [area, radius]

Die Kreisflächenformel ist eine der grundlegenden geometrischen Formeln.

Parameter:
- A (area): Kreisfläche [mm²]
- r (radius): Radius [mm]

Das Tool kann entweder die Fläche aus dem Radius oder den Radius aus der Fläche berechnen.""",
    "tags": ["elementar"],
    "function": solve_circle_area,
    "examples": [
        {
            "description": "Berechne Kreisfläche aus Radius",
            "input": {"radius": 10},
            "expected_output": {"unknown_variable": "area", "result": 314.159, "unit": "mm²"}
        },
        {
            "description": "Berechne Radius aus Kreisfläche", 
            "input": {"area": 314.159},
            "expected_output": {"unknown_variable": "radius", "result": 10.0, "unit": "mm"}
        }
    ]
} 