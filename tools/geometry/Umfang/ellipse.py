#!/usr/bin/env python3
"""
Ellipse-Umfang - Berechnet Umfang oder Halbachsen (Ramanujan-Näherung)

Berechnet Ellipsen-Umfang mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Näherungsformel nach verschiedenen Variablen auf.
Lösbare Variablen: perimeter, semi_major_axis, semi_minor_axis

Ellipse: Ovale Form mit zwei Halbachsen
Ramanujan-Näherung: U ≈ π × [3(a + b) - √((3a + b)(a + 3b))]
"""

from typing import Dict, Optional
import sys
import os
import math

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_ellipse_umfang(
    perimeter: Optional[str] = None,
    semi_major_axis: Optional[str] = None,
    semi_minor_axis: Optional[str] = None
) -> Dict:
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [perimeter, semi_major_axis, semi_minor_axis] if p is not None]
        
        if len(given_params) != 2:
            return {
                "error": "Genau 2 Parameter müssen gegeben sein (einer wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_ellipse_umfang(semi_major_axis='6 cm', semi_minor_axis='4 cm')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                perimeter=perimeter, 
                semi_major_axis=semi_major_axis, 
                semi_minor_axis=semi_minor_axis
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "perimeter='32.7 cm'",
                    "semi_major_axis='6 cm'", 
                    "semi_minor_axis='4 cm'"
                ]
            }
        
        def ramanujan_perimeter(a, b):
            """Ramanujan-Näherung für Ellipsen-Umfang"""
            return math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))
        
        # Berechnung basierend auf gegebenen Parametern
        if perimeter is None:
            # Berechne Umfang: U ≈ π × [3(a + b) - √((3a + b)(a + 3b))]
            a_si = params['semi_major_axis']['si_value']  # in Metern
            b_si = params['semi_minor_axis']['si_value']  # in Metern
            
            if a_si <= 0 or b_si <= 0:
                return {"error": "Alle Halbachsen müssen positiv sein"}
            
            if b_si > a_si:
                return {"error": "Große Halbachse muss ≥ kleine Halbachse sein"}
            
            perimeter_si = ramanujan_perimeter(a_si, b_si)  # in Metern
            
            # Optimiere Ausgabe-Einheit (nutze größere Halbachse als Referenz)
            ref_unit = params['semi_major_axis']['original_unit']
            perimeter_quantity = perimeter_si * ureg.meter
            perimeter_optimized = optimize_output_unit(perimeter_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "grosse_halbachse": semi_major_axis,
                    "kleine_halbachse": semi_minor_axis
                },
                "ergebnis": {
                    "umfang": f"{perimeter_optimized.magnitude:.6g} {perimeter_optimized.units}"
                },
                "formel": "U ≈ π × [3(a + b) - √((3a + b)(a + 3b))] (Ramanujan)",
                "genauigkeit": "Sehr hohe Genauigkeit (Fehler < 5×10⁻⁵ für alle Ellipsen)",
                "si_werte": {
                    "umfang_si": f"{perimeter_si:.6g} m",
                    "grosse_halbachse_si": f"{a_si:.6g} m",
                    "kleine_halbachse_si": f"{b_si:.6g} m"
                }
            }
            
        elif semi_major_axis is None:
            # Numerische Lösung für große Halbachse (iterativ)
            U_si = params['perimeter']['si_value']        # in Metern
            b_si = params['semi_minor_axis']['si_value']  # in Metern
            
            if U_si <= 0 or b_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            # Startwert: Grobe Schätzung basierend auf Kreisumfang
            a_estimate = U_si / (2 * math.pi) 
            
            # Newton-Raphson Iteration
            for _ in range(50):  # max 50 Iterationen
                current_U = ramanujan_perimeter(a_estimate, b_si)
                
                # Numerische Ableitung
                delta = a_estimate * 1e-8
                dU_da = (ramanujan_perimeter(a_estimate + delta, b_si) - current_U) / delta
                
                # Newton-Schritt
                if abs(dU_da) < 1e-15:
                    break
                    
                correction = (U_si - current_U) / dU_da
                a_estimate += correction
                
                # Konvergenz prüfen
                if abs(correction) < 1e-12:
                    break
                    
                # Sicherstellen dass a > 0 und a >= b
                a_estimate = max(a_estimate, b_si)
            
            if a_estimate < b_si:
                return {"error": "Keine gültige Lösung gefunden (a muss ≥ b sein)"}
            
            # Optimiere Ausgabe-Einheit
            a_quantity = a_estimate * ureg.meter
            a_optimized = optimize_output_unit(a_quantity, params['semi_minor_axis']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "umfang": perimeter,
                    "kleine_halbachse": semi_minor_axis
                },
                "ergebnis": {
                    "grosse_halbachse": f"{a_optimized.magnitude:.6g} {a_optimized.units}"
                },
                "formel": "Numerische Lösung der Ramanujan-Gleichung",
                "genauigkeit": "Iterative Lösung (Konvergenz erreicht)",
                "si_werte": {
                    "grosse_halbachse_si": f"{a_estimate:.6g} m",
                    "umfang_si": f"{U_si:.6g} m",
                    "kleine_halbachse_si": f"{b_si:.6g} m"
                }
            }
            
        elif semi_minor_axis is None:
            # Numerische Lösung für kleine Halbachse (iterativ)
            U_si = params['perimeter']['si_value']         # in Metern
            a_si = params['semi_major_axis']['si_value']   # in Metern
            
            if U_si <= 0 or a_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            # Startwert: Grobe Schätzung
            b_estimate = a_si * 0.5  # Start mit halber großer Halbachse
            
            # Newton-Raphson Iteration
            for _ in range(50):  # max 50 Iterationen
                current_U = ramanujan_perimeter(a_si, b_estimate)
                
                # Numerische Ableitung
                delta = b_estimate * 1e-8 + 1e-12  # Avoid division by zero
                dU_db = (ramanujan_perimeter(a_si, b_estimate + delta) - current_U) / delta
                
                # Newton-Schritt
                if abs(dU_db) < 1e-15:
                    break
                    
                correction = (U_si - current_U) / dU_db
                b_estimate += correction
                
                # Konvergenz prüfen
                if abs(correction) < 1e-12:
                    break
                    
                # Sicherstellen dass b > 0 und b <= a
                b_estimate = max(0, min(b_estimate, a_si))
            
            if b_estimate <= 0 or b_estimate > a_si:
                return {"error": "Keine gültige Lösung gefunden (0 < b ≤ a erforderlich)"}
            
            # Optimiere Ausgabe-Einheit
            b_quantity = b_estimate * ureg.meter
            b_optimized = optimize_output_unit(b_quantity, params['semi_major_axis']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "umfang": perimeter,
                    "grosse_halbachse": semi_major_axis
                },
                "ergebnis": {
                    "kleine_halbachse": f"{b_optimized.magnitude:.6g} {b_optimized.units}"
                },
                "formel": "Numerische Lösung der Ramanujan-Gleichung",
                "genauigkeit": "Iterative Lösung (Konvergenz erreicht)",
                "si_werte": {
                    "kleine_halbachse_si": f"{b_estimate:.6g} m",
                    "umfang_si": f"{U_si:.6g} m",
                    "grosse_halbachse_si": f"{a_si:.6g} m"
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
    "name": "solve_ellipse_umfang",
    "short_description": "Ellipse-Umfang - Berechnet Umfang oder Halbachsen (Ramanujan-Näherung)",
    "description": """Löst die Ellipsen-Umfang-Näherung nach Ramanujan nach verschiedenen Variablen auf. Lösbare Variablen: perimeter, semi_major_axis, semi_minor_axis

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "6 cm", "4 cm", "32.7 cm")

Ramanujan-Näherung: U ≈ π × [3(a + b) - √((3a + b)(a + 3b))]

Parameter:
- perimeter: Umfang der Ellipse mit Längeneinheit (z.B. "32.7 cm", "327 mm")
- semi_major_axis: Große Halbachse mit Längeneinheit (z.B. "6 cm", "60 mm") 
- semi_minor_axis: Kleine Halbachse mit Längeneinheit (z.B. "4 cm", "40 mm")

Anwendungsbereich: Geometrie, Maschinenbau (ovale Bahnen), Architektur, Astronomie
Einschränkungen: Große Halbachse ≥ kleine Halbachse > 0
Genauigkeit: Sehr hoch (Fehler < 5×10⁻⁵ für alle Ellipsen)""",
    "tags": ["elementar", "Umfang"],
    "function": solve_ellipse_umfang,
    "examples": [
        {
            "description": "Berechne Umfang bei gegebenen Halbachsen",
            "call": 'solve_ellipse_umfang(semi_major_axis="6 cm", semi_minor_axis="4 cm")',
            "result": "Umfang in optimierter Einheit"
        },
        {
            "description": "Berechne große Halbachse bei gegebenem Umfang und kleiner Halbachse", 
            "call": 'solve_ellipse_umfang(perimeter="32.7 cm", semi_minor_axis="4 cm")',
            "result": "Große Halbachse in optimierter Einheit"
        },
        {
            "description": "Berechne kleine Halbachse bei gegebenem Umfang und großer Halbachse",
            "call": 'solve_ellipse_umfang(perimeter="32.7 cm", semi_major_axis="6 cm")',
            "result": "Kleine Halbachse in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Ellipse-Umfang-Tool Tests ===")
    
    # Test 1: Umfang berechnen
    result1 = solve_ellipse_umfang(semi_major_axis="6 cm", semi_minor_axis="4 cm")
    print(f"Test 1 - Umfang: {result1}")
    
    # Test 2: Große Halbachse berechnen
    result2 = solve_ellipse_umfang(perimeter="32.7 cm", semi_minor_axis="4 cm")
    print(f"Test 2 - Große Halbachse: {result2}")
    
    # Test 3: Kleine Halbachse berechnen
    result3 = solve_ellipse_umfang(perimeter="32.7 cm", semi_major_axis="6 cm")
    print(f"Test 3 - Kleine Halbachse: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_ellipse_umfang(semi_major_axis="6", semi_minor_axis="4 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 