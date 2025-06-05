#!/usr/bin/env python3
"""
Quader-Volumen - Berechnet Volumen, Länge, Breite oder Höhe eines Quaders

Berechnet Quadervolumen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel V = l × b × h nach verschiedenen Variablen auf.
Lösbare Variablen: volume, length, width, height
"""

from typing import Dict, Optional
import sys
import os

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_quader(
    volume: Optional[str] = None,
    length: Optional[str] = None,
    width: Optional[str] = None,
    height: Optional[str] = None
) -> Dict:
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [volume, length, width, height] if p is not None]
        
        if len(given_params) != 3:
            return {
                "error": "Genau 3 Parameter müssen gegeben sein (einer wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_quader(length='10 cm', width='5 cm', height='2.5 cm')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                volume=volume,
                length=length, 
                width=width,
                height=height
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "volume='125 cm³'",
                    "length='10 cm'", 
                    "width='5 cm'",
                    "height='2.5 cm'"
                ]
            }
        
        # Berechnung basierend auf gegebenen Parametern
        if volume is None:
            # Berechne Volumen: V = l × b × h
            length_si = params['length']['si_value']  # in Metern
            width_si = params['width']['si_value']    # in Metern
            height_si = params['height']['si_value']  # in Metern
            
            if length_si <= 0 or width_si <= 0 or height_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            volume_si = length_si * width_si * height_si  # in m³
            
            # Optimiere Ausgabe-Einheit (nutze kleinste Seitenlänge als Referenz)
            ref_sizes = [width_si, length_si, height_si]
            ref_units = [params['width']['original_unit'], params['length']['original_unit'], params['height']['original_unit']]
            min_idx = ref_sizes.index(min(ref_sizes))
            ref_unit = ref_units[min_idx]
            
            volume_quantity = volume_si * ureg.meter**3
            volume_optimized = optimize_volume_unit(volume_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "laenge": length,
                    "breite": width,
                    "hoehe": height
                },
                "ergebnis": {
                    "volumen": f"{volume_optimized.magnitude:.6g} {volume_optimized.units}"
                },
                "formel": "V = l × b × h",
                "si_werte": {
                    "volumen_si": f"{volume_si:.6g} m³",
                    "laenge_si": f"{length_si:.6g} m",
                    "breite_si": f"{width_si:.6g} m",
                    "hoehe_si": f"{height_si:.6g} m"
                }
            }
            
        elif length is None:
            # Berechne Länge: l = V / (b × h)
            volume_si = params['volume']['si_value']  # in m³
            width_si = params['width']['si_value']    # in Metern
            height_si = params['height']['si_value']  # in Metern
            
            if volume_si <= 0 or width_si <= 0 or height_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            length_si = volume_si / (width_si * height_si)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            length_quantity = length_si * ureg.meter
            length_optimized = optimize_output_unit(length_quantity, params['width']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "volumen": volume,
                    "breite": width,
                    "hoehe": height
                },
                "ergebnis": {
                    "laenge": f"{length_optimized.magnitude:.6g} {length_optimized.units}"
                },
                "formel": "l = V / (b × h)",
                "si_werte": {
                    "laenge_si": f"{length_si:.6g} m",
                    "volumen_si": f"{volume_si:.6g} m³",
                    "breite_si": f"{width_si:.6g} m",
                    "hoehe_si": f"{height_si:.6g} m"
                }
            }
            
        elif width is None:
            # Berechne Breite: b = V / (l × h)
            volume_si = params['volume']['si_value']  # in m³
            length_si = params['length']['si_value']  # in Metern
            height_si = params['height']['si_value']  # in Metern
            
            if volume_si <= 0 or length_si <= 0 or height_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            width_si = volume_si / (length_si * height_si)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            width_quantity = width_si * ureg.meter
            width_optimized = optimize_output_unit(width_quantity, params['length']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "volumen": volume,
                    "laenge": length,
                    "hoehe": height
                },
                "ergebnis": {
                    "breite": f"{width_optimized.magnitude:.6g} {width_optimized.units}"
                },
                "formel": "b = V / (l × h)",
                "si_werte": {
                    "breite_si": f"{width_si:.6g} m",
                    "volumen_si": f"{volume_si:.6g} m³",
                    "laenge_si": f"{length_si:.6g} m",
                    "hoehe_si": f"{height_si:.6g} m"
                }
            }
            
        elif height is None:
            # Berechne Höhe: h = V / (l × b)
            volume_si = params['volume']['si_value']  # in m³
            length_si = params['length']['si_value']  # in Metern
            width_si = params['width']['si_value']    # in Metern
            
            if volume_si <= 0 or length_si <= 0 or width_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            height_si = volume_si / (length_si * width_si)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            height_quantity = height_si * ureg.meter
            height_optimized = optimize_output_unit(height_quantity, params['length']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "volumen": volume,
                    "laenge": length,
                    "breite": width
                },
                "ergebnis": {
                    "hoehe": f"{height_optimized.magnitude:.6g} {height_optimized.units}"
                },
                "formel": "h = V / (l × b)",
                "si_werte": {
                    "hoehe_si": f"{height_si:.6g} m",
                    "volumen_si": f"{volume_si:.6g} m³",
                    "laenge_si": f"{length_si:.6g} m",
                    "breite_si": f"{width_si:.6g} m"
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
    "name": "solve_quader",
    "short_description": "Quader-Volumen - Berechnet Volumen und Abmessungen",
    "description": """Löst die Quaderformel V = l × b × h nach verschiedenen Variablen auf. Lösbare Variablen: volume, length, width, height

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "5.2 mm", "10 cm", "125 cm³")

Grundformel: V = l × b × h

Parameter:
- volume: Volumen des Quaders mit Volumeneinheit (z.B. "125 cm³", "0.5 l", "2 m³")
- length: Länge des Quaders mit Längeneinheit (z.B. "10 cm", "5.2 mm") 
- width: Breite des Quaders mit Längeneinheit (z.B. "5 cm", "25 mm")
- height: Höhe des Quaders mit Längeneinheit (z.B. "2.5 cm", "15 mm")

Anwendungsbereich: Volumenberechnungen, Behälterplanung, Lagerung
Einschränkungen: Alle Werte müssen positiv sein""",
    "tags": ["elementar", "Volumen"],
    "function": solve_quader,
    "examples": [
        {
            "description": "Berechne Volumen bei gegebenen Abmessungen",
            "call": 'solve_quader(length="10 cm", width="5 cm", height="2.5 cm")',
            "result": "Volumen in optimierter Einheit"
        },
        {
            "description": "Berechne Länge bei gegebenem Volumen", 
            "call": 'solve_quader(volume="125 cm³", width="5 cm", height="2.5 cm")',
            "result": "Länge in optimierter Einheit"
        },
        {
            "description": "Berechne Höhe bei gegebenem Volumen",
            "call": 'solve_quader(volume="125 cm³", length="10 cm", width="5 cm")',
            "result": "Höhe in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Quader-Tool Tests ===")
    
    # Test 1: Volumen berechnen
    result1 = solve_quader(length="10 cm", width="5 cm", height="2.5 cm")
    print(f"Test 1 - Volumen: {result1}")
    
    # Test 2: Länge berechnen
    result2 = solve_quader(volume="125 cm³", width="5 cm", height="2.5 cm")
    print(f"Test 2 - Länge: {result2}")
    
    # Test 3: Höhe berechnen
    result3 = solve_quader(volume="125 cm³", length="10 cm", width="5 cm")
    print(f"Test 3 - Höhe: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_quader(length="10", width="5 cm", height="2.5 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 