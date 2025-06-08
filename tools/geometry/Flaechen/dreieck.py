#!/usr/bin/env python3
"""
Dreieck-Fläche - Berechnet Fläche, Grundseite oder Höhe eines Dreiecks

Berechnet Dreieckflächen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel A = (g × h) / 2 nach verschiedenen Variablen auf.
Lösbare Variablen: flaeche, grundseite, hoehe

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke

🔄 BATCH-MODUS: Unterstützt Verarbeitung mehrerer Parametersätze gleichzeitig!
Beispiel: grundseite=["10 mm", "20 mm", "30 mm"] statt grundseite="10 mm"

Dreiecksformel: A = (g × h) / 2 - Berechnet die Fläche eines Dreiecks aus Grundseite und Höhe
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "dreieck_flaeche"
TOOL_TAGS = ["elementar"]
TOOL_SHORT_DESCRIPTION = "Dreieck-Fläche - Berechnet Fläche, Grundseite oder Höhe"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic"  # Alle Berechnungen sind analytisch lösbar

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
FUNCTION_PARAM_1_NAME = "flaeche"
FUNCTION_PARAM_1_DESC = "Fläche des Dreiecks mit Flächeneinheit (z.B. '25.5 cm²', '0.1 m²', '255 mm²') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_1_EXAMPLE = "25.5 cm²"

FUNCTION_PARAM_2_NAME = "grundseite"
FUNCTION_PARAM_2_DESC = "Grundseite des Dreiecks mit Längeneinheit (z.B. '10 cm', '5.2 mm', '0.1 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_2_EXAMPLE = "10 cm"

FUNCTION_PARAM_3_NAME = "hoehe"
FUNCTION_PARAM_3_DESC = "Höhe des Dreiecks mit Längeneinheit (z.B. '8 cm', '25 mm', '0.08 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_3_EXAMPLE = "8 cm"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst die Dreieckformel A = (g × h) / 2 nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

🔄 BATCH-MODUS: Unterstützt Listen von Parametern für Massenberechnungen!
⚠️ WICHTIG: Bei Batch-Berechnungen müssen ALLE Parameter Listen gleicher Länge sein!
Jeder Index repräsentiert einen vollständigen Parametersatz.

Beispiel Batch-Aufruf:
solve_dreieck(
    flaeche=['target', '20 cm²', 'target'],
    grundseite=['10 cm', '8 cm', '12 cm'],
    hoehe=['4 cm', 'target', '6 cm']
)
Dies berechnet 3 separate Dreiecke mit jeweils einem anderen Target-Parameter.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel A = (g × h) / 2)
{FUNCTION_PARAM_2_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel g = 2A / h)
{FUNCTION_PARAM_3_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel h = 2A / g)

Dreiecksformel: A = (g × h) / 2

Anwendungsbereich: Geometrische Berechnungen, Konstruktion, Dachflächen, Grundstücksberechnungen
Einschränkungen: Alle Werte müssen positiv sein
Genauigkeit: Exakte analytische Lösung"""

# Parameter-Definitionen für Metadaten
PARAMETER_FLAECHE = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "batch_example": ["target", "20 cm²", "target"]  # NEU
}

PARAMETER_GRUNDSEITE = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE,
    "batch_example": ["10 cm", "8 cm", "12 cm"]  # NEU
}

PARAMETER_HOEHE = {
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
            FUNCTION_PARAM_1_NAME: ["target", "20 cm²", "target"],
            FUNCTION_PARAM_2_NAME: ["10 cm", "8 cm", "12 cm"],
            FUNCTION_PARAM_3_NAME: ["4 cm", "target", "6 cm"]
        },
        "output": f"Liste von 3 Ergebnissen, jeweils mit unterschiedlichem Target-Parameter"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_2_NAME} (analytisch) bei gegebenen {FUNCTION_PARAM_1_NAME} und {FUNCTION_PARAM_3_NAME}", 
        "input": {FUNCTION_PARAM_1_NAME: "40 cm²", FUNCTION_PARAM_2_NAME: "target", FUNCTION_PARAM_3_NAME: FUNCTION_PARAM_3_EXAMPLE},
        "output": f"{FUNCTION_PARAM_2_NAME} in optimierter Einheit mit geschlossener Formel"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_3_NAME} (analytisch) bei gegebenen {FUNCTION_PARAM_1_NAME} und {FUNCTION_PARAM_2_NAME}",
        "input": {FUNCTION_PARAM_1_NAME: "40 cm²", FUNCTION_PARAM_2_NAME: FUNCTION_PARAM_2_EXAMPLE, FUNCTION_PARAM_3_NAME: "target"},
        "output": f"{FUNCTION_PARAM_3_NAME} in optimierter Einheit mit geschlossener Formel"
    }
]

# Annahmen
TOOL_ASSUMPTIONS = [
    "Dreieck mit bekannter Grundseite und zugehöriger Höhe",
    "Alle Eingabewerte sind positiv",
    "Höhe steht senkrecht zur Grundseite"
]

# Einschränkungen  
TOOL_LIMITATIONS = [
    "Nur für positive Werte gültig",
    "Höhe muss zur Grundseite gehören",
    "Nicht für spitze Winkel ohne entsprechende Höhe"
]

# Mathematische Grundlagen
MATHEMATICAL_FOUNDATION = "Dreiecksformel: A = (g × h) / 2, wobei g die Grundseite und h die Höhe ist"

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
        'flaeche': ['target', '20 cm²', 'target'],
        'grundseite': ['10 cm', '8 cm', '12 cm'],
        'hoehe': ['4 cm', 'target', '6 cm']
    }
    Output: [
        {'flaeche': 'target', 'grundseite': '10 cm', 'hoehe': '4 cm'},
        {'flaeche': '20 cm²', 'grundseite': '8 cm', 'hoehe': 'target'},
        {'flaeche': 'target', 'grundseite': '12 cm', 'hoehe': '6 cm'}
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

def solve_dreieck(
    # ⚠️ Hier die konfigurierten Parameter-Namen und -Beschreibungen verwenden:
    flaeche: Annotated[Union[str, List[str]], FUNCTION_PARAM_1_DESC],  
    grundseite: Annotated[Union[str, List[str]], FUNCTION_PARAM_2_DESC],
    hoehe: Annotated[Union[str, List[str]], FUNCTION_PARAM_3_DESC]
) -> Union[Dict, List[Dict]]:
    """
    Löst die Dreiecksformel A = (g × h) / 2 nach verschiedenen Variablen auf.
    
    Unterstützt Batch-Verarbeitung: Wenn Listen als Parameter übergeben werden,
    müssen ALLE Parameter Listen gleicher Länge sein. Jeder Index repräsentiert
    einen vollständigen Parametersatz.
    """
    try:
        # Erstelle Parameter-Dictionary
        params_dict = {
            'flaeche': flaeche,
            'grundseite': grundseite, 
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
                combinations[0]['grundseite'],
                combinations[0]['hoehe']
            )
        
        # Batch-Verarbeitung: Berechne alle Kombinationen
        results = []
        for i, combo in enumerate(combinations):
            try:
                result = _solve_single(
                    combo['flaeche'],
                    combo['grundseite'],
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
            "error": f"Fehler in solve_dreieck: {str(e)}",
            "type": type(e).__name__
        }

def _solve_single(
    flaeche: str,
    grundseite: str,
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
            'var2': grundseite, 
            'var3': hoehe
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
                "example": f"solve_dreieck({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 2:
            return {
                "error": f"Genau 2 Parameter müssen Werte mit Einheiten haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": f"solve_dreieck({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')"
            }
        
        target_param = target_params[0]
        
        # Erstelle kwargs für Validierung (nur gegebene Parameter)
        validation_kwargs = {}
        param_names = {
            'var1': 'flaeche',
            'var2': 'grundseite', 
            'var3': 'hoehe'
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
            # Berechne Fläche: A = (g × h) / 2
            grundseite_si = params['grundseite']['si_value']
            hoehe_si = params['hoehe']['si_value']
            
            if grundseite_si <= 0 or hoehe_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            flaeche_si = (grundseite_si * hoehe_si) / 2
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['hoehe']['original_unit'] if hoehe_si < grundseite_si else params['grundseite']['original_unit']
            flaeche_quantity = flaeche_si * ureg.meter**2
            flaeche_optimized = optimize_output_unit(flaeche_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "flaeche",
                "gegebene_werte": {
                    "grundseite": grundseite,
                    "hoehe": hoehe
                },
                "ergebnis": {
                    "flaeche": f"{flaeche_optimized.magnitude:.6g} {flaeche_optimized.units}"
                },
                "formel": "A = (g × h) / 2",
                "si_werte": {
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "grundseite_si": f"{grundseite_si:.6g} m",
                    "hoehe_si": f"{hoehe_si:.6g} m"
                }
            }
            
        elif target_param == 'var2':  # grundseite
            # Berechne Grundseite: g = 2A / h
            flaeche_si = params['flaeche']['si_value']
            hoehe_si = params['hoehe']['si_value']
            
            if flaeche_si <= 0 or hoehe_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            grundseite_si = (2 * flaeche_si) / hoehe_si
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['hoehe']['original_unit']
            grundseite_quantity = grundseite_si * ureg.meter
            grundseite_optimized = optimize_output_unit(grundseite_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "grundseite",
                "gegebene_werte": {
                    "flaeche": flaeche,
                    "hoehe": hoehe
                },
                "ergebnis": {
                    "grundseite": f"{grundseite_optimized.magnitude:.6g} {grundseite_optimized.units}"
                },
                "formel": "g = 2A / h",
                "si_werte": {
                    "grundseite_si": f"{grundseite_si:.6g} m",
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "hoehe_si": f"{hoehe_si:.6g} m"
                }
            }
            
        elif target_param == 'var3':  # hoehe
            # Berechne Höhe: h = 2A / g
            flaeche_si = params['flaeche']['si_value']
            grundseite_si = params['grundseite']['si_value']
            
            if flaeche_si <= 0 or grundseite_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            hoehe_si = (2 * flaeche_si) / grundseite_si
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['grundseite']['original_unit']
            hoehe_quantity = hoehe_si * ureg.meter
            hoehe_optimized = optimize_output_unit(hoehe_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "hoehe",
                "gegebene_werte": {
                    "flaeche": flaeche,
                    "grundseite": grundseite
                },
                "ergebnis": {
                    "hoehe": f"{hoehe_optimized.magnitude:.6g} {hoehe_optimized.units}"
                },
                "formel": "h = 2A / g",
                "si_werte": {
                    "hoehe_si": f"{hoehe_si:.6g} m",
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "grundseite_si": f"{grundseite_si:.6g} m"
                }
            }
        
    except UnitsError as e:
        return {"error": f"Einheiten-Fehler: {str(e)}"}
    except Exception as e:
        return {
            "error": f"Fehler in solve_dreieck: {str(e)}",
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
            FUNCTION_PARAM_2_NAME: PARAMETER_GRUNDSEITE,
            FUNCTION_PARAM_3_NAME: PARAMETER_HOEHE,
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
        "parameter_grundseite": PARAMETER_GRUNDSEITE,
        "parameter_hoehe": PARAMETER_HOEHE
    }

def calculate(flaeche: Union[str, List[str]], grundseite: Union[str, List[str]], hoehe: Union[str, List[str]]) -> Union[Dict, List[Dict]]:
    """Legacy-Funktion für Kompatibilität - unterstützt nun auch Batch-Mode"""
    return solve_dreieck(flaeche, grundseite, hoehe) 