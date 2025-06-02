"""
[Tool Name] - [Kurzbeschreibung für list_engineering_tools]

Löst die Formel [FORMEL] nach verschiedenen Variablen auf.
Lösbare Variablen: [var1, var2, var3]

[Detaillierte Beschreibung der Formel, Anwendungsbereich, physikalische Bedeutung]

Parameter:
- var1: [Beschreibung] [Einheit]
- var2: [Beschreibung] [Einheit]
- var3: [Beschreibung] [Einheit]

Anwendungsbereich: [Wann wird diese Formel verwendet]
"""

from typing import Dict, Optional
from fastmcp import Context
from sympy import symbols, Eq, solve, N
from pydantic import BaseModel, field_validator


class ToolNameInput(BaseModel):
    """Input-Validierung für [Tool Name] Parameter"""
    var1: Optional[float] = None    # [Beschreibung] [Einheit]
    var2: Optional[float] = None    # [Beschreibung] [Einheit]
    var3: Optional[float] = None    # [Beschreibung] [Einheit]
    
    @field_validator('var1', 'var2', 'var3')
    @classmethod
    def must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Alle Werte müssen positiv sein")
        return v


async def solve_tool_name(
    var1: Optional[float] = None,
    var2: Optional[float] = None,
    var3: Optional[float] = None,
    ctx: Context = None
) -> Dict:
    """
    Löst [FORMEL] symbolisch nach der unbekannten Variable.
    
    Args:
        var1: [Beschreibung] [Einheit]
        var2: [Beschreibung] [Einheit]
        var3: [Beschreibung] [Einheit]
        ctx: FastMCP Context für Logging
        
    Returns:
        Dict: Berechnungsergebnis mit Lösung und Metadaten
    """
    # 1. Context-Logging
    if ctx:
        await ctx.info("Starte [Tool Name] Berechnung...")
    
    # 2. Input-Validierung
    inputs = ToolNameInput(var1=var1, var2=var2, var3=var3)
    provided_params = {k: v for k, v in inputs.model_dump().items() if v is not None}
    solvable_vars = ['var1', 'var2', 'var3']
    
    # Anzahl der Parameter prüfen: n-1 von n müssen gegeben sein
    if len(provided_params) != len(solvable_vars) - 1:
        raise ValueError(f"Genau {len(solvable_vars) - 1} von {len(solvable_vars)} Parametern müssen angegeben werden")
    
    # 3. SymPy-Symbole definieren
    var1_sym, var2_sym, var3_sym = symbols('var1 var2 var3', positive=True)
    
    # 4. Formel definieren
    formula = Eq(var1_sym, var2_sym * var3_sym)  # Beispiel: var1 = var2 * var3
    
    # 5. Unbekannte Variable identifizieren
    unknown_var = next(k for k in solvable_vars if k not in provided_params)
    target_symbol = {
        'var1': var1_sym,
        'var2': var2_sym,
        'var3': var3_sym
    }[unknown_var]
    
    # 6. Symbolische Lösung
    solution_expr = solve(formula, target_symbol)[0]
    
    # 7. Robuste Substitution mit Symbol-Mapping
    symbol_mapping = {
        var1_sym: provided_params.get('var1'),
        var2_sym: provided_params.get('var2'),
        var3_sym: provided_params.get('var3')
    }
    symbol_mapping = {k: v for k, v in symbol_mapping.items() if v is not None}
    
    # 8. Numerische Auswertung
    substituted_expr = solution_expr.subs(symbol_mapping)
    result_value = float(N(substituted_expr))
    
    # 9. Einheit bestimmen (anpassen je nach Variablen)
    unit_mapping = {
        'var1': 'Einheit1',
        'var2': 'Einheit2',
        'var3': 'Einheit3'
    }
    unit = unit_mapping[unknown_var]
    
    # 10. Strukturierte Rückgabe
    return {
        "unknown_variable": unknown_var,
        "result": result_value,
        "unit": unit,
        "formula": str(formula),
        "solution_expression": str(solution_expr),
        "input_parameters": provided_params,
        "solvable_variables": solvable_vars,
        "calculation_steps": f"[FORMEL] → {unknown_var} = {solution_expr}"
    }


# Tool-Metadaten für Registry
TOOL_METADATA = {
    "name": "solve_tool_name",
    "short_description": "[Kurze Beschreibung] - [Was das Tool macht]",
    "description": """Löst [FORMEL] nach verschiedenen Variablen auf. Lösbare Variablen: [var1, var2, var3]

[Ausführliche Beschreibung der Formel und ihres Anwendungsbereichs]

Parameter:
- var1: [Detaillierte Beschreibung] [Einheit]
- var2: [Detaillierte Beschreibung] [Einheit]  
- var3: [Detaillierte Beschreibung] [Einheit]

Anwendungsbereich: [Wann und wo wird diese Formel verwendet]
Einschränkungen: [Falls vorhanden, z.B. nur für positive Werte]""",
    "tags": ["elementar"],  # Wähle: ["meta"] | ["elementar"] | ["mechanik"]
    "function": solve_tool_name,
    "examples": [
        {
            "description": "Berechne var1 aus var2 und var3",
            "input": {"var2": 10, "var3": 20},
            "expected_output": {"unknown_variable": "var1", "result": 200, "unit": "Einheit1"}
        },
        {
            "description": "Berechne var2 aus var1 und var3",
            "input": {"var1": 200, "var3": 20},
            "expected_output": {"unknown_variable": "var2", "result": 10, "unit": "Einheit2"}
        }
    ]
}

# Tag-Zuordnung:
# ["meta"]      - Discovery und Workflow-Tools (nur für server.py meta-functions)
# ["elementar"] - Grundlegende geometrische und mathematische Berechnungen  
# ["mechanik"]  - Spezialisierte Formeln aus Mechanik und Maschinenbau 