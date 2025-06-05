#!/usr/bin/env python3
"""
Kreis-Umfang - Berechnet Umfang, Radius oder Durchmesser

Berechnet Kreis-Umfang mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel U = 2 × π × r nach verschiedenen Variablen auf.
Lösbare Variablen: perimeter, radius, diameter

Kreis: Vollständig geschlossene runde Form
Formel: U = 2 × π × r = π × d
"""

from typing import Dict, Optional
import sys
import os
import math

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_kreis_umfang(
    perimeter: Optional[str] = None,
    radius: Optional[str] = None,
    diameter: Optional[str] = None
) -> Dict:
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [perimeter, radius, diameter] if p is not None]
        
        if len(given_params) != 1:
            return {
                "error": "Genau 1 Parameter muss gegeben sein (die anderen werden berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_kreis_umfang(radius='5 cm')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                perimeter=perimeter, 
                radius=radius, 
                diameter=diameter
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "perimeter='31.42 cm'",
                    "radius='5 cm'", 
                    "diameter='10 cm'"
                ]
            }
        
        # Berechnung basierend auf gegebenem Parameter
        if radius is not None:
            # Gegeben: Radius → Berechne Umfang und Durchmesser
            r_si = params['radius']['si_value']  # in Metern
            
            if r_si <= 0:
                return {"error": "Radius muss positiv sein"}
            
            perimeter_si = 2 * math.pi * r_si   # in Metern
            diameter_si = 2 * r_si              # in Metern
            
            # Optimiere Ausgabe-Einheiten
            perimeter_quantity = perimeter_si * ureg.meter
            diameter_quantity = diameter_si * ureg.meter
            ref_unit = params['radius']['original_unit']
            
            perimeter_optimized = optimize_output_unit(perimeter_quantity, ref_unit)
            diameter_optimized = optimize_output_unit(diameter_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "radius": radius
                },
                "ergebnis": {
                    "umfang": f"{perimeter_optimized.magnitude:.6g} {perimeter_optimized.units}",
                    "durchmesser": f"{diameter_optimized.magnitude:.6g} {diameter_optimized.units}"
                },
                "formel": "U = 2 × π × r, d = 2 × r",
                "si_werte": {
                    "umfang_si": f"{perimeter_si:.6g} m",
                    "durchmesser_si": f"{diameter_si:.6g} m",
                    "radius_si": f"{r_si:.6g} m"
                }
            }
            
        elif diameter is not None:
            # Gegeben: Durchmesser → Berechne Umfang und Radius
            d_si = params['diameter']['si_value']  # in Metern
            
            if d_si <= 0:
                return {"error": "Durchmesser muss positiv sein"}
            
            radius_si = d_si / 2                   # in Metern
            perimeter_si = math.pi * d_si          # in Metern
            
            # Optimiere Ausgabe-Einheiten
            radius_quantity = radius_si * ureg.meter
            perimeter_quantity = perimeter_si * ureg.meter
            ref_unit = params['diameter']['original_unit']
            
            radius_optimized = optimize_output_unit(radius_quantity, ref_unit)
            perimeter_optimized = optimize_output_unit(perimeter_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "durchmesser": diameter
                },
                "ergebnis": {
                    "umfang": f"{perimeter_optimized.magnitude:.6g} {perimeter_optimized.units}",
                    "radius": f"{radius_optimized.magnitude:.6g} {radius_optimized.units}"
                },
                "formel": "U = π × d, r = d / 2",
                "si_werte": {
                    "umfang_si": f"{perimeter_si:.6g} m",
                    "radius_si": f"{radius_si:.6g} m",
                    "durchmesser_si": f"{d_si:.6g} m"
                }
            }
            
        elif perimeter is not None:
            # Gegeben: Umfang → Berechne Radius und Durchmesser
            U_si = params['perimeter']['si_value']  # in Metern
            
            if U_si <= 0:
                return {"error": "Umfang muss positiv sein"}
            
            radius_si = U_si / (2 * math.pi)       # in Metern
            diameter_si = U_si / math.pi           # in Metern
            
            # Optimiere Ausgabe-Einheiten
            radius_quantity = radius_si * ureg.meter
            diameter_quantity = diameter_si * ureg.meter
            ref_unit = params['perimeter']['original_unit']
            
            radius_optimized = optimize_output_unit(radius_quantity, ref_unit)
            diameter_optimized = optimize_output_unit(diameter_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "umfang": perimeter
                },
                "ergebnis": {
                    "radius": f"{radius_optimized.magnitude:.6g} {radius_optimized.units}",
                    "durchmesser": f"{diameter_optimized.magnitude:.6g} {diameter_optimized.units}"
                },
                "formel": "r = U / (2 × π), d = U / π",
                "si_werte": {
                    "radius_si": f"{radius_si:.6g} m",
                    "durchmesser_si": f"{diameter_si:.6g} m",
                    "umfang_si": f"{U_si:.6g} m"
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
    "name": "solve_kreis_umfang",
    "short_description": "Kreis-Umfang - Berechnet Umfang, Radius oder Durchmesser",
    "description": """Löst die Kreis-Umfang-Formeln U = 2 × π × r = π × d nach verschiedenen Variablen auf. Lösbare Variablen: perimeter, radius, diameter

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "5 cm", "10 cm", "31.42 cm")

Grundformeln: U = 2 × π × r = π × d

Parameter:
- perimeter: Umfang des Kreises mit Längeneinheit (z.B. "31.42 cm", "314.2 mm")
- radius: Radius des Kreises mit Längeneinheit (z.B. "5 cm", "50 mm") 
- diameter: Durchmesser des Kreises mit Längeneinheit (z.B. "10 cm", "100 mm")

Anwendungsbereich: Geometrie, Maschinenbau (Räder, Rohre), Konstruktion kreisförmiger Objekte
Einschränkungen: Alle Werte müssen positiv sein""",
    "tags": ["elementar", "Umfang"],
    "function": solve_kreis_umfang,
    "examples": [
        {
            "description": "Berechne Umfang und Durchmesser bei gegebenem Radius",
            "call": 'solve_kreis_umfang(radius="5 cm")',
            "result": "Umfang und Durchmesser in optimierter Einheit"
        },
        {
            "description": "Berechne Umfang und Radius bei gegebenem Durchmesser", 
            "call": 'solve_kreis_umfang(diameter="10 cm")',
            "result": "Umfang und Radius in optimierter Einheit"
        },
        {
            "description": "Berechne Radius und Durchmesser bei gegebenem Umfang",
            "call": 'solve_kreis_umfang(perimeter="31.42 cm")',
            "result": "Radius und Durchmesser in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Kreis-Umfang-Tool Tests ===")
    
    # Test 1: Umfang und Durchmesser bei gegebenem Radius
    result1 = solve_kreis_umfang(radius="5 cm")
    print(f"Test 1 - Von Radius: {result1}")
    
    # Test 2: Umfang und Radius bei gegebenem Durchmesser
    result2 = solve_kreis_umfang(diameter="10 cm")
    print(f"Test 2 - Von Durchmesser: {result2}")
    
    # Test 3: Radius und Durchmesser bei gegebenem Umfang
    result3 = solve_kreis_umfang(perimeter="31.42 cm")
    print(f"Test 3 - Von Umfang: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_kreis_umfang(radius="5")
    print(f"Test 4 - Keine Einheit: {result4}") 