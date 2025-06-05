#!/usr/bin/env python3
"""
Kegel-Volumen - Berechnet Volumen, Radius oder Höhe

Berechnet Kegel-Volumen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel V = (1/3) × π × r² × h nach verschiedenen Variablen auf.
Lösbare Variablen: volume, radius, height

Kegel: Rotationskörper mit kreisförmiger Grundfläche und Spitze
Formel: V = (1/3) × π × r² × h (⅓ × π × Radius² × Höhe)
"""

from typing import Dict, Optional
import sys
import os
import math

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_kegel(
    volume: Optional[str] = None,
    radius: Optional[str] = None,
    height: Optional[str] = None
) -> Dict:
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [volume, radius, height] if p is not None]
        
        if len(given_params) != 2:
            return {
                "error": "Genau 2 Parameter müssen gegeben sein (einer wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_kegel(radius='4 cm', height='6 cm')"
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
                    "volume='100.53 cm³'",
                    "radius='4 cm'", 
                    "height='6 cm'"
                ]
            }
        
        # Berechnung basierend auf gegebenen Parametern
        if volume is None:
            # Berechne Volumen: V = (1/3) × π × r² × h
            r_si = params['radius']['si_value']    # in Metern
            h_si = params['height']['si_value']    # in Metern
            
            if r_si <= 0 or h_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            volume_si = (1/3) * math.pi * r_si**2 * h_si  # in m³
            
            # Optimiere Ausgabe-Einheit (nutze Radius als Referenz)
            volume_quantity = volume_si * ureg.meter**3
            volume_optimized = optimize_output_unit(volume_quantity, params['radius']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "radius": radius,
                    "hoehe": height
                },
                "ergebnis": {
                    "volumen": f"{volume_optimized.magnitude:.6g} {volume_optimized.units}"
                },
                "formel": "V = (1/3) × π × r² × h",
                "si_werte": {
                    "volumen_si": f"{volume_si:.6g} m³",
                    "radius_si": f"{r_si:.6g} m",
                    "hoehe_si": f"{h_si:.6g} m"
                }
            }
            
        elif radius is None:
            # Berechne Radius: r = √((3 × V) / (π × h))
            V_si = params['volume']['si_value']    # in m³
            h_si = params['height']['si_value']    # in Metern
            
            if V_si <= 0 or h_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            r_squared = (3 * V_si) / (math.pi * h_si)
            if r_squared < 0:
                return {"error": "Ungültige Kombination von Volumen und Höhe"}
            
            r_si = math.sqrt(r_squared)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            r_quantity = r_si * ureg.meter
            r_optimized = optimize_output_unit(r_quantity, params['height']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "volumen": volume,
                    "hoehe": height
                },
                "ergebnis": {
                    "radius": f"{r_optimized.magnitude:.6g} {r_optimized.units}"
                },
                "formel": "r = √((3 × V) / (π × h))",
                "si_werte": {
                    "radius_si": f"{r_si:.6g} m",
                    "volumen_si": f"{V_si:.6g} m³",
                    "hoehe_si": f"{h_si:.6g} m"
                }
            }
            
        elif height is None:
            # Berechne Höhe: h = (3 × V) / (π × r²)
            V_si = params['volume']['si_value']    # in m³
            r_si = params['radius']['si_value']    # in Metern
            
            if V_si <= 0 or r_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            h_si = (3 * V_si) / (math.pi * r_si**2)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            h_quantity = h_si * ureg.meter
            h_optimized = optimize_output_unit(h_quantity, params['radius']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "volumen": volume,
                    "radius": radius
                },
                "ergebnis": {
                    "hoehe": f"{h_optimized.magnitude:.6g} {h_optimized.units}"
                },
                "formel": "h = (3 × V) / (π × r²)",
                "si_werte": {
                    "hoehe_si": f"{h_si:.6g} m",
                    "volumen_si": f"{V_si:.6g} m³",
                    "radius_si": f"{r_si:.6g} m"
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
    "name": "solve_kegel",
    "short_description": "Kegel-Volumen - Berechnet Volumen, Radius oder Höhe",
    "description": """Löst die Kegel-Formel V = (1/3) × π × r² × h nach verschiedenen Variablen auf. Lösbare Variablen: volume, radius, height

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "4 cm", "6 cm", "100.53 cm³")

Grundformel: V = (1/3) × π × r² × h

Parameter:
- volume: Volumen des Kegels mit Volumeneinheit (z.B. "100.53 cm³", "0.0001 m³")
- radius: Grundradius mit Längeneinheit (z.B. "4 cm", "40 mm") 
- height: Höhe des Kegels mit Längeneinheit (z.B. "6 cm", "60 mm")

Anwendungsbereich: Geometrie, Maschinenbau (konische Teile), Trichter-Berechnungen
Einschränkungen: Alle Werte müssen positiv sein""",
    "tags": ["elementar", "Volumen"],
    "function": solve_kegel,
    "examples": [
        {
            "description": "Berechne Volumen bei gegebenem Radius und Höhe",
            "call": 'solve_kegel(radius="4 cm", height="6 cm")',
            "result": "Volumen in optimierter Einheit"
        },
        {
            "description": "Berechne Radius bei gegebenem Volumen und Höhe", 
            "call": 'solve_kegel(volume="100.53 cm³", height="6 cm")',
            "result": "Radius in optimierter Einheit"
        },
        {
            "description": "Berechne Höhe bei gegebenem Volumen und Radius",
            "call": 'solve_kegel(volume="100.53 cm³", radius="4 cm")',
            "result": "Höhe in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Kegel-Tool Tests ===")
    
    # Test 1: Volumen berechnen
    result1 = solve_kegel(radius="4 cm", height="6 cm")
    print(f"Test 1 - Volumen: {result1}")
    
    # Test 2: Radius berechnen
    result2 = solve_kegel(volume="100.53 cm³", height="6 cm")
    print(f"Test 2 - Radius: {result2}")
    
    # Test 3: Höhe berechnen
    result3 = solve_kegel(volume="100.53 cm³", radius="4 cm")
    print(f"Test 3 - Höhe: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_kegel(radius="4", height="6 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 