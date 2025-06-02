#!/usr/bin/env python3
"""
Zylinder-Volumen - Berechnet Volumen, Radius oder Höhe eines Zylinders

Berechnet Zylindervolumen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel V = π × r² × h nach verschiedenen Variablen auf.
Lösbare Variablen: volume, radius, height
"""

import math
from typing import Dict, Optional
import sys
import os

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_zylinder(
    volume: Optional[str] = None,
    radius: Optional[str] = None,
    height: Optional[str] = None
) -> Dict:
    """
    Berechnet Zylinder-Parameter mit Einheiten-Support.
    
    WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
    Format: "Wert Einheit" (z.B. "5.2 mm", "10 cm", "785 cm³")
    
    Zylinderformel: V = π × r² × h
    
    Lösbare Variablen: volume, radius, height
    
    Args:
        volume: Volumen des Zylinders mit Einheit (z.B. "785 cm³", "0.5 l")
        radius: Radius des Zylinders mit Einheit (z.B. "5 cm") 
        height: Höhe des Zylinders mit Einheit (z.B. "10 cm")
        
    Returns:
        Dict mit Ergebnissen in optimierten Einheiten
        
    Raises:
        ValueError: Bei ungültigen Parametern oder fehlenden Einheiten
    """
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [volume, radius, height] if p is not None]
        
        if len(given_params) != 2:
            return {
                "error": "Genau 2 Parameter müssen gegeben sein (einer wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_zylinder(radius='5 cm', height='10 cm')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                volume=volume,
                radius=radius, 
                height=height
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "volume='785 cm³'",
                    "radius='5 cm'", 
                    "height='10 cm'"
                ]
            }
        
        # Berechnung basierend auf gegebenen Parametern
        if volume is None:
            # Berechne Volumen: V = π × r² × h
            radius_si = params['radius']['si_value']  # in Metern
            height_si = params['height']['si_value']  # in Metern
            
            if radius_si <= 0 or height_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            volume_si = math.pi * radius_si**2 * height_si  # in m³
            
            # Optimiere Ausgabe-Einheit (nutze kleinere Dimension als Referenz)
            ref_unit = params['radius']['original_unit'] if radius_si < height_si else params['height']['original_unit']
            volume_quantity = volume_si * ureg.meter**3
            volume_optimized = optimize_volume_unit(volume_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "radius": radius,
                    "hoehe": height
                },
                "ergebnis": {
                    "volumen": f"{volume_optimized.magnitude:.6g} {volume_optimized.units}"
                },
                "formel": "V = π × r² × h",
                "si_werte": {
                    "volumen_si": f"{volume_si:.6g} m³",
                    "radius_si": f"{radius_si:.6g} m",
                    "hoehe_si": f"{height_si:.6g} m"
                }
            }
            
        elif radius is None:
            # Berechne Radius: r = √(V / (π × h))
            volume_si = params['volume']['si_value']  # in m³
            height_si = params['height']['si_value']  # in Metern
            
            if volume_si <= 0 or height_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            radius_si = math.sqrt(volume_si / (math.pi * height_si))  # in Metern
            
            # Optimiere Ausgabe-Einheit
            radius_quantity = radius_si * ureg.meter
            radius_optimized = optimize_output_unit(radius_quantity, params['height']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "volumen": volume,
                    "hoehe": height
                },
                "ergebnis": {
                    "radius": f"{radius_optimized.magnitude:.6g} {radius_optimized.units}"
                },
                "formel": "r = √(V / (π × h))",
                "si_werte": {
                    "radius_si": f"{radius_si:.6g} m",
                    "volumen_si": f"{volume_si:.6g} m³",
                    "hoehe_si": f"{height_si:.6g} m"
                }
            }
            
        elif height is None:
            # Berechne Höhe: h = V / (π × r²)
            volume_si = params['volume']['si_value']  # in m³
            radius_si = params['radius']['si_value']  # in Metern
            
            if volume_si <= 0 or radius_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            height_si = volume_si / (math.pi * radius_si**2)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            height_quantity = height_si * ureg.meter
            height_optimized = optimize_output_unit(height_quantity, params['radius']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "volumen": volume,
                    "radius": radius
                },
                "ergebnis": {
                    "hoehe": f"{height_optimized.magnitude:.6g} {height_optimized.units}"
                },
                "formel": "h = V / (π × r²)",
                "si_werte": {
                    "hoehe_si": f"{height_si:.6g} m",
                    "volumen_si": f"{volume_si:.6g} m³",
                    "radius_si": f"{radius_si:.6g} m"
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
    "name": "solve_zylinder",
    "short_description": "Zylinder-Volumen - Berechnet Volumen, Radius oder Höhe",
    "description": """Löst die Zylinderformel V = π × r² × h nach verschiedenen Variablen auf. Lösbare Variablen: volume, radius, height

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "5.2 mm", "10 cm", "785 cm³")

Grundformel: V = π × r² × h

Parameter:
- volume: Volumen des Zylinders mit Volumeneinheit (z.B. "785 cm³", "0.5 l", "2 m³")
- radius: Radius des Zylinders mit Längeneinheit (z.B. "5 cm", "25 mm") 
- height: Höhe des Zylinders mit Längeneinheit (z.B. "10 cm", "15 mm")

Anwendungsbereich: Behälterplanung, Rohre, Tanks, Motorzylinder
Einschränkungen: Alle Werte müssen positiv sein""",
    "tags": ["elementar", "Volumen"],
    "function": solve_zylinder,
    "examples": [
        {
            "description": "Berechne Volumen bei gegebenem Radius und Höhe",
            "call": 'solve_zylinder(radius="5 cm", height="10 cm")',
            "result": "Volumen in optimierter Einheit"
        },
        {
            "description": "Berechne Radius bei gegebenem Volumen und Höhe", 
            "call": 'solve_zylinder(volume="785 cm³", height="10 cm")',
            "result": "Radius in optimierter Einheit"
        },
        {
            "description": "Berechne Höhe bei gegebenem Volumen und Radius",
            "call": 'solve_zylinder(volume="785 cm³", radius="5 cm")',
            "result": "Höhe in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Zylinder-Tool Tests ===")
    
    # Test 1: Volumen berechnen
    result1 = solve_zylinder(radius="5 cm", height="10 cm")
    print(f"Test 1 - Volumen: {result1}")
    
    # Test 2: Radius berechnen
    result2 = solve_zylinder(volume="785 cm³", height="10 cm")
    print(f"Test 2 - Radius: {result2}")
    
    # Test 3: Höhe berechnen
    result3 = solve_zylinder(volume="785 cm³", radius="5 cm")
    print(f"Test 3 - Höhe: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_zylinder(radius="5", height="10 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 