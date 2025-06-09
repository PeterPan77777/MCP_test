#!/usr/bin/env python3
"""
Pyramide-Volumen - Berechnet Volumen, Grundfläche oder Höhe einer Pyramide

Berechnet Pyramiden-Volumen mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel V = (1/3) × A × h nach verschiedenen Variablen auf.
Lösbare Variablen: volumen, grundflaeche, hoehe

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke

Pyramide: Körper mit einer Grundfläche und einer Spitze - V = (1/3) × A × h
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "pyramide_volumen"
TOOL_TAGS = ["elementar"]
TOOL_SHORT_DESCRIPTION = "Pyramide-Volumen - Berechnet Volumen, Grundfläche oder Höhe"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic"  # Alle Berechnungen sind analytisch lösbar

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
FUNCTION_PARAM_1_NAME = "volumen"
FUNCTION_PARAM_1_DESC = "Volumen der Pyramide mit Volumeneinheit (z.B. '333.3 cm³', '0.0003333 m³', '333300 mm³') oder 'target' für Berechnung"
FUNCTION_PARAM_1_EXAMPLE = "333.3 cm³"

FUNCTION_PARAM_2_NAME = "grundflaeche"
FUNCTION_PARAM_2_DESC = "Grundfläche der Pyramide mit Flächeneinheit (z.B. '100 cm²', '0.01 m²', '10000 mm²') oder 'target' für Berechnung"
FUNCTION_PARAM_2_EXAMPLE = "100 cm²"

FUNCTION_PARAM_3_NAME = "hoehe"
FUNCTION_PARAM_3_DESC = "Höhe der Pyramide mit Längeneinheit (z.B. '10 cm', '100 mm', '0.1 m') oder 'target' für Berechnung"
FUNCTION_PARAM_3_EXAMPLE = "10 cm"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst die Pyramiden-Volumen-Formel V = (1/3) × A × h nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel V = (1/3)×A×h)
{FUNCTION_PARAM_2_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel A = 3V/h)
{FUNCTION_PARAM_3_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel h = 3V/A)

Pyramide-Formel: V = (1/3) × A × h

Anwendungsbereich: Geometrie, Architektur, Lagerhallen mit Pyramidendach
Einschränkungen: Alle Werte müssen positiv sein
Genauigkeit: Exakte analytische Lösung"""

# Parameter-Definitionen für Metadaten
PARAMETER_VOLUMEN = {
    "type": "string",
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE
}

PARAMETER_GRUNDFLAECHE = {
    "type": "string", 
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE
}

PARAMETER_HOEHE = {
    "type": "string",
    "description": FUNCTION_PARAM_3_DESC,
    "example": FUNCTION_PARAM_3_EXAMPLE
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
        "title": "Berechne Volumen bei gegebener Grundfläche und Höhe",
        "input": {f"{FUNCTION_PARAM_1_NAME}": "target", f"{FUNCTION_PARAM_2_NAME}": FUNCTION_PARAM_2_EXAMPLE, f"{FUNCTION_PARAM_3_NAME}": FUNCTION_PARAM_3_EXAMPLE},
        "output": "Volumen in optimierter Einheit"
    },
    {
        "title": "Berechne Grundfläche bei gegebenem Volumen und Höhe", 
        "input": {f"{FUNCTION_PARAM_1_NAME}": FUNCTION_PARAM_1_EXAMPLE, f"{FUNCTION_PARAM_2_NAME}": "target", f"{FUNCTION_PARAM_3_NAME}": FUNCTION_PARAM_3_EXAMPLE},
        "output": "Grundfläche in optimierter Einheit"
    },
    {
        "title": "Berechne Höhe bei gegebenem Volumen und Grundfläche",
        "input": {f"{FUNCTION_PARAM_1_NAME}": FUNCTION_PARAM_1_EXAMPLE, f"{FUNCTION_PARAM_2_NAME}": FUNCTION_PARAM_2_EXAMPLE, f"{FUNCTION_PARAM_3_NAME}": "target"},
        "output": "Höhe in optimierter Einheit"
    }
]

# Mathematische Grundlagen
MATHEMATICAL_FOUNDATION = "Pyramiden-Volumen: V = (1/3) × A × h, wobei A die Grundfläche und h die Höhe ist"

# Annahmen
TOOL_ASSUMPTIONS = [
    "Pyramide mit einer Grundfläche beliebiger Form",
    "Alle Eingabewerte sind positiv",
    "Spitze liegt senkrecht über dem Schwerpunkt der Grundfläche"
]

# Einschränkungen
TOOL_LIMITATIONS = [
    "Nur für positive Werte gültig",
    "Grundfläche muss bekannt sein",
    "Nicht für abgestumpfte Pyramiden"
]

# Referenz-Einheiten
REFERENCE_UNITS = {
    f"{FUNCTION_PARAM_1_NAME}": "m³",
    f"{FUNCTION_PARAM_2_NAME}": "m²",
    f"{FUNCTION_PARAM_3_NAME}": "m"
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
# 🎯 TOOL FUNCTIONS 🎯
# ================================================================================================

def solve_pyramide(
    volumen: Annotated[Union[str, List[str]], FUNCTION_PARAM_1_DESC],
    grundflaeche: Annotated[Union[str, List[str]], FUNCTION_PARAM_2_DESC],
    hoehe: Annotated[Union[str, List[str]], FUNCTION_PARAM_3_DESC]
) -> Union[Dict, List[Dict]]:
    """
    📊 ANALYTICAL SOLUTION
    
    Löst die Pyramiden-Volumen-Formel V = (1/3) × A × h nach verschiedenen Variablen auf.
    
    Args:
        volumen: Volumen mit Einheit oder 'target'
        grundflaeche: Grundfläche mit Einheit oder 'target' 
        hoehe: Höhe mit Einheit oder 'target'
    
    Returns:
        Dict mit Berechnungsergebnis und Metadaten
    """
    try:
        # Identifiziere target Parameter
        target_params = []
        given_params = []
        
        params_info = {
            f'{FUNCTION_PARAM_1_NAME}': volumen,
            f'{FUNCTION_PARAM_2_NAME}': grundflaeche,
            f'{FUNCTION_PARAM_3_NAME}': hoehe
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
                "example": f"solve_pyramide({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 2:
            return {
                "error": f"Genau 2 Parameter müssen Werte mit Einheiten haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": f"solve_pyramide({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')"
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
                    f"{FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}'"
                ]
            }
        
        # Berechnung basierend auf target Parameter
        if target_param == FUNCTION_PARAM_1_NAME:
            # Berechne Volumen: V = (1/3) × A × h
            A_si = params[FUNCTION_PARAM_2_NAME]['si_value']  # in m²
            h_si = params[FUNCTION_PARAM_3_NAME]['si_value']  # in Metern
            
            if A_si <= 0 or h_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            v_si = (1/3) * A_si * h_si  # in m³
            
            # Optimiere Ausgabe-Einheit
            volume_quantity = v_si * ureg.meter**3
            volume_optimized = optimize_volume_unit(volume_quantity, params[FUNCTION_PARAM_3_NAME]['original_unit'])
            
            return {
                "target_parameter": FUNCTION_PARAM_1_NAME,
                "gegebene_werte": {
                    FUNCTION_PARAM_2_NAME: grundflaeche,
                    FUNCTION_PARAM_3_NAME: hoehe
                },
                "ergebnis": {
                    FUNCTION_PARAM_1_NAME: f"{volume_optimized.magnitude:.6g} {volume_optimized.units}"
                },
                "formel": "V = (1/3) × A × h",
                "berechnungsart": "📊 ANALYTICAL SOLUTION",
                "si_werte": {
                    f"{FUNCTION_PARAM_1_NAME}_si": f"{v_si:.6g} m³",
                    f"{FUNCTION_PARAM_2_NAME}_si": f"{A_si:.6g} m²",
                    f"{FUNCTION_PARAM_3_NAME}_si": f"{h_si:.6g} m"
                }
            }
        
        elif target_param == FUNCTION_PARAM_2_NAME:
            # Berechne Grundfläche: A = (3 × V) / h
            v_si = params[FUNCTION_PARAM_1_NAME]['si_value']  # in m³
            h_si = params[FUNCTION_PARAM_3_NAME]['si_value']  # in Metern
            
            if v_si <= 0 or h_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            A_si = (3 * v_si) / h_si  # in m²
            
            # Optimiere Ausgabe-Einheit
            area_quantity = A_si * ureg.meter**2
            area_optimized = optimize_output_unit(area_quantity, params[FUNCTION_PARAM_3_NAME]['original_unit'])
            
            return {
                "target_parameter": FUNCTION_PARAM_2_NAME,
                "gegebene_werte": {
                    FUNCTION_PARAM_1_NAME: volumen,
                    FUNCTION_PARAM_3_NAME: hoehe
                },
                "ergebnis": {
                    FUNCTION_PARAM_2_NAME: f"{area_optimized.magnitude:.6g} {area_optimized.units}"
                },
                "formel": "A = (3 × V) / h",
                "berechnungsart": "📊 ANALYTICAL SOLUTION",
                "si_werte": {
                    f"{FUNCTION_PARAM_1_NAME}_si": f"{v_si:.6g} m³",
                    f"{FUNCTION_PARAM_2_NAME}_si": f"{A_si:.6g} m²",
                    f"{FUNCTION_PARAM_3_NAME}_si": f"{h_si:.6g} m"
                }
            }
        
        elif target_param == FUNCTION_PARAM_3_NAME:
            # Berechne Höhe: h = (3 × V) / A
            v_si = params[FUNCTION_PARAM_1_NAME]['si_value']  # in m³
            A_si = params[FUNCTION_PARAM_2_NAME]['si_value']  # in m²
            
            if v_si <= 0 or A_si <= 0:
                return {"error": "Alle Werte müssen positiv sein"}
            
            h_si = (3 * v_si) / A_si  # in Metern
            
            # Optimiere Ausgabe-Einheit
            length_quantity = h_si * ureg.meter
            length_optimized = optimize_output_unit(length_quantity, params[FUNCTION_PARAM_2_NAME]['original_unit'])
            
            return {
                "target_parameter": FUNCTION_PARAM_3_NAME,
                "gegebene_werte": {
                    FUNCTION_PARAM_1_NAME: volumen,
                    FUNCTION_PARAM_2_NAME: grundflaeche
                },
                "ergebnis": {
                    FUNCTION_PARAM_3_NAME: f"{length_optimized.magnitude:.6g} {length_optimized.units}"
                },
                "formel": "h = (3 × V) / A",
                "berechnungsart": "📊 ANALYTICAL SOLUTION",
                "si_werte": {
                    f"{FUNCTION_PARAM_1_NAME}_si": f"{v_si:.6g} m³",
                    f"{FUNCTION_PARAM_2_NAME}_si": f"{A_si:.6g} m²",
                    f"{FUNCTION_PARAM_3_NAME}_si": f"{h_si:.6g} m"
                }
            }
        
        else:
            return {"error": f"Unbekannter target Parameter: {target_param}"}
        
    except Exception as e:
        return {
            "error": "Unerwarteter Fehler in solve_pyramide",
            "message": str(e),
            "funktion": "solve_pyramide"
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
            FUNCTION_PARAM_2_NAME: PARAMETER_GRUNDFLAECHE,
            FUNCTION_PARAM_3_NAME: PARAMETER_HOEHE
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
def calculate(volumen: str, grundflaeche: str, hoehe: str) -> Dict:
    """Legacy-Funktion für Kompatibilität"""
    return solve_pyramide(volumen=volumen, grundflaeche=grundflaeche, hoehe=hoehe)

if __name__ == "__main__":
    # Test-Beispiele
    print("=== Pyramide-Tool Tests ===")
    
    # Test 1: Volumen berechnen
    result1 = solve_pyramide(base_area="25 cm²", height="6 cm")
    print(f"Test 1 - Volumen: {result1}")
    
    # Test 2: Grundfläche berechnen
    result2 = solve_pyramide(volume="50 cm³", height="6 cm")
    print(f"Test 2 - Grundfläche: {result2}")
    
    # Test 3: Höhe berechnen
    result3 = solve_pyramide(volume="50 cm³", base_area="25 cm²")
    print(f"Test 3 - Höhe: {result3}")
    
    # Test 4: Fehler - keine Einheit
    result4 = solve_pyramide(base_area="25", height="6 cm")
    print(f"Test 4 - Keine Einheit: {result4}") 