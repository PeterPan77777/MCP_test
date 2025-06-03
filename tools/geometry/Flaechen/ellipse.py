#!/usr/bin/env python3
"""
Ellipse-Fläche - Berechnet Fläche oder Halbachsen

Berechnet Ellipsen-Flächen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel A = π × a × b nach verschiedenen Variablen auf.
Lösbare Variablen: area, semi_major_axis, semi_minor_axis

Ellipse: Ovale Form mit zwei Halbachsen
Formel: A = π × a × b (große Halbachse × kleine Halbachse × π)
"""

from typing import Dict, Optional
import sys
import os
import math

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_ellipse(
    area: Optional[str] = None,
    semi_major_axis: Optional[str] = None,
    semi_minor_axis: Optional[str] = None
) -> Dict:
    """
    Berechnet Ellipsen-Fläche mit Einheiten-Support.
    
    WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
    Format: "Wert Einheit" (z.B. "6 cm", "4 cm", "75.4 cm²")
    
    Ellipsen-Formel: A = π × a × b
    
    Lösbare Variablen: area, semi_major_axis, semi_minor_axis
    
    Args:
        area: Fläche der Ellipse mit Einheit (z.B. "75.4 cm²")
        semi_major_axis: Große Halbachse mit Einheit (z.B. "6 cm") 
        semi_minor_axis: Kleine Halbachse mit Einheit (z.B. "4 cm")
        
    Returns:
        Dict mit Ergebnissen in optimierten Einheiten
        
    Raises:
        ValueError: Bei ungültigen Parametern oder fehlenden Einheiten
    """
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [area, semi_major_axis, semi_minor_axis] if p is not None]
        
        if len(given_params) != 2:
            return {
                "error": "Genau 2 Parameter müssen gegeben sein (einer wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_ellipse(semi_major_axis='6 cm', semi_minor_axis='4 cm')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                area=area, 
                semi_major_axis=semi_major_axis, 
                semi_minor_axis=semi_minor_axis
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "area='75.4 cm²'",
                    "semi_major_axis='6 cm'", 
                    "semi_minor_axis='4 cm'"
                ]
            }
        
        # Berechnung basierend auf gegebenen Parametern
        if area is None:
            # Berechne Fläche: A = π × a × b
            a_si = params['semi_major_axis']['si_value']  # in Metern
            b_si = params['semi_minor_axis']['si_value']  # in Metern
            
            if a_si <= 0 or b_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            area_si = math.pi * a_si * b_si  # in m²
            
            # Optimiere Ausgabe-Einheit (nutze kleinere Halbachse als Referenz)
            ref_unit = params['semi_minor_axis']['original_unit'] if b_si < a_si else params['semi_major_axis']['original_unit']
            area_quantity = area_si * ureg.meter**2
            area_optimized = optimize_output_unit(area_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "grosse_halbachse": semi_major_axis,
                    "kleine_halbachse": semi_minor_axis
                },
                "ergebnis": {
                    "flaeche": f"{area_optimized.magnitude:.6g} {area_optimized.units}"
                },
                "formel": "A = π × a × b",
                "si_werte": {
                    "flaeche_si": f"{area_si:.6g} m²",
                    "grosse_halbachse_si": f"{a_si:.6g} m",
                    "kleine_halbachse_si": f"{b_si:.6g} m"
                }
            }
            
        elif semi_major_axis is None:
            # Berechne große Halbachse: a = A / (π × b)
            area_si = params['area']['si_value']              # in m²
            b_si = params['semi_minor_axis']['si_value']      # in Metern
            
            if area_si <= 0 or b_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            a_si = area_si / (math.pi * b_si)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            a_quantity = a_si * ureg.meter
            a_optimized = optimize_output_unit(a_quantity, params['semi_minor_axis']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "flaeche": area,
                    "kleine_halbachse": semi_minor_axis
                },
                "ergebnis": {
                    "grosse_halbachse": f"{a_optimized.magnitude:.6g} {a_optimized.units}"
                },
                "formel": "a = A / (π × b)",
                "si_werte": {
                    "grosse_halbachse_si": f"{a_si:.6g} m",
                    "flaeche_si": f"{area_si:.6g} m²",
                    "kleine_halbachse_si": f"{b_si:.6g} m"
                }
            }
            
        elif semi_minor_axis is None:
            # Berechne kleine Halbachse: b = A / (π × a)
            area_si = params['area']['si_value']             # in m²
            a_si = params['semi_major_axis']['si_value']     # in Metern
            
            if area_si <= 0 or a_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            b_si = area_si / (math.pi * a_si)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            b_quantity = b_si * ureg.meter
            b_optimized = optimize_output_unit(b_quantity, params['semi_major_axis']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "flaeche": area,
                    "grosse_halbachse": semi_major_axis
                },
                "ergebnis": {
                    "kleine_halbachse": f"{b_optimized.magnitude:.6g} {b_optimized.units}"
                },
                "formel": "b = A / (π × a)",
                "si_werte": {
                    "kleine_halbachse_si": f"{b_si:.6g} m",
                    "flaeche_si": f"{area_si:.6g} m²",
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
    "name": "solve_ellipse",
    "short_description": "Ellipse-Fläche - Berechnet Fläche oder Halbachsen",
    "description": """Löst die Ellipsen-Formel A = π × a × b nach verschiedenen Variablen auf. Lösbare Variablen: area, semi_major_axis, semi_minor_axis

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "6 cm", "4 cm", "75.4 cm²")

Grundformel: A = π × a × b

Parameter:
- area: Fläche der Ellipse mit Flächeneinheit (z.B. "75.4 cm²", "0.00754 m²")
- semi_major_axis: Große Halbachse mit Längeneinheit (z.B. "6 cm", "60 mm") 
- semi_minor_axis: Kleine Halbachse mit Längeneinheit (z.B. "4 cm", "40 mm")

Anwendungsbereich: Geometrie, Maschinenbau (Ovale Öffnungen), Architektur
Einschränkungen: Alle Werte müssen positiv sein, große Halbachse ≥ kleine Halbachse""",
    "tags": ["elementar", "Fläche"],
    "function": solve_ellipse,
    "examples": [
        {
            "description": "Berechne Fläche bei gegebenen Halbachsen",
            "call": 'solve_ellipse(semi_major_axis="6 cm", semi_minor_axis="4 cm")',
            "result": "Fläche in optimierter Einheit"
        },
        {
            "description": "Berechne große Halbachse bei gegebener Fläche und kleiner Halbachse", 
            "call": 'solve_ellipse(area="75.4 cm²", semi_minor_axis="4 cm")',
            "result": "Große Halbachse in optimierter Einheit"
        },
        {
            "description": "Berechne kleine Halbachse bei gegebener Fläche und großer Halbachse",
            "call": 'solve_ellipse(area="75.4 cm²", semi_major_axis="6 cm")',
            "result": "Kleine Halbachse in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Ellipse-Tool Tests ===")
    
    # Test 1: Fläche berechnen
    result1 = solve_ellipse(semi_major_axis="6 cm", semi_minor_axis="4 cm")
    print(f"Test 1 - Fläche: {result1}")
    
    # Test 2: Große Halbachse berechnen
    result2 = solve_ellipse(area="75.4 cm²", semi_minor_axis="4 cm")
    print(f"Test 2 - Große Halbachse: {result2}")
    
    # Test 3: Kleine Halbachse berechnen
    result3 = solve_ellipse(area="75.4 cm²", semi_major_axis="6 cm")
    print(f"Test 3 - Kleine Halbachse: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_ellipse(semi_major_axis="6", semi_minor_axis="4 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 