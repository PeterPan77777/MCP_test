#!/usr/bin/env python3
"""
Schrauben-Suche nach Vorspannkraft - Spezialisierte Optimierungsfunktion

Ermöglicht gezielte Suche nach Schrauben mit spezifischen Vorspannkraft-Anforderungen
für optimale Schraubenauswahl in der Konstruktion.
"""

# 🎯 TOOL-KONFIGURATION
FUNCTION_PARAM_MIN_VORSPANNKRAFT_NAME = "min_vorspannkraft"
FUNCTION_PARAM_MIN_VORSPANNKRAFT_DESC = "Mindest-Vorspannkraft mit Einheit (z.B. '100 kN', '50000 N') - ERFORDERLICH"
FUNCTION_PARAM_MIN_VORSPANNKRAFT_EXAMPLE = "100 kN"

FUNCTION_PARAM_SCHRAUBENTYP_NAME = "schraubentyp"
FUNCTION_PARAM_SCHRAUBENTYP_DESC = "Schraubentyp: 'Schaftschrauben', 'Dehnschrauben' oder 'beide'"
FUNCTION_PARAM_SCHRAUBENTYP_EXAMPLE = "Schaftschrauben"

FUNCTION_PARAM_FESTIGKEITSKLASSE_NAME = "festigkeitsklasse"
FUNCTION_PARAM_FESTIGKEITSKLASSE_DESC = "Festigkeitsklasse: '8.8', '10.9', '12.9' oder 'alle'"
FUNCTION_PARAM_FESTIGKEITSKLASSE_EXAMPLE = "10.9"

FUNCTION_PARAM_REIBBEIWERT_NAME = "reibbeiwert"
FUNCTION_PARAM_REIBBEIWERT_DESC = "Reibungskoeffizient: '0.08', '0.10', '0.12', '0.14', '0.16' oder 'alle'"
FUNCTION_PARAM_REIBBEIWERT_EXAMPLE = "0.10"

FUNCTION_PARAM_REIHE_FILTER_NAME = "reihe_filter"
FUNCTION_PARAM_REIHE_FILTER_DESC = "Reihen-Filter: ['Reihe 1'] für nur Standardreihe oder None für alle Reihen"
FUNCTION_PARAM_REIHE_FILTER_EXAMPLE = "['Reihe 1']"

# 🔧 IMPORTS
from typing import Dict, Optional, List
import pandas as pd
import numpy as np
import sys
import os
import re

# Import der gemeinsamen Funktionen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 🎯 TOOL FUNCTIONS

def parse_kraft_einheit(kraft_str: str) -> float:
    """
    Parst Kraft-String und konvertiert zu Newton.
    
    Args:
        kraft_str: Kraft mit Einheit, z.B. "100 kN", "50000 N"
    
    Returns:
        Kraft in Newton
    """
    kraft_str = kraft_str.strip()
    
    # Pattern für Zahl + Einheit
    pattern = r'(\d+(?:\.\d+)?)\s*(kN|N|MN)'
    match = re.match(pattern, kraft_str, re.IGNORECASE)
    
    if not match:
        raise ValueError(f"Ungültiges Kraftformat: {kraft_str}. Verwenden Sie z.B. '{FUNCTION_PARAM_MIN_VORSPANNKRAFT_EXAMPLE}' oder '50000 N'")
    
    wert = float(match.group(1))
    einheit = match.group(2).upper()
    
    # Konvertierung zu Newton
    if einheit == 'N':
        return wert
    elif einheit == 'KN':
        return wert * 1000
    elif einheit == 'MN':
        return wert * 1000000
    
    raise ValueError(f"Unbekannte Krafteinheit: {einheit}")

def load_schrauben_datenbank() -> pd.DataFrame:
    """Lädt die Schrauben-CSV-Datenbank."""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'Tabellen', 'ISO_Metrische_Gewinde_Komplett.csv')
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        raise Exception(f"Fehler beim Laden der Schrauben-Datenbank: {str(e)}")

def filter_nach_vorspannkraft(df: pd.DataFrame, min_kraft_n: float, schraubentyp: str, 
                             festigkeitsklasse: Optional[str], reibbeiwert: Optional[str],
                             reihe_filter: Optional[List[str]]) -> pd.DataFrame:
    """
    Filtert DataFrame nach Vorspannkraft-Kriterien.
    
    Args:
        df: Schrauben-DataFrame
        min_kraft_n: Mindest-Vorspannkraft in Newton
        schraubentyp: "Schaftschrauben", "Dehnschrauben", "beide"
        festigkeitsklasse: Gewünschte Festigkeitsklasse oder None für alle
        reibbeiwert: Gewünschter Reibbeiwert oder None für alle
        reihe_filter: Liste von Reihen oder None für alle
    
    Returns:
        Gefilterter DataFrame mit zusätzlichen Spalten für Analyse
    """
    filtered_df = df.copy()
    
    # Reihen-Filter
    if reihe_filter:
        filtered_df = filtered_df[filtered_df['Reihe'].isin(reihe_filter)]
    
    # Bestimme relevante Vorspannkraft-Spalten
    if schraubentyp == "Schaftschrauben":
        vorspann_prefix = "Vorspannkraft Schaftschrauben F_sp, "
    elif schraubentyp == "Dehnschrauben":
        vorspann_prefix = "Vorspannkraft Dehnschrauben F_sp, "
    else:  # beide
        vorspann_prefix = "Vorspannkraft"  # Beide Typen einschließen
    
    # Finde relevante Spalten
    relevante_spalten = [col for col in df.columns if vorspann_prefix in col]
    
    # Weitere Filter anwenden
    if festigkeitsklasse and festigkeitsklasse != "alle":
        relevante_spalten = [col for col in relevante_spalten if f"- {festigkeitsklasse}" in col]
    
    if reibbeiwert and reibbeiwert != "alle":
        mu_pattern = reibbeiwert.replace("0.", "")  # "0.08" -> "8"
        relevante_spalten = [col for col in relevante_spalten if f"µ{mu_pattern} = {reibbeiwert}" in col]
    
    if not relevante_spalten:
        return pd.DataFrame()  # Keine passenden Spalten gefunden
    
    # Prüfe für jede Zeile, ob mindestens eine Spalte die Mindest-Vorspannkraft erreicht
    mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
    
    for spalte in relevante_spalten:
        mask = mask | (filtered_df[spalte] >= min_kraft_n)
    
    result_df = filtered_df[mask].copy()
    
    # Füge Analyse-Spalten hinzu
    if len(result_df) > 0:
        # Finde maximale Vorspannkraft pro Zeile
        max_vorspann = result_df[relevante_spalten].max(axis=1)
        result_df['max_vorspannkraft_n'] = max_vorspann
        result_df['max_vorspannkraft_kn'] = max_vorspann / 1000
        
        # Finde die Spalte mit maximaler Vorspannkraft
        max_spalten = result_df[relevante_spalten].idxmax(axis=1)
        result_df['optimale_konfiguration'] = max_spalten
    
    return result_df

def extrahiere_konfiguration_info(spaltenname: str) -> Dict:
    """
    Extrahiert Konfigurationsinformationen aus Spaltenname.
    
    Args:
        spaltenname: Name der Vorspannkraft-Spalte
    
    Returns:
        Dict mit Konfigurationsinformationen
    """
    # Pattern für Spaltenname-Parsing
    # Beispiel: "Vorspannkraft Schaftschrauben F_sp, µ1 = 0.08 - 10.9 (940 N/mm²)"
    
    schraubentyp = "Schaftschrauben" if "Schaftschrauben" in spaltenname else "Dehnschrauben"
    
    # Extrahiere μ-Wert
    mu_match = re.search(r'µ\d+ = (0\.\d+)', spaltenname)
    mu_wert = mu_match.group(1) if mu_match else "unbekannt"
    
    # Extrahiere Festigkeitsklasse
    fk_match = re.search(r'- (\d+\.\d+)', spaltenname)
    festigkeitsklasse = fk_match.group(1) if fk_match else "unbekannt"
    
    # Extrahiere Rp-Wert
    rp_match = re.search(r'\((\d+)\s*N/mm²\)', spaltenname)
    rp_wert = rp_match.group(1) if rp_match else "unbekannt"
    
    return {
        "schraubentyp": schraubentyp,
        "reibbeiwert": mu_wert,
        "festigkeitsklasse": festigkeitsklasse,
        "rp_wert": rp_wert,
        "schmierung": get_schmierung_beschreibung(mu_wert)
    }

def get_schmierung_beschreibung(mu_wert: str) -> str:
    """Gibt Beschreibung der Schmierung basierend auf μ-Wert zurück."""
    schmierung_map = {
        "0.08": "Beste Schmierung (MoS₂, Graphit)",
        "0.10": "Gute Schmierung (Öl, Fett)",
        "0.12": "Standard-Schmierung (trocken)",
        "0.14": "Schlechte Schmierung (verschmutzt)", 
        "0.16": "Keine Schmierung (Rost, hohe Reibung)"
    }
    return schmierung_map.get(mu_wert, "Unbekannte Schmierung")

def format_suchergebnis(df: pd.DataFrame, min_kraft_kn: float, suchparameter: Dict) -> str:
    """
    Formatiert Suchergebnis als Markdown.
    
    Args:
        df: Gefilterter DataFrame mit Suchergebnissen
        min_kraft_kn: Mindest-Vorspannkraft in kN
        suchparameter: Dict mit Suchparametern
    
    Returns:
        Formatierte Markdown-Ausgabe
    """
    anzahl = len(df)
    
    if anzahl == 0:
        return f"""# 🔍 Schrauben-Suche: Keine Ergebnisse

**Suchkriterien:**
- Mindest-Vorspannkraft: {min_kraft_kn:.1f} kN
- Schraubentyp: {suchparameter.get(FUNCTION_PARAM_SCHRAUBENTYP_NAME, 'alle')}
- Festigkeitsklasse: {suchparameter.get(FUNCTION_PARAM_FESTIGKEITSKLASSE_NAME, 'alle')}
- Reibbeiwert: {suchparameter.get(FUNCTION_PARAM_REIBBEIWERT_NAME, 'alle')}

❌ **Keine Gewinde gefunden**, die alle Kriterien erfüllen.

**Empfehlungen:**
- Mindest-Vorspannkraft reduzieren
- Höhere Festigkeitsklasse wählen
- Bessere Schmierung (niedrigerer μ-Wert) erwägen
- Größere Gewindedurchmesser in Betracht ziehen"""

    # Sortiere nach max. Vorspannkraft (absteigend)
    df_sorted = df.sort_values('max_vorspannkraft_kn', ascending=False)
    
    ausgabe = f"""# 🔍 Schrauben-Suche: {anzahl} Treffer gefunden

**Suchkriterien:**
- Mindest-Vorspannkraft: {min_kraft_kn:.1f} kN
- Schraubentyp: {suchparameter.get(FUNCTION_PARAM_SCHRAUBENTYP_NAME, 'alle')}
- Festigkeitsklasse: {suchparameter.get(FUNCTION_PARAM_FESTIGKEITSKLASSE_NAME, 'alle')}
- Reibbeiwert: {suchparameter.get(FUNCTION_PARAM_REIBBEIWERT_NAME, 'alle')}

## 📊 OPTIMALE LÖSUNGEN (sortiert nach max. Vorspannkraft)

| Gewinde | Reihe | Max. F_sp [kN] | Optimale Konfiguration | Schraubentyp | FK | μ | Schmierung |
|---------|-------|----------------|------------------------|--------------|----|----|------------|"""
    
    for _, row in df_sorted.iterrows():
        config_info = extrahiere_konfiguration_info(row['optimale_konfiguration'])
        
        # Reihe-Indikator
        reihe_symbol = "✅" if row['Reihe'] == 'Reihe 1' else "⚠️"
        
        ausgabe += f"\n| {row['Gewinde']} | {reihe_symbol} {row['Reihe']} | {row['max_vorspannkraft_kn']:.1f} | {config_info['festigkeitsklasse']}, μ={config_info['reibbeiwert']} | {config_info['schraubentyp']} | {config_info['festigkeitsklasse']} | {config_info['reibbeiwert']} | {config_info['schmierung']} |"
    
    # Statistiken
    reihe1_count = len(df_sorted[df_sorted['Reihe'] == 'Reihe 1'])
    andere_reihen = anzahl - reihe1_count
    max_vorspann = df_sorted['max_vorspannkraft_kn'].max()
    min_vorspann = df_sorted['max_vorspannkraft_kn'].min()
    
    ausgabe += f"""

## 📈 ANALYSE

### **Statistische Auswertung:**
- **Treffer gesamt**: {anzahl} Gewinde
- **Reihe 1 (empfohlen)**: {reihe1_count} Gewinde (✅)
- **Andere Reihen**: {andere_reihen} Gewinde (⚠️)
- **Vorspannkraft-Bereich**: {min_vorspann:.1f} - {max_vorspann:.1f} kN

### **Top-Empfehlungen:**"""
    
    # Top 3 Empfehlungen
    top_3 = df_sorted.head(3)
    for i, (_, row) in enumerate(top_3.iterrows(), 1):
        config_info = extrahiere_konfiguration_info(row['optimale_konfiguration'])
        status = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        reihe_hinweis = "" if row['Reihe'] == 'Reihe 1' else f" (⚠️ {row['Reihe']})"
        
        ausgabe += f"""
{status} **{row['Gewinde']}**: {row['max_vorspannkraft_kn']:.1f} kN
   - Konfiguration: {config_info['schraubentyp']}, FK {config_info['festigkeitsklasse']}, μ = {config_info['reibbeiwert']}
   - Schmierung: {config_info['schmierung']}
   - Klassifikation: {row['Reihe']}{reihe_hinweis}"""
    
    # Hinweise
    if andere_reihen > 0:
        ausgabe += f"""

### ⚠️ **WICHTIGE HINWEISE:**
- {andere_reihen} Gewinde gehören nicht zu Reihe 1
- **Empfehlung**: Prüfen Sie zuerst Reihe 1-Lösungen
- Bei gleicher Leistung immer Reihe 1 bevorzugen"""
    
    if reihe1_count > 0:
        beste_reihe1 = df_sorted[df_sorted['Reihe'] == 'Reihe 1'].iloc[0]
        ausgabe += f"""

### ✅ **BESTE REIHE 1-LÖSUNG:**
**{beste_reihe1['Gewinde']}** mit {beste_reihe1['max_vorspannkraft_kn']:.1f} kN Vorspannkraft"""
    
    return ausgabe

def schrauben_suche_vorspannkraft(
    min_vorspannkraft: str,
    schraubentyp: str = "Schaftschrauben",
    festigkeitsklasse: str = "alle",
    reibbeiwert: str = "alle",
    reihe_filter: Optional[List[str]] = None
) -> Dict:
    """
    📊 SEARCH AND ANALYSIS SOLUTION
    
    Spezialisierte Suche nach Schrauben mit Mindest-Vorspannkraft.
    
    Args:
        min_vorspannkraft: Kraft mit Einheit z.B. "100 kN", "50000 N"
        schraubentyp: "Schaftschrauben", "Dehnschrauben", "beide"
        festigkeitsklasse: "8.8", "10.9", "12.9", "alle"
        reibbeiwert: "0.08", "0.10", "0.12", "0.14", "0.16", "alle"
        reihe_filter: Liste von Reihen z.B. ["Reihe 1", "Reihe 2"] oder None
    
    Returns:
        Dict: Formatierte Suchergebnisse mit Optimierungsempfehlungen
    """
    
    try:
        # Parse Parameter
        min_kraft_n = parse_kraft_einheit(min_vorspannkraft)
        min_kraft_kn = min_kraft_n / 1000
        
        # Validiere Parameter
        if schraubentyp not in ["Schaftschrauben", "Dehnschrauben", "beide"]:
            return {
                "error": "Ungültiger Schraubentyp",
                "gültig": ["Schaftschrauben", "Dehnschrauben", "beide"]
            }
        
        if festigkeitsklasse not in ["8.8", "10.9", "12.9", "alle"]:
            return {
                "error": "Ungültige Festigkeitsklasse",
                "gültig": ["8.8", "10.9", "12.9", "alle"]
            }
        
        if reibbeiwert not in ["0.08", "0.10", "0.12", "0.14", "0.16", "alle"]:
            return {
                "error": "Ungültiger Reibbeiwert",
                "gültig": ["0.08", "0.10", "0.12", "0.14", "0.16", "alle"]
            }
        
        # Lade Datenbank
        df = load_schrauben_datenbank()
        
        # Filtere nach Kriterien
        filtered_df = filter_nach_vorspannkraft(
            df, min_kraft_n, schraubentyp, 
            festigkeitsklasse if festigkeitsklasse != "alle" else None,
            reibbeiwert if reibbeiwert != "alle" else None,
            reihe_filter
        )
        
        # Sammle Suchparameter für Ausgabe
        suchparameter = {
            FUNCTION_PARAM_SCHRAUBENTYP_NAME: schraubentyp,
            FUNCTION_PARAM_FESTIGKEITSKLASSE_NAME: festigkeitsklasse,
            FUNCTION_PARAM_REIBBEIWERT_NAME: reibbeiwert,
            FUNCTION_PARAM_REIHE_FILTER_NAME: reihe_filter
        }
        
        # Formatiere Ergebnis
        suchergebnis = format_suchergebnis(filtered_df, min_kraft_kn, suchparameter)
        
        return {
            "suchergebnis": suchergebnis,
            "anzahl_treffer": len(filtered_df),
            "min_vorspannkraft_kn": min_kraft_kn,
            "suchparameter": suchparameter,
            "hat_reihe1_treffer": len(filtered_df[filtered_df['Reihe'] == 'Reihe 1']) > 0 if len(filtered_df) > 0 else False
        }
        
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {
            "error": "Systemfehler",
            "message": str(e),
            "hinweis": "Überprüfen Sie die Parameter und versuchen Sie es erneut"
        }

def get_metadata():
    """
    Liefert Tool-Metadaten für Registry-Discovery.
    
    Returns:
        Dict: Tool-Metadaten im neuen System-Format
    """
    return {
        "tool_name": "schrauben_suche_vorspannkraft",
        "short_description": "Schrauben-Vorspannkraft-Suche - Optimale Schraubenauswahl nach Kraftanforderungen",
        "description": f"""Spezialisierte Suchfunktion für optimale Schraubenauswahl basierend auf Vorspannkraft-Anforderungen.

Findet alle Gewinde, die eine Mindest-Vorspannkraft erreichen und sortiert sie nach Leistung.
Berücksichtigt automatisch das Reihen-System (bevorzugt Reihe 1) und gibt Optimierungsempfehlungen.

Ausgabe-Features:
- Sortiert nach maximaler Vorspannkraft
- Top 3-Empfehlungen mit detaillierter Konfiguration
- Reihen-Analyse und Warnungen
- Optimierungshinweise bei leeren Ergebnissen
- Schmierungs-Empfehlungen basierend auf μ-Wert

Anwendung: Konstruktionsoptimierung, Schraubenauswahl, Festigkeitsanalyse

Normen: DIN 13-6 (Reihen), VDI 2230 (Vorspannkraft), ISO 262 (Geometrie)""",
        "tags": ["DIN 13", "VDI 2230"],

        "has_solving": "none",
        "parameters": {
            FUNCTION_PARAM_MIN_VORSPANNKRAFT_NAME: {
                "type": "string",
                "description": FUNCTION_PARAM_MIN_VORSPANNKRAFT_DESC,
                "required": True
            },
            FUNCTION_PARAM_SCHRAUBENTYP_NAME: {
                "type": "string",
                "description": FUNCTION_PARAM_SCHRAUBENTYP_DESC,
                "default": FUNCTION_PARAM_SCHRAUBENTYP_EXAMPLE
            },
            FUNCTION_PARAM_FESTIGKEITSKLASSE_NAME: {
                "type": "string",
                "description": FUNCTION_PARAM_FESTIGKEITSKLASSE_DESC,
                "default": "alle"
            },
            FUNCTION_PARAM_REIBBEIWERT_NAME: {
                "type": "string",
                "description": FUNCTION_PARAM_REIBBEIWERT_DESC,
                "default": "alle"
            },
            FUNCTION_PARAM_REIHE_FILTER_NAME: {
                "type": "array",
                "description": FUNCTION_PARAM_REIHE_FILTER_DESC,
                "required": False
            }
        },
        "examples": [
            {
                "description": "Finde Schrauben mit mindestens 200 kN Vorspannkraft",
                "parameters": {FUNCTION_PARAM_MIN_VORSPANNKRAFT_NAME: "200 kN"},
                "result": "Sortierte Liste aller geeigneten Gewinde mit Optimierungsempfehlungen"
            },
            {
                "description": "Hochfeste Schrauben mit spezifischer Schmierung",
                "parameters": {FUNCTION_PARAM_MIN_VORSPANNKRAFT_NAME: "150 kN", FUNCTION_PARAM_FESTIGKEITSKLASSE_NAME: "12.9", FUNCTION_PARAM_REIBBEIWERT_NAME: "0.08"},
                "result": "Optimierte Auswahl für beste Schmierung und höchste Festigkeit"
            },
            {
                "description": "Nur Reihe 1-Gewinde für Standard-Anwendungen",
                "parameters": {FUNCTION_PARAM_MIN_VORSPANNKRAFT_NAME: FUNCTION_PARAM_MIN_VORSPANNKRAFT_EXAMPLE, FUNCTION_PARAM_REIHE_FILTER_NAME: ["Reihe 1"]},
                "result": "Ausschließlich empfohlene Reihe 1-Gewinde"
            }
        ]
    }

def calculate(**kwargs) -> Dict:
    """
    Führt Vorspannkraft-Suche durch.
    
    Args:
        **kwargs: Alle Parameter für die Vorspannkraft-Suche
        
    Returns:
        Dict: Vorspannkraft-Suchergebnisse
    """
    return schrauben_suche_vorspannkraft(**kwargs)

# 🎯 METADATA
if __name__ == "__main__":
    # Test-Beispiele
    print("=== Schrauben-Vorspannkraft-Suche Template Tests ===")
    
    # Test 1: Einfache Suche
    result1 = schrauben_suche_vorspannkraft(min_vorspannkraft="100 kN")
    print("Test 1 - 100 kN Mindest-Vorspannkraft:")
    if 'suchergebnis' in result1:
        print(result1['suchergebnis'][:300] + "...")
        print(f"Treffer: {result1['anzahl_treffer']}")
    else:
        print(result1)
    
    print("\n" + "="*50)
    
    # Test 2: Spezifische Suche
    result2 = schrauben_suche_vorspannkraft(
        min_vorspannkraft="200 kN", 
        festigkeitsklasse="10.9",
        reibbeiwert="0.12"
    )
    print("Test 2 - 200 kN, FK 10.9, μ=0.12:")
    if 'suchergebnis' in result2:
        print(result2['suchergebnis'][:300] + "...")
        print(f"Treffer: {result2['anzahl_treffer']}")
    else:
        print(result2) 