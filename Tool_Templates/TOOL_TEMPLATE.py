#!/usr/bin/env python3
"""
🧮 SOLVING/CALCULATION TOOL TEMPLATE 🧮

[Tool Name] - [Kurzbeschreibung für list_engineering_tools]

Berechnet [BESCHREIBUNG] mit automatischer Einheiten-Konvertierung.
Alle Eingaben MÜSSEN mit Einheiten angegeben werden.

Löst die Formel [FORMEL] nach verschiedenen Variablen auf.
Lösbare Variablen: [deutsche_variable_1], [deutsche_variable_2], [deutsche_variable_3]

⚠️ FÜR TABELLENWERK-TOOLS: Verwenden Sie TABELLENWERK_TEMPLATE.py stattdessen!

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke

🔄 BATCH-MODUS: Unterstützt Verarbeitung mehrerer Parametersätze gleichzeitig!
Beispiel: durchmesser=["10 mm", "20 mm", "30 mm"] statt durchmesser="10 mm"

[Detaillierte Beschreibung der Formel, Anwendungsbereich, physikalische Bedeutung]
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "[tool_name]"  # ANPASSEN: eindeutiger Tool-Name
TOOL_TAGS = ["elementar", "Flaechen"]  # ANPASSEN: ["elementar", "Flaechen"] | ["elementar", "Volumen"] | ["mechanik"]
TOOL_SHORT_DESCRIPTION = "[Kurze Beschreibung] - [Was das Tool macht]"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "symbolic"  # "symbolic" | "numeric" | "symbolic/numeric" | "none"

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
# ⚠️ WICHTIGE NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein! ⚠️
# ✅ RICHTIG:  durchmesser, druck, laenge, breite, hoehe, radius, flaeche, volumen, wanddicke,
#             umfang, grundflaeche, halb_achse_a, halb_achse_b, seite_a, seite_b, seite_c,
#             zul_spannung, min_vorspannkraft, festigkeitsklasse, reibbeiwert
# ❌ FALSCH:   diameter, pressure, length, width, height, area, volume, wall_thickness

FUNCTION_PARAM_1_NAME = "deutsche_variable_1"  # ANPASSEN: z.B. "durchmesser", "laenge", "flaeche" 
FUNCTION_PARAM_1_DESC = "[Beschreibung der deutschen Variable 1] mit [Einheiten-Typ] (z.B. '5.2 mm', '2.5 cm', '0.052 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_1_EXAMPLE = "5.2 mm"

FUNCTION_PARAM_2_NAME = "deutsche_variable_2"  # ANPASSEN: z.B. "breite", "hoehe", "volumen"
FUNCTION_PARAM_2_DESC = "[Beschreibung der deutschen Variable 2] mit [Einheiten-Typ] (z.B. '10 mm', '1 cm', '0.01 m') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_2_EXAMPLE = "10 mm"

FUNCTION_PARAM_3_NAME = "deutsche_variable_3"  # ANPASSEN: z.B. "radius", "umfang", "druck"
FUNCTION_PARAM_3_DESC = "[Beschreibung der deutschen Variable 3] mit [Einheiten-Typ] (z.B. '25.5 cm²', '0.00255 m²', '2550 mm²') oder 'target' für Berechnung. BATCH: Als Teil einer Liste mit vollständigen Parametersätzen"
FUNCTION_PARAM_3_EXAMPLE = "25.5 cm²"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Löst [FORMEL] nach verschiedenen Variablen auf mit TARGET-System.

WICHTIG: Alle Parameter sind PFLICHT - einer als 'target', die anderen mit Einheiten!
Target-System: Geben Sie 'target' für den zu berechnenden Parameter an.

🔄 BATCH-MODUS: Unterstützt Listen von Parametern für Massenberechnungen!
⚠️ WICHTIG: Bei Batch-Berechnungen müssen ALLE Parameter Listen gleicher Länge sein!
Jeder Index repräsentiert einen vollständigen Parametersatz.

Beispiel Batch-Aufruf:
solve_tool_name(
    param1=['target', '10 mm', 'target'],
    param2=['20 mm', 'target', '30 mm'],
    param3=['5 cm', '6 cm', '7 cm']
)
Dies berechnet 3 separate Parametersätze mit jeweils einem anderen Target.

BERECHNUNGSARTEN:
{FUNCTION_PARAM_1_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel)
{FUNCTION_PARAM_2_NAME}: NUMERISCHE ITERATION ([Methode])
{FUNCTION_PARAM_3_NAME}: ANALYTISCHE LÖSUNG (geschlossene Formel)
[nur bei has_solving: "symbolic/numeric" - dokumentiere explizit welche Parameter symbolisch vs. numerisch]

[GRUNDFORMEL]

Anwendungsbereich: [Wann und wo wird diese Formel verwendet]
Einschränkungen: [Falls vorhanden, z.B. nur für positive Werte]
Genauigkeit: [Bei numerischen Methoden: Toleranz und Fehlerabschätzung]"""

# Parameter-Definitionen für Metadaten
PARAMETER_DEUTSCHE_VARIABLE_1 = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "batch_example": ["target", "10 mm", "target"]  # NEU
}

PARAMETER_DEUTSCHE_VARIABLE_2 = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE,
    "batch_example": ["20 mm", "target", "30 mm"]  # NEU
}

PARAMETER_DEUTSCHE_VARIABLE_3 = {
    "type": "string | array",  # ERWEITERT für Batch
    "description": FUNCTION_PARAM_3_DESC,
    "example": FUNCTION_PARAM_3_EXAMPLE,
    "batch_example": ["5 cm", "6 cm", "7 cm"]  # NEU
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
            FUNCTION_PARAM_1_NAME: ["target", "50 mm²", "target"],
            FUNCTION_PARAM_2_NAME: ["10 mm", "target", "30 mm"],
            FUNCTION_PARAM_3_NAME: ["100 mm²", "150 mm²", "200 mm²"]
        },
        "output": f"Liste von 3 Ergebnissen, jeweils mit unterschiedlichem Target-Parameter"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_2_NAME} (numerisch) bei gegebenen {FUNCTION_PARAM_1_NAME} und {FUNCTION_PARAM_3_NAME}", 
        "input": {FUNCTION_PARAM_1_NAME: "50 cm²", FUNCTION_PARAM_2_NAME: "target", FUNCTION_PARAM_3_NAME: FUNCTION_PARAM_3_EXAMPLE},
        "output": f"{FUNCTION_PARAM_2_NAME} in optimierter Einheit mit numerischer Iteration"
    },
    {
        "title": f"Berechne {FUNCTION_PARAM_3_NAME} (analytisch) bei gegebenen {FUNCTION_PARAM_1_NAME} und {FUNCTION_PARAM_2_NAME}",
        "input": {FUNCTION_PARAM_1_NAME: "50 cm²", FUNCTION_PARAM_2_NAME: FUNCTION_PARAM_2_EXAMPLE, FUNCTION_PARAM_3_NAME: "target"},
        "output": f"{FUNCTION_PARAM_3_NAME} in optimierter Einheit mit geschlossener Formel"
    }
]

# Annahmen
TOOL_ASSUMPTIONS = [
    "[Annahme 1: z.B. Geometrische Form ist perfekt]",
    "[Annahme 2: z.B. Alle Eingabewerte sind positiv]",
    "[Annahme 3: z.B. Materialverhalten ist linear]"
]

# Einschränkungen  
TOOL_LIMITATIONS = [
    "[Einschränkung 1: z.B. Nur für positive Werte gültig]",
    "[Einschränkung 2: z.B. Nicht für degenerierte Fälle]",
    "[Einschränkung 3: z.B. Keine komplexen Zahlen]"
]

# Mathematische Grundlagen (PFLICHTFELD - leer lassen wenn keine klare Formel)
MATHEMATICAL_FOUNDATION = "[Beschreibung der mathematischen Grundlagen und Formeln, z.B. 'Dreiecksfläche: A = (1/2) × b × h, wobei b die Basis und h die Höhe ist' oder leer lassen '']"

# Normengrundlage (PFLICHTFELD - leer lassen wenn keine Norm)
NORM_FOUNDATION = "[Norm/Standard auf dem das Tool basiert, z.B. 'DIN EN 1993-1-8', 'VDI 2230', 'ISO 4762' oder leer lassen '']"

# ===== AUTOMATISCH BERECHNET =====
# Parameter-Count wird automatisch ermittelt - NICHT manuell definieren!
PARAMETER_COUNT = len([name for name in globals() if name.startswith('PARAMETER_')])

# ================================================================================================
# 🔧 IMPORTS & DEPENDENCIES 🔧
# ================================================================================================

from typing import Dict, Annotated, List, Any, Optional, Union
import sys
import os

# Import des Einheiten-Utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

def solve_tool_name(
    # ⚠️ Hier die konfigurierten Parameter-Namen und -Beschreibungen verwenden:
    deutsche_variable_1: Annotated[Union[str, List[str]], FUNCTION_PARAM_1_DESC],  
    deutsche_variable_2: Annotated[Union[str, List[str]], FUNCTION_PARAM_2_DESC],
    deutsche_variable_3: Annotated[Union[str, List[str]], FUNCTION_PARAM_3_DESC]
) -> Union[Dict, List[Dict]]:
    """
    Löst [FORMEL] nach verschiedenen Variablen auf.
    
    Unterstützt Batch-Verarbeitung: Wenn Listen als Parameter übergeben werden,
    müssen ALLE Parameter Listen gleicher Länge sein. Jeder Index repräsentiert
    einen vollständigen Parametersatz.
    """
    try:
        # Erstelle Parameter-Dictionary
        params_dict = {
            'deutsche_variable_1': deutsche_variable_1,
            'deutsche_variable_2': deutsche_variable_2, 
            'deutsche_variable_3': deutsche_variable_3
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
                combinations[0]['deutsche_variable_1'],
                combinations[0]['deutsche_variable_2'],
                combinations[0]['deutsche_variable_3']
            )
        
        # Batch-Verarbeitung: Berechne alle Kombinationen
        results = []
        for i, combo in enumerate(combinations):
            try:
                result = _solve_single(
                    combo['deutsche_variable_1'],
                    combo['deutsche_variable_2'],
                    combo['deutsche_variable_3']
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
            "error": f"Fehler in solve_tool_name: {str(e)}",
            "type": type(e).__name__
        }

def _solve_single(
    deutsche_variable_1: str,
    deutsche_variable_2: str,
    deutsche_variable_3: str
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
            'var1': deutsche_variable_1,
            'var2': deutsche_variable_2, 
            'var3': deutsche_variable_3
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
                "example": f"solve_tool_name({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')",
                "hinweis": "Geben Sie genau einen Parameter als 'target' an"
            }
        
        if len(given_params) != 2:
            return {
                "error": f"Genau 2 Parameter müssen Werte mit Einheiten haben (gefunden: {len(given_params)})",
                "given_params": given_params,
                "example": f"solve_tool_name({FUNCTION_PARAM_1_NAME}='target', {FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}', {FUNCTION_PARAM_3_NAME}='{FUNCTION_PARAM_3_EXAMPLE}')"
            }
        
        target_param = target_params[0]
        
        # Erstelle kwargs für Validierung (nur gegebene Parameter)
        validation_kwargs = {}
        for param_name in given_params:
            validation_kwargs[param_name] = params_info[param_name]

        # Validierung der Eingaben
        validated_inputs = validate_inputs_have_units(**validation_kwargs)

        # [HIER: Implementierung der spezifischen Berechnungslogik]
        # ... Berechnungslogik basierend auf target_param ...
        
        return {
            "error": "Template: Implementierung der Berechnungslogik erforderlich",
            "target_param": target_param,
            "validated_inputs": str(validated_inputs)
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
        # ⚠️ WICHTIG: Verwenden Sie IMMER FUNCTION_PARAM_*_NAME Konstanten!
        # ❌ FALSCH: grundseite_a: PARAMETER_GRUNDSEITE_A (Variable existiert nicht!)
        # ✅ RICHTIG: FUNCTION_PARAM_2_NAME: PARAMETER_GRUNDSEITE_A (Konstante)
        "parameters": {
            FUNCTION_PARAM_1_NAME: PARAMETER_DEUTSCHE_VARIABLE_1,
            FUNCTION_PARAM_2_NAME: PARAMETER_DEUTSCHE_VARIABLE_2,
            FUNCTION_PARAM_3_NAME: PARAMETER_DEUTSCHE_VARIABLE_3
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
        "tool_description": TOOL_DESCRIPTION
    }

def calculate(deutsche_variable_1: str, deutsche_variable_2: str, deutsche_variable_3: str) -> Dict:
    """Legacy-Funktion für Kompatibilität"""
    return solve_tool_name(deutsche_variable_1, deutsche_variable_2, deutsche_variable_3)

# ================================================================================================
# 🎯 SOLVING/CALCULATION TEMPLATE USAGE EXAMPLE 🎯
# ================================================================================================
"""
🧮 SOLVING/CALCULATION TOOL TEMPLATE - Für mathematische Berechnungen mit Target-System

⚠️ ⚠️ ⚠️ HÄUFIGER FEHLER - REGISTRY-DISCOVERY ⚠️ ⚠️ ⚠️
VERWENDEN SIE IMMER FUNCTION_PARAM_*_NAME KONSTANTEN IM PARAMETERS DICTIONARY!

❌ FALSCH:
"parameters": {
    grundseite_a: PARAMETER_GRUNDSEITE_A,  # Variable existiert nicht!
}

✅ RICHTIG:
"parameters": {
    FUNCTION_PARAM_2_NAME: PARAMETER_GRUNDSEITE_A,  # Konstante
}

Dieser Fehler führt zu: "ERROR: Failed to load metadata: name 'grundseite_a' is not defined"
⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️

ANPASSUNGS-CHECKLISTE für neue Solving-Tools:

1. ✅ GRUNDKONFIGURATION anpassen:
   - TOOL_NAME, TOOL_TAGS, TOOL_SHORT_DESCRIPTION
   - HAS_SOLVING: "symbolic" | "numeric" | "symbolic/numeric"

2. ✅ FUNKTIONSPARAMETER-DEFINITIONEN anpassen:
   - FUNCTION_PARAM_*_NAME mit deutschen Namen
   - FUNCTION_PARAM_*_DESC mit korrekten Beschreibungen
   - FUNCTION_PARAM_*_EXAMPLE mit passenden Beispielen

3. ✅ TOOL_DESCRIPTION im f-String automatisch angepasst
4. ✅ TOOL_EXAMPLES automatisch generiert aus Parametern
5. ✅ solve_tool_name Funktion mit spezifischer Logik implementieren
6. ✅ TOOL_ASSUMPTIONS, TOOL_LIMITATIONS anpassen
7. ✅ MATHEMATICAL_FOUNDATION und NORM_FOUNDATION setzen

🔄 BATCH-MODE IMPLEMENTIERUNG:

Das Template enthält bereits vollständige Batch-Unterstützung:
- is_batch_input() prüft auf Batch-Modus
- prepare_batch_combinations() erstellt Parametersätze
- solve_tool_name() validiert und orchestriert
- _solve_single() enthält die eigentliche Berechnungslogik

Batch-Regeln:
- ALLE Parameter müssen Listen gleicher Länge sein
- Jeder Index = ein vollständiger Parametersatz
- Automatische Fehlerbehandlung pro Berechnung
- Unbegrenzte Batch-Größe

Implementierungs-Schritte:
1. Kopiere das Template
2. Passe Metadaten an (Name, Parameter, etc.)
3. Implementiere _solve_single() mit Berechnungslogik
4. Fertig! Batch-Mode funktioniert automatisch

Eigenschaften von Solving/Calculation-Tools:
- ✅ Target-Parameter-System ("target" vs Werte mit Einheiten)
- ✅ Mathematische Berechnungen (analytisch/numerisch)
- ✅ HAS_SOLVING = "symbolic" | "numeric" | "symbolic/numeric"
- ✅ validate_inputs_have_units() für Einheiten-Validierung
- ✅ optimize_output_unit() für optimierte Ausgabe-Einheiten
- ✅ Batch-Mode für Massenberechnungen

📊 FÜR TABELLENWERK-TOOLS:
Verwenden Sie TABELLENWERK_TEMPLATE.py für:
- Normwerte-Tabellen ohne Berechnungen
- DIN/VDI/ISO Standard-Lookup-Tables
- HAS_SOLVING = "none"
- Kein Target-System, sondern Input → Output Mapping
- allowed_values für Parameter

Vorteile dieser Struktur:
- Alle Parameter werden zentral definiert
- Konsistenz zwischen Funktionssignaturen und Metadaten  
- F-String Interpolation für automatische Beschreibungen
- DRY-Prinzip: Parameter nur einmal definieren
- Übersichtliche Struktur für einfache Wartung
- Klare Trennung zwischen Solving- und Tabellenwerk-Tools
- Automatische Batch-Unterstützung ohne Zusatzaufwand
"""


