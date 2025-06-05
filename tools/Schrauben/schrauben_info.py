#!/usr/bin/env python3
"""
Schrauben-Informationssystem - Übersicht und Einstiegspunkt

Bietet umfassende Informationen über verfügbare Schraubenfunktionen,
DIN 13-Gewinde, VDI 2230-Berechnungen und Best Practices.
"""

from typing import Dict

def schrauben_info() -> Dict:
    """
    Gibt umfassende Informationen über das Schraubensystem aus.
    
    Returns:
        Dict: Formatierte Markdown-Dokumentation des Schraubensystems
    """
    
    info_text = """# 🔧 Schrauben-Engineering-System - Vollständige Übersicht

## 📋 **VERFÜGBARE FUNKTIONEN**

### 🔍 **1. schrauben_info()**
- **Zweck**: Diese Funktion - zeigt Systemübersicht und Hilfe
- **Verwendung**: `schrauben_info()`

### 📊 **2. schrauben_datenbank()**
- **Zweck**: Flexible Hauptabfrage für Gewindedaten und Vorspannkräfte
- **Verwendung**: Einzelgewinde oder Bereichsabfragen
- **Parameter**: gewinde, gewinde_bereich, schraubentyp, festigkeitsklasse, reibbeiwert, min_vorspannkraft, ausgabe_detail, berechnung_zeigen

### 🔎 **3. schrauben_suche_vorspannkraft()**
- **Zweck**: Spezialisierte Suche nach Schrauben mit Mindest-Vorspannkraft
- **Verwendung**: Optimierung und Schraubenauswahl
- **Parameter**: min_vorspannkraft, schraubentyp, festigkeitsklasse, reibbeiwert, reihe_filter

---

## 🎯 **WICHTIGE GRUNDPRINZIPIEN**

### **📏 Gewindebezeichnungen:**
- **M24** → M24.0 Regelgewinde (Standardsteigung)
- **M24x2** → M24.0x2.0 Feingewinde (spezielle Steigung)
- **Ohne Steigungsangabe = Regelgewinde**

### **🔩 Schraubentypen:**
- **Standard**: Schaftschrauben (wenn nicht spezifiziert)
- **Optional**: Dehnschrauben (ca. 25-30% geringere Vorspannkraft)

### **⚙️ Reihen-System nach DIN 13-6:**
- **Reihe 1**: BEVORZUGT - Standardgeometrie (erste Wahl)
- **Reihe 2**: Nur in Ausnahmefällen verwenden
- **Reihe 3**: Nur in besonderen Ausnahmefällen verwenden
- **System warnt bei Reihe 2/3 automatisch**

---

## 📚 **NORMGRUNDLAGEN**

### **🔧 DIN 13 - ISO-Metrische Gewinde:**
- **DIN 13-1**: Regelgewinde M1-M68
- **DIN 13-2 bis DIN 13-11**: Feingewinde-Serien
- **DIN 13-6**: Reihen-Klassifizierung
- **1.081 Gewinde**: Vollständige Engineering-Datenbank

### **📐 VDI 2230 - Schraubenverbindungen:**
- **Montagezugspannung**: σ_m = 0.9 × Rp / √[1 + 3 × (Torsionsfaktor)²]
- **Vorspannkraft**: F_sp = σ_m × As (Schaftschrauben) / A_dehn (Dehnschrauben)
- **Festigkeitsklassen**: 8.8, 10.9, 12.9 mit optimierten Rp-Werten
- **Reibungskoeffizienten**: μ = 0.08-0.16 (geschmiert bis trocken)

---

## 🛠️ **PRAKTISCHE ANWENDUNGSBEISPIELE**

### **📊 Vollständige Gewindeanalyse:**
```
schrauben_datenbank(
    gewinde="M24",
    ausgabe_detail="vollständig",
    berechnung_zeigen=True
)
```

### **🔍 Bereichssuche:**
```
schrauben_datenbank(
    gewinde_bereich={"von": "M12", "bis": "M24"},
    festigkeitsklasse="10.9",
    reibbeiwert="0.12"
)
```

### **⚡ Vorspannkraft-Optimierung:**
```
schrauben_suche_vorspannkraft(
    min_vorspannkraft="100 kN",
    festigkeitsklasse="8.8",
    reibbeiwert="0.12"
)
```

### **🔩 Dehnschrauben-Vergleich:**
```
schrauben_datenbank(
    gewinde="M20",
    schraubentyp="beide",
    festigkeitsklasse="10.9"
)
```

---

## ⚙️ **TECHNISCHE PARAMETER**

### **💪 Festigkeitsklassen:**
- **8.8**: Standard-Festigkeit
  - **≤ M16**: Rp = 640 N/mm² (174 Gewinde)
  - **> M16**: Rp = 660 N/mm² (907 Gewinde)
- **10.9**: Hohe Festigkeit, Rp = 940 N/mm²
- **12.9**: Sehr hohe Festigkeit, Rp = 1100 N/mm²

### **🔄 Reibungskoeffizienten:**
- **μ = 0.08**: Beste Schmierung (MoS₂, Graphit)
- **μ = 0.10**: Gute Schmierung (Öl, Fett)
- **μ = 0.12**: Standard-Schmierung (trocken)
- **μ = 0.14**: Schlechte Schmierung (verschmutzt)
- **μ = 0.16**: Keine Schmierung (Rost, hohe Reibung)

### **📏 Geometrische Berechnungen:**
- **Flankendurchmesser**: d2 = D - 0.649519 × P
- **Kerndurchmesser**: d3 = D - 1.22687 × P
- **Spannungsquerschnitt**: As = π × (d2 + d3)² / 16

---

## 🎯 **ANWENDUNGSEMPFEHLUNGEN**

### **✅ Wann Regelgewinde verwenden:**
- Standard-Schraubverbindungen
- Häufiges Montieren/Demontieren
- Raue Umgebungen
- Kostengünstige Lösung

### **⚡ Wann Feingewinde verwenden:**
- Präzise Einstellungen erforderlich
- Hohe Vibrationsbelastung
- Maximale Vorspannkraft auf kleinem Raum
- Dünnwandige Bauteile

### **🔧 Wann Dehnschrauben verwenden:**
- Präzise Kraftkontrolle erforderlich
- Sicherheitskritische Anwendungen
- Gleichmäßige Spannungsverteilung
- Qualitätskontrolle durch Längenmessung

---

## 💡 **EXPERTENTIPPS**

### **🎯 Optimale Schraubenauswahl:**
1. **Immer Reihe 1 bevorzugen** (außer spezielle Gründe)
2. **Regelgewinde als Standard** (außer Feineinstellung nötig)
3. **Schaftschrauben standard** (außer Kraftkontrolle wichtig)
4. **FK 10.9 für hochbelastete Verbindungen**
5. **μ = 0.12 als konservative Annahme**

### **⚠️ Häufige Fehler vermeiden:**
- Nicht automatisch höchste Festigkeitsklasse wählen
- Reibungskoeffizient nicht unterschätzen
- Bei Feingewinde erhöhte Montagesorgfalt
- Reihe 2/3 nur bei klarem Bedarf

### **🔍 Systemfeatures nutzen:**
- **Intelligente Einheitenkonvertierung**: Automatisch optimierte Ausgabe
- **Reihen-Warnsystem**: Hinweise bei Abweichung von Reihe 1
- **Umfassende Validierung**: Fehlerprüfung und Hinweise
- **Vollständige Dokumentation**: Formeln und Berechnungswege

---

## 📞 **SCHNELLSTART-GUIDE**

### **1. Einfache Gewindeabfrage:**
```
schrauben_datenbank(gewinde="M16")
```

### **2. Detaillierte Analyse:**
```
schrauben_datenbank(
    gewinde="M20", 
    ausgabe_detail="vollständig",
    berechnung_zeigen=True
)
```

### **3. Optimierung finden:**
```
schrauben_suche_vorspannkraft(
    min_vorspannkraft="50 kN",
    festigkeitsklasse="10.9"
)
```

---

**💎 Dieses System basiert auf der vollständigsten verfügbaren ISO-Metrischen Gewinde-Datenbank mit 1.081 Gewindeeinträgen und professionellen VDI 2230-Berechnungen.**

**🚀 Starten Sie mit `schrauben_datenbank(gewinde="M10")` für Ihren ersten Test!**"""

    return {
        "dokumentation": info_text,
        "system_status": "Vollständig verfügbar",
        "datenbank_umfang": "1.081 ISO-Gewinde",
        "funktionen_verfügbar": 3,
        "normgrundlagen": ["DIN 13-1 bis DIN 13-11", "DIN 13-6", "VDI 2230"],
        "berechnungsarten": ["Vorspannkraft", "Montagezugspannung", "Gewindegeometrie"],
        "hinweis": "Verwenden Sie schrauben_datenbank() für konkrete Berechnungen"
    }

# Tool-Metadaten für Registry
TOOL_METADATA = {
    "name": "schrauben_info",
    "short_description": "Schrauben-Infosystem - Vollständige Übersicht über Schraubenfunktionen und Normen",
    "description": """Bietet umfassende Informationen über das Schrauben-Engineering-System.

Diese Funktion ist der ideale Einstiegspunkt und erklärt:
- Verfügbare Schraubenfunktionen (schrauben_datenbank, schrauben_suche_vorspannkraft)
- DIN 13-Gewinde-System mit Reihen-Klassifizierung
- VDI 2230-Berechnungsgrundlagen
- Best Practices für Schraubenauswahl
- Praktische Anwendungsbeispiele
- Technische Parameter (Festigkeitsklassen, Reibungskoeffizienten)

Keine Parameter erforderlich - zeigt vollständige Systemdokumentation.

Datengrundlage: 1.081 ISO-metrische Gewinde (M1-M1000) mit vollständiger Geometrie und VDI 2230-Berechnungen.

Normen: DIN 13-1 bis DIN 13-11, DIN 13-6, VDI 2230, ISO 262""",
    "tags": ["DIN 13", "VDI 2230", "info"],
    "function": schrauben_info,
    "examples": [
        {
            "description": "Zeige vollständige Systemdokumentation",
            "call": 'schrauben_info()',
            "result": "Umfassende Markdown-Dokumentation des Schrauben-Systems"
        }
    ]
}

if __name__ == "__main__":
    # Test der Info-Funktion
    result = schrauben_info()
    print("=== Schrauben-Info Test ===")
    print(result["dokumentation"]) 