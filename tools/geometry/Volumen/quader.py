#!/usr/bin/env python3
"""
Quader-Volumen - Berechnet Volumen oder fehlende Kantenlänge eines Quaders

Berechnet Quader-Volumen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel V = l × b × h nach verschiedenen Variablen auf.
Lösbare Variablen: volumen, laenge, breite, hoehe

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke

Quader: Rechteckiger Kasten mit sechs rechteckigen Flächen - V = l × b × h
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "quader_volumen"
TOOL_TAGS = ["elementar"]
TOOL_SHORT_DESCRIPTION = "Quader-Volumen - Berechnet Volumen oder fehlende Kantenlänge"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic"  # Alle Berechnungen sind analytisch lösbar

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
FUNCTION_PARAM_1_NAME = "volumen"
FUNCTION_PARAM_1_DESC = "Volumen des Quaders mit Volumeneinheit (z.B. '1000 cm³', '0.001 m³', '1 l') oder 'target' für Berechnung"
FUNCTION_PARAM_1_EXAMPLE = "1000 cm³"

FUNCTION_PARAM_2_NAME = "laenge"
FUNCTION_PARAM_2_DESC = "Länge des Quaders mit Längeneinheit (z.B. '10 cm', '100 mm', '0.1 m') oder 'target' für Berechnung"
FUNCTION_PARAM_2_EXAMPLE = "10 cm"

FUNCTION_PARAM_3_NAME = "breite"
FUNCTION_PARAM_3_DESC = "Breite des Quaders mit Längeneinheit (z.B. '5 cm', '50 mm', '0.05 m') oder 'target' für Berechnung"
FUNCTION_PARAM_3_EXAMPLE = "5 cm"

FUNCTION_PARAM_4_NAME = "hoehe"
FUNCTION_PARAM_4_DESC = "Höhe des Quaders mit Längeneinheit (z.B. '20 cm', '200 mm', '0.2 m') oder 'target' für Berechnung"
FUNCTION_PARAM_4_EXAMPLE = "20 cm"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst die Quader-Volumen-Formel V = l × b × h nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel V = l×b×h)
{FUNCTION_PARAM_2_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel l = V/(b×h))
{FUNCTION_PARAM_3_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel b = V/(l×h))
{FUNCTION_PARAM_4_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel h = V/(l×b))

Quader-Formel: V = l × b × h

Anwendungsbereich: Behältervolumen, Raumberechnung, Kartons, Architektur
Einschränkungen: Alle Werte müssen positiv sein
Genauigkeit: Exakte analytische Lösung"""

# Parameter-Definitionen für Metadaten
PARAMETER_VOLUMEN = {
    "type": "string | array",
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "batch_example": ["target", "2000 cm³", "target", "500 cm³"]
}

PARAMETER_LAENGE = {
    "type": "string | array", 
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE,
    "batch_example": ["12 cm", "target", "8 cm", "10 cm"]
}

PARAMETER_BREITE = {
    "type": "string | array",
    "description": FUNCTION_PARAM_3_DESC,
    "example": FUNCTION_PARAM_3_EXAMPLE,
    "batch_example": ["6 cm", "10 cm", "target", "5 cm"]
}

PARAMETER_HOEHE = {
    "type": "string | array",
    "description": FUNCTION_PARAM_4_DESC,
    "example": FUNCTION_PARAM_4_EXAMPLE,
    "batch_example": ["15 cm", "20 cm", "25 cm", "target"]
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
        "title": "Berechne Volumen bei gegebenen Kantenlängen",
        "input": {f"{FUNCTION_PARAM_1_NAME}": "target", f"{FUNCTION_PARAM_2_NAME}": FUNCTION_PARAM_2_EXAMPLE, f"{FUNCTION_PARAM_3_NAME}": FUNCTION_PARAM_3_EXAMPLE, f"{FUNCTION_PARAM_4_NAME}": FUNCTION_PARAM_4_EXAMPLE},
        "output": "Volumen in optimierter Einheit"
    },
    {
        "title": "Berechne Länge bei gegebenem Volumen", 
        "input": {f"{FUNCTION_PARAM_1_NAME}": FUNCTION_PARAM_1_EXAMPLE, f"{FUNCTION_PARAM_2_NAME}": "target", f"{FUNCTION_PARAM_3_NAME}": FUNCTION_PARAM_3_EXAMPLE, f"{FUNCTION_PARAM_4_NAME}": FUNCTION_PARAM_4_EXAMPLE},
        "output": "Länge in optimierter Einheit"
    },
    {
        "title": "Berechne Höhe bei gegebenem Volumen",
        "input": {f"{FUNCTION_PARAM_1_NAME}": FUNCTION_PARAM_1_EXAMPLE, f"{FUNCTION_PARAM_2_NAME}": FUNCTION_PARAM_2_EXAMPLE, f"{FUNCTION_PARAM_3_NAME}": FUNCTION_PARAM_3_EXAMPLE, f"{FUNCTION_PARAM_4_NAME}": "target"},
        "output": "Höhe in optimierter Einheit"
    }
]

# Mathematische Grundlagen
MATHEMATICAL_FOUNDATION = "Quader-Volumen: V = l × b × h, wobei l die Länge, b die Breite und h die Höhe ist"

# Annahmen
TOOL_ASSUMPTIONS = [
    "Quader mit rechteckigen Flächen",
    "Alle Eingabewerte sind positiv",
    "Rechte Winkel an allen Kanten"
]

# Einschränkungen
TOOL_LIMITATIONS = [
    "Nur für positive Werte gültig",
    "Nur für rechteckige Quader",
    "Nicht für schräge oder gerundete Formen"
]

# Referenz-Einheiten
REFERENCE_UNITS = {
    f"{FUNCTION_PARAM_1_NAME}": "m³",
    f"{FUNCTION_PARAM_2_NAME}": "m",
    f"{FUNCTION_PARAM_3_NAME}": "m",
    f"{FUNCTION_PARAM_4_NAME}": "m"
}

# ================================================================================================
# 🔧 IMPORTS & DEPENDENCIES 🔧
# ================================================================================================

from typing import Dict, Optional, Annotated, List, Any, Union
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

def solve_quader(
    volumen: Annotated[Union[str, List[str]], f"{FUNCTION_PARAM_1_DESC}. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"],
    laenge: Annotated[Union[str, List[str]], f"{FUNCTION_PARAM_2_DESC}. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"],
    breite: Annotated[Union[str, List[str]], f"{FUNCTION_PARAM_3_DESC}. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"],
    hoehe: Annotated[Union[str, List[str]], f"{FUNCTION_PARAM_4_DESC}. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"]
) -> Union[Dict, List[Dict]]:
    """
    📊 ANALYTICAL SOLUTION
    
    Löst die Quader-Volumen-Formel V = l × b × h nach verschiedenen Variablen auf.
    
    Unterstützt Batch-Verarbeitung: Wenn Listen als Parameter übergeben werden,
    müssen ALLE Parameter Listen gleicher Länge sein. Jeder Index repräsentiert
    einen vollständigen Parametersatz.
    
    Args:
        volumen: Volumen mit Einheit oder 'target'
        laenge: Länge mit Einheit oder 'target' 
        breite: Breite mit Einheit oder 'target'
        hoehe: Höhe mit Einheit oder 'target'
    
    Returns:
        Dict mit Berechnungsergebnis und Metadaten oder Liste von Dicts für Batch
    """
    try:
        # Erstelle Parameter-Dictionary
        params_dict = {
            'volumen': volumen,
            'laenge': laenge,
            'breite': breite,
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
                combinations[0]['volumen'],
                combinations[0]['laenge'],
                combinations[0]['breite'],
                combinations[0]['hoehe']
            )
        
        # Batch-Verarbeitung: Berechne alle Kombinationen
        results = []
        for i, combo in enumerate(combinations):
            try:
                result = _solve_single(
                    combo['volumen'],
                    combo['laenge'],
                    combo['breite'],
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
            "error": f"Fehler in solve_quader: {str(e)}",
            "type": type(e).__name__
        }

def _solve_single(
    volumen: str,
    laenge: str,
    breite: str,
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
            f'{FUNCTION_PARAM_2_NAME}': laenge,
            f'{FUNCTION_PARAM_3_NAME}': breite,
            f'{FUNCTION_PARAM_4_NAME}': hoehe
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
                "example": f"solve_quader({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}', {FUNCTION_PARAM_4_NAME}='{FUNCTION_PARAM_4_EXAMPLE}')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 3:
            return {
                "error": f"Genau 3 Parameter müssen Werte mit Einheiten haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": f"solve_quader({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}', {FUNCTION_PARAM_4_NAME}='{FUNCTION_PARAM_4_EXAMPLE}')"
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
                    f"{FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}'",
                    f"{FUNCTION_PARAM_4_NAME}='{FUNCTION_PARAM_4_EXAMPLE}'"
                ]
            }
        
        # Berechnung basierend auf target Parameter
        if target_param == FUNCTION_PARAM_1_NAME:
            # Berechne Volumen: V = l × b × h
            l_si = params[FUNCTION_PARAM_2_NAME]['si_value']  # in Metern
            b_si = params[FUNCTION_PARAM_3_NAME]['si_value']  # in Metern
            h_si = params[FUNCTION_PARAM_4_NAME]['si_value']  # in Metern
            
            if l_si <= 0 or b_si <= 0 or h_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            v_si = l_si * b_si * h_si  # in m³
            
            # Optimiere Ausgabe-Einheit (nutze kleinste Dimension als Referenz)
            dimensions = [
                (params[FUNCTION_PARAM_2_NAME]['si_value'], params[FUNCTION_PARAM_2_NAME]['original_unit']),
                (params[FUNCTION_PARAM_3_NAME]['si_value'], params[FUNCTION_PARAM_3_NAME]['original_unit']),
                (params[FUNCTION_PARAM_4_NAME]['si_value'], params[FUNCTION_PARAM_4_NAME]['original_unit'])
            ]
            min_dim = min(dimensions, key=lambda x: x[0])
            
            volume_quantity = v_si * ureg.meter**3
            volume_optimized = optimize_volume_unit(volume_quantity, min_dim[1])
            
            return {
                "target_parameter": FUNCTION_PARAM_1_NAME,
                "gegebene_werte": {
                    FUNCTION_PARAM_2_NAME: laenge,
                    FUNCTION_PARAM_3_NAME: breite,
                    FUNCTION_PARAM_4_NAME: hoehe
                },
                "ergebnis": {
                    FUNCTION_PARAM_1_NAME: f"{volume_optimized.magnitude:.6g} {volume_optimized.units}"
                },
                "formel": "V = l × b × h",
                "berechnungsart": "📊 ANALYTICAL SOLUTION",
                "si_werte": {
                    f"{FUNCTION_PARAM_1_NAME}_si": f"{v_si:.6g} m³",
                    f"{FUNCTION_PARAM_2_NAME}_si": f"{l_si:.6g} m",
                    f"{FUNCTION_PARAM_3_NAME}_si": f"{b_si:.6g} m",
                    f"{FUNCTION_PARAM_4_NAME}_si": f"{h_si:.6g} m"
                }
            }
        
        elif target_param == FUNCTION_PARAM_2_NAME:
            # Berechne Länge: l = V / (b × h)
            v_si = params[FUNCTION_PARAM_1_NAME]['si_value']  # in m³
            b_si = params[FUNCTION_PARAM_3_NAME]['si_value']  # in Metern
            h_si = params[FUNCTION_PARAM_4_NAME]['si_value']  # in Metern
            
            if v_si <= 0 or b_si <= 0 or h_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            l_si = v_si / (b_si * h_si)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            smaller_dim = min(params[FUNCTION_PARAM_3_NAME]['si_value'], params[FUNCTION_PARAM_4_NAME]['si_value'])
            ref_unit = params[FUNCTION_PARAM_3_NAME]['original_unit'] if params[FUNCTION_PARAM_3_NAME]['si_value'] == smaller_dim else params[FUNCTION_PARAM_4_NAME]['original_unit']
            
            length_quantity = l_si * ureg.meter
            length_optimized = optimize_output_unit(length_quantity, ref_unit)
            
            return {
                "target_parameter": FUNCTION_PARAM_2_NAME,
                "gegebene_werte": {
                    FUNCTION_PARAM_1_NAME: volumen,
                    FUNCTION_PARAM_3_NAME: breite,
                    FUNCTION_PARAM_4_NAME: hoehe
                },
                "ergebnis": {
                    FUNCTION_PARAM_2_NAME: f"{length_optimized.magnitude:.6g} {length_optimized.units}"
                },
                "formel": "l = V / (b × h)",
                "berechnungsart": "📊 ANALYTICAL SOLUTION",
                "si_werte": {
                    f"{FUNCTION_PARAM_1_NAME}_si": f"{v_si:.6g} m³",
                    f"{FUNCTION_PARAM_2_NAME}_si": f"{l_si:.6g} m",
                    f"{FUNCTION_PARAM_3_NAME}_si": f"{b_si:.6g} m",
                    f"{FUNCTION_PARAM_4_NAME}_si": f"{h_si:.6g} m"
                }
            }
        
        elif target_param == FUNCTION_PARAM_3_NAME:
            # Berechne Breite: b = V / (l × h)
            v_si = params[FUNCTION_PARAM_1_NAME]['si_value']  # in m³
            l_si = params[FUNCTION_PARAM_2_NAME]['si_value']  # in Metern
            h_si = params[FUNCTION_PARAM_4_NAME]['si_value']  # in Metern
            
            if v_si <= 0 or l_si <= 0 or h_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            b_si = v_si / (l_si * h_si)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            smaller_dim = min(params[FUNCTION_PARAM_2_NAME]['si_value'], params[FUNCTION_PARAM_4_NAME]['si_value'])
            ref_unit = params[FUNCTION_PARAM_2_NAME]['original_unit'] if params[FUNCTION_PARAM_2_NAME]['si_value'] == smaller_dim else params[FUNCTION_PARAM_4_NAME]['original_unit']
            
            width_quantity = b_si * ureg.meter
            width_optimized = optimize_output_unit(width_quantity, ref_unit)
            
            return {
                "target_parameter": FUNCTION_PARAM_3_NAME,
                "gegebene_werte": {
                    FUNCTION_PARAM_1_NAME: volumen,
                    FUNCTION_PARAM_2_NAME: laenge,
                    FUNCTION_PARAM_4_NAME: hoehe
                },
                "ergebnis": {
                    FUNCTION_PARAM_3_NAME: f"{width_optimized.magnitude:.6g} {width_optimized.units}"
                },
                "formel": "b = V / (l × h)",
                "berechnungsart": "📊 ANALYTICAL SOLUTION",
                "si_werte": {
                    f"{FUNCTION_PARAM_1_NAME}_si": f"{v_si:.6g} m³",
                    f"{FUNCTION_PARAM_2_NAME}_si": f"{l_si:.6g} m",
                    f"{FUNCTION_PARAM_3_NAME}_si": f"{b_si:.6g} m",
                    f"{FUNCTION_PARAM_4_NAME}_si": f"{h_si:.6g} m"
                }
            }
        
        elif target_param == FUNCTION_PARAM_4_NAME:
            # Berechne Höhe: h = V / (l × b)
            v_si = params[FUNCTION_PARAM_1_NAME]['si_value']  # in m³
            l_si = params[FUNCTION_PARAM_2_NAME]['si_value']  # in Metern
            b_si = params[FUNCTION_PARAM_3_NAME]['si_value']  # in Metern
            
            if v_si <= 0 or l_si <= 0 or b_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            h_si = v_si / (l_si * b_si)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            smaller_dim = min(params[FUNCTION_PARAM_2_NAME]['si_value'], params[FUNCTION_PARAM_3_NAME]['si_value'])
            ref_unit = params[FUNCTION_PARAM_2_NAME]['original_unit'] if params[FUNCTION_PARAM_2_NAME]['si_value'] == smaller_dim else params[FUNCTION_PARAM_3_NAME]['original_unit']
            
            height_quantity = h_si * ureg.meter
            height_optimized = optimize_output_unit(height_quantity, ref_unit)
            
            return {
                "target_parameter": FUNCTION_PARAM_4_NAME,
                "gegebene_werte": {
                    FUNCTION_PARAM_1_NAME: volumen,
                    FUNCTION_PARAM_2_NAME: laenge,
                    FUNCTION_PARAM_3_NAME: breite
                },
                "ergebnis": {
                    FUNCTION_PARAM_4_NAME: f"{height_optimized.magnitude:.6g} {height_optimized.units}"
                },
                "formel": "h = V / (l × b)",
                "berechnungsart": "📊 ANALYTICAL SOLUTION",
                "si_werte": {
                    f"{FUNCTION_PARAM_1_NAME}_si": f"{v_si:.6g} m³",
                    f"{FUNCTION_PARAM_2_NAME}_si": f"{l_si:.6g} m",
                    f"{FUNCTION_PARAM_3_NAME}_si": f"{b_si:.6g} m",
                    f"{FUNCTION_PARAM_4_NAME}_si": f"{h_si:.6g} m"
                }
            }
        
        else:
            return {"error": f"Unbekannter target Parameter: {target_param}"}
    
    except Exception as e:
        return {
            "error": "Unerwarteter Fehler in _solve_single",
            "message": str(e),
            "funktion": "_solve_single"
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
            FUNCTION_PARAM_2_NAME: PARAMETER_LAENGE,
            FUNCTION_PARAM_3_NAME: PARAMETER_BREITE,
            FUNCTION_PARAM_4_NAME: PARAMETER_HOEHE
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
def calculate(volume: str, length: str, width: str, height: str) -> Dict:
    """Legacy-Wrapper-Funktion für Abwärtskompatibilität"""
    return solve_quader(
        volumen=volume,
        laenge=length,
        breite=width,
        hoehe=height
    )

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Quader-Tool Tests ===")
    
    # Test 1: Volumen berechnen
    result1 = solve_quader(laenge="10 cm", breite="5 cm", hoehe="2.5 cm")
    print(f"Test 1 - Volumen: {result1}")
    
    # Test 2: Länge berechnen
    result2 = solve_quader(volumen="125 cm³", breite="5 cm", hoehe="2.5 cm")
    print(f"Test 2 - Länge: {result2}")
    
    # Test 3: Höhe berechnen
    result3 = solve_quader(volumen="125 cm³", laenge="10 cm", breite="5 cm")
    print(f"Test 3 - Höhe: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_quader(laenge="10", breite="5 cm", hoehe="2.5 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 