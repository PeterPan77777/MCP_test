#!/usr/bin/env python3
"""
Trapez-Fläche - Berechnet Fläche, parallele Seiten oder Höhe eines Trapezes

Berechnet Trapezflächen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel A = (a + b) × h / 2 nach verschiedenen Variablen auf.
Lösbare Variablen: flaeche, grundseite_a, grundseite_b, hoehe

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke

🔄 BATCH-MODUS: Unterstützt Verarbeitung mehrerer Parametersätze gleichzeitig!
Beispiel: grundseite_a=["8 cm", "10 cm", "12 cm"] statt grundseite_a="8 cm"

Trapez: Viereck mit zwei parallelen Seiten - A = (a + b) × h / 2 (Grundseiten × Höhe / 2)
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "trapez_flaeche"
TOOL_TAGS = ["elementar"]
TOOL_SHORT_DESCRIPTION = "Trapez-Fläche - Berechnet Fläche, parallele Seiten oder Höhe"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic"  # Alle Berechnungen sind analytisch lösbar

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
FUNCTION_PARAM_1_NAME = "flaeche"
FUNCTION_PARAM_1_DESC = "Fläche des Trapezes mit Flächeneinheit (z.B. '60 cm²', '0.006 m²', '6000 mm²') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_1_EXAMPLE = "60 cm²"

FUNCTION_PARAM_2_NAME = "grundseite_a"
FUNCTION_PARAM_2_DESC = "Grundseite a des Trapezes mit Längeneinheit (z.B. '8 cm', '80 mm', '0.08 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_2_EXAMPLE = "8 cm"

FUNCTION_PARAM_3_NAME = "grundseite_b"
FUNCTION_PARAM_3_DESC = "Grundseite b des Trapezes mit Längeneinheit (z.B. '12 cm', '120 mm', '0.12 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_3_EXAMPLE = "12 cm"

FUNCTION_PARAM_4_NAME = "hoehe"
FUNCTION_PARAM_4_DESC = "Höhe des Trapezes mit Längeneinheit (z.B. '6 cm', '60 mm', '0.06 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_4_EXAMPLE = "6 cm"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst die Trapezformel A = (a + b) × h / 2 nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

🔄 BATCH-MODUS: Unterstützt Listen von Parametern für Massenberechnungen!
⚠️ WICHTIG: Bei Batch-Berechnungen müssen ALLE Parameter Listen gleicher Länge sein!
Jeder Index repräsentiert einen vollständigen Parametersatz.

Beispiel Batch-Aufruf:
solve_trapez(
    flaeche=['target', '70 cm²', 'target'],
    grundseite_a=['8 cm', '9 cm', '10 cm'],
    grundseite_b=['12 cm', '11 cm', '14 cm'],
    hoehe=['6 cm', 'target', '7 cm']
)
Dies berechnet 3 separate Trapeze mit jeweils einem anderen Target-Parameter.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel A = (a + b) × h / 2)
{FUNCTION_PARAM_2_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel a = (2A / h) - b)
{FUNCTION_PARAM_3_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel b = (2A / h) - a)
{FUNCTION_PARAM_4_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel h = 2A / (a + b))

Trapezformel: A = (a + b) × h / 2

Anwendungsbereich: Geometrische Berechnungen, Dachflächen, Querschnitte
Einschränkungen: Alle Werte müssen positiv sein, parallele Seiten dürfen nicht null sein
Genauigkeit: Exakte analytische Lösung"""

# Parameter-Definitionen für Metadaten
PARAMETER_FLAECHE = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "batch_example": ["target", "70 cm²", "target"]  # NEU
}

PARAMETER_GRUNDSEITE_A = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE,
    "batch_example": ["8 cm", "9 cm", "10 cm"]  # NEU
}

PARAMETER_GRUNDSEITE_B = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_3_DESC,
    "example": FUNCTION_PARAM_3_EXAMPLE,
    "batch_example": ["12 cm", "11 cm", "14 cm"]  # NEU
}

PARAMETER_HOEHE = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_4_DESC,
    "example": FUNCTION_PARAM_4_EXAMPLE,
    "batch_example": ["6 cm", "target", "7 cm"]  # NEU
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
        "title": f"Berechne {FUNCTION_PARAM_1_NAME} (analytisch) bei gegebenen parallelen Seiten und Höhe",
        "input": {FUNCTION_PARAM_1_NAME: "target", FUNCTION_PARAM_2_NAME: FUNCTION_PARAM_2_EXAMPLE, FUNCTION_PARAM_3_NAME: FUNCTION_PARAM_3_EXAMPLE, FUNCTION_PARAM_4_NAME: FUNCTION_PARAM_4_EXAMPLE},
        "output": f"{FUNCTION_PARAM_1_NAME} in optimierter Einheit mit geschlossener Formel"
    },
    {
        "title": f"Batch-Berechnung: Drei vollständige Parametersätze",
        "input": {
            FUNCTION_PARAM_1_NAME: ["target", "70 cm²", "target"],
            FUNCTION_PARAM_2_NAME: ["8 cm", "9 cm", "10 cm"],
            FUNCTION_PARAM_3_NAME: ["12 cm", "11 cm", "14 cm"],
            FUNCTION_PARAM_4_NAME: ["6 cm", "target", "7 cm"]
        },
        "output": f"Liste von 3 Ergebnissen, jeweils mit unterschiedlichem Target-Parameter"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_2_NAME} (analytisch) bei gegebener Fläche", 
        "input": {FUNCTION_PARAM_1_NAME: FUNCTION_PARAM_1_EXAMPLE, FUNCTION_PARAM_2_NAME: "target", FUNCTION_PARAM_3_NAME: FUNCTION_PARAM_3_EXAMPLE, FUNCTION_PARAM_4_NAME: FUNCTION_PARAM_4_EXAMPLE},
        "output": f"{FUNCTION_PARAM_2_NAME} in optimierter Einheit mit geschlossener Formel"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_4_NAME} (analytisch) bei gegebener Fläche und Seiten",
        "input": {FUNCTION_PARAM_1_NAME: FUNCTION_PARAM_1_EXAMPLE, FUNCTION_PARAM_2_NAME: FUNCTION_PARAM_2_EXAMPLE, FUNCTION_PARAM_3_NAME: FUNCTION_PARAM_3_EXAMPLE, FUNCTION_PARAM_4_NAME: "target"},
        "output": f"{FUNCTION_PARAM_4_NAME} in optimierter Einheit mit geschlossener Formel"
    }
]

# Annahmen
TOOL_ASSUMPTIONS = [
    "Trapez mit zwei parallelen Seiten",
    "Alle Eingabewerte sind positiv",
    "Höhe steht senkrecht zu den parallelen Seiten"
]

# Einschränkungen  
TOOL_LIMITATIONS = [
    "Nur für positive Werte gültig",
    "Nur für Trapeze mit parallelen Seiten",
    "Nicht für unregelmäßige Vierecke"
]

# Mathematische Grundlagen
MATHEMATICAL_FOUNDATION = "Trapezformel: A = (a + b) × h / 2, wobei a und b die parallelen Seiten und h die Höhe ist"

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
    
    Beispiel:
    Input: {
        'flaeche': ['target', '70 cm²', 'target'],
        'grundseite_a': ['8 cm', '9 cm', '10 cm'],
        'grundseite_b': ['12 cm', '11 cm', '14 cm'],
        'hoehe': ['6 cm', 'target', '7 cm']
    }
    Output: [
        {'flaeche': 'target', 'grundseite_a': '8 cm', 'grundseite_b': '12 cm', 'hoehe': '6 cm'},
        {'flaeche': '70 cm²', 'grundseite_a': '9 cm', 'grundseite_b': '11 cm', 'hoehe': 'target'},
        {'flaeche': 'target', 'grundseite_a': '10 cm', 'grundseite_b': '14 cm', 'hoehe': '7 cm'}
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

def solve_trapez(
    # ⚠️ Hier die konfigurierten Parameter-Namen und -Beschreibungen verwenden:
    flaeche: Annotated[Union[str, List[str]], FUNCTION_PARAM_1_DESC],  
    grundseite_a: Annotated[Union[str, List[str]], FUNCTION_PARAM_2_DESC],
    grundseite_b: Annotated[Union[str, List[str]], FUNCTION_PARAM_3_DESC],
    hoehe: Annotated[Union[str, List[str]], FUNCTION_PARAM_4_DESC]
) -> Union[Dict, List[Dict]]:
    """
    Löst die Trapezformel A = (a + b) × h / 2 nach verschiedenen Variablen auf.
    
    Unterstützt Batch-Verarbeitung: Wenn Listen als Parameter übergeben werden,
    müssen ALLE Parameter Listen gleicher Länge sein. Jeder Index repräsentiert
    einen vollständigen Parametersatz.
    """
    try:
        # Erstelle Parameter-Dictionary
        params_dict = {
            'flaeche': flaeche,
            'grundseite_a': grundseite_a, 
            'grundseite_b': grundseite_b,
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
            return _solve_single(
                combinations[0]['flaeche'],
                combinations[0]['grundseite_a'],
                combinations[0]['grundseite_b'],
                combinations[0]['hoehe']
            )
        
        # Batch-Verarbeitung: Berechne alle Kombinationen
        results = []
        for i, combo in enumerate(combinations):
            try:
                result = _solve_single(
                    combo['flaeche'],
                    combo['grundseite_a'],
                    combo['grundseite_b'],
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
            "error": f"Fehler in solve_trapez: {str(e)}",
            "type": type(e).__name__
        }

def _solve_single(
    flaeche: str,
    grundseite_a: str,
    grundseite_b: str,
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
            'var1': flaeche,
            'var2': grundseite_a, 
            'var3': grundseite_b,
            'var4': hoehe
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
                "example": f"solve_trapez({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}', {FUNCTION_PARAM_4_NAME}='{FUNCTION_PARAM_4_EXAMPLE}')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 3:
            return {
                "error": f"Genau 3 Parameter müssen Werte mit Einheiten haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": f"solve_trapez({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}', {FUNCTION_PARAM_4_NAME}='{FUNCTION_PARAM_4_EXAMPLE}')"
            }
        
        target_param = target_params[0]
        
        # Erstelle kwargs für Validierung (nur gegebene Parameter)
        validation_kwargs = {}
        param_names = {
            'var1': 'flaeche',
            'var2': 'grundseite_a', 
            'var3': 'grundseite_b',
            'var4': 'hoehe'
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
        
        # Trapez-Formel: A = (1/2) × (a + b) × h
        # Umgestellt: a = (2A / h) - b
        #            b = (2A / h) - a
        #            h = 2A / (a + b)
        
        if target_param == 'var1':  # flaeche
            # Berechne Fläche: A = (1/2) × (a + b) × h
            a_si = params['grundseite_a']['si_value']
            b_si = params['grundseite_b']['si_value']
            h_si = params['hoehe']['si_value']
            
            if a_si <= 0 or b_si <= 0 or h_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            flaeche_si = 0.5 * (a_si + b_si) * h_si
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['grundseite_a']['original_unit'] if a_si > b_si else params['grundseite_b']['original_unit']
            flaeche_quantity = flaeche_si * ureg.meter**2
            flaeche_optimized = optimize_output_unit(flaeche_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "flaeche",
                "gegebene_werte": {
                    "grundseite_a": grundseite_a,
                    "grundseite_b": grundseite_b,
                    "hoehe": hoehe
                },
                "ergebnis": {
                    "flaeche": f"{flaeche_optimized.magnitude:.6g} {flaeche_optimized.units}"
                },
                "formel": "A = (1/2) × (a + b) × h",
                "si_werte": {
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "grundseite_a_si": f"{a_si:.6g} m",
                    "grundseite_b_si": f"{b_si:.6g} m",
                    "hoehe_si": f"{h_si:.6g} m"
                }
            }
            
        elif target_param == 'var2':  # grundseite_a
            # Berechne Grundseite a: a = (2A / h) - b
            flaeche_si = params['flaeche']['si_value']
            b_si = params['grundseite_b']['si_value']
            h_si = params['hoehe']['si_value']
            
            if flaeche_si <= 0 or b_si <= 0 or h_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            a_si = (2 * flaeche_si / h_si) - b_si
            
            if a_si <= 0:
                return {"error": "Berechnete Grundseite a ist nicht positiv - überprüfen Sie die Parameter"}
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['grundseite_b']['original_unit']
            base_quantity = a_si * ureg.meter
            base_optimized = optimize_output_unit(base_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "grundseite_a",
                "gegebene_werte": {
                    "flaeche": flaeche,
                    "grundseite_b": grundseite_b,
                    "hoehe": hoehe
                },
                "ergebnis": {
                    "grundseite_a": f"{base_optimized.magnitude:.6g} {base_optimized.units}"
                },
                "formel": "a = (2A / h) - b",
                "si_werte": {
                    "grundseite_a_si": f"{a_si:.6g} m",
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "grundseite_b_si": f"{b_si:.6g} m",
                    "hoehe_si": f"{h_si:.6g} m"
                }
            }
            
        elif target_param == 'var3':  # grundseite_b
            # Berechne Grundseite b: b = (2A / h) - a
            flaeche_si = params['flaeche']['si_value']
            a_si = params['grundseite_a']['si_value']
            h_si = params['hoehe']['si_value']
            
            if flaeche_si <= 0 or a_si <= 0 or h_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            b_si = (2 * flaeche_si / h_si) - a_si
            
            if b_si <= 0:
                return {"error": "Berechnete Grundseite b ist nicht positiv - überprüfen Sie die Parameter"}
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['grundseite_a']['original_unit']
            base_quantity = b_si * ureg.meter
            base_optimized = optimize_output_unit(base_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "grundseite_b",
                "gegebene_werte": {
                    "flaeche": flaeche,
                    "grundseite_a": grundseite_a,
                    "hoehe": hoehe
                },
                "ergebnis": {
                    "grundseite_b": f"{base_optimized.magnitude:.6g} {base_optimized.units}"
                },
                "formel": "b = (2A / h) - a",
                "si_werte": {
                    "grundseite_b_si": f"{b_si:.6g} m",
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "grundseite_a_si": f"{a_si:.6g} m",
                    "hoehe_si": f"{h_si:.6g} m"
                }
            }
            
        elif target_param == 'var4':  # hoehe
            # Berechne Höhe: h = 2A / (a + b)
            flaeche_si = params['flaeche']['si_value']
            a_si = params['grundseite_a']['si_value']
            b_si = params['grundseite_b']['si_value']
            
            if flaeche_si <= 0 or a_si <= 0 or b_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            h_si = (2 * flaeche_si) / (a_si + b_si)
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['grundseite_a']['original_unit'] if a_si > b_si else params['grundseite_b']['original_unit']
            height_quantity = h_si * ureg.meter
            height_optimized = optimize_output_unit(height_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "hoehe",
                "gegebene_werte": {
                    "flaeche": flaeche,
                    "grundseite_a": grundseite_a,
                    "grundseite_b": grundseite_b
                },
                "ergebnis": {
                    "hoehe": f"{height_optimized.magnitude:.6g} {height_optimized.units}"
                },
                "formel": "h = 2A / (a + b)",
                "si_werte": {
                    "hoehe_si": f"{h_si:.6g} m",
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "grundseite_a_si": f"{a_si:.6g} m",
                    "grundseite_b_si": f"{b_si:.6g} m"
                }
            }
        
    except UnitsError as e:
        return {"error": f"Einheiten-Fehler: {str(e)}"}
    except Exception as e:
        return {
            "error": f"Fehler in solve_trapez: {str(e)}",
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
            FUNCTION_PARAM_2_NAME: PARAMETER_GRUNDSEITE_A,
            FUNCTION_PARAM_3_NAME: PARAMETER_GRUNDSEITE_B,
            FUNCTION_PARAM_4_NAME: PARAMETER_HOEHE,
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
        "parameter_grundseite_a": PARAMETER_GRUNDSEITE_A,
        "parameter_grundseite_b": PARAMETER_GRUNDSEITE_B,
        "parameter_hoehe": PARAMETER_HOEHE
    }

def calculate(flaeche: Union[str, List[str]], grundseite_a: Union[str, List[str]], grundseite_b: Union[str, List[str]], hoehe: Union[str, List[str]]) -> Union[Dict, List[Dict]]:
    """Legacy-Funktion für Kompatibilität - unterstützt nun auch Batch-Mode"""
    return solve_trapez(flaeche, grundseite_a, grundseite_b, hoehe) 