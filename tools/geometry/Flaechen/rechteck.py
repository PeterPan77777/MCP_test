#!/usr/bin/env python3
"""
Rechteck-Fläche - Berechnet Fläche, Länge oder Breite eines Rechtecks

Berechnet Rechteckflächen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel A = l × b nach verschiedenen Variablen auf.
Lösbare Variablen: area, length, width
"""

from typing import Dict, Optional
import sys
import os

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_rechteck(
    area: Optional[str] = None,
    length: Optional[str] = None,
    width: Optional[str] = None
) -> Dict:
    """
    Berechnet Rechteck-Parameter mit Einheiten-Support.
    
    WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
    Format: "Wert Einheit" (z.B. "5.2 mm", "10 cm", "25.5 cm²")
    
    Rechteckformel: A = l × b
    
    Lösbare Variablen: area, length, width
    
    Args:
        area: Fläche des Rechtecks mit Einheit (z.B. "25.5 cm²")
        length: Länge des Rechtecks mit Einheit (z.B. "10 cm") 
        width: Breite des Rechtecks mit Einheit (z.B. "5.2 mm")
        
    Returns:
        Dict mit Ergebnissen in optimierten Einheiten
        
    Raises:
        ValueError: Bei ungültigen Parametern oder fehlenden Einheiten
    """
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [area, length, width] if p is not None]
        
        if len(given_params) != 2:
            return {
                "error": "Genau 2 Parameter müssen gegeben sein (einer wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_rechteck(length='10 cm', width='5 cm')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                area=area, 
                length=length, 
                width=width
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "area='25.5 cm²'",
                    "length='10 cm'", 
                    "width='5.2 mm'"
                ]
            }
        
        # Berechnung basierend auf gegebenen Parametern
        if area is None:
            # Berechne Fläche: A = l × b
            length_si = params['length']['si_value']  # in Metern
            width_si = params['width']['si_value']    # in Metern
            
            if length_si <= 0 or width_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            area_si = length_si * width_si  # in m²
            
            # Optimiere Ausgabe-Einheit (nutze kürzere Seitenlänge als Referenz)
            ref_unit = params['width']['original_unit'] if width_si < length_si else params['length']['original_unit']
            area_quantity = area_si * ureg.meter**2
            area_optimized = optimize_output_unit(area_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "laenge": length,
                    "breite": width
                },
                "ergebnis": {
                    "flaeche": f"{area_optimized.magnitude:.6g} {area_optimized.units}"
                },
                "formel": "A = l × b",
                "si_werte": {
                    "flaeche_si": f"{area_si:.6g} m²",
                    "laenge_si": f"{length_si:.6g} m",
                    "breite_si": f"{width_si:.6g} m"
                }
            }
            
        elif length is None:
            # Berechne Länge: l = A / b
            area_si = params['area']['si_value']      # in m²
            width_si = params['width']['si_value']    # in Metern
            
            if area_si <= 0 or width_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            length_si = area_si / width_si  # in Metern
            
            # Optimiere Ausgabe-Einheit
            length_quantity = length_si * ureg.meter
            length_optimized = optimize_output_unit(length_quantity, params['width']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "flaeche": area,
                    "breite": width
                },
                "ergebnis": {
                    "laenge": f"{length_optimized.magnitude:.6g} {length_optimized.units}"
                },
                "formel": "l = A / b",
                "si_werte": {
                    "laenge_si": f"{length_si:.6g} m",
                    "flaeche_si": f"{area_si:.6g} m²",
                    "breite_si": f"{width_si:.6g} m"
                }
            }
            
        elif width is None:
            # Berechne Breite: b = A / l
            area_si = params['area']['si_value']       # in m²
            length_si = params['length']['si_value']   # in Metern
            
            if area_si <= 0 or length_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            width_si = area_si / length_si  # in Metern
            
            # Optimiere Ausgabe-Einheit
            width_quantity = width_si * ureg.meter
            width_optimized = optimize_output_unit(width_quantity, params['length']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "flaeche": area,
                    "laenge": length
                },
                "ergebnis": {
                    "breite": f"{width_optimized.magnitude:.6g} {width_optimized.units}"
                },
                "formel": "b = A / l",
                "si_werte": {
                    "breite_si": f"{width_si:.6g} m",
                    "flaeche_si": f"{area_si:.6g} m²",
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
    "name": "solve_rechteck",
    "short_description": "Rechteck-Fläche - Berechnet Fläche, Länge oder Breite",
    "description": """Löst die Rechteckformel A = l × b nach verschiedenen Variablen auf. Lösbare Variablen: area, length, width

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "5.2 mm", "10 cm", "25.5 cm²")

Grundformel: A = l × b

Parameter:
- area: Fläche des Rechtecks mit Flächeneinheit (z.B. "25.5 cm²", "0.1 m²")
- length: Länge des Rechtecks mit Längeneinheit (z.B. "10 cm", "5.2 mm") 
- width: Breite des Rechtecks mit Längeneinheit (z.B. "5 cm", "25 mm")

Anwendungsbereich: Flächenberechnungen, Konstruktion, Grundstücksplanung
Einschränkungen: Alle Werte müssen positiv sein""",
    "tags": ["elementar", "Fläche"],
    "function": solve_rechteck,
    "examples": [
        {
            "description": "Berechne Fläche bei gegebener Länge und Breite",
            "call": 'solve_rechteck(length="10 cm", width="5 cm")',
            "result": "Fläche in optimierter Einheit"
        },
        {
            "description": "Berechne Länge bei gegebener Fläche und Breite", 
            "call": 'solve_rechteck(area="50 cm²", width="5 cm")',
            "result": "Länge in optimierter Einheit"
        },
        {
            "description": "Berechne Breite bei gegebener Fläche und Länge",
            "call": 'solve_rechteck(area="50 cm²", length="10 cm")',
            "result": "Breite in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Rechteck-Tool Tests ===")
    
    # Test 1: Fläche berechnen
    result1 = solve_rechteck(length="10 cm", width="5 cm")
    print(f"Test 1 - Fläche: {result1}")
    
    # Test 2: Länge berechnen
    result2 = solve_rechteck(area="50 cm²", width="5 cm")
    print(f"Test 2 - Länge: {result2}")
    
    # Test 3: Breite berechnen
    result3 = solve_rechteck(area="50 cm²", length="10 cm")
    print(f"Test 3 - Breite: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_rechteck(length="10", width="5 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 