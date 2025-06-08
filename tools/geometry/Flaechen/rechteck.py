#!/usr/bin/env python3
"""
Rechteck-Fläche - Berechnet Fläche, Länge oder Breite

Berechnet Rechteckflächen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel A = l × b nach verschiedenen Variablen auf.
Lösbare Variablen: flaeche, laenge, breite

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke

🔄 BATCH-MODUS: Unterstützt Verarbeitung mehrerer Parametersätze gleichzeitig!
Beispiel: laenge=["10 cm", "15 cm", "20 cm"] statt laenge="10 cm"

Rechteck: Viereck mit vier rechten Winkeln - A = l × b (Länge × Breite)
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "rechteck_flaeche"
TOOL_TAGS = ["elementar"]
TOOL_SHORT_DESCRIPTION = "Rechteck-Fläche - Berechnet Fläche, Länge oder Breite"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic"  # Alle Berechnungen sind analytisch lösbar

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
FUNCTION_PARAM_1_NAME = "flaeche"
FUNCTION_PARAM_1_DESC = "Fläche des Rechtecks mit Flächeneinheit (z.B. '50 cm²', '0.005 m²', '5000 mm²') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_1_EXAMPLE = "50 cm²"

FUNCTION_PARAM_2_NAME = "laenge"
FUNCTION_PARAM_2_DESC = "Länge des Rechtecks mit Längeneinheit (z.B. '10 cm', '100 mm', '0.1 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_2_EXAMPLE = "10 cm"

FUNCTION_PARAM_3_NAME = "breite"
FUNCTION_PARAM_3_DESC = "Breite des Rechtecks mit Längeneinheit (z.B. '5 cm', '50 mm', '0.05 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_3_EXAMPLE = "5 cm"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst die Rechteckformel A = l × b nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

🔄 BATCH-MODUS: Unterstützt Listen von Parametern für Massenberechnungen!
⚠️ WICHTIG: Bei Batch-Berechnungen müssen ALLE Parameter Listen gleicher Länge sein!
Jeder Index repräsentiert einen vollständigen Parametersatz.

Beispiel Batch-Aufruf:
solve_rechteck(
    flaeche=['target', '40 cm²', 'target'],
    laenge=['10 cm', '8 cm', '12 cm'],
    breite=['4 cm', 'target', '6 cm']
)
Dies berechnet 3 separate Rechtecke mit jeweils einem anderen Target-Parameter.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel A = l × b)
{FUNCTION_PARAM_2_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel l = A / b)
{FUNCTION_PARAM_3_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel b = A / l)

Rechteckformel: A = l × b

Anwendungsbereich: Flächenberechnungen, Geometrie, Grundstücksmessung
Einschränkungen: Alle Werte müssen positiv sein
Genauigkeit: Exakte analytische Lösung"""

# Parameter-Definitionen für Metadaten
PARAMETER_FLAECHE = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "batch_example": ["target", "40 cm²", "target"]  # NEU
}

PARAMETER_LAENGE = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE,
    "batch_example": ["10 cm", "8 cm", "12 cm"]  # NEU
}

PARAMETER_BREITE = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_3_DESC,
    "example": FUNCTION_PARAM_3_EXAMPLE,
    "batch_example": ["4 cm", "target", "6 cm"]  # NEU
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
            FUNCTION_PARAM_1_NAME: ["target", "40 cm²", "target"],
            FUNCTION_PARAM_2_NAME: ["10 cm", "8 cm", "12 cm"],
            FUNCTION_PARAM_3_NAME: ["4 cm", "target", "6 cm"]
        },
        "output": f"Liste von 3 Ergebnissen, jeweils mit unterschiedlichem Target-Parameter"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_2_NAME} (analytisch) bei gegebenen {FUNCTION_PARAM_1_NAME} und {FUNCTION_PARAM_3_NAME}", 
        "input": {FUNCTION_PARAM_1_NAME: FUNCTION_PARAM_1_EXAMPLE, FUNCTION_PARAM_2_NAME: "target", FUNCTION_PARAM_3_NAME: FUNCTION_PARAM_3_EXAMPLE},
        "output": f"{FUNCTION_PARAM_2_NAME} in optimierter Einheit mit geschlossener Formel"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_3_NAME} (analytisch) bei gegebenen {FUNCTION_PARAM_1_NAME} und {FUNCTION_PARAM_2_NAME}",
        "input": {FUNCTION_PARAM_1_NAME: FUNCTION_PARAM_1_EXAMPLE, FUNCTION_PARAM_2_NAME: FUNCTION_PARAM_2_EXAMPLE, FUNCTION_PARAM_3_NAME: "target"},
        "output": f"{FUNCTION_PARAM_3_NAME} in optimierter Einheit mit geschlossener Formel"
    }
]

# Annahmen
TOOL_ASSUMPTIONS = [
    "Rechteck mit zwei bekannten Seitenlängen",
    "Alle Eingabewerte sind positiv",
    "Winkel sind alle 90 Grad"
]

# Einschränkungen  
TOOL_LIMITATIONS = [
    "Nur für positive Werte gültig",
    "Nur für rechteckige Formen",
    "Nicht für schräge Vierecke geeignet"
]

# Mathematische Grundlagen
MATHEMATICAL_FOUNDATION = "Rechteckformel: A = l × b, wobei l die Länge und b die Breite ist"

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
        'flaeche': ['target', '40 cm²', 'target'],
        'laenge': ['10 cm', '8 cm', '12 cm'],
        'breite': ['4 cm', 'target', '6 cm']
    }
    Output: [
        {'flaeche': 'target', 'laenge': '10 cm', 'breite': '4 cm'},
        {'flaeche': '40 cm²', 'laenge': '8 cm', 'breite': 'target'},
        {'flaeche': 'target', 'laenge': '12 cm', 'breite': '6 cm'}
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

def solve_rechteck(
    # ⚠️ Hier die konfigurierten Parameter-Namen und -Beschreibungen verwenden:
    flaeche: Annotated[Union[str, List[str]], FUNCTION_PARAM_1_DESC],  
    laenge: Annotated[Union[str, List[str]], FUNCTION_PARAM_2_DESC],
    breite: Annotated[Union[str, List[str]], FUNCTION_PARAM_3_DESC]
) -> Union[Dict, List[Dict]]:
    """
    Löst die Rechteckformel A = l × b nach verschiedenen Variablen auf.
    
    Unterstützt Batch-Verarbeitung: Wenn Listen als Parameter übergeben werden,
    müssen ALLE Parameter Listen gleicher Länge sein. Jeder Index repräsentiert
    einen vollständigen Parametersatz.
    """
    try:
        # Erstelle Parameter-Dictionary
        params_dict = {
            'flaeche': flaeche,
            'laenge': laenge, 
            'breite': breite
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
                combinations[0]['laenge'],
                combinations[0]['breite']
            )
        
        # Batch-Verarbeitung: Berechne alle Kombinationen
        results = []
        for i, combo in enumerate(combinations):
            try:
                result = _solve_single(
                    combo['flaeche'],
                    combo['laenge'],
                    combo['breite']
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
            "error": f"Fehler in solve_rechteck: {str(e)}",
            "type": type(e).__name__
        }

def _solve_single(
    flaeche: str,
    laenge: str,
    breite: str
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
            'var2': laenge, 
            'var3': breite
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
                "example": f"solve_rechteck({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 2:
            return {
                "error": f"Genau 2 Parameter müssen Werte mit Einheiten haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": f"solve_rechteck({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')"
            }
        
        target_param = target_params[0]
        
        # Erstelle kwargs für Validierung (nur gegebene Parameter)
        validation_kwargs = {}
        param_names = {
            'var1': 'flaeche',
            'var2': 'laenge', 
            'var3': 'breite'
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
            # Berechne Fläche: A = l × b
            laenge_si = params['laenge']['si_value']
            breite_si = params['breite']['si_value']
            
            if laenge_si <= 0 or breite_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            flaeche_si = laenge_si * breite_si
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['breite']['original_unit'] if breite_si < laenge_si else params['laenge']['original_unit']
            flaeche_quantity = flaeche_si * ureg.meter**2
            flaeche_optimized = optimize_output_unit(flaeche_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "flaeche",
                "gegebene_werte": {
                    "laenge": laenge,
                    "breite": breite
                },
                "ergebnis": {
                    "flaeche": f"{flaeche_optimized.magnitude:.6g} {flaeche_optimized.units}"
                },
                "formel": "A = l × b",
                "si_werte": {
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "laenge_si": f"{laenge_si:.6g} m",
                    "breite_si": f"{breite_si:.6g} m"
                }
            }
            
        elif target_param == 'var2':  # laenge
            # Berechne Länge: l = A / b
            flaeche_si = params['flaeche']['si_value']
            breite_si = params['breite']['si_value']
            
            if flaeche_si <= 0 or breite_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            laenge_si = flaeche_si / breite_si
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['breite']['original_unit']
            laenge_quantity = laenge_si * ureg.meter
            laenge_optimized = optimize_output_unit(laenge_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "laenge",
                "gegebene_werte": {
                    "flaeche": flaeche,
                    "breite": breite
                },
                "ergebnis": {
                    "laenge": f"{laenge_optimized.magnitude:.6g} {laenge_optimized.units}"
                },
                "formel": "l = A / b",
                "si_werte": {
                    "laenge_si": f"{laenge_si:.6g} m",
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "breite_si": f"{breite_si:.6g} m"
                }
            }
            
        elif target_param == 'var3':  # breite
            # Berechne Breite: b = A / l
            flaeche_si = params['flaeche']['si_value']
            laenge_si = params['laenge']['si_value']
            
            if flaeche_si <= 0 or laenge_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            breite_si = flaeche_si / laenge_si
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['laenge']['original_unit']
            breite_quantity = breite_si * ureg.meter
            breite_optimized = optimize_output_unit(breite_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "breite",
                "gegebene_werte": {
                    "flaeche": flaeche,
                    "laenge": laenge
                },
                "ergebnis": {
                    "breite": f"{breite_optimized.magnitude:.6g} {breite_optimized.units}"
                },
                "formel": "b = A / l",
                "si_werte": {
                    "breite_si": f"{breite_si:.6g} m",
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "laenge_si": f"{laenge_si:.6g} m"
                }
            }
        
    except UnitsError as e:
        return {"error": f"Einheiten-Fehler: {str(e)}"}
    except Exception as e:
        return {
            "error": f"Fehler in solve_rechteck: {str(e)}",
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
            FUNCTION_PARAM_2_NAME: PARAMETER_LAENGE,
            FUNCTION_PARAM_3_NAME: PARAMETER_BREITE,
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
        "parameter_laenge": PARAMETER_LAENGE,
        "parameter_breite": PARAMETER_BREITE
    }

def calculate(flaeche: Union[str, List[str]], laenge: Union[str, List[str]], breite: Union[str, List[str]]) -> Union[Dict, List[Dict]]:
    """Legacy-Funktion für Kompatibilität - unterstützt nun auch Batch-Mode"""
    return solve_rechteck(flaeche, laenge, breite)


