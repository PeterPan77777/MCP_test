#!/usr/bin/env python3
"""
Durchgangslöcher für metrische Schrauben - DIN-Normwerte M6-M150

Stellt Normwerte für Durchgangslöcher metrischer Schrauben bereit.
Die Werte basieren auf DIN-Normen und Industriestandards.

WICHTIG: Dieses Tool führt KEINE symbolische Berechnungen durch!
Es handelt sich um eine reine Tabellen-Abfrage mit festen Normwerten.

⚠️ NAMENSKONVENTION: ALLE Parameter-Namen MÜSSEN DEUTSCH sein!
Beispiele: schraubgroesse, lochklasse, werkstoff, festigkeitsklasse, durchmesser, dicke

Normwerte-Tabelle für Durchgangslöcher nach DIN-Standards.
Unterstützt Schraubengrößen M6 bis M150 mit drei Lochklassen (fein, mittel, grob).
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "durchgangsloecher_metrische_schrauben"
TOOL_TAGS = ["tabellenwerk", "schrauben"]
TOOL_SHORT_DESCRIPTION = "Durchgangslöcher für metrische Schrauben - DIN-Normwerte M6-M150"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "none"  # Tabellenwerk-Tools haben IMMER "none"

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
# ⚠️ WICHTIGE NAMENSKONVENTION: ALLE PARAMETER-NAMEN MÜSSEN DEUTSCH SEIN! ⚠️
FUNCTION_PARAM_1_NAME = "schraubgroesse"
FUNCTION_PARAM_1_DESC = "Schraubengröße (z.B. 'M6', 'M10', 'M20') oder 'all' für alle Größen"
FUNCTION_PARAM_1_EXAMPLE = "M10"
FUNCTION_PARAM_1_ALLOWED_VALUES = ["M6", "M7", "M8", "M10", "M12", "M14", "M16", "M18", "M20", "M22", "M24", "M27", "M30", "M33", "M36", "M39", "M42", "M45", "M48", "M52", "M56", "M60", "M64", "M68", "M72", "M76", "M80", "M85", "M90", "M95", "M100", "M105", "M110", "M115", "M120", "M125", "M130", "M140", "M150", "all"]

FUNCTION_PARAM_2_NAME = "lochklasse"
FUNCTION_PARAM_2_DESC = "Lochklasse ('fein', 'mittel', 'grob') oder 'all' für alle Klassen"
FUNCTION_PARAM_2_EXAMPLE = "mittel"
FUNCTION_PARAM_2_ALLOWED_VALUES = ["fein", "mittel", "grob", "all"]

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Stellt Normwerte für Durchgangslöcher metrischer Schrauben aus DIN-Normen bereit.

WICHTIG: Keine symbolische Berechnung - reine Tabellen-Abfrage mit festen DIN-Normwerten.
Verfügbare Schraubengrößen: M6 bis M150. Verfügbare Lochklassen: fein, mittel, grob.
ERWEITERT: Unterstützt 'all' für komplette Tabellen-Übersichten.

Eingabeparameter:
- {FUNCTION_PARAM_1_NAME}: {FUNCTION_PARAM_1_DESC}
- {FUNCTION_PARAM_2_NAME}: {FUNCTION_PARAM_2_DESC}

Ausgabe:
- durchmesser: Durchmesser des Durchgangslochs in mm

Norm-Grundlage: DIN-Normwerte für Durchgangslöcher
Tabellen-Umfang: 38 Schraubengrößen × 3 Lochklassen = 114 Werte"""

# Parameter-Definitionen für Metadaten (mit allowed_values für Tabellenwerk!)
PARAMETER_SCHRAUBGROESSE = {
    "type": "string",
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "allowed_values": FUNCTION_PARAM_1_ALLOWED_VALUES
}

PARAMETER_LOCHKLASSE = {
    "type": "string", 
    "description": FUNCTION_PARAM_2_DESC,
    "example": FUNCTION_PARAM_2_EXAMPLE,
    "allowed_values": FUNCTION_PARAM_2_ALLOWED_VALUES
}

# Output-Definition
OUTPUT_RESULT = {
    "type": "TableLookup",
    "description": "Durchgangsloch-Durchmesser oder Tabellen-Übersicht mit DIN-Normwerten",
    "format": "Einzelwert, Teilübersicht oder komplette Tabelle"
}

# Beispiele (für Tabellenwerk spezifisch - mit "all" Funktionalität)
TOOL_EXAMPLES = [
    {
        "title": f"Einzelwert-Abfrage: {FUNCTION_PARAM_1_EXAMPLE} mit {FUNCTION_PARAM_2_EXAMPLE}",
        "input": {FUNCTION_PARAM_1_NAME: FUNCTION_PARAM_1_EXAMPLE, FUNCTION_PARAM_2_NAME: FUNCTION_PARAM_2_EXAMPLE},
        "output": "11.0 mm Durchgangsloch-Durchmesser"
    },
    {
        "title": f"Alle Lochklassen für {FUNCTION_PARAM_1_EXAMPLE}",
        "input": {FUNCTION_PARAM_1_NAME: FUNCTION_PARAM_1_EXAMPLE, FUNCTION_PARAM_2_NAME: "all"},
        "output": f"Tabelle aller {FUNCTION_PARAM_2_NAME}-Werte für {FUNCTION_PARAM_1_EXAMPLE}"
    },
    {
        "title": f"Alle Schraubengrößen für {FUNCTION_PARAM_2_EXAMPLE}",
        "input": {FUNCTION_PARAM_1_NAME: "all", FUNCTION_PARAM_2_NAME: FUNCTION_PARAM_2_EXAMPLE},
        "output": f"Tabelle aller {FUNCTION_PARAM_1_NAME}-Werte für {FUNCTION_PARAM_2_EXAMPLE}"
    },
    {
        "title": "Komplette DIN-Normtabelle",
        "input": {FUNCTION_PARAM_1_NAME: "all", FUNCTION_PARAM_2_NAME: "all"},
        "output": "Vollständige DIN-Normwerte-Tabelle (114 Werte)"
    }
]

# Annahmen
TOOL_ASSUMPTIONS = [
    "DIN-Normwerte entsprechen aktuellen Standards",
    "Tabellen-Werte sind für Standardbedingungen bei Raumtemperatur gültig",
    "Durchgangslöcher für Standard-Verbindungen ohne besondere Anforderungen"
]

# Einschränkungen  
TOOL_LIMITATIONS = [
    "Nur vordefinierte Werte aus DIN-Normtabellen verfügbar",
    "Keine Interpolation zwischen Tabellen-Werten",
    "Nur für metrische Schrauben M6 bis M150",
    "Keine Berücksichtigung von Fertigungstoleranzen"
]

# Mathematische Grundlagen (für Tabellenwerk meist leer)
MATHEMATICAL_FOUNDATION = ""

# Normengrundlage (PFLICHTFELD für Tabellenwerk!)
NORM_FOUNDATION = "DIN-Normwerte für Durchgangslöcher metrischer Schrauben"

# ===== AUTOMATISCH BERECHNET =====
PARAMETER_COUNT = len([name for name in globals() if name.startswith('PARAMETER_')])

# ================================================================================================
# 🔧 IMPORTS & DEPENDENCIES 🔧
# ================================================================================================

from typing import Dict, Annotated, List, Any, Optional
import sys
import os

# Import des Einheiten-Utilities (optional für Tabellenwerk)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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
# DIN-Normwerte für Durchgangslöcher metrischer Schrauben
DURCHGANGSLOCH_TABELLE = {
    "M6": {"fein": 6.4, "mittel": 6.6, "grob": 7.0},
    "M7": {"fein": 7.4, "mittel": 7.6, "grob": 7.8},
    "M8": {"fein": 8.4, "mittel": 9.0, "grob": 10.0},
    "M10": {"fein": 10.5, "mittel": 11.0, "grob": 12.0},
    "M12": {"fein": 13.0, "mittel": 13.5, "grob": 14.5},
    "M14": {"fein": 15.0, "mittel": 15.5, "grob": 16.5},
    "M16": {"fein": 17.0, "mittel": 17.5, "grob": 18.5},
    "M18": {"fein": 19.0, "mittel": 20.0, "grob": 21.0},
    "M20": {"fein": 21.0, "mittel": 22.0, "grob": 24.0},
    "M22": {"fein": 23.0, "mittel": 24.0, "grob": 26.0},
    "M24": {"fein": 25.0, "mittel": 26.0, "grob": 28.0},
    "M27": {"fein": 28.0, "mittel": 30.0, "grob": 32.0},
    "M30": {"fein": 31.0, "mittel": 33.0, "grob": 35.0},
    "M33": {"fein": 34.0, "mittel": 36.0, "grob": 38.0},
    "M36": {"fein": 37.0, "mittel": 39.0, "grob": 42.0},
    "M39": {"fein": 40.0, "mittel": 42.0, "grob": 45.0},
    "M42": {"fein": 43.0, "mittel": 45.0, "grob": 48.0},
    "M45": {"fein": 46.0, "mittel": 48.0, "grob": 52.0},
    "M48": {"fein": 50.0, "mittel": 52.0, "grob": 56.0},
    "M52": {"fein": 54.0, "mittel": 56.0, "grob": 62.0},
    "M56": {"fein": 58.0, "mittel": 62.0, "grob": 66.0},
    "M60": {"fein": 62.0, "mittel": 66.0, "grob": 70.0},
    "M64": {"fein": 66.0, "mittel": 70.0, "grob": 74.0},
    "M68": {"fein": 70.0, "mittel": 74.0, "grob": 78.0},
    "M72": {"fein": 74.0, "mittel": 78.0, "grob": 82.0},
    "M76": {"fein": 78.0, "mittel": 82.0, "grob": 86.0},
    "M80": {"fein": 82.0, "mittel": 86.0, "grob": 91.0},
    "M85": {"fein": 87.0, "mittel": 91.0, "grob": 96.0},
    "M90": {"fein": 93.0, "mittel": 96.0, "grob": 101.0},
    "M95": {"fein": 98.0, "mittel": 101.0, "grob": 107.0},
    "M100": {"fein": 104.0, "mittel": 107.0, "grob": 112.0},
    "M105": {"fein": 109.0, "mittel": 112.0, "grob": 117.0},
    "M110": {"fein": 114.0, "mittel": 117.0, "grob": 122.0},
    "M115": {"fein": 119.0, "mittel": 122.0, "grob": 127.0},
    "M120": {"fein": 124.0, "mittel": 127.0, "grob": 132.0},
    "M125": {"fein": 129.0, "mittel": 132.0, "grob": 137.0},
    "M130": {"fein": 134.0, "mittel": 137.0, "grob": 144.0},
    "M140": {"fein": 144.0, "mittel": 147.0, "grob": 155.0},
    "M150": {"fein": 155.0, "mittel": 158.0, "grob": 165.0}
}

# Hilfsfunktionen für Tabellen-Zugriff
def get_available_schraubgroessen() -> List[str]:
    """Gibt alle verfügbaren Schraubengrößen zurück"""
    return sorted(DURCHGANGSLOCH_TABELLE.keys(), key=lambda x: int(x[1:]))

def get_available_lochklassen() -> List[str]:
    """Gibt alle verfügbaren Lochklassen zurück"""
    return ["fein", "mittel", "grob"]

def get_diameter_range() -> Dict[str, float]:
    """Gibt den Bereich der verfügbaren Durchmesser zurück"""
    all_diameters = []
    for screw_data in DURCHGANGSLOCH_TABELLE.values():
        all_diameters.extend(screw_data.values())
    
    return {
        "min_diameter_mm": min(all_diameters),
        "max_diameter_mm": max(all_diameters),
        "screw_size_range": "M6 bis M150"
    }

# ================================================================================================
# 🎯 TOOL FUNCTIONS 🎯
# ================================================================================================

def solve_durchgangsloch_lookup(
    # ⚠️ Hier die konfigurierten Parameter-Namen verwenden:
    schraubgroesse: Annotated[str, FUNCTION_PARAM_1_DESC],  
    lochklasse: Annotated[str, FUNCTION_PARAM_2_DESC]
) -> Dict:
    """
    📊 TABLE LOOKUP SOLUTION
    
    Führt Tabellen-Lookup in DIN-Normwerte-Tabelle für Durchgangslöcher durch.
    
    Unterstützt verschiedene Abfrage-Modi:
    - Einzelwert: spezifische Parameter-Kombination
    - Teilübersicht: 'all' für einen Parameter
    - Komplette Tabelle: 'all' für alle Parameter
    """
    try:
        # Parameter normalisieren
        schraubgroesse = schraubgroesse.strip().upper()
        lochklasse = lochklasse.strip().lower()
        
        # === TABELLEN-ABFRAGEN (mit "all"-Unterstützung) ===
        
        if schraubgroesse == "ALL" and lochklasse == "all":
            # Komplette Tabelle zurückgeben
            complete_table = {}
            for size, classes in DURCHGANGSLOCH_TABELLE.items():
                complete_table[size] = {
                    cls: f"{diameter} mm" for cls, diameter in classes.items()
                }
            
            return {
                "📊 TABLE LOOKUP SOLUTION": "Komplette DIN-Normwerte-Tabelle",
                "table": complete_table,
                "query_type": "complete_table",
                "total_entries": len(DURCHGANGSLOCH_TABELLE) * 3,
                "available_schraubgroessen": list(DURCHGANGSLOCH_TABELLE.keys()),
                "available_lochklassen": get_available_lochklassen(),
                "source": NORM_FOUNDATION,
                "note": "Vollständige DIN-Normwerte-Tabelle für alle Schraubengrößen und Lochklassen"
            }
        
        elif schraubgroesse == "ALL" and lochklasse in get_available_lochklassen():
            # Alle Schraubengrößen für eine Lochklasse
            lochklasse_table = {}
            for size, classes in DURCHGANGSLOCH_TABELLE.items():
                if lochklasse in classes:
                    lochklasse_table[size] = f"{classes[lochklasse]} mm"
            
            return {
                "📊 TABLE LOOKUP SOLUTION": f"Alle Schraubengrößen für {lochklasse}",
                "table": lochklasse_table,
                "query_type": "all_schraubgroessen_one_lochklasse",
                "filter_lochklasse": lochklasse,
                "total_entries": len(lochklasse_table),
                "source": NORM_FOUNDATION,
                "note": f"Alle {FUNCTION_PARAM_1_NAME}-Werte für {FUNCTION_PARAM_2_NAME}='{lochklasse}'"
            }
        
        elif schraubgroesse in DURCHGANGSLOCH_TABELLE and lochklasse == "all":
            # Alle Lochklassen für eine Schraubengröße
            schraubgroesse_table = {}
            for cls, diameter_value in DURCHGANGSLOCH_TABELLE[schraubgroesse].items():
                schraubgroesse_table[cls] = f"{diameter_value} mm"
            
            return {
                "📊 TABLE LOOKUP SOLUTION": f"Alle Lochklassen für {schraubgroesse}",
                "table": {schraubgroesse: schraubgroesse_table},
                "query_type": "one_schraubgroesse_all_lochklassen",
                "filter_schraubgroesse": schraubgroesse,
                "total_entries": len(schraubgroesse_table),
                "source": NORM_FOUNDATION,
                "note": f"Alle {FUNCTION_PARAM_2_NAME}-Werte für {FUNCTION_PARAM_1_NAME}='{schraubgroesse}'"
            }
        
        # === EINZELWERT-ABFRAGE ===
        
        else:
            # Validierung Schraubengröße
            if schraubgroesse not in DURCHGANGSLOCH_TABELLE:
                available_schraubgroessen = ", ".join(get_available_schraubgroessen())
                return {
                    "error": f"Unbekannte {FUNCTION_PARAM_1_NAME}: {schraubgroesse}",
                    "verfügbare_werte": available_schraubgroessen + " oder 'all'",
                    "example": f"{FUNCTION_PARAM_1_NAME}='{FUNCTION_PARAM_1_EXAMPLE}'"
                }
            
            # Validierung Lochklasse
            if lochklasse not in get_available_lochklassen():
                available_lochklassen = ", ".join(get_available_lochklassen())
                return {
                    "error": f"Unbekannte {FUNCTION_PARAM_2_NAME}: {lochklasse}",
                    "verfügbare_werte": available_lochklassen + " oder 'all'",
                    "example": f"{FUNCTION_PARAM_2_NAME}='{FUNCTION_PARAM_2_EXAMPLE}'"
                }
            
            # Wert aus Tabelle holen
            durchmesser_value = DURCHGANGSLOCH_TABELLE[schraubgroesse][lochklasse]
            
            # Mit Einheit als Quantity
            durchmesser_quantity = durchmesser_value * ureg.millimeter
            
            return {
                "📊 TABLE LOOKUP SOLUTION": "Einzelwert aus DIN-Normtabelle",
                "durchmesser": durchmesser_quantity,
                "query_type": "single_value",
                "input_parameters": {
                    FUNCTION_PARAM_1_NAME: schraubgroesse,
                    FUNCTION_PARAM_2_NAME: lochklasse
                },
                "source": NORM_FOUNDATION,
                "note": f"Durchgangsloch für {schraubgroesse} Schraube, Klasse '{lochklasse}'"
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
        "parameters": {
            FUNCTION_PARAM_1_NAME: PARAMETER_SCHRAUBGROESSE,
            FUNCTION_PARAM_2_NAME: PARAMETER_LOCHKLASSE,
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
        "parameter_schraubgroesse": PARAMETER_SCHRAUBGROESSE,
        "parameter_lochklasse": PARAMETER_LOCHKLASSE
    }

def calculate(schraubgroesse: str, lochklasse: str) -> Dict:
    """Legacy-Funktion für Kompatibilität"""
    return solve_durchgangsloch_lookup(schraubgroesse, lochklasse)

