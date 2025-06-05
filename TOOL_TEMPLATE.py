#!/usr/bin/env python3
"""
[Tool Name] - [Kurzbeschreibung für list_engineering_tools]

Berechnet [BESCHREIBUNG] mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel [FORMEL] nach verschiedenen Variablen auf.
Lösbare Variablen: var1, var2, var3

[Detaillierte Beschreibung der Formel, Anwendungsbereich, physikalische Bedeutung]
"""

from typing import Dict, Optional
import sys
import os

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_tool_name(
    var1: Optional[str] = None,
    var2: Optional[str] = None,
    var3: Optional[str] = None
) -> Dict:
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [var1, var2, var3] if p is not None]
        
        # n-1 von n Parametern müssen gegeben sein
        required_count = 2  # Für 3 Variablen: 2 gegeben, 1 berechnet
        if len(given_params) != required_count:
            return {
                "error": f"Genau {required_count} Parameter müssen gegeben sein (einer wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_tool_name(var1='5.2 mm', var2='10 cm')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                var1=var1, 
                var2=var2, 
                var3=var3
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "var1='5.2 mm'",
                    "var2='10 cm'", 
                    "var3='25.5 cm²'"
                ]
            }
        
        # Berechnung basierend auf gegebenen Parametern
        if var1 is None:
            # Berechne var1: [FORMEL]
            var2_si = params['var2']['si_value']  # SI-Einheit
            var3_si = params['var3']['si_value']  # SI-Einheit
            
            if var2_si <= 0 or var3_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            # BEISPIEL: var1 = var2 * var3
            var1_si = var2_si * var3_si  # SI-Einheit
            
            # Optimiere Ausgabe-Einheit
            var1_quantity = var1_si * ureg.meter  # ANPASSEN: richtige SI-Einheit
            var1_optimized = optimize_output_unit(var1_quantity, params['var2']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "var2": var2,
                    "var3": var3
                },
                "ergebnis": {
                    "var1": f"{var1_optimized.magnitude:.6g} {var1_optimized.units}"
                },
                "formel": "[FORMEL]",
                "si_werte": {
                    "var1_si": f"{var1_si:.6g} [SI-Einheit]",
                    "var2_si": f"{var2_si:.6g} [SI-Einheit]",
                    "var3_si": f"{var3_si:.6g} [SI-Einheit]"
                }
            }
            
        elif var2 is None:
            # Berechne var2: [UMGESTELLTE FORMEL]
            var1_si = params['var1']['si_value']
            var3_si = params['var3']['si_value']
            
            if var1_si <= 0 or var3_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            # BEISPIEL: var2 = var1 / var3
            var2_si = var1_si / var3_si
            
            # Optimiere Ausgabe-Einheit
            var2_quantity = var2_si * ureg.meter  # ANPASSEN
            var2_optimized = optimize_output_unit(var2_quantity, params['var1']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "var1": var1,
                    "var3": var3
                },
                "ergebnis": {
                    "var2": f"{var2_optimized.magnitude:.6g} {var2_optimized.units}"
                },
                "formel": "[UMGESTELLTE FORMEL]",
                "si_werte": {
                    "var1_si": f"{var1_si:.6g} [SI-Einheit]",
                    "var2_si": f"{var2_si:.6g} [SI-Einheit]",
                    "var3_si": f"{var3_si:.6g} [SI-Einheit]"
                }
            }
            
        elif var3 is None:
            # Berechne var3: [UMGESTELLTE FORMEL]
            var1_si = params['var1']['si_value']
            var2_si = params['var2']['si_value']
            
            if var1_si <= 0 or var2_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            # BEISPIEL: var3 = var1 / var2
            var3_si = var1_si / var2_si
            
            # Optimiere Ausgabe-Einheit
            var3_quantity = var3_si * ureg.meter  # ANPASSEN
            var3_optimized = optimize_output_unit(var3_quantity, params['var1']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "var1": var1,
                    "var2": var2
                },
                "ergebnis": {
                    "var3": f"{var3_optimized.magnitude:.6g} {var3_optimized.units}"
                },
                "formel": "[UMGESTELLTE FORMEL]",
                "si_werte": {
                    "var1_si": f"{var1_si:.6g} [SI-Einheit]",
                    "var2_si": f"{var2_si:.6g} [SI-Einheit]",
                    "var3_si": f"{var3_si:.6g} [SI-Einheit]"
                }
            }
        
    except Exception as e:
        return {
            "error": "Berechnungsfehler",
            "message": str(e),
            "hinweis": "Überprüfen Sie die Eingabe-Parameter und Einheiten"
        }

# Tool-Metadaten für Registry
TOOL_METADATA = {
    "name": "solve_tool_name",
    "short_description": "[Kurze Beschreibung] - [Was das Tool macht]",
    "description": """Löst [FORMEL] nach verschiedenen Variablen auf. Lösbare Variablen: var1, var2, var3

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "5.2 mm", "10 cm", "25.5 cm²")

[GRUNDFORMEL]

Parameter:
- var1: [Detaillierte Beschreibung] mit [Einheiten-Typ] (z.B. "5.2 mm", "2.5 cm")
- var2: [Detaillierte Beschreibung] mit [Einheiten-Typ] (z.B. "10 mm", "5 cm") 
- var3: [Detaillierte Beschreibung] mit [Einheiten-Typ] (z.B. "25.5 cm²", "0.1 m²")

Anwendungsbereich: [Wann und wo wird diese Formel verwendet]
Einschränkungen: [Falls vorhanden, z.B. nur für positive Werte]""",
    "tags": ["elementar", "Fläche"],  # ["elementar", "Fläche"] | ["elementar", "Volumen"] | ["mechanik"]
    "function": solve_tool_name,
    "examples": [
        {
            "description": "Berechne var1 bei gegebenen var2 und var3",
            "call": 'solve_tool_name(var2="10 mm", var3="5 cm")',
            "result": "var1 in optimierter Einheit"
        },
        {
            "description": "Berechne var2 bei gegebenen var1 und var3", 
            "call": 'solve_tool_name(var1="50 cm²", var3="5 cm")',
            "result": "var2 in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== [Tool Name] Tests ===")
    
    # Test 1
    result1 = solve_tool_name(var2="10 mm", var3="5 cm")
    print(f"Test 1: {result1}")
    
    # Test 2
    result2 = solve_tool_name(var1="50 cm²", var3="5 cm")
    print(f"Test 2: {result2}")
    
    # Test 3: Fehler - keine Einheit
    result3 = solve_tool_name(var1="50", var2="10 mm")
    print(f"Test 3 - Keine Einheit: {result3}") 