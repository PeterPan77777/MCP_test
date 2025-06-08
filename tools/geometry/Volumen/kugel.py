#!/usr/bin/env python3
"""
Kugel-Volumen - Berechnet Volumen oder Radius einer Kugel

Berechnet Kugel-Volumen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel V = (4/3) × π × r³ nach verschiedenen Variablen auf.
Lösbare Variablen: volumen, radius

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke

Kugel: Perfekt runde 3D-Form mit konstantem Radius - V = (4/3) × π × r³
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "kugel_volumen"
TOOL_TAGS = ["elementar"]
TOOL_SHORT_DESCRIPTION = "Kugel-Volumen - Berechnet Volumen oder Radius"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic"  # Alle Berechnungen sind analytisch lösbar

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
FUNCTION_PARAM_1_NAME = "volumen"
FUNCTION_PARAM_1_DESC = "Volumen der Kugel mit Volumeneinheit (z.B. '523.6 cm³', '0.0005236 m³', '523600 mm³') oder 'target' für Berechnung"
FUNCTION_PARAM_1_EXAMPLE = "523.6 cm³"

FUNCTION_PARAM_2_NAME = "radius"
FUNCTION_PARAM_2_DESC = "Radius der Kugel mit Längeneinheit (z.B. '5 cm', '50 mm', '0.05 m') oder 'target' für Berechnung"
FUNCTION_PARAM_2_EXAMPLE = "5 cm"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst die Kugel-Volumen-Formel V = (4/3) × π × r³ nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel V = (4/3)πr³)
{FUNCTION_PARAM_2_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel r = ∛((3V)/(4π)))

Kugel-Formel: V = (4/3) × π × r³

Anwendungsbereich: Geometrie, Behältervolumen, Ballvolumen, Architektur (Kuppeln)
Einschränkungen: Radius muss positiv sein
Genauigkeit: Exakte analytische Lösung"""

# Parameter-Definitionen für Metadaten
PARAMETER_VOLUMEN = {
    "type": "string | array",
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "batch_example": ["target", "1000 cm³", "target"]
}

PARAMETER_RADIUS = {
    "type": "string | array", 
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE,
    "batch_example": ["6 cm", "target", "8 cm"]
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
        "title": "Berechne Volumen bei gegebenem Radius",
        "input": {"volume": "target", "radius": "5 cm"},
        "output": "Volumen in optimierter Einheit"
    },
    {
        "title": "Berechne Radius bei gegebenem Volumen", 
        "input": {"volume": "523.6 cm³", "radius": "target"},
        "output": "Radius in optimierter Einheit"
    }
]

# Mathematische Grundlagen
MATHEMATICAL_FOUNDATION = "Kugel-Volumen: V = (4/3) × π × r³, wobei r der Radius ist"

# Annahmen
TOOL_ASSUMPTIONS = [
    "Perfekte Kugel mit konstantem Radius",
    "Alle Eingabewerte sind positiv",
    "Homogene Materialverteilung"
]

# Einschränkungen
TOOL_LIMITATIONS = [
    "Nur für positive Werte gültig",
    "Nur für perfekte Kugeln",
    "Nicht für ellipsoide oder andere ovale 3D-Formen"
]

# Solving-Typ
HAS_SOLVING = "symbolic"

# Referenz-Einheiten
REFERENCE_UNITS = {
    "volume": "m³",
    "radius": "m"
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

def solve_kugel(
    volume: Annotated[Union[str, List[str]], "Volumen der Kugel mit Volumeneinheit (z.B. '523.6 cm³', '0.0005236 m³', '523600 mm³') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"],
    radius: Annotated[Union[str, List[str]], "Radius der Kugel mit Längeneinheit (z.B. '5 cm', '50 mm', '0.05 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"]
) -> Union[Dict, List[Dict]]:
    try:
        # Erstelle Parameter-Dictionary
        params_dict = {
            'volume': volume,
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
                combinations[0]['volume'],
                combinations[0]['radius']
            )
        
        # Batch-Verarbeitung: Berechne alle Kombinationen
        results = []
        for i, combo in enumerate(combinations):
            try:
                result = _solve_single(
                    combo['volume'],
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
            "error": f"Fehler in solve_kugel: {str(e)}",
            "type": type(e).__name__
        }

def _solve_single(
    volume: str,
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
            'volume': volume,
            'radius': radius
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
                "example": "solve_kugel(volume='target', radius='5 cm')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 1:
            return {
                "error": f"Genau 1 Parameter muss einen Wert mit Einheit haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": "solve_kugel(volume='target', radius='5 cm')"
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
                "hinweis": "Der Nicht-Target-Parameter muss mit Einheit angegeben werden",
                "beispiele": [
                    "volume='523 cm³'",
                    "radius='5 cm'"
                ]
            }
        
        # Berechnung basierend auf target Parameter
        if target_param == 'volume':
            # Berechne Volumen: V = (4/3) × π × r³
            r_si = params['radius']['si_value']  # in Metern
            
            if r_si <= 0:
                return {"error": "Der Radius muss positiv sein"}
            
            v_si = (4/3) * math.pi * r_si**3  # in m³
            
            # Optimiere Ausgabe-Einheit
            volume_quantity = v_si * ureg.meter**3
            volume_optimized = optimize_volume_unit(volume_quantity, params['radius']['original_unit'])
            
            return {
                "target_parameter": "volume",
                "gegebene_werte": {
                    "radius": radius
                },
                "ergebnis": {
                    "volumen": f"{volume_optimized.magnitude:.6g} {volume_optimized.units}"
                },
                "formel": "V = (4/3) × π × r³",
                "si_werte": {
                    "volumen_si": f"{v_si:.6g} m³",
                    "radius_si": f"{r_si:.6g} m"
                }
            }
            
        elif target_param == 'radius':
            # Berechne Radius: r = ∛((3 × V) / (4 × π))
            v_si = params['volume']['si_value']  # in m³
            
            if v_si <= 0:
                return {"error": "Das Volumen muss positiv sein"}
            
            r_si = ((3 * v_si) / (4 * math.pi))**(1/3)  # in Metern
            
            # Optimiere Ausgabe-Einheit
            radius_quantity = r_si * ureg.meter
            
            # Extrahiere Basis-Längeneinheit aus Volumeneinheit (z.B. cm³ -> cm)
            original_unit = params['volume']['original_unit']
            if '³' in original_unit or '3' in original_unit:
                base_unit = original_unit.replace('³', '').replace('3', '')
                radius_optimized = optimize_output_unit(radius_quantity, base_unit)
            else:
                radius_optimized = radius_quantity
            
            return {
                "target_parameter": "radius",
                "gegebene_werte": {
                    "volumen": volume
                },
                "ergebnis": {
                    "radius": f"{radius_optimized.magnitude:.6g} {radius_optimized.units}"
                },
                "formel": "r = ∛((3 × V) / (4 × π))",
                "si_werte": {
                    "radius_si": f"{r_si:.6g} m",
                    "volumen_si": f"{v_si:.6g} m³"
                }
            }
        
    except Exception as e:
        return {
            "error": "Berechnungsfehler in _solve_single",
            "message": str(e),
            "hinweis": "Überprüfen Sie die Eingabe-Parameter und Einheiten"
        }

def optimize_volume_unit(si_quantity, reference_unit_str: str):
    """
    Optimiert Volumeneinheiten basierend auf Größenordnung.
    """
    try:
        magnitude = si_quantity.magnitude  # in m³
        
        # Bestimme optimale Volumeneinheit
        if magnitude >= 1:  # >= 1 m³
            return si_quantity.to(ureg.meter**3)
        elif magnitude >= 0.001:  # >= 1 dm³ (= 1 Liter)
            return si_quantity.to(ureg.liter)
        elif magnitude >= 1e-6:  # >= 1 cm³
            return si_quantity.to(ureg.centimeter**3)
        else:  # < 1 cm³
            return si_quantity.to(ureg.millimeter**3)
            
    except Exception:
        return si_quantity

# ⚡ NEUE TOOL-STRUKTUR: get_metadata() und calculate() Funktionen

def get_metadata():
    """
    Liefert Tool-Metadaten für Registry-Discovery.
    
    Returns:
        Dict: Tool-Metadaten im neuen TARGET-System Format
    """
    return {
        # ✅ Template-konforme Struktur
        "tool_name": TOOL_NAME,
        "short_description": TOOL_SHORT_DESCRIPTION,
        "description": TOOL_DESCRIPTION,
        "tags": TOOL_TAGS,  # ✅ KORRIGIERT: Verwende die Konstante statt hardcoded!
        "has_solving": HAS_SOLVING,
        
        # ✅ KRITISCH: Parameters Dictionary mit Konstanten
        "parameters": {
            FUNCTION_PARAM_1_NAME: PARAMETER_VOLUMEN,
            FUNCTION_PARAM_2_NAME: PARAMETER_RADIUS
        },
        
        # ✅ Beispiele im neuen Format
        "examples": TOOL_EXAMPLES,
        
        # ✅ Vollständige Metadaten für erweiterte Nutzung
        "tool_version": TOOL_VERSION,
        "output_result": OUTPUT_RESULT,
        "tool_assumptions": TOOL_ASSUMPTIONS,
        "tool_limitations": TOOL_LIMITATIONS,
        "mathematical_foundation": MATHEMATICAL_FOUNDATION
    }


def calculate(volume: str, radius: str) -> Dict:
    """
    Berechnet Kugel-Volumen-Parameter mit TARGET-System.
    
    ⚡ NEUE TOOL-STRUKTUR: Wrapper für solve_kugel mit neuer Signatur.
    
    Args:
        volume: Volumen mit Einheit oder 'target'
        radius: Radius mit Einheit oder 'target'  
        
    Returns:
        Dict: Berechnungsergebnis mit target_parameter
    """
    return solve_kugel(volume=volume, radius=radius)

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Kugel-Tool Tests ===")
    
    # Test 1: Volumen berechnen
    result1 = solve_kugel(radius="5 cm")
    print(f"Test 1 - Volumen: {result1}")
    
    # Test 2: Radius berechnen
    result2 = solve_kugel(volume="523 cm³")
    print(f"Test 2 - Radius: {result2}")
    
    # Test 3: Fehler - keine Einheit
    result3 = solve_kugel(radius="5")
    print(f"Test 3 - Keine Einheit: {result3}") 