#!/usr/bin/env python3
"""
Kegel-Volumen - Berechnet Volumen, Radius oder Höhe eines Kegels

Berechnet Kegel-Volumen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel V = (1/3) × π × r² × h nach verschiedenen Variablen auf.
Lösbare Variablen: volumen, radius, hoehe

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke

Kegel: Spitze Pyramide mit kreisförmiger Grundfläche - V = (1/3) × π × r² × h
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "kegel_volumen"
TOOL_TAGS = ["elementar"]
TOOL_SHORT_DESCRIPTION = "Kegel-Volumen - Berechnet Volumen, Radius oder Höhe"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic"  # Alle Berechnungen sind analytisch lösbar

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
FUNCTION_PARAM_1_NAME = "volumen"
FUNCTION_PARAM_1_DESC = "Volumen des Kegels mit Volumeneinheit (z.B. '261.8 cm³', '0.0002618 m³', '261800 mm³') oder 'target' für Berechnung"
FUNCTION_PARAM_1_EXAMPLE = "261.8 cm³"

FUNCTION_PARAM_2_NAME = "radius"
FUNCTION_PARAM_2_DESC = "Radius der Grundfläche mit Längeneinheit (z.B. '5 cm', '50 mm', '0.05 m') oder 'target' für Berechnung"
FUNCTION_PARAM_2_EXAMPLE = "5 cm"

FUNCTION_PARAM_3_NAME = "hoehe"
FUNCTION_PARAM_3_DESC = "Höhe des Kegels mit Längeneinheit (z.B. '10 cm', '100 mm', '0.1 m') oder 'target' für Berechnung"
FUNCTION_PARAM_3_EXAMPLE = "10 cm"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst die Kegel-Volumen-Formel V = (1/3) × π × r² × h nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel V = (1/3)×π×r²×h)
{FUNCTION_PARAM_2_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel r = √((3V)/(π×h)))
{FUNCTION_PARAM_3_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel h = (3V)/(π×r²))

Kegel-Formel: V = (1/3) × π × r² × h

Anwendungsbereich: Geometrie, Silos, Trichter, Architektur (Kuppeln)
Einschränkungen: Alle Werte müssen positiv sein
Genauigkeit: Exakte analytische Lösung"""

# Parameter-Definitionen für Metadaten
PARAMETER_VOLUMEN = {
    "type": "string",
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE
}

PARAMETER_RADIUS = {
    "type": "string", 
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE
}

PARAMETER_HOEHE = {
    "type": "string",
    "description": FUNCTION_PARAM_3_DESC,
    "example": FUNCTION_PARAM_3_EXAMPLE
}

# Output-Definition
OUTPUT_RESULT = {
    "type": "Quantity",
    "description": "Berechnungsergebnis mit Einheit",
    "unit": "abhängig vom Parameter"
}

# Beispiele
TOOL_EXAMPLES = [
    {
        "title": "Berechne Volumen bei gegebenem Radius und Höhe",
        "input": {f"{FUNCTION_PARAM_1_NAME}": "target", f"{FUNCTION_PARAM_2_NAME}": FUNCTION_PARAM_2_EXAMPLE, f"{FUNCTION_PARAM_3_NAME}": FUNCTION_PARAM_3_EXAMPLE},
        "output": "Volumen in optimierter Einheit"
    },
    {
        "title": "Berechne Radius bei gegebenem Volumen und Höhe", 
        "input": {f"{FUNCTION_PARAM_1_NAME}": FUNCTION_PARAM_1_EXAMPLE, f"{FUNCTION_PARAM_2_NAME}": "target", f"{FUNCTION_PARAM_3_NAME}": FUNCTION_PARAM_3_EXAMPLE},
        "output": "Radius in optimierter Einheit"
    },
    {
        "title": "Berechne Höhe bei gegebenem Volumen und Radius",
        "input": {f"{FUNCTION_PARAM_1_NAME}": FUNCTION_PARAM_1_EXAMPLE, f"{FUNCTION_PARAM_2_NAME}": FUNCTION_PARAM_2_EXAMPLE, f"{FUNCTION_PARAM_3_NAME}": "target"},
        "output": "Höhe in optimierter Einheit"
    }
]

# Mathematische Grundlagen
MATHEMATICAL_FOUNDATION = "Kegel-Volumen: V = (1/3) × π × r² × h, wobei r der Grundradius und h die Höhe ist"

# Annahmen
TOOL_ASSUMPTIONS = [
    "Kegel mit kreisförmiger Grundfläche",
    "Alle Eingabewerte sind positiv",
    "Spitze liegt senkrecht über dem Mittelpunkt der Grundfläche"
]

# Einschränkungen
TOOL_LIMITATIONS = [
    "Nur für positive Werte gültig",
    "Nur für gerade Kreiskegel",
    "Nicht für abgestumpfte Kegel oder elliptische Kegel"
]

# Referenz-Einheiten
REFERENCE_UNITS = {
    f"{FUNCTION_PARAM_1_NAME}": "m³",
    f"{FUNCTION_PARAM_2_NAME}": "m",
    f"{FUNCTION_PARAM_3_NAME}": "m"
}

# ================================================================================================
# 🔧 IMPORTS & DEPENDENCIES 🔧
# ================================================================================================

from typing import Dict, Optional, Annotated, List, Any, Union
import sys
import os
import math

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from engineering_mcp.units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

# ================================================================================================
# 🎯 TOOL FUNCTIONS 🎯
# ================================================================================================

def solve_kegel(
    volumen: Annotated[Union[str, List[str]], FUNCTION_PARAM_1_DESC],
    radius: Annotated[Union[str, List[str]], FUNCTION_PARAM_2_DESC],
    hoehe: Annotated[Union[str, List[str]], FUNCTION_PARAM_3_DESC]
) -> Union[Dict, List[Dict]]:
    """
    📊 ANALYTICAL SOLUTION
    
    Löst die Kegel-Volumen-Formel V = (1/3) × π × r² × h nach verschiedenen Variablen auf.
    
    Unterstützt Batch-Verarbeitung: Wenn Listen als Parameter übergeben werden,
    müssen ALLE Parameter Listen gleicher Länge sein. Jeder Index repräsentiert
    einen vollständigen Parametersatz.
    """
    try:
        # Erstelle Parameter-Dictionary
        params_dict = {
            'volumen': volumen,
            'radius': radius,
            'hoehe': hoehe
        }
        
        # Validiere Batch-Format
        list_params = [k for k, v in params_dict.items() if isinstance(v, list)]
        if list_params:
            # Einige Parameter sind Listen - prüfe ob ALLE Listen sind
            non_list_params = [k for k, v in params_dict.items() if not isinstance(v, list)]
            if non_list_params:
                return {
                    "error": "Batch-Modus erfordert, dass ALLE Parameter Listen sind",
                    "list_params": list_params,
                    "non_list_params": non_list_params,
                    "hinweis": "Entweder alle Parameter als einzelne Werte ODER alle als Listen gleicher Länge"
                }
            
            # Prüfe ob alle Listen gleiche Länge haben
            lengths = {k: len(v) for k, v in params_dict.items()}
            unique_lengths = set(lengths.values())
            if len(unique_lengths) > 1:
                return {
                    "error": "Alle Parameter-Listen müssen die gleiche Länge haben",
                    "lengths": lengths,
                    "hinweis": "Jeder Index repräsentiert einen vollständigen Parametersatz"
                }
        
        # Erstelle alle Kombinationen für Batch-Verarbeitung
        from engineering_mcp.batch_utils import prepare_batch_combinations
        combinations = prepare_batch_combinations(params_dict)
        
        # Wenn nur eine Kombination, führe normale Berechnung durch
        if len(combinations) == 1:
            return _solve_single_kegel(
                combinations[0]['volumen'],
                combinations[0]['radius'],
                combinations[0]['hoehe']
            )
        
        # Batch-Verarbeitung: Berechne alle Kombinationen
        results = []
        for i, combo in enumerate(combinations):
            try:
                result = _solve_single_kegel(
                    combo['volumen'],
                    combo['radius'],
                    combo['hoehe']
                )
                # Füge Batch-Index hinzu
                result['batch_index'] = i
                result['input_combination'] = combo
                results.append(result)
            except Exception as e:
                # Bei Fehler in einer Berechnung, füge Fehler-Ergebnis hinzu
                results.append({
                    'batch_index': i,
                    'input_combination': combo,
                    'error': str(e),
                    'type': type(e).__name__
                })
        
        return {
            "batch_mode": True,
            "total_calculations": len(combinations),
            "successful": sum(1 for r in results if 'error' not in r),
            "failed": sum(1 for r in results if 'error' in r),
            "results": results
        }
        
    except Exception as e:
        return {
            "error": f"Fehler in solve_kegel: {str(e)}",
            "type": type(e).__name__
        }

def _solve_single_kegel(
    volumen: str,
    radius: str,
    hoehe: str
) -> Dict:
    """
    Interne Funktion für einzelne Berechnungen.
    Enthält die ursprüngliche Berechnungslogik.
    """
    try:
        # Identifiziere target Parameter
        target_params = []
        given_params = []
        
        params_info = {
            f'{FUNCTION_PARAM_1_NAME}': volumen,
            f'{FUNCTION_PARAM_2_NAME}': radius,
            f'{FUNCTION_PARAM_3_NAME}': hoehe
        }
        
        for param_name, param_value in params_info.items():
            if param_value.lower().strip() == "target":
                target_params.append(param_name)
            else:
                given_params.append(param_name)
        
        # Validierung: Genau ein target Parameter
        if len(target_params) != 1:
            return {
                "error": f"Genau ein Parameter muss 'target' sein (gefunden: {len(target_params)})",
                "target_params": target_params,
                "example": f"solve_kegel({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 2:
            return {
                "error": f"Genau 2 Parameter müssen Werte mit Einheiten haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": f"solve_kegel({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')"
            }
        
        target_param = target_params[0]
        
        # Erstelle kwargs für Validierung (nur gegebene Parameter)
        validation_kwargs = {}
        for param_name in given_params:
            validation_kwargs[param_name] = params_info[param_name]
        
        # Validiere Einheiten und konvertiere zu SI
        try:
            params = validate_inputs_have_units(**validation_kwargs)
        except UnitsError as e:
            return {
                "error": "Einheiten-Fehler",
                "message": str(e),
                "hinweis": "Alle Nicht-Target-Parameter müssen mit Einheiten angegeben werden",
                "beispiele": [
                    f"{FUNCTION_PARAM_1_NAME}='{FUNCTION_PARAM_1_EXAMPLE}'",
                    f"{FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}'",
                    f"{FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}'"
                ]
            }
        
        # Berechnung basierend auf target Parameter
        if target_param == FUNCTION_PARAM_1_NAME:
            # Berechne Volumen: V = (1/3) × π × r² × h
            r_si = params[FUNCTION_PARAM_2_NAME]['si_value']  # in Metern
            h_si = params[FUNCTION_PARAM_3_NAME]['si_value']  # in Metern
            
            if r_si <= 0 or h_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            v_si = (1/3) * math.pi * r_si**2 * h_si  # in m³
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params[FUNCTION_PARAM_2_NAME]['original_unit'] if r_si < h_si else params[FUNCTION_PARAM_3_NAME]['original_unit']
            volume_quantity = v_si * ureg.meter**3
            volume_optimized = optimize_output_unit(volume_quantity, ref_unit)
            
            return {
                "target_parameter": FUNCTION_PARAM_1_NAME,
                "gegebene_werte": {
                    FUNCTION_PARAM_2_NAME: radius,
                    FUNCTION_PARAM_3_NAME: hoehe
                },
                "ergebnis": {
                    FUNCTION_PARAM_1_NAME: f"{volume_optimized.magnitude:.6g} {volume_optimized.units}"
                },
                "formel": "V = (1/3) × π × r² × h",
                "berechnungsart": "📊 ANALYTICAL SOLUTION",
                "si_werte": {
                    f"{FUNCTION_PARAM_1_NAME}_si": f"{v_si:.6g} m³",
                    f"{FUNCTION_PARAM_2_NAME}_si": f"{r_si:.6g} m",
                    f"{FUNCTION_PARAM_3_NAME}_si": f"{h_si:.6g} m"
                }
            }
        
        elif target_param == FUNCTION_PARAM_2_NAME:
            # Berechne Radius: r = √((3 × V) / (π × h))
            v_si = params[FUNCTION_PARAM_1_NAME]['si_value']  # in m³
            h_si = params[FUNCTION_PARAM_3_NAME]['si_value']  # in Metern
            
            if v_si <= 0 or h_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            r_si = math.sqrt((3 * v_si) / (math.pi * h_si))  # in Metern
            
            # Optimiere Ausgabe-Einheit
            radius_quantity = r_si * ureg.meter
            radius_optimized = optimize_output_unit(radius_quantity, params[FUNCTION_PARAM_3_NAME]['original_unit'])
            
            return {
                "target_parameter": FUNCTION_PARAM_2_NAME,
                "gegebene_werte": {
                    FUNCTION_PARAM_1_NAME: volumen,
                    FUNCTION_PARAM_3_NAME: hoehe
                },
                "ergebnis": {
                    FUNCTION_PARAM_2_NAME: f"{radius_optimized.magnitude:.6g} {radius_optimized.units}"
                },
                "formel": "r = √((3 × V) / (π × h))",
                "berechnungsart": "📊 ANALYTICAL SOLUTION",
                "si_werte": {
                    f"{FUNCTION_PARAM_1_NAME}_si": f"{v_si:.6g} m³",
                    f"{FUNCTION_PARAM_2_NAME}_si": f"{r_si:.6g} m",
                    f"{FUNCTION_PARAM_3_NAME}_si": f"{h_si:.6g} m"
                }
            }
        
        elif target_param == FUNCTION_PARAM_3_NAME:
            # Berechne Höhe: h = (3 × V) / (π × r²)
            v_si = params[FUNCTION_PARAM_1_NAME]['si_value']  # in m³
            r_si = params[FUNCTION_PARAM_2_NAME]['si_value']  # in Metern
            
            if v_si <= 0 or r_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            h_si = (3 * v_si) / (math.pi * r_si**2)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            height_quantity = h_si * ureg.meter
            height_optimized = optimize_output_unit(height_quantity, params[FUNCTION_PARAM_2_NAME]['original_unit'])
            
            return {
                "target_parameter": FUNCTION_PARAM_3_NAME,
                "gegebene_werte": {
                    FUNCTION_PARAM_1_NAME: volumen,
                    FUNCTION_PARAM_2_NAME: radius
                },
                "ergebnis": {
                    FUNCTION_PARAM_3_NAME: f"{height_optimized.magnitude:.6g} {height_optimized.units}"
                },
                "formel": "h = (3 × V) / (π × r²)",
                "berechnungsart": "📊 ANALYTICAL SOLUTION",
                "si_werte": {
                    f"{FUNCTION_PARAM_1_NAME}_si": f"{v_si:.6g} m³",
                    f"{FUNCTION_PARAM_2_NAME}_si": f"{r_si:.6g} m",
                    f"{FUNCTION_PARAM_3_NAME}_si": f"{h_si:.6g} m"
                }
            }
        
        else:
            return {"error": f"Unbekannter target Parameter: {target_param}"}
    
    except Exception as e:
        return {
            "error": "Unerwarteter Fehler in solve_kegel",
            "message": str(e),
            "funktion": "solve_kegel"
        }

# ================================================================================================
# 🎯 METADATA FUNCTIONS 🎯
# ================================================================================================

def get_metadata():
    """Gibt die Metadaten des Tools für Registry-Discovery zurück"""
    return {
        # ✅ Neue Registry-Struktur
        "tool_name": TOOL_NAME,
        "short_description": TOOL_SHORT_DESCRIPTION,
        "description": TOOL_DESCRIPTION,
        "tags": TOOL_TAGS,
        "has_solving": HAS_SOLVING,
        
        # ✅ KRITISCH: Parameters Dictionary für Registry-Discovery
        "parameters": {
            FUNCTION_PARAM_1_NAME: PARAMETER_VOLUMEN,
            FUNCTION_PARAM_2_NAME: PARAMETER_RADIUS,
            FUNCTION_PARAM_3_NAME: PARAMETER_HOEHE
        },
        
        # ✅ Beispiele im neuen Format
        "examples": TOOL_EXAMPLES,
        
        # ✅ Vollständige Metadaten für erweiterte Nutzung
        "tool_version": TOOL_VERSION,
        "output_result": OUTPUT_RESULT,
        "tool_assumptions": TOOL_ASSUMPTIONS,
        "tool_limitations": TOOL_LIMITATIONS,
        "mathematical_foundation": MATHEMATICAL_FOUNDATION,
        "norm_foundation": "",  # Kein spezifischer Standard
        "reference_units": REFERENCE_UNITS,
        
        # ✅ Backwards Compatibility (falls andere Teile das alte Format erwarten)
        "name": TOOL_NAME,  # Legacy
        "version": TOOL_VERSION,  # Legacy
        "output": OUTPUT_RESULT,  # Legacy
        "assumptions": TOOL_ASSUMPTIONS,  # Legacy
        "limitations": TOOL_LIMITATIONS,  # Legacy
        "tool_tags": TOOL_TAGS,
        "tool_short_description": TOOL_SHORT_DESCRIPTION,
        "parameter_count": len([name for name in globals() if name.startswith('PARAMETER_')]),
        "tool_description": TOOL_DESCRIPTION
    }

# Legacy-Wrapper für Abwärtskompatibilität
def calculate(volumen: str, radius: str, hoehe: str) -> Dict:
    """Legacy-Funktion für Kompatibilität"""
    return solve_kegel(volumen=volumen, radius=radius, hoehe=hoehe)

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Kegel-Tool Tests ===")
    
    # Test 1: Volumen berechnen
    result1 = solve_kegel(volumen="target", radius="5 cm", hoehe="10 cm")
    print(f"Test 1 - Volumen: {result1}")
    
    # Test 2: Radius berechnen
    result2 = solve_kegel(volumen="261.8 cm³", radius="target", hoehe="10 cm")
    print(f"Test 2 - Radius: {result2}")
    
    # Test 3: Höhe berechnen
    result3 = solve_kegel(volumen="261.8 cm³", radius="5 cm", hoehe="target")
    print(f"Test 3 - Höhe: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_kegel(volumen="target", radius="5", hoehe="10 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 