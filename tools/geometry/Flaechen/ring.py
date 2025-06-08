#!/usr/bin/env python3
"""
Kreisring-Fläche - Berechnet Fläche zwischen zwei konzentrischen Kreisen

Berechnet Kreisring-Flächen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel A = π × (R² - r²) nach verschiedenen Variablen auf.
Lösbare Variablen: flaeche, aussenradius, innenradius

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke

🔄 BATCH-MODUS: Unterstützt Verarbeitung mehrerer Parametersätze gleichzeitig!
Beispiel: aussenradius=["5 cm", "7 cm", "9 cm"] statt aussenradius="5 cm"

Kreisring: Fläche zwischen äußerem und innerem Kreis - A = π × (R² - r²) = π × (Raußen² - Rinnen²)
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "kreisring_flaeche"
TOOL_TAGS = ["elementar"]
TOOL_SHORT_DESCRIPTION = "Kreisring-Fläche - Berechnet Ring-Fläche oder Radien"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic"  # Alle Berechnungen sind analytisch lösbar

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
FUNCTION_PARAM_1_NAME = "flaeche"
FUNCTION_PARAM_1_DESC = "Fläche des Rings mit Flächeneinheit (z.B. '62.83 cm²', '0.006283 m²', '6283 mm²') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_1_EXAMPLE = "62.83 cm²"

FUNCTION_PARAM_2_NAME = "aussenradius"
FUNCTION_PARAM_2_DESC = "Außenradius des Rings mit Längeneinheit (z.B. '5 cm', '50 mm', '0.05 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_2_EXAMPLE = "5 cm"

FUNCTION_PARAM_3_NAME = "innenradius"
FUNCTION_PARAM_3_DESC = "Innenradius des Rings mit Längeneinheit (z.B. '3 cm', '30 mm', '0.03 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_3_EXAMPLE = "3 cm"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst die Kreisring-Formel A = π × (R² - r²) nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

🔄 BATCH-MODUS: Unterstützt Listen von Parametern für Massenberechnungen!
⚠️ WICHTIG: Bei Batch-Berechnungen müssen ALLE Parameter Listen gleicher Länge sein!
Jeder Index repräsentiert einen vollständigen Parametersatz.

Beispiel Batch-Aufruf:
solve_ring(
    flaeche=['target', '50.27 cm²', 'target'],
    aussenradius=['5 cm', '6 cm', '7 cm'],
    innenradius=['3 cm', 'target', '4 cm']
)
Dies berechnet 3 separate Ringe mit jeweils einem anderen Target-Parameter.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel A = π × (R² - r²))
{FUNCTION_PARAM_2_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel R = √((A/π) + r²))
{FUNCTION_PARAM_3_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel r = √(R² - (A/π)))

Kreisring-Formel: A = π × (R² - r²)

Anwendungsbereich: Maschinenbau (Rohre, Ringe), Architektur (Hohlprofile), Flächenberechnungen
Einschränkungen: Äußerer Radius > Innerer Radius > 0
Genauigkeit: Exakte analytische Lösung"""

# Parameter-Definitionen für Metadaten
PARAMETER_FLAECHE = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "batch_example": ["target", "50.27 cm²", "target"]  # NEU
}

PARAMETER_AUSSENRADIUS = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE,
    "batch_example": ["5 cm", "6 cm", "7 cm"]  # NEU
}

PARAMETER_INNENRADIUS = {
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
            FUNCTION_PARAM_1_NAME: ["target", "50.27 cm²", "target"],
            FUNCTION_PARAM_2_NAME: ["5 cm", "6 cm", "7 cm"],
            FUNCTION_PARAM_3_NAME: ["3 cm", "target", "4 cm"]
        },
        "output": f"Liste von 3 Ergebnissen, jeweils mit unterschiedlichem Target-Parameter"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_2_NAME} (analytisch) bei gegebenen {FUNCTION_PARAM_1_NAME} und {FUNCTION_PARAM_3_NAME}", 
        "input": {FUNCTION_PARAM_1_NAME: "50.27 cm²", FUNCTION_PARAM_2_NAME: "target", FUNCTION_PARAM_3_NAME: FUNCTION_PARAM_3_EXAMPLE},
        "output": f"{FUNCTION_PARAM_2_NAME} in optimierter Einheit mit geschlossener Formel"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_3_NAME} (analytisch) bei gegebenen {FUNCTION_PARAM_1_NAME} und {FUNCTION_PARAM_2_NAME}",
        "input": {FUNCTION_PARAM_1_NAME: "50.27 cm²", FUNCTION_PARAM_2_NAME: FUNCTION_PARAM_2_EXAMPLE, FUNCTION_PARAM_3_NAME: "target"},
        "output": f"{FUNCTION_PARAM_3_NAME} in optimierter Einheit mit geschlossener Formel"
    }
]

# Annahmen
TOOL_ASSUMPTIONS = [
    "Konzentrische Kreise mit gleichem Mittelpunkt",
    "Alle Eingabewerte sind positiv",
    "Außenradius ist größer als Innenradius"
]

# Einschränkungen  
TOOL_LIMITATIONS = [
    "Nur für positive Werte gültig",
    "Außenradius muss größer als Innenradius sein",
    "Nicht für vollständige Kreise geeignet"
]

# Mathematische Grundlagen
MATHEMATICAL_FOUNDATION = "Kreisring-Formel: A = π × (R² - r²), wobei R der Außen- und r der Innenradius ist"

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
        'flaeche': ['target', '50.27 cm²', 'target'],
        'aussenradius': ['5 cm', '6 cm', '7 cm'],
        'innenradius': ['3 cm', 'target', '4 cm']
    }
    Output: [
        {'flaeche': 'target', 'aussenradius': '5 cm', 'innenradius': '3 cm'},
        {'flaeche': '50.27 cm²', 'aussenradius': '6 cm', 'innenradius': 'target'},
        {'flaeche': 'target', 'aussenradius': '7 cm', 'innenradius': '4 cm'}
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

def solve_ring(
    # ⚠️ Hier die konfigurierten Parameter-Namen und -Beschreibungen verwenden:
    flaeche: Annotated[Union[str, List[str]], FUNCTION_PARAM_1_DESC],  
    aussenradius: Annotated[Union[str, List[str]], FUNCTION_PARAM_2_DESC],
    innenradius: Annotated[Union[str, List[str]], FUNCTION_PARAM_3_DESC]
) -> Union[Dict, List[Dict]]:
    """
    Löst die Kreisring-Formel A = π × (R² - r²) nach verschiedenen Variablen auf.
    
    Unterstützt Batch-Verarbeitung: Wenn Listen als Parameter übergeben werden,
    müssen ALLE Parameter Listen gleicher Länge sein. Jeder Index repräsentiert
    einen vollständigen Parametersatz.
    """
    try:
        # Erstelle Parameter-Dictionary
        params_dict = {
            'flaeche': flaeche,
            'aussenradius': aussenradius, 
            'innenradius': innenradius
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
                combinations[0]['aussenradius'],
                combinations[0]['innenradius']
            )
        
        # Batch-Verarbeitung: Berechne alle Kombinationen
        results = []
        for i, combo in enumerate(combinations):
            try:
                result = _solve_single(
                    combo['flaeche'],
                    combo['aussenradius'],
                    combo['innenradius']
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
            "error": f"Fehler in solve_ring: {str(e)}",
            "type": type(e).__name__
        }

def _solve_single(
    flaeche: str,
    aussenradius: str,
    innenradius: str
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
            'var2': aussenradius, 
            'var3': innenradius
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
                "example": f"solve_ring({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 2:
            return {
                "error": f"Genau 2 Parameter müssen Werte mit Einheiten haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": f"solve_ring({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')"
            }
        
        target_param = target_params[0]
        
        # Erstelle kwargs für Validierung (nur gegebene Parameter)
        validation_kwargs = {}
        param_names = {
            'var1': 'flaeche',
            'var2': 'aussenradius', 
            'var3': 'innenradius'
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
        
        # Ring-Formel: A = π × (R² - r²) wobei R = Außenradius, r = Innenradius
        # Umgestellt: R = √((A/π) + r²)
        #            r = √(R² - (A/π))
        
        if target_param == 'var1':  # flaeche
            # Berechne Fläche: A = π × (R² - r²)
            R_si = params['aussenradius']['si_value']
            r_si = params['innenradius']['si_value']
            
            if R_si <= 0 or r_si <= 0:
                return {"error": "Alle Radien müssen positiv sein"}
            
            if r_si >= R_si:
                return {"error": "Innenradius muss kleiner als Außenradius sein"}
            
            flaeche_si = math.pi * (R_si**2 - r_si**2)
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['aussenradius']['original_unit']
            flaeche_quantity = flaeche_si * ureg.meter**2
            flaeche_optimized = optimize_output_unit(flaeche_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "flaeche",
                "gegebene_werte": {
                    "aussenradius": aussenradius,
                    "innenradius": innenradius
                },
                "ergebnis": {
                    "flaeche": f"{flaeche_optimized.magnitude:.6g} {flaeche_optimized.units}"
                },
                "formel": "A = π × (R² - r²)",
                "si_werte": {
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "aussenradius_si": f"{R_si:.6g} m",
                    "innenradius_si": f"{r_si:.6g} m"
                }
            }
            
        elif target_param == 'var2':  # aussenradius
            # Berechne Außenradius: R = √((A/π) + r²)
            flaeche_si = params['flaeche']['si_value']
            r_si = params['innenradius']['si_value']
            
            if flaeche_si <= 0 or r_si <= 0:
                return {"error": "Fläche und Innenradius müssen positiv sein"}
            
            R_squared = (flaeche_si / math.pi) + r_si**2
            
            if R_squared <= 0:
                return {"error": "Ungültige Parameter - kein positiver Außenradius möglich"}
            
            R_si = math.sqrt(R_squared)
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['innenradius']['original_unit']
            radius_quantity = R_si * ureg.meter
            radius_optimized = optimize_output_unit(radius_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "aussenradius",
                "gegebene_werte": {
                    "flaeche": flaeche,
                    "innenradius": innenradius
                },
                "ergebnis": {
                    "aussenradius": f"{radius_optimized.magnitude:.6g} {radius_optimized.units}"
                },
                "formel": "R = √((A/π) + r²)",
                "si_werte": {
                    "aussenradius_si": f"{R_si:.6g} m",
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "innenradius_si": f"{r_si:.6g} m"
                }
            }
            
        elif target_param == 'var3':  # innenradius
            # Berechne Innenradius: r = √(R² - (A/π))
            flaeche_si = params['flaeche']['si_value']
            R_si = params['aussenradius']['si_value']
            
            if flaeche_si <= 0 or R_si <= 0:
                return {"error": "Fläche und Außenradius müssen positiv sein"}
            
            r_squared = R_si**2 - (flaeche_si / math.pi)
            
            if r_squared < 0:
                return {"error": "Die gegebene Fläche ist zu groß für den Außenradius"}
            
            r_si = math.sqrt(r_squared)
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['aussenradius']['original_unit']
            radius_quantity = r_si * ureg.meter
            radius_optimized = optimize_output_unit(radius_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "innenradius",
                "gegebene_werte": {
                    "flaeche": flaeche,
                    "aussenradius": aussenradius
                },
                "ergebnis": {
                    "innenradius": f"{radius_optimized.magnitude:.6g} {radius_optimized.units}"
                },
                "formel": "r = √(R² - (A/π))",
                "si_werte": {
                    "innenradius_si": f"{r_si:.6g} m",
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "aussenradius_si": f"{R_si:.6g} m"
                }
            }
        
    except UnitsError as e:
        return {"error": f"Einheiten-Fehler: {str(e)}"}
    except Exception as e:
        return {
            "error": f"Fehler in solve_ring: {str(e)}",
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
            FUNCTION_PARAM_2_NAME: PARAMETER_AUSSENRADIUS,
            FUNCTION_PARAM_3_NAME: PARAMETER_INNENRADIUS,
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
        "parameter_aussenradius": PARAMETER_AUSSENRADIUS,
        "parameter_innenradius": PARAMETER_INNENRADIUS
    }

def calculate(flaeche: Union[str, List[str]], aussenradius: Union[str, List[str]], innenradius: Union[str, List[str]]) -> Union[Dict, List[Dict]]:
    """Legacy-Funktion für Kompatibilität - unterstützt nun auch Batch-Mode"""
    return solve_ring(flaeche, aussenradius, innenradius) 