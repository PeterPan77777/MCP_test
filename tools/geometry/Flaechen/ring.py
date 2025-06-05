#!/usr/bin/env python3
"""
Kreisring-Fläche - Berechnet Fläche zwischen zwei konzentrischen Kreisen

Berechnet Kreisring-Flächen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel A = π × (R² - r²) nach verschiedenen Variablen auf.
Lösbare Variablen: area, outer_radius, inner_radius

Kreisring: Fläche zwischen äußerem und innerem Kreis
Formel: A = π × (R² - r²) = π × (Raußen² - Rinnen²)
"""

from typing import Dict, Optional
import sys
import os
import math

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_ring(
    area: Optional[str] = None,
    outer_radius: Optional[str] = None,
    inner_radius: Optional[str] = None
) -> Dict:
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [area, outer_radius, inner_radius] if p is not None]
        
        if len(given_params) != 2:
            return {
                "error": "Genau 2 Parameter müssen gegeben sein (einer wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_ring(outer_radius='8 cm', inner_radius='5 cm')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                area=area, 
                outer_radius=outer_radius, 
                inner_radius=inner_radius
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "area='109.96 cm²'",
                    "outer_radius='8 cm'", 
                    "inner_radius='5 cm'"
                ]
            }
        
        # Berechnung basierend auf gegebenen Parametern
        if area is None:
            # Berechne Fläche: A = π × (R² - r²)
            R_si = params['outer_radius']['si_value']   # in Metern
            r_si = params['inner_radius']['si_value']   # in Metern
            
            if R_si <= 0 or r_si <= 0:
                return {"error": "Alle Radien müssen positiv sein"}
            
            if r_si >= R_si:
                return {"error": "Äußerer Radius muss größer als innerer Radius sein"}
            
            area_si = math.pi * (R_si**2 - r_si**2)  # in m²
            
            # Optimiere Ausgabe-Einheit (nutze äußeren Radius als Referenz)
            area_quantity = area_si * ureg.meter**2
            area_optimized = optimize_output_unit(area_quantity, params['outer_radius']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "aeusserer_radius": outer_radius,
                    "innerer_radius": inner_radius
                },
                "ergebnis": {
                    "ringflaeche": f"{area_optimized.magnitude:.6g} {area_optimized.units}"
                },
                "formel": "A = π × (R² - r²)",
                "si_werte": {
                    "ringflaeche_si": f"{area_si:.6g} m²",
                    "aeusserer_radius_si": f"{R_si:.6g} m",
                    "innerer_radius_si": f"{r_si:.6g} m"
                }
            }
            
        elif outer_radius is None:
            # Berechne äußeren Radius: R = √((A/π) + r²)
            area_si = params['area']['si_value']        # in m²
            r_si = params['inner_radius']['si_value']   # in Metern
            
            if area_si <= 0 or r_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            R_squared = (area_si / math.pi) + r_si**2
            if R_squared <= 0:
                return {"error": "Ungültige Kombination von Fläche und innerem Radius"}
            
            R_si = math.sqrt(R_squared)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            R_quantity = R_si * ureg.meter
            R_optimized = optimize_output_unit(R_quantity, params['inner_radius']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "ringflaeche": area,
                    "innerer_radius": inner_radius
                },
                "ergebnis": {
                    "aeusserer_radius": f"{R_optimized.magnitude:.6g} {R_optimized.units}"
                },
                "formel": "R = √((A/π) + r²)",
                "si_werte": {
                    "aeusserer_radius_si": f"{R_si:.6g} m",
                    "ringflaeche_si": f"{area_si:.6g} m²",
                    "innerer_radius_si": f"{r_si:.6g} m"
                }
            }
            
        elif inner_radius is None:
            # Berechne inneren Radius: r = √(R² - (A/π))
            area_si = params['area']['si_value']       # in m²
            R_si = params['outer_radius']['si_value']  # in Metern
            
            if area_si <= 0 or R_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            r_squared = R_si**2 - (area_si / math.pi)
            if r_squared < 0:
                return {"error": "Fläche zu groß für gegebenen äußeren Radius"}
            
            r_si = math.sqrt(r_squared)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            r_quantity = r_si * ureg.meter
            r_optimized = optimize_output_unit(r_quantity, params['outer_radius']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "ringflaeche": area,
                    "aeusserer_radius": outer_radius
                },
                "ergebnis": {
                    "innerer_radius": f"{r_optimized.magnitude:.6g} {r_optimized.units}"
                },
                "formel": "r = √(R² - (A/π))",
                "si_werte": {
                    "innerer_radius_si": f"{r_si:.6g} m",
                    "ringflaeche_si": f"{area_si:.6g} m²",
                    "aeusserer_radius_si": f"{R_si:.6g} m"
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
    "name": "solve_ring",
    "short_description": "Kreisring-Fläche - Berechnet Ring-Fläche oder Radien",
    "description": """Löst die Kreisring-Formel A = π × (R² - r²) nach verschiedenen Variablen auf. Lösbare Variablen: area, outer_radius, inner_radius

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "8 cm", "5 cm", "109.96 cm²")

Grundformel: A = π × (R² - r²)

Parameter:
- area: Fläche des Kreisrings mit Flächeneinheit (z.B. "109.96 cm²", "0.011 m²")
- outer_radius: Äußerer Radius mit Längeneinheit (z.B. "8 cm", "80 mm") 
- inner_radius: Innerer Radius mit Längeneinheit (z.B. "5 cm", "50 mm")

Anwendungsbereich: Maschinenbau (Rohre, Ringe), Architektur (Hohlprofile), Flächenberechnungen
Einschränkungen: Äußerer Radius > Innerer Radius > 0""",
    "tags": ["elementar", "Fläche"],
    "function": solve_ring,
    "examples": [
        {
            "description": "Berechne Ring-Fläche bei gegebenen Radien",
            "call": 'solve_ring(outer_radius="8 cm", inner_radius="5 cm")',
            "result": "Ring-Fläche in optimierter Einheit"
        },
        {
            "description": "Berechne äußeren Radius bei gegebener Fläche und innerem Radius", 
            "call": 'solve_ring(area="109.96 cm²", inner_radius="5 cm")',
            "result": "Äußerer Radius in optimierter Einheit"
        },
        {
            "description": "Berechne inneren Radius bei gegebener Fläche und äußerem Radius",
            "call": 'solve_ring(area="109.96 cm²", outer_radius="8 cm")',
            "result": "Innerer Radius in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Kreisring-Tool Tests ===")
    
    # Test 1: Ring-Fläche berechnen
    result1 = solve_ring(outer_radius="8 cm", inner_radius="5 cm")
    print(f"Test 1 - Ring-Fläche: {result1}")
    
    # Test 2: Äußeren Radius berechnen
    result2 = solve_ring(area="109.96 cm²", inner_radius="5 cm")
    print(f"Test 2 - Äußerer Radius: {result2}")
    
    # Test 3: Inneren Radius berechnen
    result3 = solve_ring(area="109.96 cm²", outer_radius="8 cm")
    print(f"Test 3 - Innerer Radius: {result3}")
    
    # Test 4: Fehler - innerer > äußerer Radius
    result4 = solve_ring(outer_radius="5 cm", inner_radius="8 cm")
    print(f"Test 4 - Ungültige Radien: {result4}") 