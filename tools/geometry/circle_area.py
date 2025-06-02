#!/usr/bin/env python3
"""
Kreisflächen-Berechnung mit Einheiten-Support

Berechnet Fläche von Kreisen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.
"""

import math
from typing import Dict, Optional
import sys
import os

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_circle_area(
    radius: Optional[str] = None,
    diameter: Optional[str] = None,
    area: Optional[str] = None
) -> Dict:
    """
    Berechnet Kreisfläche nach verschiedenen Variablen mit Einheiten-Support.
    
    WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
    Format: "Wert Einheit" (z.B. "5.2 mm", "10 cm", "0.5 m²")
    
    Lösbare Variablen: radius, diameter, area
    
    Args:
        radius: Radius des Kreises mit Einheit (z.B. "5.2 mm")
        diameter: Durchmesser des Kreises mit Einheit (z.B. "10.4 cm") 
        area: Fläche des Kreises mit Einheit (z.B. "25.5 cm²")
        
    Returns:
        Dict mit Ergebnissen in optimierten Einheiten
        
    Raises:
        ValueError: Bei ungültigen Parametern oder fehlenden Einheiten
    """
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [radius, diameter, area] if p is not None]
        
        if len(given_params) != 1:
            return {
                "error": "Genau ein Parameter muss gegeben sein",
                "given_count": len(given_params),
                "example": "Beispiel: solve_circle_area(radius='5.2 mm')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                radius=radius, 
                diameter=diameter, 
                area=area
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden (z.B. '5.2 mm')",
                "beispiele": [
                    "radius='25 mm'",
                    "diameter='5 cm'", 
                    "area='10 cm²'"
                ]
            }
        
        # Berechnung basierend auf gegebenem Parameter
        if radius is not None:
            # Gegeben: Radius -> Berechne Fläche
            r_si = params['radius']['si_value']  # in Metern
            area_si = math.pi * r_si * r_si  # in m²
            
            # Erstelle Pint Quantity für Ausgabe-Optimierung
            area_quantity = area_si * ureg.meter**2
            area_optimized = optimize_output_unit(area_quantity, params['radius']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "radius": radius
                },
                "ergebnis": {
                    "flaeche": f"{area_optimized.magnitude:.6g} {area_optimized.units}"
                },
                "formel": "A = π × r²",
                "si_werte": {
                    "radius_si": f"{r_si:.6g} m",
                    "flaeche_si": f"{area_si:.6g} m²"
                }
            }
            
        elif diameter is not None:
            # Gegeben: Durchmesser -> Berechne Fläche
            d_si = params['diameter']['si_value']  # in Metern
            r_si = d_si / 2
            area_si = math.pi * r_si * r_si  # in m²
            
            # Erstelle Pint Quantity für Ausgabe-Optimierung
            area_quantity = area_si * ureg.meter**2
            area_optimized = optimize_output_unit(area_quantity, params['diameter']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "durchmesser": diameter
                },
                "ergebnis": {
                    "flaeche": f"{area_optimized.magnitude:.6g} {area_optimized.units}"
                },
                "formel": "A = π × (d/2)²",
                "si_werte": {
                    "durchmesser_si": f"{d_si:.6g} m",
                    "radius_si": f"{r_si:.6g} m", 
                    "flaeche_si": f"{area_si:.6g} m²"
                }
            }
            
        elif area is not None:
            # Gegeben: Fläche -> Berechne Radius und Durchmesser
            area_si = params['area']['si_value']  # in m²
            
            if area_si <= 0:
                return {
                    "error": "Fläche muss positiv sein",
                    "gegeben": area
                }
            
            r_si = math.sqrt(area_si / math.pi)  # in Metern
            d_si = 2 * r_si
            
            # Optimiere Ausgabe-Einheiten basierend auf Eingabe-Einheit
            radius_quantity = r_si * ureg.meter
            diameter_quantity = d_si * ureg.meter
            
            # Extrahiere Basis-Längeneinheit aus Flächeneinheit (z.B. cm² -> cm)
            original_unit = params['area']['original_unit']
            if '²' in original_unit or '2' in original_unit:
                # Entferne Quadrat-Zeichen um Basis-Längeneinheit zu erhalten
                base_unit = original_unit.replace('²', '').replace('2', '')
                radius_optimized = optimize_output_unit(radius_quantity, base_unit)
                diameter_optimized = optimize_output_unit(diameter_quantity, base_unit)
            else:
                radius_optimized = radius_quantity
                diameter_optimized = diameter_quantity
            
            return {
                "gegebene_werte": {
                    "flaeche": area
                },
                "ergebnis": {
                    "radius": f"{radius_optimized.magnitude:.6g} {radius_optimized.units}",
                    "durchmesser": f"{diameter_optimized.magnitude:.6g} {diameter_optimized.units}"
                },
                "formel": "r = √(A/π), d = 2×r",
                "si_werte": {
                    "flaeche_si": f"{area_si:.6g} m²",
                    "radius_si": f"{r_si:.6g} m",
                    "durchmesser_si": f"{d_si:.6g} m"
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
    "name": "solve_circle_area",
    "short_description": "Kreisflächen-Berechnung - Berechnet Fläche, Radius oder Durchmesser",
    "description": """Löst Kreisflächen-Formeln nach verschiedenen Variablen auf. Lösbare Variablen: radius, diameter, area

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "5.2 mm", "10 cm", "25.5 cm²")

Grundformel: A = π × r²

Parameter:
- radius: Radius des Kreises mit Längeneinheit (z.B. "5.2 mm", "2.5 cm")
- diameter: Durchmesser des Kreises mit Längeneinheit (z.B. "10 mm", "5 cm") 
- area: Fläche des Kreises mit Flächeneinheit (z.B. "25.5 cm²", "0.1 m²")

Anwendungsbereich: Geometrische Berechnungen, Flächenbestimmung, Konstruktion
Einschränkungen: Alle Werte müssen positiv sein""",
    "tags": ["elementar"],
    "function": solve_circle_area,
    "examples": [
        {
            "description": "Berechne Fläche bei gegebenem Radius",
            "call": 'solve_circle_area(radius="25 mm")',
            "result": "Fläche in optimierter Einheit"
        },
        {
            "description": "Berechne Fläche bei gegebenem Durchmesser", 
            "call": 'solve_circle_area(diameter="5 cm")',
            "result": "Fläche in optimierter Einheit"
        },
        {
            "description": "Berechne Radius und Durchmesser bei gegebener Fläche",
            "call": 'solve_circle_area(area="10 cm²")',
            "result": "Radius und Durchmesser in optimierten Einheiten"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Kreisflächen-Tool Tests ===")
    
    # Test 1: Radius gegeben
    result1 = solve_circle_area(radius="25 mm")
    print(f"Test 1 - Radius: {result1}")
    
    # Test 2: Durchmesser gegeben  
    result2 = solve_circle_area(diameter="5 cm")
    print(f"Test 2 - Durchmesser: {result2}")
    
    # Test 3: Fläche gegeben
    result3 = solve_circle_area(area="10 cm²")
    print(f"Test 3 - Fläche: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_circle_area(radius="25")
    print(f"Test 4 - Keine Einheit: {result4}") 