#!/usr/bin/env python3
"""
Rechteck-Umfang - Berechnet Umfang, Länge oder Breite

Berechnet Rechteck-Umfang mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel U = 2 × (a + b) nach verschiedenen Variablen auf.
Lösbare Variablen: perimeter, length, width

Rechteck: Viereck mit rechten Winkeln
Formel: U = 2 × (a + b) = 2 × (Länge + Breite)
"""

from typing import Dict, Optional
import sys
import os

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_rechteck_umfang(
    perimeter: Optional[str] = None,
    length: Optional[str] = None,
    width: Optional[str] = None
) -> Dict:
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [perimeter, length, width] if p is not None]
        
        if len(given_params) != 2:
            return {
                "error": "Genau 2 Parameter müssen gegeben sein (einer wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_rechteck_umfang(length='10 cm', width='6 cm')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                perimeter=perimeter, 
                length=length, 
                width=width
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "perimeter='32 cm'",
                    "length='10 cm'", 
                    "width='6 cm'"
                ]
            }
        
        # Berechnung basierend auf gegebenen Parametern
        if perimeter is None:
            # Berechne Umfang: U = 2 × (a + b)
            length_si = params['length']['si_value']   # in Metern
            width_si = params['width']['si_value']     # in Metern
            
            if length_si <= 0 or width_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            perimeter_si = 2 * (length_si + width_si)  # in Metern
            
            # Optimiere Ausgabe-Einheit (nutze längere Seite als Referenz)
            ref_unit = params['length']['original_unit'] if length_si > width_si else params['width']['original_unit']
            perimeter_quantity = perimeter_si * ureg.meter
            perimeter_optimized = optimize_output_unit(perimeter_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "laenge": length,
                    "breite": width
                },
                "ergebnis": {
                    "umfang": f"{perimeter_optimized.magnitude:.6g} {perimeter_optimized.units}"
                },
                "formel": "U = 2 × (a + b)",
                "si_werte": {
                    "umfang_si": f"{perimeter_si:.6g} m",
                    "laenge_si": f"{length_si:.6g} m",
                    "breite_si": f"{width_si:.6g} m"
                }
            }
            
        elif length is None:
            # Berechne Länge: a = (U / 2) - b
            perimeter_si = params['perimeter']['si_value']  # in Metern
            width_si = params['width']['si_value']          # in Metern
            
            if perimeter_si <= 0 or width_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            length_si = (perimeter_si / 2) - width_si  # in Metern
            
            if length_si <= 0:
                return {"error": "Breite ist zu groß für den gegebenen Umfang"}
            
            # Optimiere Ausgabe-Einheit
            length_quantity = length_si * ureg.meter
            length_optimized = optimize_output_unit(length_quantity, params['width']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "umfang": perimeter,
                    "breite": width
                },
                "ergebnis": {
                    "laenge": f"{length_optimized.magnitude:.6g} {length_optimized.units}"
                },
                "formel": "a = (U / 2) - b",
                "si_werte": {
                    "laenge_si": f"{length_si:.6g} m",
                    "umfang_si": f"{perimeter_si:.6g} m",
                    "breite_si": f"{width_si:.6g} m"
                }
            }
            
        elif width is None:
            # Berechne Breite: b = (U / 2) - a
            perimeter_si = params['perimeter']['si_value']  # in Metern
            length_si = params['length']['si_value']        # in Metern
            
            if perimeter_si <= 0 or length_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            width_si = (perimeter_si / 2) - length_si  # in Metern
            
            if width_si <= 0:
                return {"error": "Länge ist zu groß für den gegebenen Umfang"}
            
            # Optimiere Ausgabe-Einheit
            width_quantity = width_si * ureg.meter
            width_optimized = optimize_output_unit(width_quantity, params['length']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "umfang": perimeter,
                    "laenge": length
                },
                "ergebnis": {
                    "breite": f"{width_optimized.magnitude:.6g} {width_optimized.units}"
                },
                "formel": "b = (U / 2) - a",
                "si_werte": {
                    "breite_si": f"{width_si:.6g} m",
                    "umfang_si": f"{perimeter_si:.6g} m",
                    "laenge_si": f"{length_si:.6g} m"
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
    "name": "solve_rechteck_umfang",
    "short_description": "Rechteck-Umfang - Berechnet Umfang, Länge oder Breite",
    "description": """Löst die Rechteck-Umfang-Formel U = 2 × (a + b) nach verschiedenen Variablen auf. Lösbare Variablen: perimeter, length, width

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "10 cm", "6 cm", "32 cm")

Grundformel: U = 2 × (a + b)

Parameter:
- perimeter: Umfang des Rechtecks mit Längeneinheit (z.B. "32 cm", "320 mm")
- length: Länge des Rechtecks mit Längeneinheit (z.B. "10 cm", "100 mm") 
- width: Breite des Rechtecks mit Längeneinheit (z.B. "6 cm", "60 mm")

Anwendungsbereich: Geometrie, Konstruktion, Zaunberechnungen, Umrandungen
Einschränkungen: Alle Werte müssen positiv sein""",
    "tags": ["elementar", "Umfang"],
    "function": solve_rechteck_umfang,
    "examples": [
        {
            "description": "Berechne Umfang bei gegebener Länge und Breite",
            "call": 'solve_rechteck_umfang(length="10 cm", width="6 cm")',
            "result": "Umfang in optimierter Einheit"
        },
        {
            "description": "Berechne Länge bei gegebenem Umfang und Breite", 
            "call": 'solve_rechteck_umfang(perimeter="32 cm", width="6 cm")',
            "result": "Länge in optimierter Einheit"
        },
        {
            "description": "Berechne Breite bei gegebenem Umfang und Länge",
            "call": 'solve_rechteck_umfang(perimeter="32 cm", length="10 cm")',
            "result": "Breite in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Rechteck-Umfang-Tool Tests ===")
    
    # Test 1: Umfang berechnen
    result1 = solve_rechteck_umfang(length="10 cm", width="6 cm")
    print(f"Test 1 - Umfang: {result1}")
    
    # Test 2: Länge berechnen
    result2 = solve_rechteck_umfang(perimeter="32 cm", width="6 cm")
    print(f"Test 2 - Länge: {result2}")
    
    # Test 3: Breite berechnen
    result3 = solve_rechteck_umfang(perimeter="32 cm", length="10 cm")
    print(f"Test 3 - Breite: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_rechteck_umfang(length="10", width="6 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 