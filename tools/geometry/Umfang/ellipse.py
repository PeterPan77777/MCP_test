#!/usr/bin/env python3
"""
Ellipse-Umfang - Berechnet Umfang oder Halbachsen (Ramanujan-Näherung)

Berechnet Ellipsen-Umfang mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Näherungsformel nach verschiedenen Variablen auf.
Lösbare Variablen: perimeter, semi_major_axis, semi_minor_axis

Ellipse: Ovale Form mit zwei Halbachsen
Ramanujan-Näherung: U ≈ π × [3(a + b) - √((3a + b)(a + 3b))]
"""

# ===== TOOL METADATEN =====
TOOL_NAME = "ellipse_umfang"
TOOL_VERSION = "1.0.0"
TOOL_TAGS = ["elementar"]

TOOL_SHORT_DESCRIPTION = "Ellipse-Umfang - Berechnet Umfang oder Halbachsen (Ramanujan-Näherung)"

TOOL_DESCRIPTION = """Löst die Ellipsen-Umfang-Näherung nach Ramanujan nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

🔬 BERECHNUNGSARTEN:
📊 perimeter: ANALYTISCHE LÖSUNG (geschlossene Ramanujan-Formel)
🔢 semi_major_axis: NUMERISCHE ITERATION (Bisection-Methode mit Fehlerabschätzung)
🔢 semi_minor_axis: NUMERISCHE ITERATION (Bisection-Methode mit Fehlerabschätzung)

Ramanujan-Näherung: U ≈ π × (a+b) × [1 + 3h/(10+√(4-3h))]

Anwendungsbereich: Geometrie, Maschinenbau (ovale Bahnen), Architektur, Astronomie
Einschränkungen: Große Halbachse ≥ kleine Halbachse > 0
Genauigkeit: Ramanujan-Fehler < 5×10⁻⁵, numerische Toleranz 1×10⁻¹⁰"""

# Parameter-Definitionen
PARAMETER_PERIMETER = {
    "type": "string | array",
    "description": "Umfang der Ellipse mit Längeneinheit (z.B. '31.42 cm', '314.2 mm', '0.3142 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen",
    "example": "31.42 cm",
    "batch_example": ["target", "40 cm", "target"]
}

PARAMETER_SEMI_MAJOR_AXIS = {
    "type": "string | array", 
    "description": "Große Halbachse der Ellipse mit Längeneinheit (z.B. '5 cm', '50 mm', '0.05 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen",
    "example": "5 cm",
    "batch_example": ["6 cm", "target", "8 cm"]
}

PARAMETER_SEMI_MINOR_AXIS = {
    "type": "string | array",
    "description": "Kleine Halbachse der Ellipse mit Längeneinheit (z.B. '3 cm', '30 mm', '0.03 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen",
    "example": "3 cm",
    "batch_example": ["4 cm", "5 cm", "target"]
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
        "title": "📊 Berechne Umfang (analytisch) bei gegebenen Halbachsen",
        "input": {"perimeter": "target", "semi_major_axis": "5 cm", "semi_minor_axis": "3 cm"},
        "output": "Umfang mit geschlossener Ramanujan-Formel"
    },
    {
        "title": "🔢 Berechne große Halbachse (numerisch) bei gegebenem Umfang",
        "input": {"perimeter": "31.42 cm", "semi_major_axis": "target", "semi_minor_axis": "3 cm"},
        "output": "Große Halbachse mit numerischer Iteration und Fehlerabschätzung"
    },
    {
        "title": "🔢 Berechne kleine Halbachse (numerisch) bei gegebenem Umfang",
        "input": {"perimeter": "31.42 cm", "semi_major_axis": "5 cm", "semi_minor_axis": "target"},
        "output": "Kleine Halbachse mit numerischer Iteration und Fehlerabschätzung"
    }
]

# Mathematische Grundlagen
MATHEMATICAL_FOUNDATION = "Ramanujan-Näherung: U ≈ π × (a+b) × [1 + 3h/(10+√(4-3h))], wobei h = ((a-b)/(a+b))²"

# Annahmen
TOOL_ASSUMPTIONS = [
    "Ellipse mit zwei bekannten Halbachsen",
    "Alle Eingabewerte sind positiv",
    "Große Halbachse ≥ kleine Halbachse",
    "Ramanujan-Näherung für Ellipsen-Umfang"
]

# Einschränkungen
TOOL_LIMITATIONS = [
    "Nur für positive Werte gültig",
    "Große Halbachse muss größer oder gleich der kleinen Halbachse sein",
    "Numerische Konvergenz kann bei extremen Verhältnissen langsam sein",
    "Ramanujan-Näherung hat einen maximalen Fehler von 5×10⁻⁵"
]

# Solving-Typ
HAS_SOLVING = "symbolic/numeric"  # ⚡ GEMISCHTE BERECHNUNGSARTEN!

# Target-Parameter-Info für symbolische/numerische Methoden
TARGET_PARAMETERS_INFO = {
    "perimeter": {
        "method": "symbolic", 
        "description": "Analytisch lösbar durch geschlossene Ramanujan-Näherungsformel",
        "accuracy": "Sehr hoch (Fehler < 5×10⁻⁵)"
    },
    "semi_major_axis": {
        "method": "numeric", 
        "description": "Numerisch lösbar durch Bisection-Methode mit Umfang-Zielfunktion",
        "accuracy": "Toleranz 1×10⁻¹⁰, mit Fehlerabschätzung und Verifikation"
    },
    "semi_minor_axis": {
        "method": "numeric", 
        "description": "Numerisch lösbar durch Bisection-Methode mit Umfang-Zielfunktion",
        "accuracy": "Toleranz 1×10⁻¹⁰, mit Fehlerabschätzung und Verifikation"
    }
}

# Referenz-Einheiten
REFERENCE_UNITS = {
    "perimeter": "m",
    "semi_major_axis": "m", 
    "semi_minor_axis": "m"
}

# ===== IMPORTS =====
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

def ramanujan_perimeter(a: float, b: float) -> float:
    """
    Berechnet Ellipsen-Umfang nach Ramanujan-Näherung.
    
    Args:
        a: Große Halbachse (in SI-Einheiten)
        b: Kleine Halbachse (in SI-Einheiten)
        
    Returns:
        float: Umfang in SI-Einheiten
    """
    # Stelle sicher, dass a >= b
    if b > a:
        a, b = b, a
    
    h = ((a - b) / (a + b))**2
    return math.pi * (a + b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))

def solve_semi_axis_numerically(target_perimeter: float, known_axis: float, solve_for_major: bool, 
                               tolerance: float = 1e-10, max_iterations: int = 100) -> Dict:
    """
    Löst numerisch nach einer Halbachse bei gegebenem Umfang und der anderen Halbachse.
    
    ⚡ NUMERISCHE ITERATION: Verwendet Bisection-Methode für robuste Konvergenz
    
    Args:
        target_perimeter: Ziel-Umfang (SI)
        known_axis: Bekannte Halbachse (SI)
        solve_for_major: True wenn große Halbachse gesucht, False für kleine
        tolerance: Konvergenz-Toleranz
        max_iterations: Maximale Iterationen
        
    Returns:
        Dict: Ergebnis mit numerischen Details
    """
    
    # Definiere Zielfunktion
    def objective(unknown_axis):
        if solve_for_major:
            # Unbekannte ist große Halbachse
            a, b = unknown_axis, known_axis
        else:
            # Unbekannte ist kleine Halbachse  
            a, b = known_axis, unknown_axis
        
        # Validierung: a >= b für Ellipse
        if a < b:
            return float('inf')  # Ungültige Konfiguration
            
        calculated_perimeter = ramanujan_perimeter(a, b)
        return calculated_perimeter - target_perimeter
    
    # Bestimme Suchbereich für Bisection
    if solve_for_major:
        # Große Halbachse muss >= kleine Halbachse sein
        lower = known_axis
        # Obere Grenze: Sehr große Halbachse (konservativ)
        upper = target_perimeter / math.pi  # Grober Schätzwert
    else:
        # Kleine Halbachse: von 0 bis bekannte große Halbachse
        lower = 1e-12  # Sehr klein, aber nicht null
        upper = known_axis
    
    # Prüfe ob Lösung im Intervall existiert
    f_lower = objective(lower)
    f_upper = objective(upper)
    
    if f_lower * f_upper > 0:
        # Erweitere Suchbereich falls nötig
        if solve_for_major:
            upper = 2 * target_perimeter / math.pi
            f_upper = objective(upper)
        else:
            # Für kleine Halbachse: verwende kleineren Startwert
            lower = 1e-15
            f_lower = objective(lower)
    
    # Bisection-Algorithmus
    iteration = 0
    error_estimate = float('inf')
    
    while iteration < max_iterations and abs(upper - lower) > tolerance:
        mid = (lower + upper) / 2
        f_mid = objective(mid)
        
        if abs(f_mid) < tolerance:
            error_estimate = abs(f_mid)
            break
            
        if f_lower * f_mid < 0:
            upper = mid
            f_upper = f_mid
        else:
            lower = mid
            f_lower = f_mid
            
        iteration += 1
        error_estimate = abs(upper - lower)
    
    result_axis = (lower + upper) / 2
    final_error = abs(objective(result_axis))
    
    return {
        "result": result_axis,
        "iterations": iteration,
        "error_estimate": error_estimate,
        "final_residual": final_error,
        "converged": iteration < max_iterations,
        "tolerance_achieved": final_error < tolerance
    }

def solve_ellipse_umfang(
    perimeter: Annotated[Union[str, List[str]], "Umfang der Ellipse mit Längeneinheit (z.B. '25.13 cm', '251.3 mm', '0.2513 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"],
    semi_major_axis: Annotated[Union[str, List[str]], "Große Halbachse der Ellipse mit Längeneinheit (z.B. '5 cm', '50 mm', '0.05 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"],
    semi_minor_axis: Annotated[Union[str, List[str]], "Kleine Halbachse der Ellipse mit Längeneinheit (z.B. '3 cm', '30 mm', '0.03 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"]
) -> Union[Dict, List[Dict]]:
    try:
        # Erstelle Parameter-Dictionary
        params_dict = {
            'perimeter': perimeter,
            'semi_major_axis': semi_major_axis,
            'semi_minor_axis': semi_minor_axis
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
                combinations[0]['perimeter'],
                combinations[0]['semi_major_axis'],
                combinations[0]['semi_minor_axis']
            )
        
        # Batch-Verarbeitung: Berechne alle Kombinationen
        results = []
        for i, combo in enumerate(combinations):
            try:
                result = _solve_single(
                    combo['perimeter'],
                    combo['semi_major_axis'],
                    combo['semi_minor_axis']
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
            "error": f"Fehler in solve_ellipse_umfang: {str(e)}",
            "type": type(e).__name__
        }

def _solve_single(
    perimeter: str,
    semi_major_axis: str,
    semi_minor_axis: str
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
            'perimeter': perimeter,
            'semi_major_axis': semi_major_axis,
            'semi_minor_axis': semi_minor_axis
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
                "example": "solve_ellipse_umfang(perimeter='target', semi_major_axis='5 cm', semi_minor_axis='3 cm')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 2:
            return {
                "error": f"Genau 2 Parameter müssen Werte mit Einheiten haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": "solve_ellipse_umfang(perimeter='target', semi_major_axis='5 cm', semi_minor_axis='3 cm')"
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
                    "perimeter='25.13 cm'",
                    "semi_major_axis='5 cm'",
                    "semi_minor_axis='3 cm'"
                ]
            }
        
        # ===== UMFANG BERECHNEN (ANALYTISCH) =====
        if target_param == 'perimeter':
            # Berechne Umfang: Ramanujan-Näherung (geschlossene Formel)
            a_si = params['semi_major_axis']['si_value']  # in Metern
            b_si = params['semi_minor_axis']['si_value']  # in Metern
            
            if a_si <= 0 or b_si <= 0:
                return {"error": "Alle Halbachsen müssen positiv sein"}
            
            # Stelle sicher, dass a >= b (große Halbachse >= kleine Halbachse)
            if b_si > a_si:
                a_si, b_si = b_si, a_si
                major_is_first = False
            else:
                major_is_first = True
            
            perimeter_si = ramanujan_perimeter(a_si, b_si)
            
            # Optimiere Ausgabe-Einheit (nutze größere Halbachse als Referenz)
            ref_unit = params['semi_major_axis']['original_unit'] if major_is_first else params['semi_minor_axis']['original_unit']
            perimeter_quantity = perimeter_si * ureg.meter
            perimeter_optimized = optimize_output_unit(perimeter_quantity, ref_unit)
            
            return {
                "target_parameter": "perimeter",
                "gegebene_werte": {
                    "grosse_halbachse": semi_major_axis if major_is_first else semi_minor_axis,
                    "kleine_halbachse": semi_minor_axis if major_is_first else semi_major_axis
                },
                "ergebnis": {
                    "umfang": f"{perimeter_optimized.magnitude:.6g} {perimeter_optimized.units}"
                },
                "formel": "U ≈ π × (a+b) × [1 + 3h/(10+√(4-3h))] (Ramanujan)",
                "hinweis": "h = ((a-b)/(a+b))², a = große Halbachse, b = kleine Halbachse",
                "berechnungsart": "📊 ANALYTISCHE LÖSUNG (geschlossene Formel)",
                "si_werte": {
                    "umfang_si": f"{perimeter_si:.6g} m",
                    "grosse_halbachse_si": f"{a_si:.6g} m",
                    "kleine_halbachse_si": f"{b_si:.6g} m"
                }
            }
            
        # ===== GROSSE HALBACHSE BERECHNEN (NUMERISCH) =====
        elif target_param == 'semi_major_axis':
            perimeter_si = params['perimeter']['si_value']
            b_si = params['semi_minor_axis']['si_value']  # Kleine Halbachse
            
            if perimeter_si <= 0 or b_si <= 0:
                return {"error": "Umfang und kleine Halbachse müssen positiv sein"}
            
            # Numerische Lösung für große Halbachse
            numerical_result = solve_semi_axis_numerically(
                target_perimeter=perimeter_si,
                known_axis=b_si,
                solve_for_major=True
            )
            
            if not numerical_result["converged"]:
                return {
                    "error": "Numerische Iteration konvergierte nicht",
                    "details": numerical_result,
                    "hinweis": "Versuchen Sie andere Eingabewerte oder erhöhen Sie die Toleranz"
                }
            
            a_si = numerical_result["result"]
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['perimeter']['original_unit'] 
            a_quantity = a_si * ureg.meter
            a_optimized = optimize_output_unit(a_quantity, ref_unit)
            
            # Verifikation: Berechne Umfang zurück
            verification_perimeter = ramanujan_perimeter(a_si, b_si)
            relative_error = abs(verification_perimeter - perimeter_si) / perimeter_si * 100
            
            return {
                "target_parameter": "semi_major_axis",
                "gegebene_werte": {
                    "umfang": perimeter,
                    "kleine_halbachse": semi_minor_axis
                },
                "ergebnis": {
                    "grosse_halbachse": f"{a_optimized.magnitude:.6g} {a_optimized.units}"
                },
                "berechnungsart": "🔢 NUMERISCHE ITERATION (Bisection-Methode)",
                "numerische_details": {
                    "methode": "Bisection-Algorithmus",
                    "iterationen": numerical_result["iterations"],
                    "konvergiert": numerical_result["converged"],
                    "toleranz_erreicht": numerical_result["tolerance_achieved"],
                    "fehlerabschaetzung": f"{numerical_result['error_estimate']:.2e} m",
                    "relatives_residuum": f"{numerical_result['final_residual']/perimeter_si*100:.2e} %"
                },
                "verifikation": {
                    "rueckrechnung_umfang": f"{verification_perimeter:.6g} m",
                    "relativer_fehler": f"{relative_error:.2e} %",
                    "hinweis": "Verifikation durch Rückrechnung des Umfangs"
                },
                "formel": "U ≈ π × (a+b) × [1 + 3h/(10+√(4-3h))] → numerisch gelöst nach a",
                "si_werte": {
                    "grosse_halbachse_si": f"{a_si:.6g} m",
                    "kleine_halbachse_si": f"{b_si:.6g} m",
                    "umfang_si": f"{perimeter_si:.6g} m"
                }
            }
        
        # ===== KLEINE HALBACHSE BERECHNEN (NUMERISCH) =====
        elif target_param == 'semi_minor_axis':
            perimeter_si = params['perimeter']['si_value']
            a_si = params['semi_major_axis']['si_value']  # Große Halbachse
            
            if perimeter_si <= 0 or a_si <= 0:
                return {"error": "Umfang und große Halbachse müssen positiv sein"}
            
            # Numerische Lösung für kleine Halbachse
            numerical_result = solve_semi_axis_numerically(
                target_perimeter=perimeter_si,
                known_axis=a_si,
                solve_for_major=False
            )
            
            if not numerical_result["converged"]:
                return {
                    "error": "Numerische Iteration konvergierte nicht",
                    "details": numerical_result,
                    "hinweis": "Versuchen Sie andere Eingabewerte oder erhöhen Sie die Toleranz"
                }
            
            b_si = numerical_result["result"]
            
            # Validierung: b <= a für Ellipse
            if b_si > a_si:
                return {
                    "error": "Inkonsistente Geometrie",
                    "message": f"Berechnete kleine Halbachse ({b_si:.6g} m) > große Halbachse ({a_si:.6g} m)",
                    "hinweis": "Prüfen Sie die Eingabewerte - der Umfang ist möglicherweise zu groß für die gegebene große Halbachse"
                }
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['perimeter']['original_unit']
            b_quantity = b_si * ureg.meter
            b_optimized = optimize_output_unit(b_quantity, ref_unit)
            
            # Verifikation: Berechne Umfang zurück
            verification_perimeter = ramanujan_perimeter(a_si, b_si)
            relative_error = abs(verification_perimeter - perimeter_si) / perimeter_si * 100
            
            # Zusätzliche Validierung: Prüfe ob Lösung physikalisch sinnvoll ist
            if relative_error > 1.0:  # > 1% Fehler deutet auf Problem hin
                return {
                    "error": "Inkonsistente Geometrie - numerische Lösung unplausibel",
                    "message": f"Berechnete kleine Halbachse führt zu {relative_error:.1f}% Umfang-Abweichung",
                    "verifikation": {
                        "erwarteter_umfang": f"{perimeter_si:.6g} m",
                        "berechneter_umfang": f"{verification_perimeter:.6g} m",
                        "relativer_fehler": f"{relative_error:.2f} %"
                    },
                    "hinweis": "Der angegebene Umfang ist zu klein für die gegebene große Halbachse",
                    "empfehlung": "Prüfen Sie die Eingabewerte auf Plausibilität"
                }
            
            return {
                "target_parameter": "semi_minor_axis", 
                "gegebene_werte": {
                    "umfang": perimeter,
                    "grosse_halbachse": semi_major_axis
                },
                "ergebnis": {
                    "kleine_halbachse": f"{b_optimized.magnitude:.6g} {b_optimized.units}"
                },
                "berechnungsart": "🔢 NUMERISCHE ITERATION (Bisection-Methode)",
                "numerische_details": {
                    "methode": "Bisection-Algorithmus",
                    "iterationen": numerical_result["iterations"],
                    "konvergiert": numerical_result["converged"],
                    "toleranz_erreicht": numerical_result["tolerance_achieved"],
                    "fehlerabschaetzung": f"{numerical_result['error_estimate']:.2e} m",
                    "relatives_residuum": f"{numerical_result['final_residual']/perimeter_si*100:.2e} %"
                },
                "verifikation": {
                    "rueckrechnung_umfang": f"{verification_perimeter:.6g} m",
                    "relativer_fehler": f"{relative_error:.2e} %",
                    "hinweis": "Verifikation durch Rückrechnung des Umfangs"
                },
                "formel": "U ≈ π × (a+b) × [1 + 3h/(10+√(4-3h))] → numerisch gelöst nach b",
                "si_werte": {
                    "grosse_halbachse_si": f"{a_si:.6g} m",
                    "kleine_halbachse_si": f"{b_si:.6g} m",
                    "umfang_si": f"{perimeter_si:.6g} m"
                }
            }
        
    except Exception as e:
        return {
            "error": "Berechnungsfehler in _solve_single",
            "message": str(e),
            "hinweis": "Überprüfen Sie die Eingabe-Parameter und Einheiten"
        }

# ⚡ NEUE TOOL-STRUKTUR: get_metadata() und calculate() Funktionen

def get_metadata():
    """
    Engineering Tool Metadaten für MCP-Server Registration
    """
    metadata = {
        "tool_name": TOOL_NAME,
        "short_description": TOOL_SHORT_DESCRIPTION,
        "description": TOOL_DESCRIPTION,
        "tags": TOOL_TAGS,
        "version": TOOL_VERSION,
        "parameters": {
            "perimeter": PARAMETER_PERIMETER,
            "semi_major_axis": PARAMETER_SEMI_MAJOR_AXIS,
            "semi_minor_axis": PARAMETER_SEMI_MINOR_AXIS
        },
        "output": {
            "result": OUTPUT_RESULT
        },
        "examples": TOOL_EXAMPLES,
        "mathematical_foundation": MATHEMATICAL_FOUNDATION,
        "assumptions": TOOL_ASSUMPTIONS,
        "limitations": TOOL_LIMITATIONS,
        "has_solving": HAS_SOLVING,
        "reference_units": REFERENCE_UNITS
    }
    
    # Füge target_parameters_info hinzu für symbolic/numeric
    if HAS_SOLVING == "symbolic/numeric":
        metadata["target_parameters_info"] = TARGET_PARAMETERS_INFO
    
    return metadata


def calculate(perimeter: str, semi_major_axis: str, semi_minor_axis: str) -> Dict:
    """
    Berechnet Ellipse-Umfang-Parameter mit TARGET-System.
    
    ⚡ NEUE TOOL-STRUKTUR: Wrapper für solve_ellipse_umfang mit neuer Signatur.
    
    Args:
        perimeter: Umfang mit Einheit oder 'target'
        semi_major_axis: Große Halbachse mit Einheit oder 'target'  
        semi_minor_axis: Kleine Halbachse mit Einheit oder 'target'
        
    Returns:
        Dict: Berechnungsergebnis mit target_parameter
    """
    return solve_ellipse_umfang(perimeter=perimeter, semi_major_axis=semi_major_axis, semi_minor_axis=semi_minor_axis)

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Ellipse-Umfang-Tool Tests ===")
    
    # Test 1: Umfang berechnen (analytisch)
    print("\n1. 📊 ANALYTISCH - Umfang berechnen:")
    result1 = solve_ellipse_umfang(perimeter='target', semi_major_axis="6 cm", semi_minor_axis="4 cm")
    if 'error' in result1:
        print("❌ FEHLER:", result1['error'])
    else:
        print("✅ SUCCESS:", result1.get('ergebnis', {}).get('umfang'))
        print("   Berechnungsart:", result1.get('berechnungsart'))
    
    # Test 2: Große Halbachse berechnen (numerisch)
    print("\n2. 🔢 NUMERISCH - Große Halbachse berechnen:")
    result2 = solve_ellipse_umfang(perimeter="32.7 cm", semi_major_axis='target', semi_minor_axis="4 cm")
    if 'error' in result2:
        print("❌ FEHLER:", result2['error'])
    else:
        print("✅ SUCCESS:", result2.get('ergebnis', {}).get('grosse_halbachse'))
        print("   Berechnungsart:", result2.get('berechnungsart'))
        print("   Iterationen:", result2.get('numerische_details', {}).get('iterationen'))
        print("   Fehlerabschätzung:", result2.get('numerische_details', {}).get('fehlerabschaetzung'))
    
    # Test 3: Kleine Halbachse berechnen (numerisch)
    print("\n3. 🔢 NUMERISCH - Kleine Halbachse berechnen:")
    result3 = solve_ellipse_umfang(perimeter="32.7 cm", semi_major_axis="6 cm", semi_minor_axis='target')
    if 'error' in result3:
        print("❌ FEHLER:", result3['error'])
    else:
        print("✅ SUCCESS:", result3.get('ergebnis', {}).get('kleine_halbachse'))
        print("   Berechnungsart:", result3.get('berechnungsart'))
        print("   Iterationen:", result3.get('numerische_details', {}).get('iterationen'))
        print("   Relativer Fehler:", result3.get('verifikation', {}).get('relativer_fehler'))
    
    # Test 4: Fehler - keine Einheit
    print("\n4. ❌ FEHLER-TEST - Keine Einheit:")
    result4 = solve_ellipse_umfang(perimeter='target', semi_major_axis="6", semi_minor_axis="4 cm")
    print("   ERWARTETER FEHLER:", result4.get('error', 'Kein Fehler?')) 