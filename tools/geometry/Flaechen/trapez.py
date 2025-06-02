#!/usr/bin/env python3
"""
Trapez-Fläche - Berechnet Fläche, parallele Seiten oder Höhe eines Trapezes

Berechnet Trapezflächen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel A = (a + c) × h / 2 nach verschiedenen Variablen auf.
Lösbare Variablen: area, side_a, side_c, height
"""

from typing import Dict, Optional
import sys
import os

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_trapez(
    area: Optional[str] = None,
    side_a: Optional[str] = None,
    side_c: Optional[str] = None,
    height: Optional[str] = None
) -> Dict:
    """
    Berechnet Trapez-Parameter mit Einheiten-Support.
    
    WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
    Format: "Wert Einheit" (z.B. "5.2 mm", "10 cm", "75 cm²")
    
    Trapezformel: A = (a + c) × h / 2
    
    Lösbare Variablen: area, side_a, side_c, height
    
    Args:
        area: Fläche des Trapezes mit Einheit (z.B. "75 cm²")
        side_a: Erste parallele Seite mit Einheit (z.B. "10 cm") 
        side_c: Zweite parallele Seite mit Einheit (z.B. "5 cm")
        height: Höhe des Trapezes mit Einheit (z.B. "8 cm")
        
    Returns:
        Dict mit Ergebnissen in optimierten Einheiten
        
    Raises:
        ValueError: Bei ungültigen Parametern oder fehlenden Einheiten
    """
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [area, side_a, side_c, height] if p is not None]
        
        if len(given_params) != 3:
            return {
                "error": "Genau 3 Parameter müssen gegeben sein (einer wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_trapez(side_a='10 cm', side_c='5 cm', height='8 cm')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                area=area,
                side_a=side_a, 
                side_c=side_c,
                height=height
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "area='75 cm²'",
                    "side_a='10 cm'", 
                    "side_c='5 cm'",
                    "height='8 cm'"
                ]
            }
        
        # Berechnung basierend auf gegebenen Parametern
        if area is None:
            # Berechne Fläche: A = (a + c) × h / 2
            side_a_si = params['side_a']['si_value']  # in Metern
            side_c_si = params['side_c']['si_value']  # in Metern
            height_si = params['height']['si_value']  # in Metern
            
            if side_a_si <= 0 or side_c_si <= 0 or height_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            area_si = (side_a_si + side_c_si) * height_si / 2  # in m²
            
            # Optimiere Ausgabe-Einheit (nutze kleinste Seitenlänge als Referenz)
            ref_sizes = [side_a_si, side_c_si, height_si]
            ref_units = [params['side_a']['original_unit'], params['side_c']['original_unit'], params['height']['original_unit']]
            min_idx = ref_sizes.index(min(ref_sizes))
            ref_unit = ref_units[min_idx]
            
            area_quantity = area_si * ureg.meter**2
            area_optimized = optimize_output_unit(area_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "seite_a": side_a,
                    "seite_c": side_c,
                    "hoehe": height
                },
                "ergebnis": {
                    "flaeche": f"{area_optimized.magnitude:.6g} {area_optimized.units}"
                },
                "formel": "A = (a + c) × h / 2",
                "si_werte": {
                    "flaeche_si": f"{area_si:.6g} m²",
                    "seite_a_si": f"{side_a_si:.6g} m",
                    "seite_c_si": f"{side_c_si:.6g} m",
                    "hoehe_si": f"{height_si:.6g} m"
                }
            }
            
        elif side_a is None:
            # Berechne Seite a: a = (2 × A / h) - c
            area_si = params['area']['si_value']      # in m²
            side_c_si = params['side_c']['si_value']  # in Metern
            height_si = params['height']['si_value']  # in Metern
            
            if area_si <= 0 or side_c_si <= 0 or height_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            side_a_si = (2 * area_si / height_si) - side_c_si  # in Metern
            
            if side_a_si <= 0:
                return {"error": "Berechnete Seite a wäre negativ - überprüfen Sie die Eingabewerte"}
            
            # Optimiere Ausgabe-Einheit
            side_a_quantity = side_a_si * ureg.meter
            side_a_optimized = optimize_output_unit(side_a_quantity, params['side_c']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "flaeche": area,
                    "seite_c": side_c,
                    "hoehe": height
                },
                "ergebnis": {
                    "seite_a": f"{side_a_optimized.magnitude:.6g} {side_a_optimized.units}"
                },
                "formel": "a = (2 × A / h) - c",
                "si_werte": {
                    "seite_a_si": f"{side_a_si:.6g} m",
                    "flaeche_si": f"{area_si:.6g} m²",
                    "seite_c_si": f"{side_c_si:.6g} m",
                    "hoehe_si": f"{height_si:.6g} m"
                }
            }
            
        elif side_c is None:
            # Berechne Seite c: c = (2 × A / h) - a
            area_si = params['area']['si_value']      # in m²
            side_a_si = params['side_a']['si_value']  # in Metern
            height_si = params['height']['si_value']  # in Metern
            
            if area_si <= 0 or side_a_si <= 0 or height_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            side_c_si = (2 * area_si / height_si) - side_a_si  # in Metern
            
            if side_c_si <= 0:
                return {"error": "Berechnete Seite c wäre negativ - überprüfen Sie die Eingabewerte"}
            
            # Optimiere Ausgabe-Einheit
            side_c_quantity = side_c_si * ureg.meter
            side_c_optimized = optimize_output_unit(side_c_quantity, params['side_a']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "flaeche": area,
                    "seite_a": side_a,
                    "hoehe": height
                },
                "ergebnis": {
                    "seite_c": f"{side_c_optimized.magnitude:.6g} {side_c_optimized.units}"
                },
                "formel": "c = (2 × A / h) - a",
                "si_werte": {
                    "seite_c_si": f"{side_c_si:.6g} m",
                    "flaeche_si": f"{area_si:.6g} m²",
                    "seite_a_si": f"{side_a_si:.6g} m",
                    "hoehe_si": f"{height_si:.6g} m"
                }
            }
            
        elif height is None:
            # Berechne Höhe: h = 2 × A / (a + c)
            area_si = params['area']['si_value']      # in m²
            side_a_si = params['side_a']['si_value']  # in Metern
            side_c_si = params['side_c']['si_value']  # in Metern
            
            if area_si <= 0 or side_a_si <= 0 or side_c_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            height_si = (2 * area_si) / (side_a_si + side_c_si)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            height_quantity = height_si * ureg.meter
            height_optimized = optimize_output_unit(height_quantity, params['side_a']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "flaeche": area,
                    "seite_a": side_a,
                    "seite_c": side_c
                },
                "ergebnis": {
                    "hoehe": f"{height_optimized.magnitude:.6g} {height_optimized.units}"
                },
                "formel": "h = 2 × A / (a + c)",
                "si_werte": {
                    "hoehe_si": f"{height_si:.6g} m",
                    "flaeche_si": f"{area_si:.6g} m²",
                    "seite_a_si": f"{side_a_si:.6g} m",
                    "seite_c_si": f"{side_c_si:.6g} m"
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
    "name": "solve_trapez",
    "short_description": "Trapez-Fläche - Berechnet Fläche, parallele Seiten oder Höhe",
    "description": """Löst die Trapezformel A = (a + c) × h / 2 nach verschiedenen Variablen auf. Lösbare Variablen: area, side_a, side_c, height

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "5.2 mm", "10 cm", "75 cm²")

Grundformel: A = (a + c) × h / 2

Parameter:
- area: Fläche des Trapezes mit Flächeneinheit (z.B. "75 cm²", "0.1 m²")
- side_a: Erste parallele Seite mit Längeneinheit (z.B. "10 cm", "25 mm") 
- side_c: Zweite parallele Seite mit Längeneinheit (z.B. "5 cm", "15 mm")
- height: Höhe des Trapezes mit Längeneinheit (z.B. "8 cm", "20 mm")

Anwendungsbereich: Geometrische Berechnungen, Dachflächen, Querschnitte
Einschränkungen: Alle Werte müssen positiv sein, parallele Seiten dürfen nicht null sein""",
    "tags": ["elementar", "Fläche"],
    "function": solve_trapez,
    "examples": [
        {
            "description": "Berechne Fläche bei gegebenen parallelen Seiten und Höhe",
            "call": 'solve_trapez(side_a="10 cm", side_c="5 cm", height="8 cm")',
            "result": "Fläche in optimierter Einheit"
        },
        {
            "description": "Berechne erste Seite bei gegebener Fläche", 
            "call": 'solve_trapez(area="60 cm²", side_c="5 cm", height="8 cm")',
            "result": "Erste Seite in optimierter Einheit"
        },
        {
            "description": "Berechne Höhe bei gegebener Fläche und Seiten",
            "call": 'solve_trapez(area="60 cm²", side_a="10 cm", side_c="5 cm")',
            "result": "Höhe in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Trapez-Tool Tests ===")
    
    # Test 1: Fläche berechnen
    result1 = solve_trapez(side_a="10 cm", side_c="5 cm", height="8 cm")
    print(f"Test 1 - Fläche: {result1}")
    
    # Test 2: Erste Seite berechnen
    result2 = solve_trapez(area="60 cm²", side_c="5 cm", height="8 cm")
    print(f"Test 2 - Seite a: {result2}")
    
    # Test 3: Höhe berechnen
    result3 = solve_trapez(area="60 cm²", side_a="10 cm", side_c="5 cm")
    print(f"Test 3 - Höhe: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_trapez(side_a="10", side_c="5 cm", height="8 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 