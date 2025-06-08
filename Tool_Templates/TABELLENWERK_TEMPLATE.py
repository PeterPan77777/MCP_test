#!/usr/bin/env python3
"""
[Tool Name] - [Kurzbeschreibung für list_engineering_tools]

Stellt [TABELLEN-BESCHREIBUNG] aus [NORM/STANDARD] bereit.

WICHTIG: Dieses Tool führt KEINE symbolische Berechnungen durch!
Es handelt sich um eine reine Tabellen-Abfrage mit festen Normwerten.

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: schraubgroesse, lochklasse, werkstoff, festigkeitsklasse, durchmesser, dicke

[Detaillierte Beschreibung der Tabelle, Norm-Grundlage, Anwendungsbereich]
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "[tool_name]"  # ANPASSEN: eindeutiger Tool-Name
TOOL_TAGS = ["tabellenwerk", "normwerte"]  # ANPASSEN: ["tabellenwerk", "schrauben"] | ["tabellenwerk", "werkstoffe"]
TOOL_SHORT_DESCRIPTION = "[Kurze Beschreibung] - [Was die Tabelle enthält]"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "none"  # Tabellenwerk-Tools haben IMMER "none"

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
# ⚠️ WICHTIGE NAMENSKONVENTION: ALLE PARAMETER-NAMEN MÜSSEN DEUTSCH SEIN! ⚠️
# ✅ RICHTIG:  schraubgroesse, lochklasse, werkstoff, festigkeitsklasse, durchmesser, dicke,
#             materialnummer, oberflaeche, gewindeart, toleranzklasse
# ❌ FALSCH:   screw_size, hole_class, material, strength_class, diameter, thickness

FUNCTION_PARAM_1_NAME = "deutscher_parameter_1"  # ANPASSEN: z.B. "schraubgroesse", "werkstoff", "durchmesser"
FUNCTION_PARAM_1_DESC = "[Beschreibung des Parameters] (z.B. 'M6', 'M10', 'M20') oder 'all' für alle Werte"
FUNCTION_PARAM_1_EXAMPLE = "M10"
FUNCTION_PARAM_1_ALLOWED_VALUES = ["M6", "M8", "M10", "M12", "M16", "M20", "all"]  # ANPASSEN: Erlaubte Werte

FUNCTION_PARAM_2_NAME = "deutscher_parameter_2"  # ANPASSEN: z.B. "lochklasse", "werkstoffgruppe", "toleranzklasse"
FUNCTION_PARAM_2_DESC = "[Beschreibung des Parameters] ('klasse1', 'klasse2', 'klasse3') oder 'all' für alle Klassen"
FUNCTION_PARAM_2_EXAMPLE = "klasse2"
FUNCTION_PARAM_2_ALLOWED_VALUES = ["klasse1", "klasse2", "klasse3", "all"]  # ANPASSEN: Erlaubte Werte

# Optional: Dritter Parameter (kann entfernt werden wenn nicht benötigt)
FUNCTION_PARAM_3_NAME = "deutscher_parameter_3"  # ANPASSEN oder ENTFERNEN
FUNCTION_PARAM_3_DESC = "[Beschreibung des optionalen Parameters] oder 'all' für alle"
FUNCTION_PARAM_3_EXAMPLE = "option1"
FUNCTION_PARAM_3_ALLOWED_VALUES = ["option1", "option2", "option3", "all"]  # ANPASSEN oder ENTFERNEN

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Stellt Normwerte aus [NORM/STANDARD] bereit.

WICHTIG: Keine symbolische Berechnung - reine Tabellen-Abfrage mit festen Normwerten.
Verfügbare Werte: [BESCHREIBUNG DER VERFÜGBAREN WERTE]
ERWEITERT: Unterstützt 'all' für komplette Tabellen-Übersichten.

Eingabeparameter:
- {FUNCTION_PARAM_1_NAME}: {FUNCTION_PARAM_1_DESC}
- {FUNCTION_PARAM_2_NAME}: {FUNCTION_PARAM_2_DESC}

Ausgabe:
- [AUSGABE-BESCHREIBUNG]

Norm-Grundlage: [NORM/STANDARD]
Tabellen-Umfang: [ANZAHL/BEREICH DER WERTE]"""

# Parameter-Definitionen für Metadaten (mit allowed_values für Tabellenwerk!)
PARAMETER_DEUTSCHER_PARAMETER_1 = {
    "type": "string",
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "allowed_values": FUNCTION_PARAM_1_ALLOWED_VALUES
}

PARAMETER_DEUTSCHER_PARAMETER_2 = {
    "type": "string", 
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE,
    "allowed_values": FUNCTION_PARAM_2_ALLOWED_VALUES
}

# Optional: Dritter Parameter
PARAMETER_DEUTSCHER_PARAMETER_3 = {
    "type": "string",
    "description": FUNCTION_PARAM_3_DESC,
    "example": FUNCTION_PARAM_3_EXAMPLE,
    "allowed_values": FUNCTION_PARAM_3_ALLOWED_VALUES
}

# Output-Definition
OUTPUT_RESULT = {
    "type": "TableLookup",
    "description": "Tabellenwert oder Tabellen-Übersicht mit Normwerten",
    "format": "Einzelwert, Teilübersicht oder komplette Tabelle"
}

# Beispiele (für Tabellenwerk spezifisch - mit "all" Funktionalität)
TOOL_EXAMPLES = [
    {
        "title": f"Einzelwert-Abfrage: {FUNCTION_PARAM_1_EXAMPLE} mit {FUNCTION_PARAM_2_EXAMPLE}",
        "input": {FUNCTION_PARAM_1_NAME: FUNCTION_PARAM_1_EXAMPLE, FUNCTION_PARAM_2_NAME: FUNCTION_PARAM_2_EXAMPLE},
        "output": "Einzelner Normwert aus Tabelle"
    },
    {
        "title": f"Alle Werte für {FUNCTION_PARAM_1_EXAMPLE}",
        "input": {FUNCTION_PARAM_1_NAME: FUNCTION_PARAM_1_EXAMPLE, FUNCTION_PARAM_2_NAME: "all"},
        "output": f"Tabelle aller {FUNCTION_PARAM_2_NAME}-Werte für {FUNCTION_PARAM_1_EXAMPLE}"
    },
    {
        "title": f"Alle Werte für {FUNCTION_PARAM_2_EXAMPLE}",
        "input": {FUNCTION_PARAM_1_NAME: "all", FUNCTION_PARAM_2_NAME: FUNCTION_PARAM_2_EXAMPLE},
        "output": f"Tabelle aller {FUNCTION_PARAM_1_NAME}-Werte für {FUNCTION_PARAM_2_EXAMPLE}"
    },
    {
        "title": "Komplette Tabelle",
        "input": {FUNCTION_PARAM_1_NAME: "all", FUNCTION_PARAM_2_NAME: "all"},
        "output": "Vollständige Normwerte-Tabelle"
    }
]

# Annahmen
TOOL_ASSUMPTIONS = [
    "Norm-Werte entsprechen aktuellen Standards",
    "Tabellen-Werte sind für Standardbedingungen gültig",
    "[weitere norm-spezifische Annahmen]"
]

# Einschränkungen  
TOOL_LIMITATIONS = [
    "Nur vordefinierte Werte aus Norm-Tabellen verfügbar",
    "Keine Interpolation zwischen Tabellen-Werten",
    "[weitere norm-spezifische Einschränkungen]"
]

# Mathematische Grundlagen (für Tabellenwerk meist leer)
MATHEMATICAL_FOUNDATION = ""  # Meist leer für Tabellenwerk

# Normengrundlage (PFLICHTFELD für Tabellenwerk!)
NORM_FOUNDATION = "[NORM/STANDARD, z.B. 'DIN EN ISO 4762', 'VDI 2230', 'DIN 912']"

# ===== AUTOMATISCH BERECHNET =====
PARAMETER_COUNT = len([name for name in globals() if name.startswith('PARAMETER_')])

# ================================================================================================
# 🔧 IMPORTS & DEPENDENCIES 🔧
# ================================================================================================

from typing import Dict, Annotated, List, Any, Optional
import sys
import os

# Import des Einheiten-Utilities (optional für Tabellenwerk)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from engineering_mcp.units_utils import ureg
except ImportError:
    # Fallback wenn units_utils nicht verfügbar
    import pint
    ureg = pint.UnitRegistry()

# ================================================================================================
# 🎯 TABELLEN-DATEN 🎯
# ================================================================================================

# ===== TABELLEN-DEFINITION =====
# ANPASSEN: Hier die tatsächlichen Tabellen-Daten einfügen
NORMWERTE_TABELLE = {
    "wert1": {
        "klasse1": 10.0,
        "klasse2": 12.0, 
        "klasse3": 15.0
    },
    "wert2": {
        "klasse1": 20.0,
        "klasse2": 24.0,
        "klasse3": 30.0
    },
    # ... weitere Werte
}

# Hilfsfunktionen für Tabellen-Zugriff
def get_available_param1_values() -> List[str]:
    """Gibt alle verfügbaren Werte für Parameter 1 zurück"""
    return sorted(NORMWERTE_TABELLE.keys())

def get_available_param2_values() -> List[str]:
    """Gibt alle verfügbaren Werte für Parameter 2 zurück"""
    if NORMWERTE_TABELLE:
        return list(next(iter(NORMWERTE_TABELLE.values())).keys())
    return []

# ================================================================================================
# 🎯 TOOL FUNCTIONS 🎯
# ================================================================================================

def solve_tabellenwerk_lookup(
    # ⚠️ Hier die konfigurierten Parameter-Namen verwenden:
    deutscher_parameter_1: Annotated[str, FUNCTION_PARAM_1_DESC],  
    deutscher_parameter_2: Annotated[str, FUNCTION_PARAM_2_DESC]
    # deutscher_parameter_3: Annotated[str, FUNCTION_PARAM_3_DESC]  # Optional - entfernen wenn nicht benötigt
) -> Dict:
    """
    📊 TABLE LOOKUP SOLUTION
    
    Führt Tabellen-Lookup in Normwerte-Tabelle durch.
    
    Unterstützt verschiedene Abfrage-Modi:
    - Einzelwert: spezifische Parameter-Kombination
    - Teilübersicht: 'all' für einen Parameter
    - Komplette Tabelle: 'all' für alle Parameter
    """
    try:
        # Parameter normalisieren
        param1 = deutscher_parameter_1.strip().lower()
        param2 = deutscher_parameter_2.strip().lower()
        
        # === TABELLEN-ABFRAGEN (mit "all"-Unterstützung) ===
        
        if param1 == "all" and param2 == "all":
            # Komplette Tabelle zurückgeben
            complete_table = {}
            for p1_value, p2_dict in NORMWERTE_TABELLE.items():
                complete_table[p1_value] = {
                    p2_key: f"{p2_val} [EINHEIT]" for p2_key, p2_val in p2_dict.items()
                }
            
            return {
                "📊 TABLE LOOKUP SOLUTION": "Komplette Normwerte-Tabelle",
                "table": complete_table,
                "query_type": "complete_table",
                "total_entries": sum(len(p2_dict) for p2_dict in NORMWERTE_TABELLE.values()),
                "available_param1": list(NORMWERTE_TABELLE.keys()),
                "available_param2": get_available_param2_values(),
                "source": NORM_FOUNDATION,
                "note": "Vollständige Normwerte-Tabelle"
            }
        
        elif param1 == "all" and param2 in get_available_param2_values():
            # Alle Werte für einen spezifischen Parameter 2
            param2_table = {}
            for p1_value, p2_dict in NORMWERTE_TABELLE.items():
                if param2 in p2_dict:
                    param2_table[p1_value] = f"{p2_dict[param2]} [EINHEIT]"
            
            return {
                "📊 TABLE LOOKUP SOLUTION": f"Alle Werte für {param2}",
                "table": param2_table,
                "query_type": "all_param1_one_param2",
                "filter_param2": param2,
                "total_entries": len(param2_table),
                "source": NORM_FOUNDATION,
                "note": f"Alle {FUNCTION_PARAM_1_NAME}-Werte für {FUNCTION_PARAM_2_NAME}='{param2}'"
            }
        
        elif param1.upper() in [k.upper() for k in NORMWERTE_TABELLE.keys()] and param2 == "all":
            # Alle Werte für einen spezifischen Parameter 1
            # Finde den korrekten Schlüssel (case-insensitive)
            param1_key = None
            for key in NORMWERTE_TABELLE.keys():
                if key.upper() == param1.upper():
                    param1_key = key
                    break
            
            if param1_key:
                param1_table = {}
                for p2_key, p2_val in NORMWERTE_TABELLE[param1_key].items():
                    param1_table[p2_key] = f"{p2_val} [EINHEIT]"
                
                return {
                    "📊 TABLE LOOKUP SOLUTION": f"Alle Werte für {param1_key}",
                    "table": {param1_key: param1_table},
                    "query_type": "one_param1_all_param2",
                    "filter_param1": param1_key,
                    "total_entries": len(param1_table),
                    "source": NORM_FOUNDATION,
                    "note": f"Alle {FUNCTION_PARAM_2_NAME}-Werte für {FUNCTION_PARAM_1_NAME}='{param1_key}'"
                }
        
        # === EINZELWERT-ABFRAGE ===
        
        else:
            # Finde korrekten Parameter 1 (case-insensitive)
            param1_key = None
            for key in NORMWERTE_TABELLE.keys():
                if key.upper() == param1.upper():
                    param1_key = key
                    break
            
            # Validierung Parameter 1
            if not param1_key:
                available_param1 = ", ".join(get_available_param1_values())
                return {
                    "error": f"Unbekannter {FUNCTION_PARAM_1_NAME}: {param1}",
                    "verfügbare_werte": available_param1 + " oder 'all'",
                    "example": f"{FUNCTION_PARAM_1_NAME}='{FUNCTION_PARAM_1_EXAMPLE}'"
                }
            
            # Validierung Parameter 2
            if param2 not in get_available_param2_values():
                available_param2 = ", ".join(get_available_param2_values())
                return {
                    "error": f"Unbekannter {FUNCTION_PARAM_2_NAME}: {param2}",
                    "verfügbare_werte": available_param2 + " oder 'all'",
                    "example": f"{FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}'"
                }
            
            # Wert aus Tabelle holen
            normwert = NORMWERTE_TABELLE[param1_key][param2]
            
            # Mit Einheit als Quantity (optional)
            # result_quantity = normwert * ureg.millimeter  # ANPASSEN: passende Einheit
            
            return {
                "📊 TABLE LOOKUP SOLUTION": "Einzelwert aus Normtabelle",
                "normwert": f"{normwert} [EINHEIT]",  # ANPASSEN: richtige Einheit
                "query_type": "single_value",
                "input_parameters": {
                    FUNCTION_PARAM_1_NAME: param1_key,
                    FUNCTION_PARAM_2_NAME: param2
                },
                "source": NORM_FOUNDATION,
                "note": f"Normwert für {param1_key} mit {param2}"
            }
        
    except Exception as e:
        return {
            "error": f"Fehler bei Tabellen-Lookup: {str(e)}",
            "type": type(e).__name__,
            "hinweis": "Prüfen Sie die verfügbaren Parameter-Werte"
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
        # ❌ FALSCH: schraubgroesse: PARAMETER_SCHRAUBGROESSE (Variable existiert nicht!)
        # ✅ RICHTIG: FUNCTION_PARAM_1_NAME: PARAMETER_SCHRAUBGROESSE (Konstante)
        "parameters": {
            FUNCTION_PARAM_1_NAME: PARAMETER_DEUTSCHER_PARAMETER_1,
            FUNCTION_PARAM_2_NAME: PARAMETER_DEUTSCHER_PARAMETER_2,
            # FUNCTION_PARAM_3_NAME: PARAMETER_DEUTSCHER_PARAMETER_3,  # Optional - entfernen wenn nicht benötigt
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

def calculate(deutscher_parameter_1: str, deutscher_parameter_2: str) -> Dict:
    """Legacy-Funktion für Kompatibilität"""
    return solve_tabellenwerk_lookup(deutscher_parameter_1, deutscher_parameter_2)

# ================================================================================================
# 🎯 TABELLENWERK TEMPLATE USAGE EXAMPLE 🎯
# ================================================================================================
"""
⚠️ ⚠️ ⚠️ HÄUFIGER FEHLER - REGISTRY-DISCOVERY ⚠️ ⚠️ ⚠️
VERWENDEN SIE IMMER FUNCTION_PARAM_*_NAME KONSTANTEN IM PARAMETERS DICTIONARY!

❌ FALSCH:
"parameters": {
    schraubgroesse: PARAMETER_SCHRAUBGROESSE,  # Variable existiert nicht!
}

✅ RICHTIG:
"parameters": {
    FUNCTION_PARAM_1_NAME: PARAMETER_SCHRAUBGROESSE,  # Konstante
}

Dieser Fehler führt zu: "ERROR: Failed to load metadata: name 'schraubgroesse' is not defined"
⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️

ANPASSUNGS-CHECKLISTE für neue Tabellenwerk-Tools:

1. ✅ GRUNDKONFIGURATION anpassen:
   - TOOL_NAME, TOOL_TAGS (immer "tabellenwerk" einschließen)
   - HAS_SOLVING = "none" (immer für Tabellenwerk)
   - NORM_FOUNDATION setzen (Pflicht!)

2. ✅ FUNKTIONSPARAMETER-DEFINITIONEN anpassen:
   - FUNCTION_PARAM_*_NAME mit deutschen Namen
   - FUNCTION_PARAM_*_ALLOWED_VALUES definieren
   - Immer "all" in allowed_values einschließen

3. ✅ NORMWERTE_TABELLE mit echten Daten füllen
4. ✅ solve_tabellenwerk_lookup mit spezifischer Logik
5. ✅ Einheiten in Ausgabe anpassen ([EINHEIT] ersetzen)
6. ✅ TOOL_ASSUMPTIONS, TOOL_LIMITATIONS für Norm anpassen

Besonderheiten von Tabellenwerk-Tools:
- Kein Target-System (alle Parameter sind Input)
- allowed_values für alle Parameter definiert
- "all" Parameter für Tabellen-Übersichten
- query_type in Ausgabe für verschiedene Abfrage-Modi
- Normwerte mit source/note für Nachvollziehbarkeit
- HAS_SOLVING = "none" (keine Berechnungen)

Abfrage-Modi:
1. Einzelwert: spezifische Werte für alle Parameter
2. Teilübersicht: "all" für einen Parameter
3. Komplette Tabelle: "all" für alle Parameter
""" 