#!/usr/bin/env python3
"""
[Tool Name] - [Kurzbeschreibung für list_engineering_tools]

Bietet umfassende Informationen und Dokumentation zu [WISSENSBEREICH].

WICHTIG: Dieses Tool führt KEINE Berechnungen durch und benötigt KEINE Input-Parameter!
Es handelt sich um ein reines Wissens-/Context-Tool für strukturierte Informationsvermittlung.

⚠️ NAMENSKONVENTION: Auch Context-Tools sollten deutsche Namen verwenden!
Beispiele: schrauben_info, werkstoff_wissen, norm_uebersicht, konstruktions_leitfaden

[Detaillierte Beschreibung des Wissensbereichs, Normen, Standards, Best Practices]
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "[tool_name]"  # ANPASSEN: eindeutiger Tool-Name (z.B. "schrauben_info", "werkstoff_wissen")
TOOL_TAGS = ["wissen", "dokumentation"]  # ANPASSEN: ["wissen", "schrauben"] | ["wissen", "werkstoffe"] | ["wissen", "normen"]
TOOL_SHORT_DESCRIPTION = "[Kurze Beschreibung] - [Was für Wissen vermittelt wird]"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "none"  # Context-Tools haben IMMER "none" (keine Berechnungen, keine Tabellen-Lookups)

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
# Context-Tools haben normalerweise KEINE Parameter!
# Falls doch optionale Parameter gewünscht (z.B. für verschiedene Detail-Level):

# Optional: Parameter für verschiedene Ausgabe-Modi (meist nicht nötig)
FUNCTION_PARAM_1_NAME = "detail_level"  # OPTIONAL - kann entfernt werden
FUNCTION_PARAM_1_DESC = "Detaillierungsgrad der Ausgabe ('kurz', 'standard', 'vollständig')"
FUNCTION_PARAM_1_EXAMPLE = "standard"
FUNCTION_PARAM_1_ALLOWED_VALUES = ["kurz", "standard", "vollständig"]
FUNCTION_PARAM_1_DEFAULT = "standard"

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Bietet umfassende Informationen und Dokumentation zu [WISSENSBEREICH].

WICHTIG: Keine Parameter erforderlich - reine Wissens- und Informationsvermittlung.
Strukturierte Ausgabe mit [BESCHREIBUNG DER INHALTE].

Inhaltsbereiche:
- [WISSENSBEREICH 1]: [Beschreibung]
- [WISSENSBEREICH 2]: [Beschreibung]
- [WISSENSBEREICH 3]: [Beschreibung]

Ausgabe:
- Strukturierte Informationen (meist Markdown-formatiert)
- Best Practices und Empfehlungen
- Norm- und Standardreferenzen
- Praktische Anwendungshinweise

Wissensgrundlage: [NORMEN/STANDARDS/EXPERTISE]
Umfang: [BESCHREIBUNG DES WISSENSUMFANGS]"""

# Parameter-Definitionen für Metadaten (meist leer für Context-Tools)
PARAMETER_DETAIL_LEVEL = {
    "type": "string",  
    "description": FUNCTION_PARAM_1_DESC,
    "example": FUNCTION_PARAM_1_EXAMPLE,
    "allowed_values": FUNCTION_PARAM_1_ALLOWED_VALUES,
    "default": FUNCTION_PARAM_1_DEFAULT,
    "optional": True
}

# Output-Definition
OUTPUT_RESULT = {
    "type": "ContextInformation",
    "description": "Strukturierte Wissens- und Dokumentationsinhalte",
    "format": "Markdown-formatierte Texte, Listen, Tabellen und strukturierte Informationen"
}

# Beispiele (für Context-Tools meist nur ein Beispiel ohne Parameter)
TOOL_EXAMPLES = [
    {
        "title": "Vollständige Wissens-Dokumentation",
        "input": {},  # Keine Parameter
        "output": "Umfassende strukturierte Informationen zu [WISSENSBEREICH]"
    },
    {
        "title": "Mit optionalem Detail-Level (falls implementiert)",
        "input": {FUNCTION_PARAM_1_NAME: FUNCTION_PARAM_1_EXAMPLE},
        "output": f"Informationen mit {FUNCTION_PARAM_1_EXAMPLE} Detaillierungsgrad"
    }
]

# Annahmen
TOOL_ASSUMPTIONS = [
    "Aktuelle Normen und Standards werden referenziert",
    "Best Practices entsprechen dem Stand der Technik",
    "[weitere wissens-spezifische Annahmen]"
]

# Einschränkungen  
TOOL_LIMITATIONS = [
    "Statische Informationen - keine dynamischen Berechnungen",
    "Wissen basiert auf Implementierungsstand der Template-Anwendung",
    "Spezifische Anwendungsfälle können zusätzliche Recherche erfordern",
    "[weitere wissens-spezifische Einschränkungen]"
]

# Mathematische Grundlagen (für Context-Tools meist leer oder beschreibend)
MATHEMATICAL_FOUNDATION = ""  # Meist leer oder beschreibend für Context-Tools

# Wissensgrundlage (PFLICHTFELD für Context-Tools!)
KNOWLEDGE_FOUNDATION = "[NORMEN/STANDARDS/EXPERTISE, z.B. 'DIN EN ISO', 'VDI Richtlinien', 'Fachexpertise']"

# ===== AUTOMATISCH BERECHNET =====
PARAMETER_COUNT = len([name for name in globals() if name.startswith('PARAMETER_')])

# ================================================================================================
# 🔧 IMPORTS & DEPENDENCIES 🔧
# ================================================================================================

from typing import Dict, Annotated, List, Any, Optional
import sys
import os

# Context-Tools benötigen meist keine speziellen Imports
# Optional: Markdown-Processing, falls dynamische Markdown-Generierung gewünscht

# ================================================================================================
# 🎯 WISSENS-INHALTE 🎯
# ================================================================================================

# ===== WISSENS-DEFINITIONEN =====
# ANPASSEN: Hier die strukturierten Wissens-Inhalte definieren

# Hauptinformations-Text (meist Markdown)
MAIN_INFORMATION_TEXT = """# [Wissensbereich] - Vollständige Übersicht

**[Kurze Einführung in den Wissensbereich]**

[Detaillierte Beschreibung und Überblick]

---

## GRUNDLAGEN

### [Grundlagen-Bereich 1]:
- **[Punkt 1]**: [Beschreibung]
- **[Punkt 2]**: [Beschreibung]
- **[Punkt 3]**: [Beschreibung]

### [Grundlagen-Bereich 2]:
- **[Aspekt A]**: [Detailierte Erklärung]
- **[Aspekt B]**: [Detailierte Erklärung]

## NORMEN UND STANDARDS

### [Norm/Standard 1]:
**[Norm-Nummer und Titel]**
- [Anwendungsbereich]
- [Wichtige Inhalte]
- [Praktische Hinweise]

### [Norm/Standard 2]:
**[Norm-Nummer und Titel]**
- [Anwendungsbereich]
- [Wichtige Inhalte]
- [Praktische Hinweise]

## BEST PRACTICES

**[Empfehlung 1]:**
- [Detaillierte Beschreibung]
- [Anwendungsbeispiele]

**[Empfehlung 2]:**
- [Detaillierte Beschreibung]
- [Anwendungsbeispiele]

## PRAKTISCHE ANWENDUNG

### [Anwendungsfall 1]:
1. **[Schritt 1]**: [Beschreibung]
2. **[Schritt 2]**: [Beschreibung]
3. **[Schritt 3]**: [Beschreibung]

### [Anwendungsfall 2]:
- **[Aspekt A]**: [Beschreibung]
- **[Aspekt B]**: [Beschreibung]

## TECHNISCHE HINWEISE

**[Kategorie 1]:**
- [Hinweis 1]
- [Hinweis 2]

**[Kategorie 2]:**
- [Hinweis 1]
- [Hinweis 2]

---

## VERFÜGBARE TOOLS

### Verwandte Engineering-Tools:
1. **[tool_name_1]**: [Beschreibung]
2. **[tool_name_2]**: [Beschreibung]
3. **[tool_name_3]**: [Beschreibung]

---

## WEITERE INFORMATIONEN

**Weiterführende Normen:**
- [Norm 1]: [Kurzbeschreibung]
- [Norm 2]: [Kurzbeschreibung]

**Literaturempfehlungen:**
- [Quelle 1]: [Beschreibung]
- [Quelle 2]: [Beschreibung]

---

*Diese Dokumentation wird kontinuierlich nach aktuellen Normen und Erkenntnissen aktualisiert.*
"""

# Zusätzliche strukturierte Informationen
STRUCTURED_INFO = {
    "wissensbereich": "[WISSENSBEREICH]",
    "normen_referenzen": ["[Norm 1]", "[Norm 2]", "[Norm 3]"],
    "anwendungsbereiche": ["[Bereich 1]", "[Bereich 2]", "[Bereich 3]"],
    "verwandte_tools": ["[tool_1]", "[tool_2]", "[tool_3]"],
    "expertise_level": "Fachexperte/Ingenieur",
    "aktualisiert": "2024-01-XX"  # ANPASSEN: Aktualisierungsdatum
}

# Hilfsfunktionen für Wissens-Zugriff
def get_available_knowledge_areas() -> List[str]:
    """Gibt alle verfügbaren Wissensbereiche zurück"""
    return STRUCTURED_INFO["anwendungsbereiche"]

def get_referenced_norms() -> List[str]:
    """Gibt alle referenzierten Normen zurück"""
    return STRUCTURED_INFO["normen_referenzen"]

def get_related_tools() -> List[str]:
    """Gibt alle verwandten Tools zurück"""
    return STRUCTURED_INFO["verwandte_tools"]

# ================================================================================================
# 🎯 TOOL FUNCTIONS 🎯
# ================================================================================================

def solve_context_information(
    # Context-Tools haben meist KEINE Parameter!
    # Optional: detail_level Parameter falls verschiedene Ausgabe-Modi gewünscht
    detail_level: Annotated[str, FUNCTION_PARAM_1_DESC] = FUNCTION_PARAM_1_DEFAULT
) -> Dict:
    """
    📖 CONTEXT INFORMATION SOLUTION
    
    Liefert strukturierte Wissens- und Dokumentationsinhalte.
    
    Keine Berechnungen oder Tabellen-Lookups - reine Informationsvermittlung.
    """
    try:
        # Optional: Verschiedene Detail-Level implementieren
        if detail_level == "kurz":
            # Kurze Zusammenfassung
            short_info = MAIN_INFORMATION_TEXT.split('\n\n')[0:3]  # Erste 3 Absätze
            info_content = '\n\n'.join(short_info)
            detail_note = "Kurze Übersicht - für vollständige Informationen 'standard' oder 'vollständig' wählen"
        
        elif detail_level == "vollständig":
            # Vollständige Informationen + zusätzliche Details
            info_content = MAIN_INFORMATION_TEXT
            detail_note = "Vollständige Dokumentation mit allen Details"
        
        else:  # "standard"
            # Standard-Ausgabe (komplette Haupt-Informationen)
            info_content = MAIN_INFORMATION_TEXT
            detail_note = "Standard-Dokumentation"
        
        return {
            "📖 CONTEXT INFORMATION SOLUTION": f"Wissens-Dokumentation zu {STRUCTURED_INFO['wissensbereich']}",
            "dokumentation": info_content,
            "detail_level": detail_level,
            "wissensbereich": STRUCTURED_INFO["wissensbereich"],
            "normen_referenzen": STRUCTURED_INFO["normen_referenzen"],
            "anwendungsbereiche": STRUCTURED_INFO["anwendungsbereiche"],
            "verwandte_tools": STRUCTURED_INFO["verwandte_tools"],
            "expertise_level": STRUCTURED_INFO["expertise_level"],
            "aktualisiert": STRUCTURED_INFO["aktualisiert"],
            "source": KNOWLEDGE_FOUNDATION,
            "note": detail_note
        }
        
    except Exception as e:
        return {
            "error": f"Fehler bei Wissens-Ausgabe: {str(e)}",
            "type": type(e).__name__,
            "hinweis": "Context-Tools sollten keine Fehler produzieren - prüfen Sie die Template-Anpassung"
        }

# Alternative: Einfache Funktion ohne Parameter (häufigster Fall)
def solve_simple_context() -> Dict:
    """
    📖 CONTEXT INFORMATION SOLUTION (Einfache Version ohne Parameter)
    
    Liefert vollständige Wissens-Dokumentation ohne Parameter.
    """
    return {
        "📖 CONTEXT INFORMATION SOLUTION": f"Wissens-Dokumentation zu {STRUCTURED_INFO['wissensbereich']}",
        "dokumentation": MAIN_INFORMATION_TEXT,
        "wissensbereich": STRUCTURED_INFO["wissensbereich"],
        "normen_referenzen": STRUCTURED_INFO["normen_referenzen"],
        "anwendungsbereiche": STRUCTURED_INFO["anwendungsbereiche"],
        "verwandte_tools": STRUCTURED_INFO["verwandte_tools"],
        "expertise_level": STRUCTURED_INFO["expertise_level"],
        "aktualisiert": STRUCTURED_INFO["aktualisiert"],
        "source": KNOWLEDGE_FOUNDATION,
        "note": "Vollständige Wissens-Dokumentation"
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
        # ❌ FALSCH: detail_level: PARAMETER_DETAIL_LEVEL (Variable existiert nicht!)
        # ✅ RICHTIG: FUNCTION_PARAM_1_NAME: PARAMETER_DETAIL_LEVEL (Konstante)
        # Context-Tools haben meist keine oder nur optionale Parameter
        "parameters": {
            # Nur wenn FUNCTION_PARAM_1_NAME definiert ist (optional für Context-Tools)
            FUNCTION_PARAM_1_NAME: PARAMETER_DETAIL_LEVEL
        } if 'PARAMETER_DETAIL_LEVEL' in globals() else {},
        
        # ✅ Beispiele im neuen Format
        "examples": TOOL_EXAMPLES,
        
        # ✅ Vollständige Metadaten für erweiterte Nutzung
        "tool_version": TOOL_VERSION,
        "output_result": OUTPUT_RESULT,
        "tool_assumptions": TOOL_ASSUMPTIONS,
        "tool_limitations": TOOL_LIMITATIONS,
        "mathematical_foundation": MATHEMATICAL_FOUNDATION,
        "knowledge_foundation": KNOWLEDGE_FOUNDATION,
        
        # ✅ Context-spezifische Metadaten
        "knowledge_areas": get_available_knowledge_areas(),
        "referenced_norms": get_referenced_norms(),
        "related_tools": get_related_tools(),
        
        # ✅ Backwards Compatibility (falls andere Teile das alte Format erwarten)
        "tool_tags": TOOL_TAGS,
        "tool_short_description": TOOL_SHORT_DESCRIPTION,
        "parameter_count": len([name for name in globals() if name.startswith('PARAMETER_')]),
        "tool_description": TOOL_DESCRIPTION
    }

def calculate(**kwargs) -> Dict:
    """
    Legacy-Funktion für Kompatibilität.
    
    Context-Tools benötigen meist keine Parameter,
    aber für Konsistenz mit anderen Templates implementiert.
    """
    detail_level = kwargs.get('detail_level', FUNCTION_PARAM_1_DEFAULT)
    return solve_context_information(detail_level)

# Alternative: Einfache calculate-Funktion ohne Parameter
def calculate_simple() -> Dict:
    """Einfache Legacy-Funktion ohne Parameter"""
    return solve_simple_context()

# ================================================================================================
# 🎯 CONTEXT TEMPLATE USAGE EXAMPLE 🎯
# ================================================================================================
"""
⚠️ ⚠️ ⚠️ HÄUFIGER FEHLER - REGISTRY-DISCOVERY ⚠️ ⚠️ ⚠️
VERWENDEN SIE IMMER FUNCTION_PARAM_*_NAME KONSTANTEN IM PARAMETERS DICTIONARY!

❌ FALSCH:
"parameters": {
    detail_level: PARAMETER_DETAIL_LEVEL,  # Variable existiert nicht!
}

✅ RICHTIG:
"parameters": {
    FUNCTION_PARAM_1_NAME: PARAMETER_DETAIL_LEVEL,  # Konstante
}

Dieser Fehler führt zu: "ERROR: Failed to load metadata: name 'detail_level' is not defined"
⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️

ANPASSUNGS-CHECKLISTE für neue Context-Tools:

1. ✅ GRUNDKONFIGURATION anpassen:
   - TOOL_NAME mit deutschem Namen (z.B. "schrauben_info", "werkstoff_wissen")
   - TOOL_TAGS mit "wissen" + Fachbereich (z.B. ["wissen", "schrauben"])
   - HAS_SOLVING = "none" (immer für Context-Tools)
   - KNOWLEDGE_FOUNDATION setzen (Pflicht!)

2. ✅ PARAMETER-DEFINITIONEN anpassen (meist nicht nötig):
   - Context-Tools haben normalerweise KEINE Parameter
   - Falls doch: detail_level oder ähnliche optionale Parameter
   - parameter_count wird meist 0 oder 1 (optional)

3. ✅ MAIN_INFORMATION_TEXT mit echtem Wissen füllen:
   - Markdown-formatierte Dokumentation
   - Strukturierte Abschnitte (Grundlagen, Normen, Best Practices)
   - Praktische Anwendungshinweise

4. ✅ STRUCTURED_INFO anpassen:
   - Normen-Referenzen auflisten
   - Anwendungsbereiche definieren
   - Verwandte Tools verlinken

5. ✅ solve_context_information anpassen:
   - Meist nur MAIN_INFORMATION_TEXT ausgeben
   - Optional: verschiedene Detail-Level implementieren

6. ✅ TOOL_ASSUMPTIONS, TOOL_LIMITATIONS für Wissensbereich anpassen

Besonderheiten von Context-Tools:
- KEINE Input-Parameter (außer optional detail_level)
- KEINE Berechnungen oder Tabellen-Lookups  
- HAS_SOLVING = "none"
- Ausgabe ist strukturierte Dokumentation (meist Markdown)
- 📖 CONTEXT INFORMATION SOLUTION Kennzeichnung
- KNOWLEDGE_FOUNDATION statt NORM_FOUNDATION
- Zusätzliche Metadaten: knowledge_areas, referenced_norms, related_tools

Häufige Anwendungsfälle:
- Übersichts-Tools (schrauben_info, werkstoff_uebersicht)
- Norm-Erklärungs-Tools (din_erklaerung, vdi_leitfaden)  
- Best-Practice-Tools (konstruktions_tipps, fertigungs_leitfaden)
- Einführungs-Tools (grundlagen_mechanik, einfuehrung_festigkeitslehre)
"""