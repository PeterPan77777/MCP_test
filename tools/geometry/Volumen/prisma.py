#!/usr/bin/env python3
"""
Prisma-Volumen - Berechnet Volumen, Grundfläche oder Höhe

Berechnet Prisma-Volumen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel V = A × h nach verschiedenen Variablen auf.
Lösbare Variablen: volume, base_area, height

Prisma: Körper mit parallelen, kongruenten Grundflächen
Formel: V = A × h (Grundfläche × Höhe)
"""

from typing import Dict, Optional
import sys
import os

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_prisma(
    volume: Optional[str] = None,
    base_area: Optional[str] = None,
    height: Optional[str] = None
) -> Dict:
    """
    Berechnet Prisma-Volumen mit Einheiten-Support.
    
    WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
    Format: "Wert Einheit" (z.B. "30 cm²", "8 cm", "240 cm³")
    
    Prisma-Formel: V = A × h
    
    Lösbare Variablen: volume, base_area, height
    
    Args:
        volume: Volumen des Prismas mit Einheit (z.B. "240 cm³")
        base_area: Grundfläche mit Einheit (z.B. "30 cm²") 
        height: Höhe des Prismas mit Einheit (z.B. "8 cm")
        
    Returns:
        Dict mit Ergebnissen in optimierten Einheiten
        
    Raises:
        ValueError: Bei ungültigen Parametern oder fehlenden Einheiten
    """
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [volume, base_area, height] if p is not None]
        
        if len(given_params) != 2:
            return {
                "error": "Genau 2 Parameter müssen gegeben sein (einer wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_prisma(base_area='30 cm²', height='8 cm')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                volume=volume, 
                base_area=base_area, 
                height=height
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "volume='240 cm³'",
                    "base_area='30 cm²'", 
                    "height='8 cm'"
                ]
            }
        
        # Berechnung basierend auf gegebenen Parametern
        if volume is None:
            # Berechne Volumen: V = A × h
            A_si = params['base_area']['si_value']   # in m²
            h_si = params['height']['si_value']      # in Metern
            
            if A_si <= 0 or h_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            volume_si = A_si * h_si  # in m³
            
            # Optimiere Ausgabe-Einheit (basierend auf Höhe)
            volume_quantity = volume_si * ureg.meter**3
            volume_optimized = optimize_output_unit(volume_quantity, params['height']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "grundflaeche": base_area,
                    "hoehe": height
                },
                "ergebnis": {
                    "volumen": f"{volume_optimized.magnitude:.6g} {volume_optimized.units}"
                },
                "formel": "V = A × h",
                "si_werte": {
                    "volumen_si": f"{volume_si:.6g} m³",
                    "grundflaeche_si": f"{A_si:.6g} m²",
                    "hoehe_si": f"{h_si:.6g} m"
                }
            }
            
        elif base_area is None:
            # Berechne Grundfläche: A = V / h
            V_si = params['volume']['si_value']    # in m³
            h_si = params['height']['si_value']    # in Metern
            
            if V_si <= 0 or h_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            A_si = V_si / h_si  # in m²
            
            # Optimiere Ausgabe-Einheit
            A_quantity = A_si * ureg.meter**2
            A_optimized = optimize_output_unit(A_quantity, params['height']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "volumen": volume,
                    "hoehe": height
                },
                "ergebnis": {
                    "grundflaeche": f"{A_optimized.magnitude:.6g} {A_optimized.units}"
                },
                "formel": "A = V / h",
                "si_werte": {
                    "grundflaeche_si": f"{A_si:.6g} m²",
                    "volumen_si": f"{V_si:.6g} m³",
                    "hoehe_si": f"{h_si:.6g} m"
                }
            }
            
        elif height is None:
            # Berechne Höhe: h = V / A
            V_si = params['volume']['si_value']      # in m³
            A_si = params['base_area']['si_value']   # in m²
            
            if V_si <= 0 or A_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            h_si = V_si / A_si  # in Metern
            
            # Optimiere Ausgabe-Einheit (ableiten von Grundfläche)
            h_quantity = h_si * ureg.meter
            # Ermittle charakteristische Länge aus Grundfläche (Quadratwurzel)
            char_length = (A_si ** 0.5) * ureg.meter
            h_optimized = optimize_output_unit(h_quantity, char_length)
            
            return {
                "gegebene_werte": {
                    "volumen": volume,
                    "grundflaeche": base_area
                },
                "ergebnis": {
                    "hoehe": f"{h_optimized.magnitude:.6g} {h_optimized.units}"
                },
                "formel": "h = V / A",
                "si_werte": {
                    "hoehe_si": f"{h_si:.6g} m",
                    "volumen_si": f"{V_si:.6g} m³",
                    "grundflaeche_si": f"{A_si:.6g} m²"
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
    "name": "solve_prisma",
    "short_description": "Prisma-Volumen - Berechnet Volumen, Grundfläche oder Höhe",
    "description": """Löst die Prisma-Formel V = A × h nach verschiedenen Variablen auf. Lösbare Variablen: volume, base_area, height

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "30 cm²", "8 cm", "240 cm³")

Grundformel: V = A × h

Parameter:
- volume: Volumen des Prismas mit Volumeneinheit (z.B. "240 cm³", "0.00024 m³")
- base_area: Grundfläche mit Flächeneinheit (z.B. "30 cm²", "0.003 m²") 
- height: Höhe des Prismas mit Längeneinheit (z.B. "8 cm", "80 mm")

Anwendungsbereich: Geometrie, Konstruktion (Profile, Balken), allgemeine Volumenberechnungen
Einschränkungen: Alle Werte müssen positiv sein""",
    "tags": ["elementar", "Volumen"],
    "function": solve_prisma,
    "examples": [
        {
            "description": "Berechne Volumen bei gegebener Grundfläche und Höhe",
            "call": 'solve_prisma(base_area="30 cm²", height="8 cm")',
            "result": "Volumen in optimierter Einheit"
        },
        {
            "description": "Berechne Grundfläche bei gegebenem Volumen und Höhe", 
            "call": 'solve_prisma(volume="240 cm³", height="8 cm")',
            "result": "Grundfläche in optimierter Einheit"
        },
        {
            "description": "Berechne Höhe bei gegebenem Volumen und Grundfläche",
            "call": 'solve_prisma(volume="240 cm³", base_area="30 cm²")',
            "result": "Höhe in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Prisma-Tool Tests ===")
    
    # Test 1: Volumen berechnen
    result1 = solve_prisma(base_area="30 cm²", height="8 cm")
    print(f"Test 1 - Volumen: {result1}")
    
    # Test 2: Grundfläche berechnen
    result2 = solve_prisma(volume="240 cm³", height="8 cm")
    print(f"Test 2 - Grundfläche: {result2}")
    
    # Test 3: Höhe berechnen
    result3 = solve_prisma(volume="240 cm³", base_area="30 cm²")
    print(f"Test 3 - Höhe: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_prisma(base_area="30", height="8 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 