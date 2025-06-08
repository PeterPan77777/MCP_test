#!/usr/bin/env python3
"""
Kreis-Fläche - Berechnet Fläche, Radius oder Durchmesser

Berechnet Kreisflächen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel A = π × r² nach verschiedenen Variablen auf.
Lösbare Variablen: flaeche, radius, durchmesser

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke

🔄 BATCH-MODUS: Unterstützt Verarbeitung mehrerer Parametersätze gleichzeitig!
Beispiel: radius=["10 mm", "20 mm", "30 mm"] statt radius="10 mm"

Kreisformel: A = π × r² - Berechnet die Fläche eines Kreises aus Radius oder Durchmesser
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "kreis_flaeche"
TOOL_TAGS = ["elementar"]
TOOL_SHORT_DESCRIPTION = "Kreis-Fläche - Berechnet Fläche, Radius oder Durchmesser"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic"  # Alle Berechnungen sind analytisch lösbar

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
FUNCTION_PARAM_1_NAME = "flaeche"
FUNCTION_PARAM_1_DESC = "Fläche des Kreises mit Flächeneinheit (z.B. '78.54 cm²', '0.007854 m²', '7854 mm²') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_1_EXAMPLE = "78.54 cm²"

FUNCTION_PARAM_2_NAME = "radius"
FUNCTION_PARAM_2_DESC = "Radius des Kreises mit Längeneinheit (z.B. '5 cm', '50 mm', '0.05 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_2_EXAMPLE = "5 cm"

FUNCTION_PARAM_3_NAME = "durchmesser"
FUNCTION_PARAM_3_DESC = "Durchmesser des Kreises mit Längeneinheit (z.B. '10 cm', '100 mm', '0.1 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_3_EXAMPLE = "10 cm"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst die Kreisformel A = π × r² nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

🔄 BATCH-MODUS: Unterstützt Listen von Parametern für Massenberechnungen!
⚠️ WICHTIG: Bei Batch-Berechnungen müssen ALLE Parameter Listen gleicher Länge sein!
Jeder Index repräsentiert einen vollständigen Parametersatz.

Beispiel Batch-Aufruf:
solve_kreis(
    flaeche=['target', '10 cm²', 'target'],
    radius=['5 cm', '10 cm', '15 cm'],
    durchmesser=['30 cm', 'target', '45 cm']
)
Dies berechnet 3 separate Kreise mit jeweils einem anderen Target-Parameter.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel A = π × r²)
{FUNCTION_PARAM_2_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel r = √(A/π))
{FUNCTION_PARAM_3_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel d = 2 × √(A/π))

Kreisformel: A = π × r²

Anwendungsbereich: Geometrische Berechnungen, Flächenbestimmung, Konstruktion, Rohrdimensionierung
Einschränkungen: Alle Werte müssen positiv sein, perfekte Kreisform angenommen
Genauigkeit: Exakte analytische Lösung"""

# Parameter-Definitionen für Metadaten
PARAMETER_FLAECHE = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "batch_example": ["target", "50 cm²", "100 cm²"]  # NEU
}

PARAMETER_RADIUS = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE,
    "batch_example": ["5 cm", "target", "10 cm"]  # NEU
}

PARAMETER_DURCHMESSER = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_3_DESC,
    "example": FUNCTION_PARAM_3_EXAMPLE,
    "batch_example": ["10 cm", "20 cm", "target"]  # NEU
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
            FUNCTION_PARAM_1_NAME: ["target", "50 cm²", "target"],
            FUNCTION_PARAM_2_NAME: ["5 cm", "target", "15 cm"],
            FUNCTION_PARAM_3_NAME: ["10 cm", "20 cm", "30 cm"]
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
    "Perfekter Kreis (keine Verformungen)",
    "Alle Eingabewerte sind positiv",
    "Euklidische Geometrie",
    "Radius = Durchmesser / 2"
]

# Einschränkungen  
TOOL_LIMITATIONS = [
    "Nur für zweidimensionale Kreise",
    "Keine Berücksichtigung von Materialdicke",
    "Keine Toleranzberechnungen",
    "Nur für positive Werte gültig"
]

# Mathematische Grundlagen
MATHEMATICAL_FOUNDATION = "Kreisformel: A = π × r², wobei r der Radius ist. Alternative: A = π × (d/2)², wobei d der Durchmesser ist"

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
        'flaeche': ['target', '10 cm²', 'target'],
        'radius': ['5 cm', '10 cm', '15 cm'],
        'durchmesser': ['30 cm', 'target', '45 cm']
    }
    Output: [
        {'flaeche': 'target', 'radius': '5 cm', 'durchmesser': '30 cm'},
        {'flaeche': '10 cm²', 'radius': '10 cm', 'durchmesser': 'target'},
        {'flaeche': 'target', 'radius': '15 cm', 'durchmesser': '45 cm'}
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

def solve_kreis(
    # ⚠️ Hier die konfigurierten Parameter-Namen und -Beschreibungen verwenden:
    flaeche: Annotated[Union[str, List[str]], FUNCTION_PARAM_1_DESC],  
    radius: Annotated[Union[str, List[str]], FUNCTION_PARAM_2_DESC],
    durchmesser: Annotated[Union[str, List[str]], FUNCTION_PARAM_3_DESC]
) -> Union[Dict, List[Dict]]:
    """
    Löst die Kreisformel A = π × r² nach verschiedenen Variablen auf.
    
    Unterstützt Batch-Verarbeitung: Wenn Listen als Parameter übergeben werden,
    müssen ALLE Parameter Listen gleicher Länge sein. Jeder Index repräsentiert
    einen vollständigen Parametersatz.
    """
    try:
        # Erstelle Parameter-Dictionary
        params_dict = {
            'flaeche': flaeche,
            'radius': radius, 
            'durchmesser': durchmesser
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
                combinations[0]['radius'],
                combinations[0]['durchmesser']
            )
        
        # Batch-Verarbeitung: Berechne alle Kombinationen
        results = []
        for i, combo in enumerate(combinations):
            try:
                result = _solve_single(
                    combo['flaeche'],
                    combo['radius'],
                    combo['durchmesser']
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
            "error": f"Fehler in solve_kreis: {str(e)}",
            "type": type(e).__name__
        }

def _solve_single(
    flaeche: str,
    radius: str,
    durchmesser: str
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
            'var2': radius, 
            'var3': durchmesser
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
                "example": f"solve_kreis({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) < 1:
            return {
                "error": f"Mindestens ein Parameter muss Werte mit Einheiten haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": f"solve_kreis({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')"
            }
        
        target_param = target_params[0]
        
        # Erstelle kwargs für Validierung (nur gegebene Parameter)
        validation_kwargs = {}
        param_names = {
            'var1': 'flaeche',
            'var2': 'radius', 
            'var3': 'durchmesser'
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
            # Bestimme Radius (aus radius oder durchmesser)
            if 'radius' in params:
                r_si = params['radius']['si_value']
                ref_unit = params['radius']['original_unit']
                gegebene_werte = {"radius": radius}
            elif 'durchmesser' in params:
                d_si = params['durchmesser']['si_value']
                r_si = d_si / 2.0
                ref_unit = params['durchmesser']['original_unit']
                gegebene_werte = {"durchmesser": durchmesser}
            else:
                return {"error": "Für Flächenberechnung muss entweder Radius oder Durchmesser gegeben sein"}
            
            if r_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            # Berechne Fläche: A = π × r²
            flaeche_si = math.pi * r_si * r_si
            
            # Optimiere Ausgabe-Einheit
            flaeche_quantity = flaeche_si * ureg.meter**2
            flaeche_optimized = optimize_output_unit(flaeche_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "flaeche",
                "gegebene_werte": gegebene_werte,
                "ergebnis": {
                    "flaeche": f"{flaeche_optimized.magnitude:.6g} {flaeche_optimized.units}"
                },
                "formel": "A = π × r²",
                "si_werte": {
                    "flaeche_si": f"{flaeche_si:.6g} m²",
                    "radius_si": f"{r_si:.6g} m"
                }
            }
            
        elif target_param == 'var2':  # radius
            # Bestimme Fläche
            if 'flaeche' not in params:
                return {"error": "Für Radiusberechnung muss Fläche gegeben sein"}
            
            flaeche_si = params['flaeche']['si_value']
            if flaeche_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            # Berechne Radius: r = √(A/π)
            radius_si = math.sqrt(flaeche_si / math.pi)
            
            # Validiere gegen Durchmesser wenn gegeben
            if 'durchmesser' in params:
                d_si = params['durchmesser']['si_value']
                expected_radius = d_si / 2.0
                error_percent = abs(radius_si - expected_radius) / expected_radius * 100
                if error_percent > 1:  # 1% Toleranz
                    return {
                        "error": "Inkonsistente Eingaben: Berechneter Radius stimmt nicht mit Durchmesser überein",
                        "berechneter_radius": f"{radius_si:.6g} m",
                        "erwarteter_radius": f"{expected_radius:.6g} m",
                        "abweichung": f"{error_percent:.2f}%"
                    }
            
            # Optimiere Ausgabe-Einheit
            ref_unit = params['flaeche']['original_unit']
            radius_quantity = radius_si * ureg.meter
            radius_optimized = optimize_output_unit(radius_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "radius",
                "gegebene_werte": {"flaeche": flaeche},
                "ergebnis": {
                    "radius": f"{radius_optimized.magnitude:.6g} {radius_optimized.units}"
                },
                "formel": "r = √(A/π)",
                "si_werte": {
                    "radius_si": f"{radius_si:.6g} m",
                    "flaeche_si": f"{flaeche_si:.6g} m²"
                }
            }
            
        elif target_param == 'var3':  # durchmesser
            # Bestimme Radius
            if 'radius' in params:
                r_si = params['radius']['si_value']
                ref_unit = params['radius']['original_unit']
                gegebene_werte = {"radius": radius}
            elif 'flaeche' in params:
                flaeche_si = params['flaeche']['si_value']
                if flaeche_si <= 0:
                    return {"error": "Alle Werte müssen positiv sein"}
                r_si = math.sqrt(flaeche_si / math.pi)
                ref_unit = params['flaeche']['original_unit']
                gegebene_werte = {"flaeche": flaeche}
            else:
                return {"error": "Für Durchmesserberechnung muss entweder Radius oder Fläche gegeben sein"}
            
            if r_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            # Berechne Durchmesser: d = 2 × r
            durchmesser_si = 2.0 * r_si
            
            # Optimiere Ausgabe-Einheit
            durchmesser_quantity = durchmesser_si * ureg.meter
            durchmesser_optimized = optimize_output_unit(durchmesser_quantity, ref_unit)
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "durchmesser",
                "gegebene_werte": gegebene_werte,
                "ergebnis": {
                    "durchmesser": f"{durchmesser_optimized.magnitude:.6g} {durchmesser_optimized.units}"
                },
                "formel": "d = 2 × r",
                "si_werte": {
                    "durchmesser_si": f"{durchmesser_si:.6g} m",
                    "radius_si": f"{r_si:.6g} m"
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
            FUNCTION_PARAM_1_NAME: PARAMETER_FLAECHE,
            FUNCTION_PARAM_2_NAME: PARAMETER_RADIUS,
            FUNCTION_PARAM_3_NAME: PARAMETER_DURCHMESSER
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
        "parameter_count": PARAMETER_COUNT,
        "tool_description": TOOL_DESCRIPTION,
        "parameter_flaeche": PARAMETER_FLAECHE,
        "parameter_radius": PARAMETER_RADIUS,
        "parameter_durchmesser": PARAMETER_DURCHMESSER
    }

def calculate(flaeche: Union[str, List[str]], radius: Union[str, List[str]], durchmesser: Union[str, List[str]]) -> Union[Dict, List[Dict]]:
    """Legacy-Funktion für Kompatibilität - unterstützt nun auch Batch-Mode"""
    return solve_kreis(flaeche, radius, durchmesser)