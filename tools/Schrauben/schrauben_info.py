#!/usr/bin/env python3
"""
Schrauben-Informationssystem - Umfassende Übersicht über Schraubentechnik

Bietet umfassende Informationen und Dokumentation zu Schraubentechnik, DIN-Normen und VDI-Richtlinien.

WICHTIG: Dieses Tool führt KEINE Berechnungen durch und benötigt KEINE Input-Parameter!
Es handelt sich um ein reines Wissens-/Context-Tool für strukturierte Informationsvermittlung.

⚠️ NAMENSKONVENTION: Context-Tool mit deutschem Namen!
Beispiel: schrauben_info, werkstoff_wissen, norm_uebersicht, konstruktions_leitfaden

Umfassende Dokumentation zu Schraubentechnik nach DIN 13, VDI 2230 und ISO-Standards.
Idealer Einstiegspunkt für Engineering-Berechnungen und Best Practices.
"""

# ================================================================================================
# 🎯 TOOL-KONFIGURATION & PARAMETER-DEFINITIONEN 🎯
# ================================================================================================

# ===== 🔧 GRUNDKONFIGURATION =====
TOOL_NAME = "schrauben_info"
TOOL_TAGS = ["wissen", "schrauben", "DIN 13", "VDI 2230"]  # "wissen" als Haupt-Tag für Context-Tools
TOOL_SHORT_DESCRIPTION = "Schrauben-Informationssystem - Umfassende Übersicht über Schraubentechnik und Normen"
TOOL_VERSION = "1.0.0"
HAS_SOLVING = "none"  # Context-Tools haben IMMER "none"

# ===== 📝 FUNKTIONSPARAMETER-DEFINITIONEN =====
# Context-Tools haben normalerweise KEINE Parameter!
# Für schrauben_info: Keine Parameter erforderlich (reine Info-Ausgabe)

# ===== 📊 METADATEN-STRUKTUR =====
TOOL_DESCRIPTION = f"""Bietet umfassende Informationen und Dokumentation zu Schraubentechnik nach DIN 13 und VDI 2230.

WICHTIG: Keine Parameter erforderlich - reine Wissens- und Informationsvermittlung.
Strukturierte Ausgabe mit Schrauben-Engineering-Wissen, Normen und Best Practices.

Inhaltsbereiche:
- DIN 13 ISO-Metrische Gewinde: Vollständige Reihen-Klassifizierung und Geometrie
- VDI 2230 Schraubenverbindungen: Berechnungsgrundlagen und Auslegungsmethodik
- Engineering-Tools: Verfügbare Berechnungs- und Tabellenwerk-Tools
- Best Practices: Praktische Anwendungsempfehlungen und Konstruktionshinweise

Ausgabe:
- Strukturierte Informationen (Markdown-formatiert)
- Norm-Übersichten und Referenzen
- Tool-Übersicht mit Anwendungsempfehlungen
- Praktische Engineering-Hinweise

Wissensgrundlage: DIN 13-1 bis DIN 13-11, DIN 13-6, VDI 2230, ISO 262, Fachexpertise
Umfang: Vollständige Schrauben-Engineering-Dokumentation mit 1.081 ISO-Gewindedarstellung"""

# Output-Definition
OUTPUT_RESULT = {
    "type": "ContextInformation",
    "description": "Strukturierte Schrauben-Wissens- und Dokumentationsinhalte",
    "format": "Markdown-formatierte Schrauben-Dokumentation mit Normen, Tools und Best Practices"
}

# Beispiele (für Context-Tools meist nur ein Beispiel ohne Parameter)
TOOL_EXAMPLES = [
    {
        "title": "Vollständige Schrauben-Wissens-Dokumentation",
        "input": {},  # Keine Parameter
        "output": "Umfassende strukturierte Informationen zu Schraubentechnik, DIN/VDI-Normen und verfügbaren Tools"
    }
]

# Annahmen
TOOL_ASSUMPTIONS = [
    "Aktuelle DIN 13 und VDI 2230 Normen werden referenziert",
    "Best Practices entsprechen dem Stand der Schrauben-Engineering-Technik",
    "Tool-Referenzen entsprechen dem aktuellen MCP-Server-Stand",
    "ISO-Gewinde-Datenbank ist vollständig und aktuell"
]

# Einschränkungen  
TOOL_LIMITATIONS = [
    "Statische Informationen - keine dynamischen Berechnungen",
    "Wissen basiert auf Implementierungsstand der Schrauben-Tools im MCP-Server",
    "Spezifische Anwendungsfälle können zusätzliche Norm-Recherche erfordern",
    "Keine projekt-spezifischen Sicherheitsfaktoren oder Sonderfälle"
]

# Mathematische Grundlagen (für Context-Tools meist beschreibend)
MATHEMATICAL_FOUNDATION = "Beschreibung der VDI 2230 Berechnungsgrundlagen für Schraubenverbindungen, DIN 13 Gewindegeometrie-Formeln"

# Wissensgrundlage (PFLICHTFELD für Context-Tools!)
KNOWLEDGE_FOUNDATION = "DIN 13-1 bis DIN 13-11, DIN 13-6, VDI 2230, ISO 262, Schrauben-Engineering-Fachexpertise"

# ===== AUTOMATISCH BERECHNET =====
PARAMETER_COUNT = 0  # Keine Parameter für Context-Tools

# ================================================================================================
# 🔧 IMPORTS & DEPENDENCIES 🔧
# ================================================================================================

from typing import Dict, List, Any
import sys
import os

# Context-Tools benötigen meist keine speziellen Imports

# ================================================================================================
# 🎯 WISSENS-INHALTE 🎯
# ================================================================================================

# ===== WISSENS-DEFINITIONEN =====
# Schrauben-spezifische Wissens-Inhalte

# Hauptinformations-Text (Markdown-formatiert)
MAIN_INFORMATION_TEXT = """# Schrauben-Engineering-System - Vollständige Übersicht

**Umfassendes Engineering-Tool für Schraubenverbindungen nach VDI 2230**

Dieses System bietet vollständige Unterstützung für die Auslegung und Berechnung von Schraubenverbindungen nach den aktuellen Normen und Richtlinien.

---

## WICHTIGE GRUNDPRINZIPIEN

### Gewindebezeichnungen:
- **Regelgewinde**: M12, M16, M20 (Standard-Steigung nach DIN 13)
- **Feingewinde**: M12x1.25, M16x1.5, M20x1.5 (reduzierte Steigung)
- **Automatische Erkennung**: System erkennt automatisch Regel- vs. Feingewinde
- **Vollständige Abdeckung**: M1 bis M68 nach DIN 13/ISO 262

**Beispiele:**
- M12 → Regelgewinde mit 1.75mm Steigung
- M12x1.25 → Feingewinde mit 1.25mm Steigung  
- M16 → Regelgewinde mit 2.0mm Steigung
- M16x1.5 → Feingewinde mit 1.5mm Steigung

### DIN 13 - ISO-Metrische Gewinde:
- **Reihe 1**: Bevorzugte Gewinde (M1, M1.2, M1.6, M2, M2.5, M3, M4, M5, M6, M8, M10, M12, M16, M20, M24, M30, M36, M42, M48, M56, M64)
- **Reihe 2**: Zusätzliche Gewinde (M1.1, M1.4, M1.8, M2.2, M3.5, M4.5, M5.5, M7, M9, M11, M14, M18, M22, M27, M33, M39, M45, M52, M60, M68)
- **Reihe 3**: Sondergewinde (M1.3, M1.5, M1.7, M2.3, M2.6, M3.2, M4.2, M4.8, M5.2, M6.5, M7.5, M8.5, M9.5, M10.5, M12.5, M13.5, M15, M17, M19, M21, M23, M25, M26, M28, M29, M31, M32, M34, M35, M37, M38, M40, M41, M43, M44, M46, M47, M49, M50, M51, M53, M54, M55, M57, M58, M59, M61, M62, M63, M65, M66, M67)

### VDI 2230 - Schraubenverbindungen:
**Grundlagen der systematischen Berechnung von Schraubenverbindungen**

**Vorspannkraft-Berechnung:**
- F_V = F_Kerf × α_A (Erforderliche Vorspannkraft)
- α_A = Anziehfaktor (typisch 1.2-1.4)
- Berücksichtigung von Setzverlust und Relaxation

**Festigkeitsnachweis:**
- σ_zul = R_p0.2 / S_F (Zulässige Spannung)
- S_F = Sicherheitsfaktor (typisch 1.2-2.5)
- Kombinierte Beanspruchung aus Zug und Torsion

**Reibungskoeffizienten:**
- μ_G = 0.16 (ungeschmiert, Standard)
- μ_G = 0.12 (leicht geölt)
- μ_G = 0.08 (MoS₂-Paste, optimal)

**Anziehmomente:**
- M_A = F_V × d₂ × (P/(2π) + μ_G × d₂/2 + μ_K × D_Km/2)
- Berücksichtigung von Gewinde- und Kopfreibung
- Automatische Optimierung für verschiedene Schmierungen

### Vorspannkraft-Optimierung:
**Systematische Auswahl der optimalen Schrauben**

**Auswahlkriterien:**
1. **Vorspannkraft-Erfüllung**: F_V,max ≥ F_V,erf
2. **Festigkeitsklassen-Optimierung**: 8.8 → 10.9 → 12.9
3. **Gewinde-Reihen-Präferenz**: Reihe 1 > Reihe 2 > Reihe 3
4. **Reibungsoptimierung**: μ = 0.08 (MoS₂) bevorzugt
5. **Steigungsoptimierung**: Feingewinde für höhere Vorspannkraft

**Ranking-System:**
- Primär: Vorspannkraft-Erfüllung (Ausschlusskriterium)
- Sekundär: Festigkeitsklasse (höher = besser)
- Tertiär: Gewinde-Reihe (niedriger = besser)
- Quartär: Reibungskoeffizient (niedriger = besser)
- Quintär: Steigung (Feingewinde bevorzugt)

**Ausgabe-Optimierung:**
- Sortierung nach Eignung (beste Optionen zuerst)
- Klare Empfehlungen mit Begründung
- Vollständige technische Daten für Konstruktion

### Geometrische Berechnungen:
- **Spannungsquerschnitt**: A_s nach DIN 13 (exakte Formeln)
- **Kernquerschnitt**: A_3 = π × d₃²/4
- **Flankendurchmesser**: d₂ = d - 0.6495 × P
- **Kerndurchmesser**: d₃ = d - 1.2269 × P

## ANWENDUNGSEMPFEHLUNGEN

**Für Standard-Konstruktionen:**
- Verwenden Sie Reihe 1-Gewinde (M6, M8, M10, M12, M16, M20, M24...)
- Festigkeitsklasse 8.8 für normale Belastungen
- Festigkeitsklasse 10.9 für erhöhte Anforderungen

### Wann Feingewinde verwenden:
- **Höhere Vorspannkraft erforderlich**: Feingewinde bietet ca. 15-25% höhere Vorspannkraft
- **Dünnwandige Bauteile**: Geringere Gewindehöhe reduziert Kerbwirkung
- **Präzisionsanwendungen**: Feinere Einstellmöglichkeiten
- **Vibrationsbeanspruchung**: Bessere Selbsthemmung

### Wann Dehnschrauben verwenden:
- **Dynamische Belastungen**: Bessere Dauerfestigkeit
- **Große Klemmlängen**: Reduzierte Vorspannkraftverluste
- **Kritische Verbindungen**: Definierte Elastizität
- **Temperaturwechsel**: Bessere Kompensation von Längenänderungen

**Wichtig**: Dehnschrauben erfordern spezielle Anziehmethoden (Drehwinkelverfahren)

### Optimale Schraubenauswahl:
1. **Lastanalyse**: Bestimmen Sie die erforderliche Vorspannkraft
2. **Geometrie-Check**: Prüfen Sie verfügbaren Bauraum
3. **Werkstoff-Wahl**: Wählen Sie passende Festigkeitsklasse
4. **Schmierung**: Optimieren Sie Reibungskoeffizienten
5. **Anzugsstrategie**: Definieren Sie Anzugsmethode und -momente

---

## VERFÜGBARE TOOLS

### 1. schrauben_datenbank
**Vollständige Schraubendatenbank mit VDI 2230-Berechnungen**
- Alle metrischen Gewinde M1 bis M68
- Regel- und Feingewinde nach DIN 13
- Festigkeitsklassen 8.8, 10.9, 12.9
- Reibungskoeffizienten 0.08, 0.12, 0.16
- Vollständige VDI 2230-Berechnungen
- Optimierte Ausgabe für Engineering

### 2. schrauben_suche_vorspannkraft  
**Intelligente Schraubenauswahl nach Vorspannkraft-Anforderungen**
- Eingabe: Mindest-Vorspannkraft
- Ausgabe: Sortierte Liste aller geeigneten Schrauben
- Optimierungsempfehlungen
- Berücksichtigung aller Parameter

### 3. durchgangsloecher_metrische_schrauben
**Durchgangsloch-Dimensionen für metrische Schrauben**
- Normgerechte Bohrungsdurchmesser
- Toleranzangaben
- Konstruktionsempfehlungen

---

## TECHNISCHE HINWEISE

**Einheiten-System:**
- Kräfte: N, kN (automatische Konvertierung)
- Spannungen: MPa, N/mm² (automatische Konvertierung)  
- Momente: Nm, mNm (automatische Konvertierung)
- Längen: mm (Standard), m, cm (automatische Konvertierung)

**Genauigkeit:**
- Berechnungen nach VDI 2230 (aktuelle Ausgabe)
- Rundung auf technisch sinnvolle Stellen
- Berücksichtigung von Fertigungstoleranzen

**Sicherheitshinweise:**
- Alle Berechnungen sind Richtwerte
- Berücksichtigen Sie spezifische Anwendungsbedingungen
- Prüfen Sie kritische Verbindungen durch Versuche
- Beachten Sie Herstellerangaben für spezielle Schrauben

---

*Dieses System wird kontinuierlich nach aktuellen Normen und Erkenntnissen aktualisiert.*
"""

# Zusätzliche strukturierte Informationen
STRUCTURED_INFO = {
    "wissensbereich": "Schraubentechnik und Verbindungsauslegung",
    "normen_referenzen": ["DIN 13-1 bis DIN 13-11", "DIN 13-6", "VDI 2230", "ISO 262"],
    "anwendungsbereiche": ["Maschinenbau", "Konstruktion", "Festigkeitsberechnung", "Verbindungstechnik"],
    "verwandte_tools": ["schrauben_datenbank", "schrauben_suche_vorspannkraft", "durchgangsloecher_metrische_schrauben"],
    "expertise_level": "Fachexperte/Ingenieur",
    "aktualisiert": "2024-01-15"
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

def solve_context_information() -> Dict:
    """
    📖 CONTEXT INFORMATION SOLUTION
    
    Liefert strukturierte Schrauben-Wissens- und Dokumentationsinhalte.
    
    Keine Berechnungen oder Tabellen-Lookups - reine Informationsvermittlung.
    """
    return {
        "📖 CONTEXT INFORMATION SOLUTION": f"Wissens-Dokumentation zu {STRUCTURED_INFO['wissensbereich']}",
        "dokumentation": MAIN_INFORMATION_TEXT,
        "system_status": "Vollständig verfügbar",
        "datenbank_umfang": "1.081 ISO-Gewinde",
        "funktionen_verfügbar": len(STRUCTURED_INFO["verwandte_tools"]),
        "wissensbereich": STRUCTURED_INFO["wissensbereich"],
        "normen_referenzen": STRUCTURED_INFO["normen_referenzen"],
        "anwendungsbereiche": STRUCTURED_INFO["anwendungsbereiche"],
        "verwandte_tools": STRUCTURED_INFO["verwandte_tools"],
        "expertise_level": STRUCTURED_INFO["expertise_level"],
        "aktualisiert": STRUCTURED_INFO["aktualisiert"],
        "source": KNOWLEDGE_FOUNDATION,
        "note": "Vollständige Schrauben-Engineering-Dokumentation",
        "hinweis": "Verwenden Sie schrauben_datenbank() für konkrete Berechnungen"
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
        # Context-Tools haben meist keine Parameter
        "parameters": {},
        
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
        "parameter_count": PARAMETER_COUNT,
        "tool_description": TOOL_DESCRIPTION
    }

def calculate(**kwargs) -> Dict:
    """
    Legacy-Funktion für Kompatibilität.
    
    Context-Tools benötigen keine Parameter.
    """
    return solve_context_information()

# Legacy-Funktion für Rückwärtskompatibilität
def schrauben_info() -> Dict:
    """Legacy-Funktion - für Rückwärtskompatibilität"""
    return solve_context_information()