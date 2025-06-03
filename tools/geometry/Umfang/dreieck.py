#!/usr/bin/env python3
"""
Dreieck-Umfang - Berechnet Umfang oder fehlende Seite

Berechnet Dreieck-Umfang mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel U = a + b + c nach verschiedenen Variablen auf.
Lösbare Variablen: perimeter, side_a, side_b, side_c

Dreieck: Polygon mit drei Seiten
Formel: U = a + b + c (Summe aller drei Seiten)
"""

from typing import Dict, Optional
import sys
import os

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_dreieck_umfang(
    perimeter: Optional[str] = None,
    side_a: Optional[str] = None,
    side_b: Optional[str] = None,
    side_c: Optional[str] = None
) -> Dict:
    """
    Berechnet Dreieck-Umfang mit Einheiten-Support.
    
    WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
    Format: "Wert Einheit" (z.B. "3 cm", "4 cm", "5 cm", "12 cm")
    
    Dreieck-Umfang-Formel: U = a + b + c
    
    Lösbare Variablen: perimeter, side_a, side_b, side_c
    
    Args:
        perimeter: Umfang des Dreiecks mit Einheit (z.B. "12 cm")
        side_a: Seite a des Dreiecks mit Einheit (z.B. "3 cm") 
        side_b: Seite b des Dreiecks mit Einheit (z.B. "4 cm")
        side_c: Seite c des Dreiecks mit Einheit (z.B. "5 cm")
        
    Returns:
        Dict mit Ergebnissen in optimierten Einheiten
        
    Raises:
        ValueError: Bei ungültigen Parametern oder fehlenden Einheiten
    """
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [perimeter, side_a, side_b, side_c] if p is not None]
        
        if len(given_params) != 3:
            return {
                "error": "Genau 3 Parameter müssen gegeben sein (einer wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_dreieck_umfang(side_a='3 cm', side_b='4 cm', side_c='5 cm')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                perimeter=perimeter, 
                side_a=side_a, 
                side_b=side_b,
                side_c=side_c
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "perimeter='12 cm'",
                    "side_a='3 cm'", 
                    "side_b='4 cm'",
                    "side_c='5 cm'"
                ]
            }
        
        # Berechnung basierend auf gegebenen Parametern
        if perimeter is None:
            # Berechne Umfang: U = a + b + c
            a_si = params['side_a']['si_value']   # in Metern
            b_si = params['side_b']['si_value']   # in Metern
            c_si = params['side_c']['si_value']   # in Metern
            
            if a_si <= 0 or b_si <= 0 or c_si <= 0:
                return {"error": "Alle Seiten müssen positiv sein"}
            
            # Prüfe Dreiecksungleichung
            if (a_si + b_si <= c_si) or (a_si + c_si <= b_si) or (b_si + c_si <= a_si):
                return {"error": "Die gegebenen Seiten können kein gültiges Dreieck bilden (Dreiecksungleichung verletzt)"}
            
            perimeter_si = a_si + b_si + c_si  # in Metern
            
            # Optimiere Ausgabe-Einheit (nutze längste Seite als Referenz)
            longest_side = max(a_si, b_si, c_si)
            if longest_side == a_si:
                ref_unit = params['side_a']['original_unit']
            elif longest_side == b_si:
                ref_unit = params['side_b']['original_unit']
            else:
                ref_unit = params['side_c']['original_unit']
            
            perimeter_quantity = perimeter_si * ureg.meter
            perimeter_optimized = optimize_output_unit(perimeter_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "seite_a": side_a,
                    "seite_b": side_b,
                    "seite_c": side_c
                },
                "ergebnis": {
                    "umfang": f"{perimeter_optimized.magnitude:.6g} {perimeter_optimized.units}"
                },
                "formel": "U = a + b + c",
                "si_werte": {
                    "umfang_si": f"{perimeter_si:.6g} m",
                    "seite_a_si": f"{a_si:.6g} m",
                    "seite_b_si": f"{b_si:.6g} m",
                    "seite_c_si": f"{c_si:.6g} m"
                }
            }
            
        elif side_a is None:
            # Berechne Seite a: a = U - b - c
            U_si = params['perimeter']['si_value']  # in Metern
            b_si = params['side_b']['si_value']     # in Metern
            c_si = params['side_c']['si_value']     # in Metern
            
            if U_si <= 0 or b_si <= 0 or c_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            a_si = U_si - b_si - c_si  # in Metern
            
            if a_si <= 0:
                return {"error": "Die verbleibende Seite wäre nicht positiv"}
            
            # Prüfe Dreiecksungleichung
            if (a_si + b_si <= c_si) or (a_si + c_si <= b_si) or (b_si + c_si <= a_si):
                return {"error": "Die resultierenden Seiten können kein gültiges Dreieck bilden"}
            
            # Optimiere Ausgabe-Einheit
            a_quantity = a_si * ureg.meter
            longer_side = max(b_si, c_si)
            ref_unit = params['side_b']['original_unit'] if longer_side == b_si else params['side_c']['original_unit']
            a_optimized = optimize_output_unit(a_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "umfang": perimeter,
                    "seite_b": side_b,
                    "seite_c": side_c
                },
                "ergebnis": {
                    "seite_a": f"{a_optimized.magnitude:.6g} {a_optimized.units}"
                },
                "formel": "a = U - b - c",
                "si_werte": {
                    "seite_a_si": f"{a_si:.6g} m",
                    "umfang_si": f"{U_si:.6g} m",
                    "seite_b_si": f"{b_si:.6g} m",
                    "seite_c_si": f"{c_si:.6g} m"
                }
            }
            
        elif side_b is None:
            # Berechne Seite b: b = U - a - c
            U_si = params['perimeter']['si_value']  # in Metern
            a_si = params['side_a']['si_value']     # in Metern
            c_si = params['side_c']['si_value']     # in Metern
            
            if U_si <= 0 or a_si <= 0 or c_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            b_si = U_si - a_si - c_si  # in Metern
            
            if b_si <= 0:
                return {"error": "Die verbleibende Seite wäre nicht positiv"}
            
            # Prüfe Dreiecksungleichung
            if (a_si + b_si <= c_si) or (a_si + c_si <= b_si) or (b_si + c_si <= a_si):
                return {"error": "Die resultierenden Seiten können kein gültiges Dreieck bilden"}
            
            # Optimiere Ausgabe-Einheit
            b_quantity = b_si * ureg.meter
            longer_side = max(a_si, c_si)
            ref_unit = params['side_a']['original_unit'] if longer_side == a_si else params['side_c']['original_unit']
            b_optimized = optimize_output_unit(b_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "umfang": perimeter,
                    "seite_a": side_a,
                    "seite_c": side_c
                },
                "ergebnis": {
                    "seite_b": f"{b_optimized.magnitude:.6g} {b_optimized.units}"
                },
                "formel": "b = U - a - c",
                "si_werte": {
                    "seite_b_si": f"{b_si:.6g} m",
                    "umfang_si": f"{U_si:.6g} m",
                    "seite_a_si": f"{a_si:.6g} m",
                    "seite_c_si": f"{c_si:.6g} m"
                }
            }
            
        elif side_c is None:
            # Berechne Seite c: c = U - a - b
            U_si = params['perimeter']['si_value']  # in Metern
            a_si = params['side_a']['si_value']     # in Metern
            b_si = params['side_b']['si_value']     # in Metern
            
            if U_si <= 0 or a_si <= 0 or b_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            c_si = U_si - a_si - b_si  # in Metern
            
            if c_si <= 0:
                return {"error": "Die verbleibende Seite wäre nicht positiv"}
            
            # Prüfe Dreiecksungleichung
            if (a_si + b_si <= c_si) or (a_si + c_si <= b_si) or (b_si + c_si <= a_si):
                return {"error": "Die resultierenden Seiten können kein gültiges Dreieck bilden"}
            
            # Optimiere Ausgabe-Einheit
            c_quantity = c_si * ureg.meter
            longer_side = max(a_si, b_si)
            ref_unit = params['side_a']['original_unit'] if longer_side == a_si else params['side_b']['original_unit']
            c_optimized = optimize_output_unit(c_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "umfang": perimeter,
                    "seite_a": side_a,
                    "seite_b": side_b
                },
                "ergebnis": {
                    "seite_c": f"{c_optimized.magnitude:.6g} {c_optimized.units}"
                },
                "formel": "c = U - a - b",
                "si_werte": {
                    "seite_c_si": f"{c_si:.6g} m",
                    "umfang_si": f"{U_si:.6g} m",
                    "seite_a_si": f"{a_si:.6g} m",
                    "seite_b_si": f"{b_si:.6g} m"
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
    "name": "solve_dreieck_umfang",
    "short_description": "Dreieck-Umfang - Berechnet Umfang oder fehlende Seite",
    "description": """Löst die Dreieck-Umfang-Formel U = a + b + c nach verschiedenen Variablen auf. Lösbare Variablen: perimeter, side_a, side_b, side_c

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "3 cm", "4 cm", "5 cm", "12 cm")

Grundformel: U = a + b + c

Parameter:
- perimeter: Umfang des Dreiecks mit Längeneinheit (z.B. "12 cm", "120 mm")
- side_a: Seite a des Dreiecks mit Längeneinheit (z.B. "3 cm", "30 mm") 
- side_b: Seite b des Dreiecks mit Längeneinheit (z.B. "4 cm", "40 mm")
- side_c: Seite c des Dreiecks mit Längeneinheit (z.B. "5 cm", "50 mm")

Anwendungsbereich: Geometrie, Konstruktion, Zaunberechnungen für dreieckige Grundstücke
Einschränkungen: Alle Seiten müssen positiv sein, Dreiecksungleichung muss erfüllt sein""",
    "tags": ["elementar", "Umfang"],
    "function": solve_dreieck_umfang,
    "examples": [
        {
            "description": "Berechne Umfang bei gegebenen drei Seiten",
            "call": 'solve_dreieck_umfang(side_a="3 cm", side_b="4 cm", side_c="5 cm")',
            "result": "Umfang in optimierter Einheit"
        },
        {
            "description": "Berechne fehlende Seite bei gegebenem Umfang und zwei Seiten", 
            "call": 'solve_dreieck_umfang(perimeter="12 cm", side_a="3 cm", side_b="4 cm")',
            "result": "Fehlende Seite in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Dreieck-Umfang-Tool Tests ===")
    
    # Test 1: Umfang berechnen
    result1 = solve_dreieck_umfang(side_a="3 cm", side_b="4 cm", side_c="5 cm")
    print(f"Test 1 - Umfang: {result1}")
    
    # Test 2: Fehlende Seite berechnen
    result2 = solve_dreieck_umfang(perimeter="12 cm", side_a="3 cm", side_b="4 cm")
    print(f"Test 2 - Seite c: {result2}")
    
    # Test 3: Ungültiges Dreieck
    result3 = solve_dreieck_umfang(side_a="1 cm", side_b="2 cm", side_c="5 cm")
    print(f"Test 3 - Ungültiges Dreieck: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_dreieck_umfang(side_a="3", side_b="4 cm", side_c="5 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 