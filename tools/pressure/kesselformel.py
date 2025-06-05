#!/usr/bin/env python3
"""
Kesselformel-Berechnung mit Einheiten-Support

Berechnet zulässige Drücke für Druckbehälter mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.
"""

from typing import Dict, Optional
import sys
import os

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

def solve_kesselformel(
    pressure: Optional[str] = None,
    wall_thickness: Optional[str] = None,
    diameter: Optional[str] = None,
    allowable_stress: Optional[str] = None
) -> Dict:
    try:
        # Zähle gegebene Parameter
        given_params = [p for p in [pressure, wall_thickness, diameter, allowable_stress] if p is not None]
        
        if len(given_params) != 3:
            return {
                "error": "Genau 3 Parameter müssen gegeben sein (einer wird berechnet)",
                "given_count": len(given_params),
                "example": "Beispiel: solve_kesselformel(wall_thickness='5 mm', diameter='500 mm', allowable_stress='200 MPa')"
            }
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(
                pressure=pressure,
                wall_thickness=wall_thickness, 
                diameter=diameter,
                allowable_stress=allowable_stress
            )
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    "pressure='10 bar'",
                    "wall_thickness='5 mm'",
                    "diameter='500 mm'", 
                    "allowable_stress='200 MPa'"
                ]
            }
        
        # Kesselformel: p = (2 × σ_zul × s) / D
        # Umgestellt: σ_zul = (p × D) / (2 × s)
        #            s = (p × D) / (2 × σ_zul)  
        #            D = (2 × σ_zul × s) / p
        
        if pressure is None:
            # Berechne Druck: p = (2 × σ_zul × s) / D
            sigma_si = params['allowable_stress']['si_value']  # Pa
            s_si = params['wall_thickness']['si_value']        # m
            d_si = params['diameter']['si_value']              # m
            
            if d_si <= 0 or s_si <= 0 or sigma_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            p_si = (2 * sigma_si * s_si) / d_si  # Pa
            
            # Optimiere Ausgabe-Einheit basierend auf typischer Eingabe
            pressure_quantity = p_si * ureg.pascal
            
            # Verwende eine sinnvolle Referenz-Einheit für Druck
            if 'bar' in str(params.get('allowable_stress', {}).get('original_unit', '')):
                ref_unit = 'bar'
            elif 'MPa' in str(params.get('allowable_stress', {}).get('original_unit', '')):
                ref_unit = 'MPa'
            else:
                ref_unit = 'bar'  # Standard-Referenz
            
            pressure_optimized = optimize_output_unit(pressure_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "wanddicke": wall_thickness,
                    "durchmesser": diameter,
                    "zulaessige_spannung": allowable_stress
                },
                "ergebnis": {
                    "druck": f"{pressure_optimized.magnitude:.6g} {pressure_optimized.units}"
                },
                "formel": "p = (2 × σ_zul × s) / D",
                "si_werte": {
                    "druck_si": f"{p_si:.6g} Pa",
                    "wanddicke_si": f"{s_si:.6g} m",
                    "durchmesser_si": f"{d_si:.6g} m",
                    "zulaessige_spannung_si": f"{sigma_si:.6g} Pa"
                }
            }
            
        elif wall_thickness is None:
            # Berechne Wanddicke: s = (p × D) / (2 × σ_zul)
            p_si = params['pressure']['si_value']              # Pa
            d_si = params['diameter']['si_value']              # m
            sigma_si = params['allowable_stress']['si_value']  # Pa
            
            if p_si <= 0 or d_si <= 0 or sigma_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            s_si = (p_si * d_si) / (2 * sigma_si)  # m
            
            # Optimiere Ausgabe-Einheit
            thickness_quantity = s_si * ureg.meter
            thickness_optimized = optimize_output_unit(thickness_quantity, params['diameter']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "druck": pressure,
                    "durchmesser": diameter,
                    "zulaessige_spannung": allowable_stress
                },
                "ergebnis": {
                    "wanddicke": f"{thickness_optimized.magnitude:.6g} {thickness_optimized.units}"
                },
                "formel": "s = (p × D) / (2 × σ_zul)",
                "si_werte": {
                    "wanddicke_si": f"{s_si:.6g} m",
                    "druck_si": f"{p_si:.6g} Pa",
                    "durchmesser_si": f"{d_si:.6g} m",
                    "zulaessige_spannung_si": f"{sigma_si:.6g} Pa"
                }
            }
            
        elif diameter is None:
            # Berechne Durchmesser: D = (2 × σ_zul × s) / p
            p_si = params['pressure']['si_value']              # Pa
            s_si = params['wall_thickness']['si_value']        # m
            sigma_si = params['allowable_stress']['si_value']  # Pa
            
            if p_si <= 0 or s_si <= 0 or sigma_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            d_si = (2 * sigma_si * s_si) / p_si  # m
            
            # Optimiere Ausgabe-Einheit
            diameter_quantity = d_si * ureg.meter
            diameter_optimized = optimize_output_unit(diameter_quantity, params['wall_thickness']['original_unit'])
            
            return {
                "gegebene_werte": {
                    "druck": pressure,
                    "wanddicke": wall_thickness,
                    "zulaessige_spannung": allowable_stress
                },
                "ergebnis": {
                    "durchmesser": f"{diameter_optimized.magnitude:.6g} {diameter_optimized.units}"
                },
                "formel": "D = (2 × σ_zul × s) / p",
                "si_werte": {
                    "durchmesser_si": f"{d_si:.6g} m",
                    "druck_si": f"{p_si:.6g} Pa",
                    "wanddicke_si": f"{s_si:.6g} m",
                    "zulaessige_spannung_si": f"{sigma_si:.6g} Pa"
                }
            }
            
        elif allowable_stress is None:
            # Berechne zulässige Spannung: σ_zul = (p × D) / (2 × s)
            p_si = params['pressure']['si_value']       # Pa
            d_si = params['diameter']['si_value']       # m
            s_si = params['wall_thickness']['si_value'] # m
            
            if p_si <= 0 or d_si <= 0 or s_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            sigma_si = (p_si * d_si) / (2 * s_si)  # Pa
            
            # Optimiere Ausgabe-Einheit
            stress_quantity = sigma_si * ureg.pascal
            
            # Verwende eine sinnvolle Referenz-Einheit für Spannung
            if 'MPa' in str(params.get('pressure', {}).get('original_unit', '')):
                ref_unit = 'MPa'
            elif 'bar' in str(params.get('pressure', {}).get('original_unit', '')):
                ref_unit = 'MPa'  # Für Spannungen ist MPa üblicher als N/mm²
            else:
                ref_unit = 'MPa'  # Standard-Referenz
            
            stress_optimized = optimize_output_unit(stress_quantity, ref_unit)
            
            return {
                "gegebene_werte": {
                    "druck": pressure,
                    "durchmesser": diameter,
                    "wanddicke": wall_thickness
                },
                "ergebnis": {
                    "zulaessige_spannung": f"{stress_optimized.magnitude:.6g} {stress_optimized.units}"
                },
                "formel": "σ_zul = (p × D) / (2 × s)",
                "si_werte": {
                    "zulaessige_spannung_si": f"{sigma_si:.6g} Pa",
                    "druck_si": f"{p_si:.6g} Pa",
                    "durchmesser_si": f"{d_si:.6g} m",
                    "wanddicke_si": f"{s_si:.6g} m"
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
    "name": "solve_kesselformel",
    "short_description": "Kesselformel - Druckbehälter-Berechnungen für zulässige Drücke",
    "description": """Löst die Kesselformel nach verschiedenen Variablen auf. Lösbare Variablen: pressure, wall_thickness, diameter, allowable_stress

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "10 bar", "5 mm", "200 MPa")

Kesselformel: p = (2 × σ_zul × s) / D

Parameter:
- pressure: Innendruck mit Druckeinheit (z.B. "10 bar", "1.5 MPa", "150 psi")
- wall_thickness: Wanddicke mit Längeneinheit (z.B. "5 mm", "0.5 cm", "0.2 inch")
- diameter: Innendurchmesser mit Längeneinheit (z.B. "500 mm", "1 m", "20 inch") 
- allowable_stress: Zulässige Spannung mit Spannungseinheit (z.B. "200 MPa", "20000 N/cm²")

Anwendungsbereich: Druckbehälter-Auslegung, Kesselberechnung, Rohrleitungstechnik
Einschränkungen: Gilt für dünnwandige Behälter (s/D < 0.1), alle Werte müssen positiv sein""",
    "tags": ["mechanik"],
    "function": solve_kesselformel,
    "examples": [
        {
            "description": "Berechne zulässigen Druck",
            "call": 'solve_kesselformel(wall_thickness="5 mm", diameter="500 mm", allowable_stress="200 MPa")',
            "result": "Zulässiger Druck in optimierter Einheit"
        },
        {
            "description": "Berechne erforderliche Wanddicke",
            "call": 'solve_kesselformel(pressure="10 bar", diameter="1 m", allowable_stress="160 MPa")',
            "result": "Erforderliche Wanddicke in optimierter Einheit"
        },
        {
            "description": "Berechne maximal zulässigen Durchmesser",
            "call": 'solve_kesselformel(pressure="15 bar", wall_thickness="8 mm", allowable_stress="200 MPa")',
            "result": "Maximal zulässiger Durchmesser in optimierter Einheit"
        }
    ]
}

if __name__ == "__main__":
    # Test-Beispiele für Kesselformel
    print("=== Kesselformel Tests ===")
    
    # Test 1: Berechne Druck
    result1 = solve_kesselformel(wall_thickness="5 mm", diameter="500 mm", allowable_stress="200 MPa")
    print(f"Test 1 - Druckberechnung: {result1}")
    
    # Test 2: Berechne Wanddicke
    result2 = solve_kesselformel(pressure="10 bar", diameter="1 m", allowable_stress="160 MPa")
    print(f"Test 2 - Wanddickenberechnung: {result2}")
    
    # Test 3: Berechne Durchmesser 
    result3 = solve_kesselformel(pressure="15 bar", wall_thickness="8 mm", allowable_stress="200 MPa")
    print(f"Test 3 - Durchmesserberechnung: {result3}")
    
    # Test 4: Berechne zulässige Spannung
    result4 = solve_kesselformel(pressure="10 bar", diameter="500 mm", wall_thickness="5 mm")
    print(f"Test 4 - Spannungsberechnung: {result4}")
    
    # Test 5: Fehler - keine Einheit
    result5 = solve_kesselformel(pressure="10", diameter="500 mm", wall_thickness="5 mm")
    print(f"Test 5 - Einheitenfehler: {result5}") 