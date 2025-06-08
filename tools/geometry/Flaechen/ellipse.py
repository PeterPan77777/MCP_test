#!/usr/bin/env python3
"""
Ellipse-Fläche - Berechnet Fläche oder Halbachsen

Berechnet Ellipsen-Flächen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel A = π × a × b nach verschiedenen Variablen auf.
Lösbare Variablen: flaeche, halb_achse_a, halb_achse_b

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke

🔄 BATCH-MODUS: Unterstützt Verarbeitung mehrerer Parametersätze gleichzeitig!
Beispiel: halb_achse_a=["5 cm", "7 cm", "9 cm"] statt halb_achse_a="5 cm"

Ellipse: Ovale Form mit zwei Halbachsen - A = π × a × b (große Halbachse × kleine Halbachse × π)
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "ellipse_flaeche"
TOOL_TAGS = ["elementar"]
TOOL_SHORT_DESCRIPTION = "Ellipse-Fläche - Berechnet Fläche oder Halbachsen"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic/numeric"  # Fläche analytisch, Halbachsen numerisch

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
FUNCTION_PARAM_1_NAME = "flaeche"
FUNCTION_PARAM_1_DESC = "Fläche der Ellipse mit Flächeneinheit (z.B. '78.54 cm²', '0.007854 m²', '7854 mm²') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_1_EXAMPLE = "78.54 cm²"

FUNCTION_PARAM_2_NAME = "halb_achse_a"
FUNCTION_PARAM_2_DESC = "Große Halbachse der Ellipse mit Längeneinheit (z.B. '5 cm', '50 mm', '0.05 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_2_EXAMPLE = "5 cm"

FUNCTION_PARAM_3_NAME = "halb_achse_b"
FUNCTION_PARAM_3_DESC = "Kleine Halbachse der Ellipse mit Längeneinheit (z.B. '3 cm', '30 mm', '0.03 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_3_EXAMPLE = "3 cm"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst die Ellipsenformel A = π × a × b nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

🔄 BATCH-MODUS: Unterstützt Listen von Parametern für Massenberechnungen!
⚠️ WICHTIG: Bei Batch-Berechnungen müssen ALLE Parameter Listen gleicher Länge sein!
Jeder Index repräsentiert einen vollständigen Parametersatz.

Beispiel Batch-Aufruf:
solve_ellipse(
    flaeche=['target', '47.12 cm²', 'target'],
    halb_achse_a=['5 cm', '4 cm', '6 cm'],
    halb_achse_b=['3 cm', 'target', '4 cm']
)
Dies berechnet 3 separate Ellipsen mit jeweils einem anderen Target-Parameter.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel A = π × a × b)
{FUNCTION_PARAM_2_NAME}: NUMERISCHE ITERATION (Bisektionsverfahren für a = A / (π × b))
{FUNCTION_PARAM_3_NAME}: NUMERISCHE ITERATION (Bisektionsverfahren für b = A / (π × a))

Ellipsenformel: A = π × a × b

Anwendungsbereich: Geometrie, Maschinenbau (Ovale Öffnungen), Architektur, Flächenberechnungen
Einschränkungen: Alle Werte müssen positiv sein, große Halbachse ≥ kleine Halbachse
Genauigkeit: Analytisch exakt, numerisch 1×10⁻¹⁰ m Toleranz"""

# Parameter-Definitionen für Metadaten
PARAMETER_FLAECHE = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "batch_example": ["target", "47.12 cm²", "target"]  # NEU
}

PARAMETER_HALB_ACHSE_A = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE,
    "batch_example": ["5 cm", "4 cm", "6 cm"]  # NEU
}

PARAMETER_HALB_ACHSE_B = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_3_DESC,
    "example": FUNCTION_PARAM_3_EXAMPLE,
    "batch_example": ["3 cm", "target", "4 cm"]  # NEU
}

# Output-Definition
OUTPUT_RESULT = {
    "type": "Quantity",
    "description": "Berechnungsergebnis mit optimierter Einheit",
    "unit": "abhängig vom Parameter"
}

# Beispiele (verwenden die definierten Parameter-Namen)
TOOL_EXAMPLES = [
    {
        "title": f"Berechne {FUNCTION_PARAM_1_NAME} (analytisch) bei gegebenen {FUNCTION_PARAM_2_NAME} und {FUNCTION_PARAM_3_NAME}",
        "input": {FUNCTION_PARAM_1_NAME: "target", FUNCTION_PARAM_2_NAME: FUNCTION_PARAM_2_EXAMPLE, FUNCTION_PARAM_3_NAME: FUNCTION_PARAM_3_EXAMPLE},
        "output": f"{FUNCTION_PARAM_1_NAME} in optimierter Einheit mit geschlossener Formel"
    },
    {
        "title": f"Batch-Berechnung: Drei vollständige Parametersätze",
        "input": {
            FUNCTION_PARAM_1_NAME: ["target", "47.12 cm²", "target"],
            FUNCTION_PARAM_2_NAME: ["5 cm", "4 cm", "6 cm"],
            FUNCTION_PARAM_3_NAME: ["3 cm", "target", "4 cm"]
        },
        "output": f"Liste von 3 Ergebnissen, jeweils mit unterschiedlichem Target-Parameter"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_2_NAME} (numerisch) bei gegebenen {FUNCTION_PARAM_1_NAME} und {FUNCTION_PARAM_3_NAME}", 
        "input": {FUNCTION_PARAM_1_NAME: "47.12 cm²", FUNCTION_PARAM_2_NAME: "target", FUNCTION_PARAM_3_NAME: FUNCTION_PARAM_3_EXAMPLE},
        "output": f"{FUNCTION_PARAM_2_NAME} in optimierter Einheit mit numerischer Iteration"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_3_NAME} (numerisch) bei gegebenen {FUNCTION_PARAM_1_NAME} und {FUNCTION_PARAM_2_NAME}",
        "input": {FUNCTION_PARAM_1_NAME: "47.12 cm²", FUNCTION_PARAM_2_NAME: FUNCTION_PARAM_2_EXAMPLE, FUNCTION_PARAM_3_NAME: "target"},
        "output": f"{FUNCTION_PARAM_3_NAME} in optimierter Einheit mit numerischer Iteration"
    }
]

# Annahmen
TOOL_ASSUMPTIONS = [
    "Ellipse mit zwei bekannten Halbachsen",
    "Alle Eingabewerte sind positiv",
    "Große Halbachse ≥ kleine Halbachse"
]

# Einschränkungen  
TOOL_LIMITATIONS = [
    "Nur für positive Werte gültig",
    "Große Halbachse muss größer oder gleich der kleinen Halbachse sein",
    "Nicht für Kreise optimiert (verwenden Sie Kreis-Tool)"
]

# Mathematische Grundlagen
MATHEMATICAL_FOUNDATION = "Ellipsenformel: A = π × a × b, wobei a die große und b die kleine Halbachse ist"

# Normengrundlage
NORM_FOUNDATION = ""

# ===== AUTOMATISCH BERECHNET =====
PARAMETER_COUNT = len([name for name in globals() if name.startswith('PARAMETER_')])

# ================================================================================================
# 🔧 IMPORTS & DEPENDENCIES 🔧
# ================================================================================================

from typing import Dict, Annotated, List, Any, Optional, Union
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
    
    Beispiel:
    Input: {
        'flaeche': ['target', '47.12 cm²', 'target'],
        'halb_achse_a': ['5 cm', '4 cm', '6 cm'],
        'halb_achse_b': ['3 cm', 'target', '4 cm']
    }
    Output: [
        {'flaeche': 'target', 'halb_achse_a': '5 cm', 'halb_achse_b': '3 cm'},
        {'flaeche': '47.12 cm²', 'halb_achse_a': '4 cm', 'halb_achse_b': 'target'},
        {'flaeche': 'target', 'halb_achse_a': '6 cm', 'halb_achse_b': '4 cm'}
    ]
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

def solve_semi_axis_numerically(target_value_si, other_axis_si, is_major_axis=True, tolerance=1e-10, max_iterations=100):
    """
    Löst numerisch nach Halbachse auf: A = π × a × b
    - Bei is_major_axis=True: löst nach großer Halbachse a = A / (π × b)
    - Bei is_major_axis=False: löst nach kleiner Halbachse b = A / (π × a)
    """
    def ellipse_area(axis):
        if is_major_axis:
            return math.pi * axis * other_axis_si
        else:
            return math.pi * other_axis_si * axis
    
    # Bisektionsverfahren
    lower = 1e-12  # Sehr kleine positive Zahl
    upper = target_value_si / (math.pi * other_axis_si) * 10  # Groß genug für jede realistische Ellipse
    
    for iteration in range(max_iterations):
        mid = (lower + upper) / 2
        calculated_area = ellipse_area(mid)
        
        if abs(calculated_area - target_value_si) < tolerance:
            return mid, iteration + 1, abs(calculated_area - target_value_si)
        
        if calculated_area < target_value_si:
            lower = mid
        else:
            upper = mid
    
    return mid, max_iterations, abs(ellipse_area(mid) - target_value_si)

def solve_ellipse(
    # ⚠️ Hier die konfigurierten Parameter-Namen und -Beschreibungen verwenden:
    flaeche: Annotated[Union[str, List[str]], FUNCTION_PARAM_1_DESC],  
    halb_achse_a: Annotated[Union[str, List[str]], FUNCTION_PARAM_2_DESC],
    halb_achse_b: Annotated[Union[str, List[str]], FUNCTION_PARAM_3_DESC]
) -> Union[Dict, List[Dict]]:
    """
    Löst die Ellipsenformel A = π × a × b nach verschiedenen Variablen auf.
    
    Unterstützt Batch-Verarbeitung: Wenn Listen als Parameter übergeben werden,
    müssen ALLE Parameter Listen gleicher Länge sein. Jeder Index repräsentiert
    einen vollständigen Parametersatz.
    """
    try:
        # Erstelle Parameter-Dictionary
        params_dict = {
            'flaeche': flaeche,
            'halb_achse_a': halb_achse_a, 
            'halb_achse_b': halb_achse_b
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
            return _solve_single(
                combinations[0]['flaeche'],
                combinations[0]['halb_achse_a'],
                combinations[0]['halb_achse_b']
            )
        
        # Batch-Verarbeitung: Berechne alle Kombinationen
        results = []
        for i, combo in enumerate(combinations):
            try:
                result = _solve_single(
                    combo['flaeche'],
                    combo['halb_achse_a'],
                    combo['halb_achse_b']
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
            "error": f"Fehler in solve_ellipse: {str(e)}",
            "type": type(e).__name__
        }

def _solve_single(
    flaeche: str,
    halb_achse_a: str,
    halb_achse_b: str
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
            'var1': flaeche,
            'var2': halb_achse_a, 
            'var3': halb_achse_b
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
                "example": f"solve_ellipse({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 2:
            return {
                "error": f"Genau 2 Parameter müssen Werte mit Einheiten haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": f"solve_ellipse({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')"
            }
        
        target_param = target_params[0]
        
        # Erstelle kwargs für Validierung (nur gegebene Parameter)
        validation_kwargs = {}
        param_names = {
            'var1': 'flaeche',
            'var2': 'halb_achse_a', 
            'var3': 'halb_achse_b'
        }
        
        for param_name in given_params:
            real_param_name = param_names[param_name]
            validation_kwargs[real_param_name] = params_info[param_name]

        # Validierung der Eingaben
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
        if target_param == 'var1':  # flaeche
            # Berechne Fläche: A = π × a × b
            a_si = params['halb_achse_a']['si_value']
            b_si = params['halb_achse_b']['si_value']
            
            if a_si <= 0 or b_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            flaeche_si = math.pi * a_si * b_si
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['halb_achse_b']['original_unit'] if b_si < a_si else params['halb_achse_a']['original_unit']
            flaeche_quantity = flaeche_si * ureg.meter**2
            flaeche_optimized = optimize_output_unit(flaeche_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "flaeche",
                "gegebene_werte": {
                    "grosse_halbachse": halb_achse_a,
                    "kleine_halbachse": halb_achse_b
                },
                "ergebnis": {
                    "flaeche": f"{flaeche_optimized.magnitude:.6g} {flaeche_optimized.units}"
                },
                "formel": "A = π × a × b",
                "si_werte": {
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "grosse_halbachse_si": f"{a_si:.6g} m",
                    "kleine_halbachse_si": f"{b_si:.6g} m"
                }
            }
            
        elif target_param == 'var2':  # halb_achse_a
            # Berechne große Halbachse numerisch: a = A / (π × b)
            flaeche_si = params['flaeche']['si_value']
            b_si = params['halb_achse_b']['si_value']
            
            if flaeche_si <= 0 or b_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            a_si, iterations, error_estimate = solve_semi_axis_numerically(flaeche_si, b_si, is_major_axis=True)
            
            # Geometrische Validierung: große Halbachse muss >= kleine Halbachse sein
            if a_si < b_si * 0.99:  # 1% Toleranz für numerische Ungenauigkeiten
                return {
                    "error": "Geometrisch inkonsistent: Große Halbachse wäre kleiner als kleine Halbachse",
                    "berechnete_grosse_halbachse": f"{a_si:.6g} m",
                    "kleine_halbachse": f"{b_si:.6g} m",
                    "hinweis": "Überprüfen Sie die Eingabewerte"
                }
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['halb_achse_b']['original_unit']
            a_quantity = a_si * ureg.meter
            a_optimized = optimize_output_unit(a_quantity, ref_unit)
            
            return {
                "🔢 NUMERICAL ITERATION": "Bisektionsverfahren",
                "target_parameter": "halb_achse_a",
                "gegebene_werte": {
                    "flaeche": flaeche,
                    "kleine_halbachse": halb_achse_b
                },
                "ergebnis": {
                    "grosse_halbachse": f"{a_optimized.magnitude:.6g} {a_optimized.units}"
                },
                "formel": "a = A / (π × b)",
                "numerische_details": {
                    "iterationen": iterations,
                    "toleranz": "1×10⁻¹⁰ m",
                    "fehlerabschaetzung": f"{error_estimate:.2e} m²"
                },
                "si_werte": {
                    "grosse_halbachse_si": f"{a_si:.6g} m",
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "kleine_halbachse_si": f"{b_si:.6g} m"
                }
            }
            
        elif target_param == 'var3':  # halb_achse_b
            # Berechne kleine Halbachse numerisch: b = A / (π × a)
            flaeche_si = params['flaeche']['si_value']
            a_si = params['halb_achse_a']['si_value']
            
            if flaeche_si <= 0 or a_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            b_si, iterations, error_estimate = solve_semi_axis_numerically(flaeche_si, a_si, is_major_axis=False)
            
            # Geometrische Validierung: kleine Halbachse muss <= große Halbachse sein
            if b_si > a_si * 1.01:  # 1% Toleranz für numerische Ungenauigkeiten
                return {
                    "error": "Geometrisch inkonsistent: Kleine Halbachse wäre größer als große Halbachse",
                    "berechnete_kleine_halbachse": f"{b_si:.6g} m",
                    "grosse_halbachse": f"{a_si:.6g} m",
                    "hinweis": "Überprüfen Sie die Eingabewerte"
                }
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['halb_achse_a']['original_unit']
            b_quantity = b_si * ureg.meter
            b_optimized = optimize_output_unit(b_quantity, ref_unit)
            
            return {
                "🔢 NUMERICAL ITERATION": "Bisektionsverfahren",
                "target_parameter": "halb_achse_b",
                "gegebene_werte": {
                    "flaeche": flaeche,
                    "grosse_halbachse": halb_achse_a
                },
                "ergebnis": {
                    "kleine_halbachse": f"{b_optimized.magnitude:.6g} {b_optimized.units}"
                },
                "formel": "b = A / (π × a)",
                "numerische_details": {
                    "iterationen": iterations,
                    "toleranz": "1×10⁻¹⁰ m",
                    "fehlerabschaetzung": f"{error_estimate:.2e} m²"
                },
                "si_werte": {
                    "kleine_halbachse_si": f"{b_si:.6g} m",
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "grosse_halbachse_si": f"{a_si:.6g} m"
                }
            }
        
    except UnitsError as e:
        return {"error": f"Einheiten-Fehler: {str(e)}"}
    except Exception as e:
        return {
            "error": f"Fehler in solve_ellipse: {str(e)}",
            "type": type(e).__name__
        }

# ================================================================================================
# 🎯 METADATA FUNCTIONS 🎯
# ================================================================================================

def get_metadata():
    """Gibt die Metadaten des Tools für Registry-Discovery zurück"""
    return {
        # ✅ Neue Registry-Struktur
        "tool_name": TOOL_NAME,
        "short_description": TOOL_SHORT_DESCRIPTION,  # ✅ Neu
        "description": TOOL_DESCRIPTION,  # ✅ Neu
        "tags": TOOL_TAGS,  # ✅ Neu: "tags" statt "tool_tags"
        "has_solving": HAS_SOLVING,
        
        # ✅ KRITISCH: Parameters Dictionary für Registry-Discovery
        "parameters": {
            FUNCTION_PARAM_1_NAME: PARAMETER_FLAECHE,
            FUNCTION_PARAM_2_NAME: PARAMETER_HALB_ACHSE_A,
            FUNCTION_PARAM_3_NAME: PARAMETER_HALB_ACHSE_B,
        },
        
        # ✅ Beispiele im neuen Format
        "examples": TOOL_EXAMPLES,
        
        # ✅ Vollständige Metadaten für erweiterte Nutzung
        "tool_version": TOOL_VERSION,
        "output_result": OUTPUT_RESULT,
        "tool_assumptions": TOOL_ASSUMPTIONS,
        "tool_limitations": TOOL_LIMITATIONS,
        "mathematical_foundation": MATHEMATICAL_FOUNDATION,
        "norm_foundation": NORM_FOUNDATION,
        
        # ✅ Backwards Compatibility (falls andere Teile das alte Format erwarten)
        "tool_tags": TOOL_TAGS,
        "tool_short_description": TOOL_SHORT_DESCRIPTION,
        "parameter_count": len([name for name in globals() if name.startswith('PARAMETER_')]),
        "tool_description": TOOL_DESCRIPTION,
        "parameter_count": PARAMETER_COUNT,
        "parameter_flaeche": PARAMETER_FLAECHE,
        "parameter_halb_achse_a": PARAMETER_HALB_ACHSE_A,
        "parameter_halb_achse_b": PARAMETER_HALB_ACHSE_B
    }

def calculate(flaeche: Union[str, List[str]], halb_achse_a: Union[str, List[str]], halb_achse_b: Union[str, List[str]]) -> Union[Dict, List[Dict]]:
    """Legacy-Funktion für Kompatibilität - unterstützt nun auch Batch-Mode"""
    return solve_ellipse(flaeche, halb_achse_a, halb_achse_b) 