#!/usr/bin/env python3
"""
Zylinder-Volumen - Berechnet Volumen, Radius oder Höhe eines Zylinders

Berechnet Zylinder-Volumen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel V = π × r² × h nach verschiedenen Variablen auf.
Lösbare Variablen: volumen, radius, hoehe

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke

Zylinder: Runde Säule mit konstantem Querschnitt - V = π × r² × h
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "zylinder_volumen"
TOOL_TAGS = ["elementar"]
TOOL_SHORT_DESCRIPTION = "Zylinder-Volumen - Berechnet Volumen, Radius oder Höhe"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic"  # Alle Berechnungen sind analytisch lösbar

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
FUNCTION_PARAM_1_NAME = "volumen"
FUNCTION_PARAM_1_DESC = "Volumen des Zylinders mit Volumeneinheit (z.B. '785.4 cm³', '0.0007854 m³', '785400 mm³') oder 'target' für Berechnung"
FUNCTION_PARAM_1_EXAMPLE = "785.4 cm³"

FUNCTION_PARAM_2_NAME = "radius"
FUNCTION_PARAM_2_DESC = "Radius des Zylinders mit Längeneinheit (z.B. '5 cm', '50 mm', '0.05 m') oder 'target' für Berechnung"
FUNCTION_PARAM_2_EXAMPLE = "5 cm"

FUNCTION_PARAM_3_NAME = "hoehe"
FUNCTION_PARAM_3_DESC = "Höhe des Zylinders mit Längeneinheit (z.B. '10 cm', '100 mm', '0.1 m') oder 'target' für Berechnung"
FUNCTION_PARAM_3_EXAMPLE = "10 cm"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst die Zylinder-Volumen-Formel V = π × r² × h nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel V = π×r²×h)
{FUNCTION_PARAM_2_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel r = √(V/(π×h)))
{FUNCTION_PARAM_3_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel h = V/(π×r²))

Zylinder-Formel: V = π × r² × h

Anwendungsbereich: Behältervolumen, Rohre, Tanks, Maschinenbau
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
MATHEMATICAL_FOUNDATION = "Zylinder-Volumen: V = π × r² × h, wobei r der Radius und h die Höhe ist"

# Annahmen
TOOL_ASSUMPTIONS = [
    "Zylinder mit kreisförmigem Querschnitt",
    "Alle Eingabewerte sind positiv",
    "Konstanter Radius über die gesamte Höhe"
]

# Einschränkungen
TOOL_LIMITATIONS = [
    "Nur für positive Werte gültig",
    "Nur für kreisförmige Zylinder",
    "Nicht für konische oder elliptische Formen"
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
# 🔄 BATCH PROCESSING HELPERS 🔄
# ================================================================================================

def is_batch_input(params: Dict[str, Any]) -> bool:
    """
    Prüft ob die Parameter im Batch-Modus sind.
    Batch-Modus: ALLE Parameter sind Listen gleicher Länge.
    """
    list_params = [k for k, v in params.items() if isinstance(v, list)]
    
    # Wenn keine Listen, kein Batch-Modus
    if not list_params:
        return False
    
    # ALLE Parameter müssen Listen sein
    if len(list_params) != len(params):
        return False
    
    # Alle Listen müssen gleiche Länge haben
    lengths = [len(params[k]) for k in list_params]
    return len(set(lengths)) == 1 and lengths[0] > 0

def prepare_batch_combinations(params: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Erstellt Parametersätze für Batch-Verarbeitung.
    
    NEU: Alle Parameter müssen Listen gleicher Länge sein!
    Jeder Index repräsentiert einen vollständigen Parametersatz.
    """
    # Prüfe ob Batch-Modus
    if not is_batch_input(params):
        # Einzelberechnung - gib Parameter unverändert zurück
        return [params]
    
    # Batch-Modus: Alle Parameter sind Listen
    # Hole die Anzahl der Berechnungen (alle Listen haben gleiche Länge)
    num_calculations = len(next(iter(params.values())))
    
    # Erstelle Parametersätze für jeden Index
    combinations = []
    for i in range(num_calculations):
        combo = {}
        for key, values in params.items():
            combo[key] = values[i]
        combinations.append(combo)
    
    return combinations

# ================================================================================================
# 🎯 TOOL FUNCTIONS 🎯
# ================================================================================================

def solve_zylinder(
    volumen: Annotated[Union[str, List[str]], FUNCTION_PARAM_1_DESC],
    radius: Annotated[Union[str, List[str]], FUNCTION_PARAM_2_DESC],
    hoehe: Annotated[Union[str, List[str]], FUNCTION_PARAM_3_DESC]
) -> Union[Dict, List[Dict]]:
    """
    📊 ANALYTICAL SOLUTION
    
    Löst die Zylinder-Volumen-Formel V = π × r² × h nach verschiedenen Variablen auf.
    
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
        combinations = prepare_batch_combinations(params_dict)
        
        # Wenn nur eine Kombination, führe normale Berechnung durch
        if len(combinations) == 1:
            return _solve_single_zylinder(
                combinations[0]['volumen'],
                combinations[0]['radius'],
                combinations[0]['hoehe']
            )
        
        # Batch-Verarbeitung: Berechne alle Kombinationen
        results = []
        for i, combo in enumerate(combinations):
            try:
                result = _solve_single_zylinder(
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
            "error": f"Fehler in solve_zylinder: {str(e)}",
            "type": type(e).__name__
        }

def _solve_single_zylinder(
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
                "example": f"solve_zylinder({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 2:
            return {
                "error": f"Genau 2 Parameter müssen Werte mit Einheiten haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": f"solve_zylinder({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')"
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
            # Berechne Volumen: V = π × r² × h
            radius_si = params[FUNCTION_PARAM_2_NAME]['si_value']  # in Metern
            height_si = params[FUNCTION_PARAM_3_NAME]['si_value']  # in Metern
            
            if radius_si <= 0 or height_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            volume_si = math.pi * radius_si**2 * height_si  # in m³
            
            # Optimiere Ausgabe-Einheit (nutze kleinere Dimension als Referenz)
            ref_unit = params[FUNCTION_PARAM_2_NAME]['original_unit'] if radius_si < height_si else params[FUNCTION_PARAM_3_NAME]['original_unit']
            volume_quantity = volume_si * ureg.meter**3
            volume_optimized = optimize_volume_unit(volume_quantity, ref_unit)
            
            return {
                "target_parameter": FUNCTION_PARAM_1_NAME,
                "gegebene_werte": {
                    FUNCTION_PARAM_2_NAME: radius,
                    FUNCTION_PARAM_3_NAME: hoehe
                },
                "ergebnis": {
                    FUNCTION_PARAM_1_NAME: f"{volume_optimized.magnitude:.6g} {volume_optimized.units}"
                },
                "formel": "V = π × r² × h",
                "berechnungsart": "📊 ANALYTICAL SOLUTION",
                "si_werte": {
                    f"{FUNCTION_PARAM_1_NAME}_si": f"{volume_si:.6g} m³",
                    f"{FUNCTION_PARAM_2_NAME}_si": f"{radius_si:.6g} m",
                    f"{FUNCTION_PARAM_3_NAME}_si": f"{height_si:.6g} m"
                }
            }
        
        elif target_param == FUNCTION_PARAM_2_NAME:
            # Berechne Radius: r = √(V / (π × h))
            volume_si = params[FUNCTION_PARAM_1_NAME]['si_value']  # in m³
            height_si = params[FUNCTION_PARAM_3_NAME]['si_value']  # in Metern
            
            if volume_si <= 0 or height_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            radius_si = math.sqrt(volume_si / (math.pi * height_si))  # in Metern
            
            # Optimiere Ausgabe-Einheit
            radius_quantity = radius_si * ureg.meter
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
                "formel": "r = √(V / (π × h))",
                "berechnungsart": "📊 ANALYTICAL SOLUTION",
                "si_werte": {
                    f"{FUNCTION_PARAM_1_NAME}_si": f"{volume_si:.6g} m³",
                    f"{FUNCTION_PARAM_2_NAME}_si": f"{radius_si:.6g} m",
                    f"{FUNCTION_PARAM_3_NAME}_si": f"{height_si:.6g} m"
                }
            }
        
        elif target_param == FUNCTION_PARAM_3_NAME:
            # Berechne Höhe: h = V / (π × r²)
            volume_si = params[FUNCTION_PARAM_1_NAME]['si_value']  # in m³
            radius_si = params[FUNCTION_PARAM_2_NAME]['si_value']  # in Metern
            
            if volume_si <= 0 or radius_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            height_si = volume_si / (math.pi * radius_si**2)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            height_quantity = height_si * ureg.meter
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
                "formel": "h = V / (π × r²)",
                "berechnungsart": "📊 ANALYTICAL SOLUTION",
                "si_werte": {
                    f"{FUNCTION_PARAM_1_NAME}_si": f"{volume_si:.6g} m³",
                    f"{FUNCTION_PARAM_2_NAME}_si": f"{radius_si:.6g} m",
                    f"{FUNCTION_PARAM_3_NAME}_si": f"{height_si:.6g} m"
                }
            }
        
        else:
            return {"error": f"Unbekannter target Parameter: {target_param}"}
    
    except Exception as e:
        return {
            "error": "Unerwarteter Fehler in solve_zylinder",
            "message": str(e),
            "funktion": "solve_zylinder"
        }

def optimize_volume_unit(si_quantity, reference_unit_str: str):
    """Optimiert die Ausgabe-Einheit für Volumen basierend auf der Referenz-Einheit"""
    try:
        return optimize_output_unit(si_quantity, reference_unit_str)
    except:
        # Standard-Optimierung wenn Referenz-Einheit nicht funktioniert
        return optimize_output_unit(si_quantity, "meter")

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
    return solve_zylinder(volumen=volumen, radius=radius, hoehe=hoehe)

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Zylinder-Tool Tests ===")
    
    # Test 1: Volumen berechnen
    result1 = solve_zylinder(radius="5 cm", hoehe="10 cm")
    print(f"Test 1 - Volumen: {result1}")
    
    # Test 2: Radius berechnen
    result2 = solve_zylinder(volumen="785 cm³", hoehe="10 cm")
    print(f"Test 2 - Radius: {result2}")
    
    # Test 3: Höhe berechnen
    result3 = solve_zylinder(volumen="785 cm³", radius="5 cm")
    print(f"Test 3 - Höhe: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_zylinder(radius="5", hoehe="10 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 