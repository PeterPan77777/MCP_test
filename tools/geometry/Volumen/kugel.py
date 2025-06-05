#!/usr/bin/env python3
"""
Kugel-Volumen - Berechnet Volumen oder Radius einer Kugel

Berechnet Kugelvolumen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel V = (4/3) × π × r³ nach verschiedenen Variablen auf.
Lösbare Variablen: volume, radius
"""

import math
from typing import Dict, Optional
import sys
import os

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_kugel(
    volume: Optional[str] = None,
    radius: Optional[str] = None
) -> Dict:
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [volume, radius] if p is not None]
        
        if len(given_params) != 1:
            return {
                "error": "Genau 1 Parameter muss gegeben sein (der andere wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_kugel(radius='5 cm') oder solve_kugel(volume='523 cm³')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                volume=volume,
                radius=radius
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "volume='523 cm³'",
                    "radius='5 cm'"
                ]
            }
        
        # Berechnung basierend auf gegebenem Parameter
        if volume is None:
            # Berechne Volumen: V = (4/3) × π × r³
            radius_si = params['radius']['si_value']  # in Metern
            
            if radius_si <= 0:
                return {"error": "Radius muss positiv sein"}
            
            volume_si = (4/3) * math.pi * radius_si**3  # in m³
            
            # Optimiere Ausgabe-Einheit
            volume_quantity = volume_si * ureg.meter**3
            volume_optimized = optimize_volume_unit(volume_quantity, params['radius']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "radius": radius
                },
                "ergebnis": {
                    "volumen": f"{volume_optimized.magnitude:.6g} {volume_optimized.units}"
                },
                "formel": "V = (4/3) × π × r³",
                "si_werte": {
                    "volumen_si": f"{volume_si:.6g} m³",
                    "radius_si": f"{radius_si:.6g} m"
                }
            }
            
        elif radius is None:
            # Berechne Radius: r = ∛(3V / (4π))
            volume_si = params['volume']['si_value']  # in m³
            
            if volume_si <= 0:
                return {"error": "Volumen muss positiv sein"}
            
            radius_si = ((3 * volume_si) / (4 * math.pi))**(1/3)  # in Metern
            
            # Optimiere Ausgabe-Einheit - extrahiere Basis-Längeneinheit aus Volumeneinheit
            volume_unit = params['volume']['original_unit']
            if 'cm³' in volume_unit or 'cm3' in volume_unit:
                ref_unit = 'cm'
            elif 'mm³' in volume_unit or 'mm3' in volume_unit:
                ref_unit = 'mm'
            elif 'l' in volume_unit or 'liter' in volume_unit:
                ref_unit = 'dm'  # 1 Liter = 1 dm³
            elif 'm³' in volume_unit or 'm3' in volume_unit:
                ref_unit = 'm'
            else:
                ref_unit = 'cm'  # Standard-Fallback
            
            radius_quantity = radius_si * ureg.meter
            radius_optimized = optimize_output_unit(radius_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "volumen": volume
                },
                "ergebnis": {
                    "radius": f"{radius_optimized.magnitude:.6g} {radius_optimized.units}"
                },
                "formel": "r = ∛(3V / (4π))",
                "si_werte": {
                    "radius_si": f"{radius_si:.6g} m",
                    "volumen_si": f"{volume_si:.6g} m³"
                }
            }
        
    except Exception as e:
        return {
            "error": "Berechnungsfehler",
            "message": str(e),
            "hinweis": "Überprüfen Sie die Eingabe-Parameter und Einheiten"
        }

def optimize_volume_unit(si_quantity, reference_unit_str: str):
    """
    Optimiert Volumeneinheiten basierend auf Größenordnung.
    """
    try:
        magnitude = si_quantity.magnitude  # in m³
        
        # Bestimme optimale Volumeneinheit
        if magnitude >= 1:  # >= 1 m³
            return si_quantity.to(ureg.meter**3)
        elif magnitude >= 0.001:  # >= 1 dm³ (= 1 Liter)
            return si_quantity.to(ureg.liter)
        elif magnitude >= 1e-6:  # >= 1 cm³
            return si_quantity.to(ureg.centimeter**3)
        else:  # < 1 cm³
            return si_quantity.to(ureg.millimeter**3)
            
    except Exception:
        return si_quantity

# Tool-Metadaten für Registry
TOOL_METADATA = {
    "name": "solve_kugel",
    "short_description": "Kugel-Volumen - Berechnet Volumen oder Radius",
    "description": """Löst die Kugelformel V = (4/3) × π × r³ nach verschiedenen Variablen auf. Lösbare Variablen: volume, radius

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "5.2 mm", "523 cm³")

Grundformel: V = (4/3) × π × r³

Parameter:
- volume: Volumen der Kugel mit Volumeneinheit (z.B. "523 cm³", "0.5 l", "2 m³")
- radius: Radius der Kugel mit Längeneinheit (z.B. "5 cm", "25 mm")

Anwendungsbereich: Behälterplanung, Ballvolumen, Kugelförmige Tanks
Einschränkungen: Alle Werte müssen positiv sein""",
    "tags": ["elementar", "Volumen"],
    "function": solve_kugel,
    "examples": [
        {
            "description": "Berechne Volumen bei gegebenem Radius",
            "call": 'solve_kugel(radius="5 cm")',
            "result": "Volumen in optimierter Einheit"
        },
        {
            "description": "Berechne Radius bei gegebenem Volumen", 
            "call": 'solve_kugel(volume="523 cm³")',
            "result": "Radius in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Kugel-Tool Tests ===")
    
    # Test 1: Volumen berechnen
    result1 = solve_kugel(radius="5 cm")
    print(f"Test 1 - Volumen: {result1}")
    
    # Test 2: Radius berechnen
    result2 = solve_kugel(volume="523 cm³")
    print(f"Test 2 - Radius: {result2}")
    
    # Test 3: Fehler - keine Einheit
    result3 = solve_kugel(radius="5")
    print(f"Test 3 - Keine Einheit: {result3}") 