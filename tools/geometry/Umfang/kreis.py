#!/usr/bin/env python3
"""
Kreis-Umfang - Berechnet Umfang oder Radius eines Kreises

Berechnet Kreis-Umfang mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel U = 2 × π × r nach verschiedenen Variablen auf.
Lösbare Variablen: umfang, radius

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke

Kreis: Perfekte runde Form mit konstantem Radius - U = 2 × π × r = π × d
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "kreis_umfang"
TOOL_TAGS = ["elementar"]
TOOL_SHORT_DESCRIPTION = "Kreis-Umfang - Berechnet Umfang oder Radius"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic"  # Alle Berechnungen sind analytisch lösbar

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
FUNCTION_PARAM_1_NAME = "umfang"
FUNCTION_PARAM_1_DESC = "Umfang des Kreises mit Längeneinheit (z.B. '31.42 cm', '314.2 mm', '0.3142 m') oder 'target' für Berechnung"
FUNCTION_PARAM_1_EXAMPLE = "31.42 cm"

FUNCTION_PARAM_2_NAME = "radius"
FUNCTION_PARAM_2_DESC = "Radius des Kreises mit Längeneinheit (z.B. '5 cm', '50 mm', '0.05 m') oder 'target' für Berechnung"
FUNCTION_PARAM_2_EXAMPLE = "5 cm"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst die Kreis-Umfang-Formel U = 2 × π × r nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel U = 2πr)
{FUNCTION_PARAM_2_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel r = U/(2π))

Kreis-Formel: U = 2 × π × r

Anwendungsbereich: Geometrie, Maschinenbau (Rohre, Rollen), Architektur, Räder
Einschränkungen: Radius muss positiv sein
Genauigkeit: Exakte analytische Lösung"""

# Parameter-Definitionen für Metadaten
PARAMETER_UMFANG = {
    "type": "string | array",
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "batch_example": ["target", "62.83 cm", "target"]
}

PARAMETER_RADIUS = {
    "type": "string | array", 
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE,
    "batch_example": ["5 cm", "target", "8 cm"]
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
        "title": f"Berechne {FUNCTION_PARAM_1_NAME} (analytisch) bei gegebenem {FUNCTION_PARAM_2_NAME}",
        "input": {FUNCTION_PARAM_1_NAME: "target", FUNCTION_PARAM_2_NAME: FUNCTION_PARAM_2_EXAMPLE},
        "output": f"{FUNCTION_PARAM_1_NAME} in optimierter Einheit mit geschlossener Formel"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_2_NAME} (analytisch) bei gegebenem {FUNCTION_PARAM_1_NAME}", 
        "input": {FUNCTION_PARAM_1_NAME: FUNCTION_PARAM_1_EXAMPLE, FUNCTION_PARAM_2_NAME: "target"},
        "output": f"{FUNCTION_PARAM_2_NAME} in optimierter Einheit mit geschlossener Formel"
    }
]

# Annahmen
TOOL_ASSUMPTIONS = [
    "Perfekter Kreis mit konstantem Radius",
    "Alle Eingabewerte sind positiv",
    "Ebener Kreis (nicht auf gekrümmten Oberflächen)"
]

# Einschränkungen
TOOL_LIMITATIONS = [
    "Nur für positive Werte gültig",
    "Nur für perfekte Kreise",
    "Nicht für Ellipsen oder andere ovale Formen"
]

# Mathematische Grundlagen
MATHEMATICAL_FOUNDATION = "Kreis-Umfang: U = 2 × π × r, wobei r der Radius ist"

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

def solve_kreis_umfang(
    # ⚠️ Hier die konfigurierten Parameter-Namen und -Beschreibungen verwenden:
    umfang: Annotated[Union[str, List[str]], FUNCTION_PARAM_1_DESC],  
    radius: Annotated[Union[str, List[str]], FUNCTION_PARAM_2_DESC]
) -> Union[Dict, List[Dict]]:
    """
    Löst die Kreis-Umfang-Formel U = 2 × π × r nach verschiedenen Variablen auf.
    
    Unterstützt Batch-Verarbeitung: Wenn Listen als Parameter übergeben werden,
    müssen ALLE Parameter Listen gleicher Länge sein. Jeder Index repräsentiert
    einen vollständigen Parametersatz.
    """
    try:
        # Erstelle Parameter-Dictionary
        params_dict = {
            'umfang': umfang,
            'radius': radius
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
                combinations[0]['radius']
            )
        
        # Batch-Verarbeitung: Berechne alle Kombinationen
        results = []
        for i, combo in enumerate(combinations):
            try:
                result = _solve_single(
                    combo['umfang'],
                    combo['radius']
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
            "error": f"Fehler in solve_kreis_umfang: {str(e)}",
            "type": type(e).__name__
        }

def _solve_single(
    umfang: str,
    radius: str
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
            'var2': radius
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
                "example": f"solve_kreis_umfang({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 1:
            return {
                "error": f"Genau 1 Parameter muss einen Wert mit Einheit haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": f"solve_kreis_umfang({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}')"
            }
        
        target_param = target_params[0]
        
        # Erstelle kwargs für Validierung (nur gegebene Parameter)
        validation_kwargs = {}
        param_names = {
            'var1': 'umfang',
            'var2': 'radius'
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
                "hinweis": "Der Nicht-Target-Parameter muss mit Einheit angegeben werden",
                "beispiele": [
                    f"{FUNCTION_PARAM_1_NAME}='{FUNCTION_PARAM_1_EXAMPLE}'",
                    f"{FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}'"
                ]
            }
        
        # Kreisumfang-Formeln: U = 2πr
        # Umgestellt: r = U / (2π)
        
        if target_param == 'var1':  # umfang
            if 'radius' in params:
                # Berechne Umfang über Radius: U = 2πr
                r_si = params['radius']['si_value']  # in Metern
                
                if r_si <= 0:
                    return {"error": "Der Radius muss positiv sein"}
                
                u_si = 2 * math.pi * r_si  # in Metern
                
                # Optimiere Ausgabe-Einheit
                umfang_quantity = u_si * ureg.meter
                umfang_optimized = optimize_output_unit(umfang_quantity, params['radius']['original_unit'])
                
                return {
                    "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                    "target_parameter": "umfang",
                    "gegebene_werte": {
                        "radius": radius
                    },
                    "ergebnis": {
                        "umfang": f"{umfang_optimized.magnitude:.6g} {umfang_optimized.units}"
                    },
                    "formel": "U = 2πr",
                    "si_werte": {
                        "umfang_si": f"{u_si:.6g} m",
                        "radius_si": f"{r_si:.6g} m"
                    }
                }
                
        elif target_param == 'var2':  # radius
            # Berechne Radius: r = U / (2π)
            u_si = params['umfang']['si_value']  # in Metern
            
            if u_si <= 0:
                return {"error": "Der Umfang muss positiv sein"}
            
            r_si = u_si / (2 * math.pi)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            radius_quantity = r_si * ureg.meter
            radius_optimized = optimize_output_unit(radius_quantity, params['umfang']['original_unit'])
            
            return {
                "📊 ANALYTICAL SOLUTION": "Geschlossene Formel",
                "target_parameter": "radius",
                "gegebene_werte": {
                    "umfang": umfang
                },
                "ergebnis": {
                    "radius": f"{radius_optimized.magnitude:.6g} {radius_optimized.units}"
                },
                "formel": "r = U / (2π)",
                "si_werte": {
                    "radius_si": f"{r_si:.6g} m",
                    "umfang_si": f"{u_si:.6g} m"
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
            FUNCTION_PARAM_2_NAME: PARAMETER_RADIUS,
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
        "parameter_radius": PARAMETER_RADIUS
    }

def calculate(umfang: str, radius: str) -> Dict:
    """Legacy-Funktion für Kompatibilität"""
    return solve_kreis_umfang(umfang, radius)

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Kreis-Umfang-Tool Tests ===")
    
    # Test 1: Umfang berechnen
    result1 = solve_kreis_umfang(umfang="target", radius="5 cm")
    print(f"Test 1 - Umfang: {result1}")
    
    # Test 2: Radius berechnen
    result2 = solve_kreis_umfang(umfang="31.42 cm", radius="target")
    print(f"Test 2 - Radius: {result2}")
    
    # Test 3: Fehler - keine Einheit
    result3 = solve_kreis_umfang(umfang="target", radius="5")
    print(f"Test 3 - Keine Einheit: {result3}") 