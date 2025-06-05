#!/usr/bin/env python3
"""
Parallelogramm-Fläche - Berechnet Fläche, Grundseite oder Höhe

Berechnet Parallelogramm-Flächen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel A = a × h nach verschiedenen Variablen auf.
Lösbare Variablen: area, base, height

Parallelogramm: Viereck mit parallelen Gegenseiten
Formel: A = a × h (Grundseite × Höhe)
"""

from typing import Dict, Optional
import sys
import os

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_parallelogramm(
    area: Optional[str] = None,
    base: Optional[str] = None,
    height: Optional[str] = None
) -> Dict:
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [area, base, height] if p is not None]
        
        if len(given_params) != 2:
            return {
                "error": "Genau 2 Parameter müssen gegeben sein (einer wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_parallelogramm(base='8 cm', height='5 cm')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                area=area, 
                base=base, 
                height=height
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "area='40 cm²'",
                    "base='8 cm'", 
                    "height='5 cm'"
                ]
            }
        
        # Berechnung basierend auf gegebenen Parametern
        if area is None:
            # Berechne Fläche: A = a × h
            base_si = params['base']['si_value']      # in Metern
            height_si = params['height']['si_value']  # in Metern
            
            if base_si <= 0 or height_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            area_si = base_si * height_si  # in m²
            
            # Optimiere Ausgabe-Einheit (nutze kürzere Seitenlänge als Referenz)
            ref_unit = params['height']['original_unit'] if height_si < base_si else params['base']['original_unit']
            area_quantity = area_si * ureg.meter**2
            area_optimized = optimize_output_unit(area_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "grundseite": base,
                    "hoehe": height
                },
                "ergebnis": {
                    "flaeche": f"{area_optimized.magnitude:.6g} {area_optimized.units}"
                },
                "formel": "A = a × h",
                "si_werte": {
                    "flaeche_si": f"{area_si:.6g} m²",
                    "grundseite_si": f"{base_si:.6g} m",
                    "hoehe_si": f"{height_si:.6g} m"
                }
            }
            
        elif base is None:
            # Berechne Grundseite: a = A / h
            area_si = params['area']['si_value']      # in m²
            height_si = params['height']['si_value']  # in Metern
            
            if area_si <= 0 or height_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            base_si = area_si / height_si  # in Metern
            
            # Optimiere Ausgabe-Einheit
            base_quantity = base_si * ureg.meter
            base_optimized = optimize_output_unit(base_quantity, params['height']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "flaeche": area,
                    "hoehe": height
                },
                "ergebnis": {
                    "grundseite": f"{base_optimized.magnitude:.6g} {base_optimized.units}"
                },
                "formel": "a = A / h",
                "si_werte": {
                    "grundseite_si": f"{base_si:.6g} m",
                    "flaeche_si": f"{area_si:.6g} m²",
                    "hoehe_si": f"{height_si:.6g} m"
                }
            }
            
        elif height is None:
            # Berechne Höhe: h = A / a
            area_si = params['area']['si_value']    # in m²
            base_si = params['base']['si_value']    # in Metern
            
            if area_si <= 0 or base_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            height_si = area_si / base_si  # in Metern
            
            # Optimiere Ausgabe-Einheit
            height_quantity = height_si * ureg.meter
            height_optimized = optimize_output_unit(height_quantity, params['base']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "flaeche": area,
                    "grundseite": base
                },
                "ergebnis": {
                    "hoehe": f"{height_optimized.magnitude:.6g} {height_optimized.units}"
                },
                "formel": "h = A / a",
                "si_werte": {
                    "hoehe_si": f"{height_si:.6g} m",
                    "flaeche_si": f"{area_si:.6g} m²",
                    "grundseite_si": f"{base_si:.6g} m"
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
    "name": "solve_parallelogramm",
    "short_description": "Parallelogramm-Fläche - Berechnet Fläche, Grundseite oder Höhe",
    "description": """Löst die Parallelogramm-Formel A = a × h nach verschiedenen Variablen auf. Lösbare Variablen: area, base, height

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "8 cm", "5.2 mm", "40 cm²")

Grundformel: A = a × h

Parameter:
- area: Fläche des Parallelogramms mit Flächeneinheit (z.B. "40 cm²", "0.004 m²")
- base: Grundseite mit Längeneinheit (z.B. "8 cm", "80 mm") 
- height: Höhe (senkrechter Abstand) mit Längeneinheit (z.B. "5 cm", "50 mm")

Anwendungsbereich: Geometrie, Konstruktion, Flächenberechnungen schiefer Vierecke
Einschränkungen: Alle Werte müssen positiv sein""",
    "tags": ["elementar", "Fläche"],
    "function": solve_parallelogramm,
    "examples": [
        {
            "description": "Berechne Fläche bei gegebener Grundseite und Höhe",
            "call": 'solve_parallelogramm(base="8 cm", height="5 cm")',
            "result": "Fläche in optimierter Einheit"
        },
        {
            "description": "Berechne Grundseite bei gegebener Fläche und Höhe", 
            "call": 'solve_parallelogramm(area="40 cm²", height="5 cm")',
            "result": "Grundseite in optimierter Einheit"
        },
        {
            "description": "Berechne Höhe bei gegebener Fläche und Grundseite",
            "call": 'solve_parallelogramm(area="40 cm²", base="8 cm")',
            "result": "Höhe in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Parallelogramm-Tool Tests ===")
    
    # Test 1: Fläche berechnen
    result1 = solve_parallelogramm(base="8 cm", height="5 cm")
    print(f"Test 1 - Fläche: {result1}")
    
    # Test 2: Grundseite berechnen
    result2 = solve_parallelogramm(area="40 cm²", height="5 cm")
    print(f"Test 2 - Grundseite: {result2}")
    
    # Test 3: Höhe berechnen
    result3 = solve_parallelogramm(area="40 cm²", base="8 cm")
    print(f"Test 3 - Höhe: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_parallelogramm(base="8", height="5 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 