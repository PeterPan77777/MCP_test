#!/usr/bin/env python3
"""
Dreieck-Umfang - Berechnet Umfang oder fehlende Seite

Berechnet Dreieck-Umfang mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel U = a + b + c nach verschiedenen Variablen auf.
Lösbare Variablen: umfang, seite_a, seite_b, seite_c

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke

Dreieck: Polygon mit drei Seiten - U = a + b + c (Summe aller drei Seiten)
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "dreieck_umfang"
TOOL_TAGS = ["elementar"]
TOOL_SHORT_DESCRIPTION = "Dreieck-Umfang - Berechnet Umfang oder fehlende Seite"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic"  # Alle Berechnungen sind analytisch lösbar

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
FUNCTION_PARAM_1_NAME = "umfang"
FUNCTION_PARAM_1_DESC = "Umfang des Dreiecks mit Längeneinheit (z.B. '30 cm', '300 mm', '0.3 m') oder 'target' für Berechnung"
FUNCTION_PARAM_1_EXAMPLE = "30 cm"

FUNCTION_PARAM_2_NAME = "seite_a"
FUNCTION_PARAM_2_DESC = "Seite a des Dreiecks mit Längeneinheit (z.B. '10 cm', '100 mm', '0.1 m') oder 'target' für Berechnung"
FUNCTION_PARAM_2_EXAMPLE = "10 cm"

FUNCTION_PARAM_3_NAME = "seite_b"
FUNCTION_PARAM_3_DESC = "Seite b des Dreiecks mit Längeneinheit (z.B. '8 cm', '80 mm', '0.08 m') oder 'target' für Berechnung"
FUNCTION_PARAM_3_EXAMPLE = "8 cm"

FUNCTION_PARAM_4_NAME = "seite_c"
FUNCTION_PARAM_4_DESC = "Seite c des Dreiecks mit Längeneinheit (z.B. '12 cm', '120 mm', '0.12 m') oder 'target' für Berechnung"
FUNCTION_PARAM_4_EXAMPLE = "12 cm"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst die Dreieck-Umfang-Formel U = a + b + c nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel U = a + b + c)
{FUNCTION_PARAM_2_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel a = U - b - c)
{FUNCTION_PARAM_3_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel b = U - a - c)
{FUNCTION_PARAM_4_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel c = U - a - b)

Dreieck-Formel: U = a + b + c

Anwendungsbereich: Geometrie, Konstruktion, Zaunberechnungen für dreieckige Grundstücke
Einschränkungen: Alle Seiten müssen positiv sein, Dreiecksungleichung muss erfüllt sein
Genauigkeit: Exakte analytische Lösung"""

# Parameter-Definitionen für Metadaten
PARAMETER_UMFANG = {
    "type": "string | array",
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "batch_example": ["target", "36 cm", "target"]
}

PARAMETER_SEITE_A = {
    "type": "string | array", 
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE,
    "batch_example": ["3 cm", "target", "10 cm"]
}

PARAMETER_SEITE_B = {
    "type": "string | array",
    "description": FUNCTION_PARAM_3_DESC,
    "example": FUNCTION_PARAM_3_EXAMPLE,
    "batch_example": ["4 cm", "12 cm", "target"]
}

PARAMETER_SEITE_C = {
    "type": "string | array",
    "description": FUNCTION_PARAM_4_DESC,
    "example": FUNCTION_PARAM_4_EXAMPLE,
    "batch_example": ["5 cm", "16 cm", "8 cm"]
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
        "title": f"Berechne {FUNCTION_PARAM_1_NAME} (analytisch) bei gegebenen drei Seiten",
        "input": {FUNCTION_PARAM_1_NAME: "target", FUNCTION_PARAM_2_NAME: "3 cm", FUNCTION_PARAM_3_NAME: "4 cm", FUNCTION_PARAM_4_NAME: "5 cm"},
        "output": f"{FUNCTION_PARAM_1_NAME} in optimierter Einheit mit geschlossener Formel"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_4_NAME} (analytisch) bei gegebenem {FUNCTION_PARAM_1_NAME} und zwei Seiten", 
        "input": {FUNCTION_PARAM_1_NAME: "12 cm", FUNCTION_PARAM_2_NAME: "3 cm", FUNCTION_PARAM_3_NAME: "4 cm", FUNCTION_PARAM_4_NAME: "target"},
        "output": f"{FUNCTION_PARAM_4_NAME} in optimierter Einheit mit geschlossener Formel"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_2_NAME} (analytisch) bei gegebenem {FUNCTION_PARAM_1_NAME} und anderen Seiten",
        "input": {FUNCTION_PARAM_1_NAME: "12 cm", FUNCTION_PARAM_2_NAME: "target", FUNCTION_PARAM_3_NAME: "4 cm", FUNCTION_PARAM_4_NAME: "5 cm"},
        "output": f"{FUNCTION_PARAM_2_NAME} in optimierter Einheit mit geschlossener Formel"
    }
]

# Annahmen
TOOL_ASSUMPTIONS = [
    "Dreieck mit drei bekannten Seiten",
    "Alle Eingabewerte sind positiv",
    "Dreiecksungleichung ist erfüllt: a + b > c, a + c > b, b + c > a"
]

# Einschränkungen
TOOL_LIMITATIONS = [
    "Nur für positive Werte gültig",
    "Dreiecksungleichung muss erfüllt sein",
    "Entartete Dreiecke (eine Seite = Summe der anderen) sind nicht erlaubt"
]

# Mathematische Grundlagen
MATHEMATICAL_FOUNDATION = "Dreieck-Umfang: U = a + b + c, wobei a, b und c die drei Seitenlängen sind"

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

def solve_dreieck_umfang(
    # ⚠️ Hier die konfigurierten Parameter-Namen und -Beschreibungen verwenden:
    umfang: Annotated[Union[str, List[str]], FUNCTION_PARAM_1_DESC],  
    seite_a: Annotated[Union[str, List[str]], FUNCTION_PARAM_2_DESC],
    seite_b: Annotated[Union[str, List[str]], FUNCTION_PARAM_3_DESC],
    seite_c: Annotated[Union[str, List[str]], FUNCTION_PARAM_4_DESC]
) -> Union[Dict, List[Dict]]:
    """
    Löst die Dreieck-Umfang-Formel U = a + b + c nach verschiedenen Variablen auf.
    
    Unterstützt Batch-Verarbeitung: Wenn Listen als Parameter übergeben werden,
    müssen ALLE Parameter Listen gleicher Länge sein. Jeder Index repräsentiert
    einen vollständigen Parametersatz.
    """
    try:
        # Erstelle Parameter-Dictionary
        params_dict = {
            'umfang': umfang,
            'seite_a': seite_a, 
            'seite_b': seite_b,
            'seite_c': seite_c
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
                combinations[0]['umfang'],
                combinations[0]['seite_a'],
                combinations[0]['seite_b'],
                combinations[0]['seite_c']
            )
        
        # Batch-Verarbeitung: Berechne alle Kombinationen
        results = []
        for i, combo in enumerate(combinations):
            try:
                result = _solve_single(
                    combo['umfang'],
                    combo['seite_a'],
                    combo['seite_b'],
                    combo['seite_c']
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
            "error": f"Fehler in solve_dreieck_umfang: {str(e)}",
            "type": type(e).__name__
        }

def _solve_single(
    umfang: str,
    seite_a: str,
    seite_b: str,
    seite_c: str
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
            'var1': umfang,
            'var2': seite_a,
            'var3': seite_b,
            'var4': seite_c
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
                "example": f"solve_dreieck_umfang({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}', {FUNCTION_PARAM_4_NAME}='{FUNCTION_PARAM_4_EXAMPLE}')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 3:
            return {
                "error": f"Genau 3 Parameter müssen Werte mit Einheiten haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": f"solve_dreieck_umfang({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}', {FUNCTION_PARAM_4_NAME}='{FUNCTION_PARAM_4_EXAMPLE}')"
            }
        
        target_param = target_params[0]
        
        # Erstelle kwargs für Validierung (nur gegebene Parameter)
        validation_kwargs = {}
        param_names = {
            'var1': 'umfang',
            'var2': 'seite_a',
            'var3': 'seite_b',
            'var4': 'seite_c'
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
                    f"{FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}'",
                    f"{FUNCTION_PARAM_4_NAME}='{FUNCTION_PARAM_4_EXAMPLE}'"
                ]
            }
        
        # Dreieck-Umfang: U = a + b + c
        # Umgestellt: a = U - b - c, b = U - a - c, c = U - a - b
        
        if target_param == 'var1':  # umfang
            # Berechne Umfang: U = a + b + c
            a_si = params['seite_a']['si_value']  # in Metern
            b_si = params['seite_b']['si_value']  # in Metern
            c_si = params['seite_c']['si_value']  # in Metern
            
            if a_si <= 0 or b_si <= 0 or c_si <= 0:
                return {"error": "Alle Seiten müssen positiv sein"}
            
            # Prüfe Dreiecksungleichung
            if (a_si + b_si <= c_si) or (a_si + c_si <= b_si) or (b_si + c_si <= a_si):
                return {"error": "Die gegebenen Seiten können kein gültiges Dreieck bilden (Dreiecksungleichung verletzt)"}
            
            umfang_si = a_si + b_si + c_si  # in Metern
            
            # Optimiere Ausgabe-Einheit (nutze längste Seite als Referenz)
            longest_side = max(a_si, b_si, c_si)
            if longest_side == a_si:
                ref_unit = params['seite_a']['original_unit']
            elif longest_side == b_si:
                ref_unit = params['seite_b']['original_unit']
            else:
                ref_unit = params['seite_c']['original_unit']
            
            umfang_quantity = umfang_si * ureg.meter
            umfang_optimized = optimize_output_unit(umfang_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "umfang",
                "gegebene_werte": {
                    "seite_a": seite_a,
                    "seite_b": seite_b,
                    "seite_c": seite_c
                },
                "ergebnis": {
                    "umfang": f"{umfang_optimized.magnitude:.6g} {umfang_optimized.units}"
                },
                "formel": "U = a + b + c",
                "si_werte": {
                    "umfang_si": f"{umfang_si:.6g} m",
                    "seite_a_si": f"{a_si:.6g} m",
                    "seite_b_si": f"{b_si:.6g} m",
                    "seite_c_si": f"{c_si:.6g} m"
                }
            }
            
        elif target_param == 'var2':  # seite_a
            # Berechne Seite a: a = U - b - c
            U_si = params['umfang']['si_value']  # in Metern
            b_si = params['seite_b']['si_value']     # in Metern
            c_si = params['seite_c']['si_value']     # in Metern
            
            if U_si <= 0 or b_si <= 0 or c_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            a_si = U_si - b_si - c_si  # in Metern
            
            if a_si <= 0:
                return {"error": "Die verbleibende Seite wäre nicht positiv"}
            
            # Prüfe Dreiecksungleichung
            if (a_si + b_si <= c_si) or (a_si + c_si <= b_si) or (b_si + c_si <= a_si):
                return {"error": "Die resultierenden Seiten können kein gültiges Dreieck bilden"}
            
            # Optimiere Ausgabe-Einheit
            a_quantity = a_si * ureg.meter
            longer_side = max(b_si, c_si)
            ref_unit = params['seite_b']['original_unit'] if longer_side == b_si else params['seite_c']['original_unit']
            a_optimized = optimize_output_unit(a_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "seite_a",
                "gegebene_werte": {
                    "umfang": umfang,
                    "seite_b": seite_b,
                    "seite_c": seite_c
                },
                "ergebnis": {
                    "seite_a": f"{a_optimized.magnitude:.6g} {a_optimized.units}"
                },
                "formel": "a = U - b - c",
                "si_werte": {
                    "seite_a_si": f"{a_si:.6g} m",
                    "umfang_si": f"{U_si:.6g} m",
                    "seite_b_si": f"{b_si:.6g} m",
                    "seite_c_si": f"{c_si:.6g} m"
                }
            }
            
        elif target_param == 'var3':  # seite_b
            # Berechne Seite b: b = U - a - c
            U_si = params['umfang']['si_value']  # in Metern
            a_si = params['seite_a']['si_value']     # in Metern
            c_si = params['seite_c']['si_value']     # in Metern
            
            if U_si <= 0 or a_si <= 0 or c_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            b_si = U_si - a_si - c_si  # in Metern
            
            if b_si <= 0:
                return {"error": "Die verbleibende Seite wäre nicht positiv"}
            
            # Prüfe Dreiecksungleichung
            if (a_si + b_si <= c_si) or (a_si + c_si <= b_si) or (b_si + c_si <= a_si):
                return {"error": "Die resultierenden Seiten können kein gültiges Dreieck bilden"}
            
            # Optimiere Ausgabe-Einheit
            b_quantity = b_si * ureg.meter
            longer_side = max(a_si, c_si)
            ref_unit = params['seite_a']['original_unit'] if longer_side == a_si else params['seite_c']['original_unit']
            b_optimized = optimize_output_unit(b_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "seite_b",
                "gegebene_werte": {
                    "umfang": umfang,
                    "seite_a": seite_a,
                    "seite_c": seite_c
                },
                "ergebnis": {
                    "seite_b": f"{b_optimized.magnitude:.6g} {b_optimized.units}"
                },
                "formel": "b = U - a - c",
                "si_werte": {
                    "seite_b_si": f"{b_si:.6g} m",
                    "umfang_si": f"{U_si:.6g} m",
                    "seite_a_si": f"{a_si:.6g} m",
                    "seite_c_si": f"{c_si:.6g} m"
                }
            }
            
        elif target_param == 'var4':  # seite_c
            # Berechne Seite c: c = U - a - b
            U_si = params['umfang']['si_value']  # in Metern
            a_si = params['seite_a']['si_value']     # in Metern
            b_si = params['seite_b']['si_value']     # in Metern
            
            if U_si <= 0 or a_si <= 0 or b_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            c_si = U_si - a_si - b_si  # in Metern
            
            if c_si <= 0:
                return {"error": "Die verbleibende Seite wäre nicht positiv"}
            
            # Prüfe Dreiecksungleichung
            if (a_si + b_si <= c_si) or (a_si + c_si <= b_si) or (b_si + c_si <= a_si):
                return {"error": "Die resultierenden Seiten können kein gültiges Dreieck bilden"}
            
            # Optimiere Ausgabe-Einheit
            c_quantity = c_si * ureg.meter
            longer_side = max(a_si, b_si)
            ref_unit = params['seite_a']['original_unit'] if longer_side == a_si else params['seite_b']['original_unit']
            c_optimized = optimize_output_unit(c_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "seite_c",
                "gegebene_werte": {
                    "umfang": umfang,
                    "seite_a": seite_a,
                    "seite_b": seite_b
                },
                "ergebnis": {
                    "seite_c": f"{c_optimized.magnitude:.6g} {c_optimized.units}"
                },
                "formel": "c = U - a - b",
                "si_werte": {
                    "seite_c_si": f"{c_si:.6g} m",
                    "umfang_si": f"{U_si:.6g} m",
                    "seite_a_si": f"{a_si:.6g} m",
                    "seite_b_si": f"{b_si:.6g} m"
                }
            }
        
    except UnitsError as e:
        return {"error": f"Einheiten-Fehler: {str(e)}"}
    except Exception as e:
        return {
            "error": f"Fehler in _solve_single: {str(e)}",
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
            FUNCTION_PARAM_1_NAME: PARAMETER_UMFANG,
            FUNCTION_PARAM_2_NAME: PARAMETER_SEITE_A,
            FUNCTION_PARAM_3_NAME: PARAMETER_SEITE_B,
            FUNCTION_PARAM_4_NAME: PARAMETER_SEITE_C,
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
        "parameter_umfang": PARAMETER_UMFANG,
        "parameter_seite_a": PARAMETER_SEITE_A,
        "parameter_seite_b": PARAMETER_SEITE_B,
        "parameter_seite_c": PARAMETER_SEITE_C
    }

def calculate(umfang: str, seite_a: str, seite_b: str, seite_c: str) -> Dict:
    """Legacy-Funktion für Kompatibilität"""
    return solve_dreieck_umfang(umfang, seite_a, seite_b, seite_c)

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Dreieck-Umfang-Tool Tests ===")
    
    # Test 1: Umfang berechnen
    result1 = solve_dreieck_umfang(umfang="target", seite_a="3 cm", seite_b="4 cm", seite_c="5 cm")
    print(f"Test 1 - Umfang: {result1}")
    
    # Test 2: Fehlende Seite berechnen
    result2 = solve_dreieck_umfang(umfang="12 cm", seite_a="3 cm", seite_b="4 cm", seite_c="target")
    print(f"Test 2 - Seite c: {result2}")
    
    # Test 3: Ungültiges Dreieck
    result3 = solve_dreieck_umfang(umfang="target", seite_a="1 cm", seite_b="2 cm", seite_c="5 cm")
    print(f"Test 3 - Ungültiges Dreieck: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_dreieck_umfang(umfang="target", seite_a="3", seite_b="4 cm", seite_c="5 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 