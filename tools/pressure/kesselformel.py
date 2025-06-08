#!/usr/bin/env python3
"""
Kesselformel-Berechnung mit Einheiten-Support

Berechnet zulässige Drücke für Druckbehälter mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel p = (2 × σ_zul × s) / D nach verschiedenen Variablen auf.
Lösbare Variablen: druck, wanddicke, durchmesser, zulaessige_spannung
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "kesselformel"
TOOL_TAGS = ["mechanik", "druckbehaelter"]
TOOL_SHORT_DESCRIPTION = "Kesselformel - Druckbehälter-Berechnungen für zulässige Drücke"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic"

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
FUNCTION_PARAM_1_NAME = "druck"
FUNCTION_PARAM_1_DESC = "Innendruck mit Druckeinheit (z.B. '10 bar', '1 MPa', '145 psi') oder 'target' für Berechnung"
FUNCTION_PARAM_1_EXAMPLE = "10 bar"

FUNCTION_PARAM_2_NAME = "wanddicke"
FUNCTION_PARAM_2_DESC = "Wanddicke mit Längeneinheit (z.B. '10 mm', '1 cm', '0.01 m') oder 'target' für Berechnung"
FUNCTION_PARAM_2_EXAMPLE = "10 mm"

FUNCTION_PARAM_3_NAME = "durchmesser"
FUNCTION_PARAM_3_DESC = "Außendurchmesser mit Längeneinheit (z.B. '500 mm', '50 cm', '0.5 m') oder 'target' für Berechnung"
FUNCTION_PARAM_3_EXAMPLE = "500 mm"

FUNCTION_PARAM_4_NAME = "zulaessige_spannung"
FUNCTION_PARAM_4_DESC = "Zulässige Spannung mit Druckeinheit (z.B. '160 MPa', '1600 bar', '23200 psi') oder 'target' für Berechnung"
FUNCTION_PARAM_4_EXAMPLE = "200 MPa"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst die Kesselformel p = (2 × σ_zul × s) / D nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel)
{FUNCTION_PARAM_2_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel)
{FUNCTION_PARAM_3_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel)
{FUNCTION_PARAM_4_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel)

Kesselformel: p = (2 × σ_zul × s) / D

Anwendungsbereich: Druckbehälter-Auslegung, Kesselberechnung, Rohrleitungstechnik
Einschränkungen: Gilt für dünnwandige Behälter (s/D < 0.1), alle Werte müssen positiv sein"""

# Parameter-Definitionen für Metadaten
PARAMETER_DRUCK = {
    "type": "string | array",
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "batch_example": ["10 bar", "15 bar", "20 bar"]
}

PARAMETER_WANDDICKE = {
    "type": "string | array", 
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE,
    "batch_example": ["5 mm", "8 mm", "10 mm"]
}

PARAMETER_DURCHMESSER = {
    "type": "string | array",
    "description": FUNCTION_PARAM_3_DESC,
    "example": FUNCTION_PARAM_3_EXAMPLE,
    "batch_example": ["300 mm", "500 mm", "800 mm"]
}

PARAMETER_ZULAESSIGE_SPANNUNG = {
    "type": "string | array",
    "description": FUNCTION_PARAM_4_DESC,
    "example": FUNCTION_PARAM_4_EXAMPLE,
    "batch_example": ["160 MPa", "200 MPa", "250 MPa"]
}

# Output-Definition
OUTPUT_RESULT = {
    "type": "Quantity",
    "description": "Berechnungsergebnis mit optimierter Einheit",
    "unit": "abhängig vom Parameter"
}

# Beispiele
TOOL_EXAMPLES = [
    {
        "title": f"Berechne {FUNCTION_PARAM_1_NAME} (analytisch) bei gegebenen anderen Parametern",
        "input": {FUNCTION_PARAM_1_NAME: "target", FUNCTION_PARAM_2_NAME: FUNCTION_PARAM_2_EXAMPLE, FUNCTION_PARAM_3_NAME: FUNCTION_PARAM_3_EXAMPLE, FUNCTION_PARAM_4_NAME: FUNCTION_PARAM_4_EXAMPLE},
        "output": f"{FUNCTION_PARAM_1_NAME} in optimierter Einheit mit geschlossener Formel"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_2_NAME} (analytisch) bei gegebenen anderen Parametern", 
        "input": {FUNCTION_PARAM_1_NAME: FUNCTION_PARAM_1_EXAMPLE, FUNCTION_PARAM_2_NAME: "target", FUNCTION_PARAM_3_NAME: "1 m", FUNCTION_PARAM_4_NAME: "160 MPa"},
        "output": f"{FUNCTION_PARAM_2_NAME} in optimierter Einheit mit geschlossener Formel"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_3_NAME} (analytisch) bei gegebenen anderen Parametern",
        "input": {FUNCTION_PARAM_1_NAME: "15 bar", FUNCTION_PARAM_2_NAME: "8 mm", FUNCTION_PARAM_3_NAME: "target", FUNCTION_PARAM_4_NAME: FUNCTION_PARAM_4_EXAMPLE},
        "output": f"{FUNCTION_PARAM_3_NAME} in optimierter Einheit mit geschlossener Formel"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_4_NAME} (analytisch) bei gegebenen anderen Parametern",
        "input": {FUNCTION_PARAM_1_NAME: FUNCTION_PARAM_1_EXAMPLE, FUNCTION_PARAM_2_NAME: "5 mm", FUNCTION_PARAM_3_NAME: FUNCTION_PARAM_3_EXAMPLE, FUNCTION_PARAM_4_NAME: "target"},
        "output": f"{FUNCTION_PARAM_4_NAME} in optimierter Einheit mit geschlossener Formel"
    }
]

# Annahmen
TOOL_ASSUMPTIONS = [
    "Dünnwandige Behälter (s/D < 0.1)",
    "Alle Eingabewerte sind positiv",
    "Materialverhalten ist linear-elastisch",
    "Keine Berücksichtigung von Spannungskonzentrationen"
]

# Einschränkungen  
TOOL_LIMITATIONS = [
    "Nur für dünnwandige Druckbehälter gültig",
    "Nicht für dickwandige Behälter oder komplexe Geometrien",
    "Keine Berücksichtigung von Temperatureffekten",
    "Keine Ermüdungsanalyse"
]

# Mathematische Grundlagen
MATHEMATICAL_FOUNDATION = "Kesselformel für dünnwandige Druckbehälter: p = (2 × σ_zul × s) / D, wobei p der Innendruck, σ_zul die zulässige Spannung, s die Wanddicke und D der Außendurchmesser ist"

# Normengrundlage
NORM_FOUNDATION = "DIN EN 13445 (Druckbehälter), AD 2000-Merkblätter"

# ===== AUTOMATISCH BERECHNET =====
PARAMETER_COUNT = len([name for name in globals() if name.startswith('PARAMETER_')])

# ================================================================================================
# 🔧 IMPORTS & DEPENDENCIES 🔧
# ================================================================================================

from typing import Dict, Annotated, List, Any, Union
import sys
import os

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engineering_mcp.units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

# ================================================================================================
# 🎯 BATCH PROCESSING HELPER FUNCTIONS 🎯
# ================================================================================================

def is_batch_input(druck, wanddicke, durchmesser, zulaessige_spannung) -> bool:
    """Prüft, ob es sich um eine Batch-Eingabe handelt"""
    return any(isinstance(param, list) for param in [druck, wanddicke, durchmesser, zulaessige_spannung])

def prepare_batch_combinations(druck, wanddicke, durchmesser, zulaessige_spannung) -> Union[List[Dict], Dict]:
    """
    Bereitet Batch-Kombinationen vor und validiert sie.
    
    Returns:
        List[Dict]: Liste von Parameter-Kombinationen
        Dict: Fehler-Dictionary bei ungültiger Eingabe
    """
    params = {
        'druck': druck,
        'wanddicke': wanddicke, 
        'durchmesser': durchmesser,
        'zulaessige_spannung': zulaessige_spannung
    }
    
    # Identifiziere Listen-Parameter
    list_params = {k: v for k, v in params.items() if isinstance(v, list)}
    single_params = {k: v for k, v in params.items() if not isinstance(v, list)}
    
    if not list_params:
        return {"error": "Keine Listen-Parameter gefunden"}
    
    # Prüfe, dass alle Listen die gleiche Länge haben
    list_lengths = [len(v) for v in list_params.values()]
    if len(set(list_lengths)) > 1:
        return {
            "error": "Alle Listen-Parameter müssen die gleiche Länge haben",
            "gefundene_laengen": {k: len(v) for k, v in list_params.items()},
            "hinweis": "Jeder Index repräsentiert eine vollständige Parameter-Kombination"
        }
    
    # Erstelle Kombinationen
    batch_length = list_lengths[0]
    combinations = []
    
    for i in range(batch_length):
        combination = {}
        
        # Füge Listen-Werte hinzu
        for param_name, param_list in list_params.items():
            combination[param_name] = param_list[i]
        
        # Füge Einzel-Werte hinzu  
        for param_name, param_value in single_params.items():
            combination[param_name] = param_value
            
        combinations.append(combination)
    
    return combinations

# ================================================================================================
# 🎯 TOOL FUNCTIONS 🎯
# ================================================================================================

def solve_kesselformel(
    druck: Annotated[Union[str, List[str]], FUNCTION_PARAM_1_DESC],  
    wanddicke: Annotated[Union[str, List[str]], FUNCTION_PARAM_2_DESC],
    durchmesser: Annotated[Union[str, List[str]], FUNCTION_PARAM_3_DESC],
    zulaessige_spannung: Annotated[Union[str, List[str]], FUNCTION_PARAM_4_DESC]
) -> Union[Dict, List[Dict]]:
    """
    📊 ANALYTICAL SOLUTION mit BATCH-SUPPORT
    
    Löst die Kesselformel p = (2 × σ_zul × s) / D nach verschiedenen Variablen auf.
    Unterstützt sowohl Einzelberechnungen als auch Batch-Verarbeitung.
    
    Args:
        druck: Innendruck mit Einheit oder 'target' (oder Liste davon)
        wanddicke: Wanddicke mit Einheit oder 'target' (oder Liste davon)
        durchmesser: Außendurchmesser mit Einheit oder 'target' (oder Liste davon)
        zulaessige_spannung: Zulässige Spannung mit Einheit oder 'target' (oder Liste davon)
    
    Returns:
        Dict: Einzelberechnung
        List[Dict]: Batch-Verarbeitung mit strukturierten Ergebnissen
    """
    try:
        # 🎯 BATCH-DETECTION & ORCHESTRATION
        if is_batch_input(druck, wanddicke, durchmesser, zulaessige_spannung):
            combinations = prepare_batch_combinations(druck, wanddicke, durchmesser, zulaessige_spannung)
            
            if isinstance(combinations, dict) and "error" in combinations:
                return combinations
            
            # Batch-Verarbeitung
            results = []
            successful = 0
            failed = 0
            
            for i, combination in enumerate(combinations):
                try:
                    single_result = _solve_kesselformel_single(
                        combination['druck'], 
                        combination['wanddicke'], 
                        combination['durchmesser'], 
                        combination['zulaessige_spannung']
                    )
                    
                    if "error" not in single_result:
                        successful += 1
                        results.append({
                            "batch_index": i,
                            "input_combination": combination,
                            "ergebnis": single_result
                        })
                    else:
                        failed += 1
                        results.append({
                            "batch_index": i,
                            "input_combination": combination,
                            "error": single_result["error"]
                        })
                        
                except Exception as e:
                    failed += 1
                    results.append({
                        "batch_index": i,
                        "input_combination": combination,
                        "error": f"Berechnungsfehler: {str(e)}"
                    })
            
            return {
                "batch_mode": True,
                "total_calculations": len(combinations),
                "successful": successful,
                "failed": failed,
                "results": results
            }
        
        else:
            # Einzelberechnung
            return _solve_kesselformel_single(druck, wanddicke, durchmesser, zulaessige_spannung)
    
    except Exception as e:
        return {
            "error": "Systemfehler in Batch-Orchestration",
            "message": str(e),
            "hinweis": "Überprüfen Sie die Eingabe-Parameter und Format"
        }

def _solve_kesselformel_single(druck: str, wanddicke: str, durchmesser: str, zulaessige_spannung: str) -> Dict:
    """
    Einzelberechnung der Kesselformel (interne Funktion).
    
    Args:
        druck: Innendruck mit Einheit oder 'target'
        wanddicke: Wanddicke mit Einheit oder 'target'
        durchmesser: Außendurchmesser mit Einheit oder 'target'
        zulaessige_spannung: Zulässige Spannung mit Einheit oder 'target'
    
    Returns:
        Dict: Berechnungsergebnis mit target_parameter und optimierten Einheiten
    """
    try:
        # Identifiziere target Parameter
        target_params = []
        given_params = []
        
        params_info = {
            'druck': druck,
            'wanddicke': wanddicke,
            'durchmesser': durchmesser,
            'zulaessige_spannung': zulaessige_spannung
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
                "example": f"solve_kesselformel({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}', {FUNCTION_PARAM_4_NAME}='{FUNCTION_PARAM_4_EXAMPLE}')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 3:
            return {
                "error": f"Genau 3 Parameter müssen Werte mit Einheiten haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": f"solve_kesselformel({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}', {FUNCTION_PARAM_4_NAME}='{FUNCTION_PARAM_4_EXAMPLE}')"
            }
        
        target_param = target_params[0]
        
        # Erstelle kwargs für Validierung (nur gegebene Parameter)
        validation_kwargs = {}
        for param_name in given_params:
            validation_kwargs[param_name] = params_info[param_name]
        
        # Validierung der Eingaben
        validated_inputs = validate_inputs_have_units(**validation_kwargs)
        
        # Kesselformel: p = (2 × σ_zul × s) / D
        # Umgestellt: σ_zul = (p × D) / (2 × s)
        #            s = (p × D) / (2 × σ_zul)  
        #            D = (2 × σ_zul × s) / p
        
        if target_param == 'druck':
            # Berechne Druck: p = (2 × σ_zul × s) / D
            sigma_si = validated_inputs['zulaessige_spannung']['si_value']  # Pa
            s_si = validated_inputs['wanddicke']['si_value']               # m
            d_si = validated_inputs['durchmesser']['si_value']             # m
            
            if d_si <= 0 or s_si <= 0 or sigma_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            p_si = (2 * sigma_si * s_si) / d_si  # Pa
            
            # Optimiere Ausgabe-Einheit
            pressure_quantity = p_si * ureg.pascal
            pressure_optimized = optimize_output_unit(pressure_quantity, 'bar')
            
            return {
                "📊 ANALYTICAL SOLUTION": "Kesselformel - Druck berechnet",
                "target_parameter": "druck",
                "gegebene_werte": {
                    "wanddicke": wanddicke,
                    "durchmesser": durchmesser,
                    "zulaessige_spannung": zulaessige_spannung
                },
                "ergebnis": {
                    "druck": f"{pressure_optimized.magnitude:.6g} {pressure_optimized.units}"
                },
                "formel": "p = (2 × σ_zul × s) / D",
                "si_werte": {
                    "druck_si": f"{p_si:.6g} Pa",
                    "wanddicke_si": f"{s_si:.6g} m",
                    "durchmesser_si": f"{d_si:.6g} m",
                    "zulaessige_spannung_si": f"{sigma_si:.6g} Pa"
                }
            }
            
        elif target_param == 'wanddicke':
            # Berechne Wanddicke: s = (p × D) / (2 × σ_zul)
            p_si = validated_inputs['druck']['si_value']                   # Pa
            d_si = validated_inputs['durchmesser']['si_value']             # m
            sigma_si = validated_inputs['zulaessige_spannung']['si_value'] # Pa
            
            if p_si <= 0 or d_si <= 0 or sigma_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            s_si = (p_si * d_si) / (2 * sigma_si)  # m
            
            # Optimiere Ausgabe-Einheit
            thickness_quantity = s_si * ureg.meter
            thickness_optimized = optimize_output_unit(thickness_quantity, 'mm')
            
            return {
                "📊 ANALYTICAL SOLUTION": "Kesselformel - Wanddicke berechnet",
                "target_parameter": "wanddicke",
                "gegebene_werte": {
                    "druck": druck,
                    "durchmesser": durchmesser,
                    "zulaessige_spannung": zulaessige_spannung
                },
                "ergebnis": {
                    "wanddicke": f"{thickness_optimized.magnitude:.6g} {thickness_optimized.units}"
                },
                "formel": "s = (p × D) / (2 × σ_zul)",
                "si_werte": {
                    "wanddicke_si": f"{s_si:.6g} m",
                    "druck_si": f"{p_si:.6g} Pa",
                    "durchmesser_si": f"{d_si:.6g} m",
                    "zulaessige_spannung_si": f"{sigma_si:.6g} Pa"
                }
            }
            
        elif target_param == 'durchmesser':
            # Berechne Durchmesser: D = (2 × σ_zul × s) / p
            p_si = validated_inputs['druck']['si_value']                   # Pa
            s_si = validated_inputs['wanddicke']['si_value']               # m
            sigma_si = validated_inputs['zulaessige_spannung']['si_value'] # Pa
            
            if p_si <= 0 or s_si <= 0 or sigma_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            d_si = (2 * sigma_si * s_si) / p_si  # m
            
            # Optimiere Ausgabe-Einheit
            diameter_quantity = d_si * ureg.meter
            diameter_optimized = optimize_output_unit(diameter_quantity, 'mm')
            
            return {
                "📊 ANALYTICAL SOLUTION": "Kesselformel - Durchmesser berechnet",
                "target_parameter": "durchmesser",
                "gegebene_werte": {
                    "druck": druck,
                    "wanddicke": wanddicke,
                    "zulaessige_spannung": zulaessige_spannung
                },
                "ergebnis": {
                    "durchmesser": f"{diameter_optimized.magnitude:.6g} {diameter_optimized.units}"
                },
                "formel": "D = (2 × σ_zul × s) / p",
                "si_werte": {
                    "durchmesser_si": f"{d_si:.6g} m",
                    "druck_si": f"{p_si:.6g} Pa",
                    "wanddicke_si": f"{s_si:.6g} m",
                    "zulaessige_spannung_si": f"{sigma_si:.6g} Pa"
                }
            }
            
        elif target_param == 'zulaessige_spannung':
            # Berechne zulässige Spannung: σ_zul = (p × D) / (2 × s)
            p_si = validated_inputs['druck']['si_value']         # Pa
            d_si = validated_inputs['durchmesser']['si_value']   # m
            s_si = validated_inputs['wanddicke']['si_value']     # m
            
            if p_si <= 0 or d_si <= 0 or s_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            sigma_si = (p_si * d_si) / (2 * s_si)  # Pa
            
            # Optimiere Ausgabe-Einheit
            stress_quantity = sigma_si * ureg.pascal
            stress_optimized = optimize_output_unit(stress_quantity, 'MPa')
            
            return {
                "📊 ANALYTICAL SOLUTION": "Kesselformel - Zulässige Spannung berechnet",
                "target_parameter": "zulaessige_spannung",
                "gegebene_werte": {
                    "druck": druck,
                    "durchmesser": durchmesser,
                    "wanddicke": wanddicke
                },
                "ergebnis": {
                    "zulaessige_spannung": f"{stress_optimized.magnitude:.6g} {stress_optimized.units}"
                },
                "formel": "σ_zul = (p × D) / (2 × s)",
                "si_werte": {
                    "zulaessige_spannung_si": f"{sigma_si:.6g} Pa",
                    "druck_si": f"{p_si:.6g} Pa",
                    "durchmesser_si": f"{d_si:.6g} m",
                    "wanddicke_si": f"{s_si:.6g} m"
                }
            }
        
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
    except Exception as e:
        return {
            "error": "Berechnungsfehler",
            "message": str(e),
            "hinweis": "Überprüfen Sie die Eingabe-Parameter und Einheiten"
        }

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
            FUNCTION_PARAM_1_NAME: PARAMETER_DRUCK,
            FUNCTION_PARAM_2_NAME: PARAMETER_WANDDICKE,
            FUNCTION_PARAM_3_NAME: PARAMETER_DURCHMESSER,
            FUNCTION_PARAM_4_NAME: PARAMETER_ZULAESSIGE_SPANNUNG
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
        
        # ✅ Backwards Compatibility
        "tool_tags": TOOL_TAGS,
        "tool_short_description": TOOL_SHORT_DESCRIPTION,
        "parameter_count": PARAMETER_COUNT,
        "tool_description": TOOL_DESCRIPTION
    }

def calculate(druck: str, wanddicke: str, durchmesser: str, zulaessige_spannung: str) -> Dict:
    """Legacy-Funktion für Kompatibilität"""
    return solve_kesselformel(druck, wanddicke, durchmesser, zulaessige_spannung)

# ================================================================================================
# 🎯 TESTS 🎯
# ================================================================================================

if __name__ == "__main__":
    # Test der Kesselformel
    print("=== Kesselformel Template Test ===")
    
    # Test 1: Druck berechnen
    result1 = solve_kesselformel(
        druck="target", 
        wanddicke="5 mm", 
        durchmesser="500 mm", 
        zulaessige_spannung="200 MPa"
    )
    print("Test 1 - Druck berechnen:")
    print(result1)
    
    print("\n" + "="*50)
    
    # Test 2: Wanddicke berechnen
    result2 = solve_kesselformel(
        druck="10 bar",
        wanddicke="target", 
        durchmesser="1 m", 
        zulaessige_spannung="160 MPa"
    )
    print("Test 2 - Wanddicke berechnen:")
    print(result2)
    
    print("\n" + "="*50)
    
    # Test 3: Batch-Verarbeitung - Multiple Drücke berechnen
    try:
        result3 = solve_kesselformel(
            druck="target",
            wanddicke=["5 mm", "8 mm", "10 mm"],
            durchmesser=["300 mm", "500 mm", "800 mm"], 
            zulaessige_spannung="200 MPa"
        )
        print("Test 3 - Batch-Verarbeitung:")
        print(f"Batch-Mode: {result3.get('batch_mode', False)}")
        print(f"Berechnungen: {result3.get('total_calculations', 0)}")
        print(f"Erfolgreich: {result3.get('successful', 0)}")
        print(f"Fehlgeschlagen: {result3.get('failed', 0)}")
    except Exception as e:
        print(f"Test 3 - Batch-Test (erwartet Fehler ohne Server-Kontext): {e}") 