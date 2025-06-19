#!/usr/bin/env python3
"""
Schrauben-Datenbank - Flexible Hauptabfrage für Gewindedaten

Ermöglicht umfassende Abfragen der ISO-metrischen Gewinde-Datenbank
mit Vorspannkräften, Geometrie und VDI 2230-Berechnungen.
"""

# 🎯 TOOL-KONFIGURATION
FUNCTION_PARAM_GEWINDE_NAME = "gewinde"
FUNCTION_PARAM_GEWINDE_DESC = "Gewindebezeichnung (z.B. 'M12', 'M16x1.5') oder leer für alle"
FUNCTION_PARAM_GEWINDE_EXAMPLE = "M24"

FUNCTION_PARAM_GEWINDE_BEREICH_NAME = "gewinde_bereich"
FUNCTION_PARAM_GEWINDE_BEREICH_DESC = "Bereichsabfrage mit {'von': 'M12', 'bis': 'M24'} oder leer für Einzelgewinde"
FUNCTION_PARAM_GEWINDE_BEREICH_EXAMPLE = "{'von': 'M16', 'bis': 'M30'}"

FUNCTION_PARAM_SCHRAUBENTYP_NAME = "schraubentyp"
FUNCTION_PARAM_SCHRAUBENTYP_DESC = "Schraubentyp: 'Schaftschrauben', 'Dehnschrauben' oder 'beide'"
FUNCTION_PARAM_SCHRAUBENTYP_EXAMPLE = "Schaftschrauben"

FUNCTION_PARAM_FESTIGKEITSKLASSE_NAME = "festigkeitsklasse"
FUNCTION_PARAM_FESTIGKEITSKLASSE_DESC = "Festigkeitsklasse (z.B. '8.8', '10.9', '12.9') oder leer für alle"
FUNCTION_PARAM_FESTIGKEITSKLASSE_EXAMPLE = "10.9"

FUNCTION_PARAM_REIBBEIWERT_NAME = "reibbeiwert"
FUNCTION_PARAM_REIBBEIWERT_DESC = "Reibungskoeffizient: '0.08', '0.10', '0.12', '0.14', '0.16' oder 'alle'"
FUNCTION_PARAM_REIBBEIWERT_EXAMPLE = "0.10"

FUNCTION_PARAM_MIN_VORSPANNKRAFT_NAME = "min_vorspannkraft"
FUNCTION_PARAM_MIN_VORSPANNKRAFT_DESC = "Mindest-Vorspannkraft mit Einheit (z.B. '100 kN', '50000 N') oder leer"
FUNCTION_PARAM_MIN_VORSPANNKRAFT_EXAMPLE = "200 kN"

FUNCTION_PARAM_AUSGABE_DETAIL_NAME = "ausgabe_detail"
FUNCTION_PARAM_AUSGABE_DETAIL_DESC = "Detail-Level: 'minimal', 'standard', 'vollständig'"
FUNCTION_PARAM_AUSGABE_DETAIL_EXAMPLE = "standard"

FUNCTION_PARAM_BERECHNUNG_ZEIGEN_NAME = "berechnung_zeigen"
FUNCTION_PARAM_BERECHNUNG_ZEIGEN_DESC = "Zeigt vollständige Berechnungsdokumentation"
FUNCTION_PARAM_BERECHNUNG_ZEIGEN_EXAMPLE = "false"

# 🔧 IMPORTS
from typing import Dict, Optional, List, Union
import sys
import os
import re

# 🔧 LAZY IMPORTS: Pandas nur bei Bedarf laden (verhindert Circular Import)
pd = None
np = None

def _ensure_pandas():
    """Lädt Pandas nur bei Bedarf - verhindert Circular Import während Tool Discovery"""
    global pd, np
    if pd is None:
        import pandas as pd_module
        import numpy as np_module
        pd = pd_module
        np = np_module

# Import des CSV-Zugriffs
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 🎯 TOOL FUNCTIONS

def parse_gewinde_bezeichnung(gewinde: str) -> Dict:
    """
    Parst Gewindebezeichnung und gibt strukturierte Informationen zurück.
    
    Args:
        gewinde: Gewindebezeichnung wie "M24", "M10x1.0", "M20x1.5"
    
    Returns:
        Dict mit parsed Informationen
    """
    # Entferne Leerzeichen
    gewinde = gewinde.strip().upper()
    
    # Pattern für M + Durchmesser + optional x + Steigung
    pattern = r'^M(\d+(?:\.\d+)?)(?:x(\d+(?:\.\d+)?))?$'
    match = re.match(pattern, gewinde)
    
    if not match:
        return {
            "error": f"Ungültige Gewindebezeichnung: {gewinde}",
            "hinweis": f"Format: '{FUNCTION_PARAM_GEWINDE_EXAMPLE}' (Regelgewinde) oder 'M24x2.0' (Feingewinde)"
        }
    
    durchmesser = float(match.group(1))
    steigung = float(match.group(2)) if match.group(2) else None
    
    # Bestimme Gewindetyp
    if steigung is None:
        gewindetyp = "Regelgewinde"
        gewinde_standard = f"M{durchmesser}"
    else:
        gewindetyp = "Feingewinde"
        gewinde_standard = f"M{durchmesser}x{steigung}"
    
    return {
        "durchmesser": durchmesser,
        "steigung": steigung,
        "gewindetyp": gewindetyp,
        "gewinde_standard": gewinde_standard,
        "gewinde_csv": f"M{durchmesser}" if steigung is None else f"M{durchmesser}x{steigung}"
    }

def parse_gewinde_bereich(bereich: Dict) -> Dict:
    """
    Parst Gewindebereich und validiert ihn.
    
    Args:
        bereich: Dict mit 'von' und 'bis' Schlüsseln
    
    Returns:
        Dict mit parsed Bereich
    """
    if 'von' not in bereich or 'bis' not in bereich:
        return {"error": "Bereich muss 'von' und 'bis' Schlüssel enthalten"}
    
    von_info = parse_gewinde_bezeichnung(bereich['von'])
    bis_info = parse_gewinde_bezeichnung(bereich['bis'])
    
    if 'error' in von_info:
        return {"error": f"Fehler in 'von': {von_info['error']}"}
    if 'error' in bis_info:
        return {"error": f"Fehler in 'bis': {bis_info['error']}"}
    
    if von_info['durchmesser'] >= bis_info['durchmesser']:
        return {"error": "'von' muss kleiner als 'bis' sein"}
    
    return {
        "von_durchmesser": von_info['durchmesser'],
        "bis_durchmesser": bis_info['durchmesser'],
        "von_gewinde": von_info['gewinde_csv'],
        "bis_gewinde": bis_info['gewinde_csv']
    }

def load_schrauben_datenbank():
    """Lädt die Schrauben-CSV-Datenbank."""
    _ensure_pandas()  # Pandas erst hier laden
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'Tabellen', 'ISO_Metrische_Gewinde_Komplett.csv')
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        raise Exception(f"Fehler beim Laden der Schrauben-Datenbank: {str(e)}")

def filter_dataframe(df, **kwargs):
    """
    Filtert DataFrame basierend auf Parametern.
    
    Args:
        df: Schrauben-DataFrame
        **kwargs: Filter-Parameter
    
    Returns:
        Gefilterter DataFrame
    """
    filtered_df = df.copy()
    
    # Gewinde-Filter
    if 'gewinde_csv' in kwargs:
        filtered_df = filtered_df[filtered_df['Gewinde'] == kwargs['gewinde_csv']]
    
    # Bereichs-Filter
    if 'von_durchmesser' in kwargs and 'bis_durchmesser' in kwargs:
        filtered_df = filtered_df[
            (filtered_df['Nenndurchmesser D'] >= kwargs['von_durchmesser']) &
            (filtered_df['Nenndurchmesser D'] <= kwargs['bis_durchmesser'])
        ]
    
    # Mindest-Vorspannkraft Filter
    if 'min_vorspannkraft_n' in kwargs:
        vorspann_cols = [col for col in df.columns if 'Vorspannkraft' in col]
        # Prüfe ob mindestens eine Vorspannkraft-Spalte den Mindestswert erreicht
        mask = False
        for col in vorspann_cols:
            mask = mask | (filtered_df[col] >= kwargs['min_vorspannkraft_n'])
        filtered_df = filtered_df[mask]
    
    return filtered_df

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

def format_geometrie_tabelle(row) -> str:
    """Formatiert Geometrie-Daten als Markdown-Tabelle."""
    
    geometrie_data = [
        ("Gewinde", row['Gewinde'], "-", "-"),
        ("Reihe", row['Reihe'], "-", "DIN 13-6"),
        ("Gewindetyp", row['Gewindetyp'], "-", "-"),
        ("Nenndurchmesser D", f"{row['Nenndurchmesser D']:.1f}", "mm", "-"),
        ("Steigung P", f"{row['Steigung P']:.2f}", "mm", "ISO 262"),
        ("Flankendurchmesser d2", f"{row['Flankendurchmesser d2 = D2']:.3f}", "mm", "d2 = D - 0.649519×P"),
        ("Kerndurchmesser d3", f"{row['Kerndurchmesser d3']:.3f}", "mm", "d3 = D - 1.22687×P"),
        ("Spannungsquerschnitt As", f"{row['Spannungsquerschnitt As']:.3f}", "mm²", "As = π×(d2+d3)²/16")
    ]
    
    tabelle = "| Parameter | Wert | Einheit | Formel/Norm |\n"
    tabelle += "|-----------|------|---------|-------------|\n"
    
    for param, wert, einheit, formel in geometrie_data:
        tabelle += f"| {param} | {wert} | {einheit} | {formel} |\n"
    
    return tabelle

def format_vorspannkraft_tabelle(row, schraubentyp: str) -> str:
    """Formatiert Vorspannkraft-Daten als Markdown-Tabelle."""
    
    # Bestimme Spalten basierend auf Schraubentyp
    if schraubentyp == "Schaftschrauben":
        cols_prefix = "Vorspannkraft Schaftschrauben F_sp, "
    elif schraubentyp == "Dehnschrauben":
        cols_prefix = "Vorspannkraft Dehnschrauben F_sp, "
    else:  # beide
        # Wir zeigen beide in einer Tabelle
        return format_beide_schraubentypen_tabelle(row)
    
    # Finde relevante Spalten
    relevante_cols = [col for col in row.index if cols_prefix in col]
    
    # Gruppiere nach μ-Wert und Festigkeitsklasse
    mu_werte = ['µ1 = 0.08', 'µ2 = 0.10', 'µ3 = 0.12', 'µ4 = 0.14', 'µ5 = 0.16']
    fk_werte = ['8.8', '10.9', '12.9']
    
    tabelle = "| μ-Wert | FK 8.8 [kN] | FK 10.9 [kN] | FK 12.9 [kN] |\n"
    tabelle += "|--------|-------------|--------------|-------------|\n"
    
    for mu in mu_werte:
        mu_clean = mu.replace('µ', '').replace(' = ', '=')
        zeile = f"| {mu_clean} |"
        
        for fk in fk_werte:
            # Finde passende Spalte
            wert = None
            for col in relevante_cols:
                if mu in col and f'- {fk}' in col:
                    wert = row[col]
                    break
            
            if wert is not None and not pd.isna(wert):
                zeile += f" {wert/1000:.1f} |"
            else:
                zeile += " - |"
        
        tabelle += zeile + "\n"
    
    return tabelle

def format_beide_schraubentypen_tabelle(row) -> str:
    """Formatiert Vergleichstabelle für beide Schraubentypen."""
    
    mu_werte = ['µ1 = 0.08', 'µ2 = 0.10', 'µ3 = 0.12', 'µ4 = 0.14', 'µ5 = 0.16']
    
    tabelle = "| μ-Wert | Schaftschrauben [kN] |  | | Dehnschrauben [kN] |  | |\n"
    tabelle += "|--------|-----|-----|-----|-----|-----|-----|\n"
    tabelle += "|        | 8.8 | 10.9| 12.9| 8.8 | 10.9| 12.9|\n"
    tabelle += "|--------|-----|-----|-----|-----|-----|-----|\n"
    
    for mu in mu_werte:
        mu_clean = mu.replace('µ', '').replace(' = ', '=')
        zeile = f"| {mu_clean} |"
        
        # Schaftschrauben-Werte
        for fk in ['8.8', '10.9', '12.9']:
            schaft_cols = [col for col in row.index if 'Vorspannkraft Schaftschrauben' in col]
            wert = None
            for col in schaft_cols:
                if mu in col and f'- {fk}' in col:
                    wert = row[col]
                    break
            zeile += f" {wert/1000:.1f} |" if (wert is not None and not pd.isna(wert)) else " - |"
        
        # Dehnschrauben-Werte
        for fk in ['8.8', '10.9', '12.9']:
            dehn_cols = [col for col in row.index if 'Vorspannkraft Dehnschrauben' in col]
            wert = None
            for col in dehn_cols:
                if mu in col and f'- {fk}' in col:
                    wert = row[col]
                    break
            zeile += f" {wert/1000:.1f} |" if (wert is not None and not pd.isna(wert)) else " - |"
        
        tabelle += zeile + "\n"
    
    return tabelle

def format_berechnungsdokumentation(row) -> str:
    """Erstellt vollständige Berechnungsdokumentation."""
    
    doku = f"""## 📝 BERECHNUNGSDOKUMENTATION - {row['Gewinde']}

### 🔧 Grundlagen nach VDI 2230

#### **Gewindegeometrie nach ISO 262:**
```
Nenndurchmesser D = {row['Nenndurchmesser D']:.1f} mm
Steigung P = {row['Steigung P']:.2f} mm

Flankendurchmesser: d2 = D - 0.649519 × P
d2 = {row['Nenndurchmesser D']:.1f} - 0.649519 × {row['Steigung P']:.2f} = {row['Flankendurchmesser d2 = D2']:.3f} mm

Kerndurchmesser: d3 = D - 1.22687 × P  
d3 = {row['Nenndurchmesser D']:.1f} - 1.22687 × {row['Steigung P']:.2f} = {row['Kerndurchmesser d3']:.3f} mm

Spannungsquerschnitt: As = π × (d2 + d3)² / 16
As = π × ({row['Flankendurchmesser d2 = D2']:.3f} + {row['Kerndurchmesser d3']:.3f})² / 16 = {row['Spannungsquerschnitt As']:.3f} mm²
```

#### **Montagezugspannung (VDI 2230):**
```
σ_m = 0.9 × Rp / √[1 + 3 × (3/d₀ × (0.159×P + 0.577×μ×d2))²]

Mit:
- d₀ = (d2 + d3) / 2 = ({row['Flankendurchmesser d2 = D2']:.3f} + {row['Kerndurchmesser d3']:.3f}) / 2 = {(row['Flankendurchmesser d2 = D2'] + row['Kerndurchmesser d3'])/2:.3f} mm
- P = {row['Steigung P']:.2f} mm
- μ = Reibungskoeffizient (0.08 - 0.16)
- Rp = Streckgrenze der Festigkeitsklasse
```

#### **Vorspannkraft-Berechnung:**

**Schaftschrauben:**
```
F_sp = σ_m × As
F_sp = σ_m × {row['Spannungsquerschnitt As']:.3f} mm²
```

**Dehnschrauben:**
```
A_dehn = (π/4) × (0.9 × d3)²
A_dehn = (π/4) × (0.9 × {row['Kerndurchmesser d3']:.3f})² = {np.pi/4 * (0.9 * row['Kerndurchmesser d3'])**2:.3f} mm²

F_sp_dehn = σ_m × A_dehn
```

#### **Festigkeitsklassen (optimierte Rp-Werte):**
```
FK 8.8:  Rp = 640 N/mm² (≤ M16) / 660 N/mm² (> M16)
FK 10.9: Rp = 940 N/mm²  
FK 12.9: Rp = 1100 N/mm²
```

### 📊 **Klassifizierung:**
- **Reihe**: {row['Reihe']} nach DIN 13-6
- **Gewindetyp**: {row['Gewindetyp']}
- **Anwendung**: {"Standard-Anwendungen" if row['Reihe'] == 'Reihe 1' else "Spezielle Anwendungen"}

### ⚠️ **Wichtige Hinweise:**
- Berechnung für 90% Vorespannung (VDI 2230 Standard)
- Bei anderen Voerspannungen: F_sp_neu = F_sp_tabelle × (Vorespannung_% / 90%)
- Reibungskoeffizient μ abhängig von Schmierung und Oberflächenqualität
- Dehnschrauben haben ca. 71-73% der Schaftschrauben-Vorspannkraft"""

    return doku

def schrauben_datenbank(
    gewinde: Optional[str] = None,
    gewinde_bereich: Optional[Dict] = None,
    schraubentyp: str = "Schaftschrauben",
    festigkeitsklasse: Optional[str] = None,
    reibbeiwert: Optional[str] = None,
    min_vorspannkraft: Optional[str] = None,
    ausgabe_detail: str = "standard",
    berechnung_zeigen: bool = False
) -> Dict:
    """
    📊 DATABASE SEARCH AND ANALYSIS SOLUTION
    
    Flexible Hauptabfrage für Schraubendaten aus der ISO-Gewinde-Datenbank.
    
    Args:
        gewinde: Einzelgewinde z.B. "M24", "M10x1.0"
        gewinde_bereich: Dict mit {"von": "M12", "bis": "M24"}
        schraubentyp: "Schaftschrauben", "Dehnschrauben", "beide"
        festigkeitsklasse: "8.8", "10.9", "12.9", "alle" oder None
        reibbeiwert: "0.08", "0.10", "0.12", "0.14", "0.16", "alle" oder None
        min_vorspannkraft: Kraft mit Einheit z.B. "100 kN", "50000 N"
        ausgabe_detail: "minimal", "standard", "vollständig"
        berechnung_zeigen: Zeigt vollständige Berechnungsdokumentation
    
    Returns:
        Dict: Formatierte Markdown-Ausgabe der Schraubendaten
    """
    
    _ensure_pandas()  # Pandas laden bevor wir es verwenden
    
    try:
        # Lade Datenbank
        df = load_schrauben_datenbank()
        
        # Parameter-Validierung
        if gewinde is None and gewinde_bereich is None:
            return {
                "error": f"Entweder '{FUNCTION_PARAM_GEWINDE_NAME}' oder '{FUNCTION_PARAM_GEWINDE_BEREICH_NAME}' muss angegeben werden",
                "beispiele": [
                    f'schrauben_datenbank({FUNCTION_PARAM_GEWINDE_NAME}="{FUNCTION_PARAM_GEWINDE_EXAMPLE}")',
                    f'schrauben_datenbank({FUNCTION_PARAM_GEWINDE_BEREICH_NAME}={FUNCTION_PARAM_GEWINDE_BEREICH_EXAMPLE})'
                ]
            }
        
        if gewinde is not None and gewinde_bereich is not None:
            return {
                "error": f"Nur entweder '{FUNCTION_PARAM_GEWINDE_NAME}' oder '{FUNCTION_PARAM_GEWINDE_BEREICH_NAME}' angeben, nicht beide"
            }
        
        # Validiere Schraubentyp
        if schraubentyp not in ["Schaftschrauben", "Dehnschrauben", "beide"]:
            return {
                "error": "Ungültiger Schraubentyp",
                "gültig": ["Schaftschrauben", "Dehnschrauben", "beide"]
            }
        
        # Validiere Detail-Level
        if ausgabe_detail not in ["minimal", "standard", "vollständig"]:
            return {
                "error": "Ungültiges Detail-Level",
                "gültig": ["minimal", "standard", "vollständig"]
            }
        
        # Parse Parameter
        filter_params = {}
        
        # Einzelgewinde
        if gewinde is not None:
            gewinde_info = parse_gewinde_bezeichnung(gewinde)
            if 'error' in gewinde_info:
                return gewinde_info
            filter_params['gewinde_csv'] = gewinde_info['gewinde_csv']
        
        # Gewindebereich
        if gewinde_bereich is not None:
            bereich_info = parse_gewinde_bereich(gewinde_bereich)
            if 'error' in bereich_info:
                return bereich_info
            filter_params.update(bereich_info)
        
        # Mindest-Vorspannkraft
        if min_vorspannkraft is not None:
            try:
                min_kraft_n = parse_kraft_einheit(min_vorspannkraft)
                filter_params['min_vorspannkraft_n'] = min_kraft_n
            except ValueError as e:
                return {"error": str(e)}
        
        # Filtere Datenbank
        filtered_df = filter_dataframe(df, **filter_params)
        
        if len(filtered_df) == 0:
            return {
                "error": "Keine Gewinde gefunden, die den Kriterien entsprechen",
                "hinweis": "Überprüfen Sie die Filterparameter"
            }
        
        # Generiere Ausgabe
        if len(filtered_df) == 1:
            # Einzelgewinde - detaillierte Ausgabe
            return format_einzelgewinde_ausgabe(filtered_df.iloc[0], schraubentyp, ausgabe_detail, berechnung_zeigen)
        else:
            # Mehrere Gewinde - Übersichtstabelle
            return format_mehrgewinde_ausgabe(filtered_df, schraubentyp, ausgabe_detail)
            
    except Exception as e:
        return {
            "error": "Systemfehler",
            "message": str(e),
            "hinweis": "Überprüfen Sie die Parameter und versuchen Sie es erneut"
        }

def format_einzelgewinde_ausgabe(row, schraubentyp: str, detail_level: str, berechnung_zeigen: bool) -> Dict:
    """Formatiert Ausgabe für ein einzelnes Gewinde."""
    
    # Prüfe Reihe und warne falls nicht Reihe 1
    reihe_warnung = ""
    if row['Reihe'] != 'Reihe 1':
        reihe_warnung = f"""
⚠️ **REIHEN-HINWEIS**: Dieses Gewinde gehört zu {row['Reihe']}. 
Es wird empfohlen, **Reihe 1-Gewinde** zu bevorzugen, außer es gibt spezielle Gründe für {row['Reihe']}.
"""
    
    # Basis-Ausgabe
    ausgabe = f"""# 🔧 {row['Gewinde']} - Vollständige Schraubendaten
{reihe_warnung}
## 📊 VORSPANNKRÄFTE

{format_vorspannkraft_tabelle(row, schraubentyp)}

## 📐 GEOMETRISCHE DATEN

{format_geometrie_tabelle(row)}"""
    
    # Erweiterte Details
    if detail_level in ["vollständig"] or berechnung_zeigen:
        ausgabe += f"\n\n{format_berechnungsdokumentation(row)}"
    
    return {
        "gewinde_daten": ausgabe,
        "gewinde": row['Gewinde'],
        "reihe": row['Reihe'],
        "gewindetyp": row['Gewindetyp'],
        "reihe_warnung": True if row['Reihe'] != 'Reihe 1' else False,
        "detail_level": detail_level
    }

def format_mehrgewinde_ausgabe(df, schraubentyp: str, detail_level: str) -> Dict:
    """Formatiert Ausgabe für mehrere Gewinde."""
    
    anzahl = len(df)
    ausgabe = f"""# 🔧 Schrauben-Übersicht - {anzahl} Gewinde gefunden

## 📊 GEWINDE-ÜBERSICHT

| Gewinde | Reihe | Typ | D [mm] | P [mm] | As [mm²] |
|---------|-------|-----|--------|--------|----------|"""
    
    for _, row in df.iterrows():
        ausgabe += f"\n| {row['Gewinde']} | {row['Reihe']} | {row['Gewindetyp']} | {row['Nenndurchmesser D']:.1f} | {row['Steigung P']:.2f} | {row['Spannungsquerschnitt As']:.1f} |"
    
    # Reihen-Statistik
    reihen_stats = df['Reihe'].value_counts()
    nicht_reihe1 = anzahl - reihen_stats.get('Reihe 1', 0)
    
    ausgabe += f"""

## 📈 STATISTIK

- **Gesamt gefunden**: {anzahl} Gewinde
- **Reihe 1 (empfohlen)**: {reihen_stats.get('Reihe 1', 0)} Gewinde
- **Andere Reihen**: {nicht_reihe1} Gewinde"""
    
    if nicht_reihe1 > 0:
        ausgabe += f"""

⚠️ **HINWEIS**: {nicht_reihe1} Gewinde gehören nicht zu Reihe 1. 
Prüfen Sie, ob Reihe 1-Alternativen verfügbar sind."""
    
    # Bei wenigen Gewindern auch Vorspannkräfte zeigen
    if anzahl <= 5 and detail_level in ["standard", "vollständig"]:
        ausgabe += "\n\n## 📊 VORSPANNKRAFT-ÜBERSICHT\n"
        for _, row in df.iterrows():
            ausgabe += f"\n### {row['Gewinde']}\n"
            ausgabe += format_vorspannkraft_tabelle(row, schraubentyp)
    
    return {
        "gewinde_uebersicht": ausgabe,
        "anzahl_gefunden": anzahl,
        "reihe_1_anteil": reihen_stats.get('Reihe 1', 0),
        "andere_reihen": nicht_reihe1,
        "detail_level": detail_level
    }

def get_metadata():
    """
    Liefert Tool-Metadaten für Registry-Discovery.
    
    Returns:
        Dict: Tool-Metadaten im neuen System-Format
    """
    return {
        "tool_name": "schrauben_datenbank",
        "short_description": "Schrauben-Datenbank - Flexible Abfrage von Gewindedaten und Vorspannkräften",
        "description": f"""Flexible Hauptabfrage für die ISO-metrische Gewinde-Datenbank mit 1.081 Gewindeeinträgen.

Ermöglicht umfassende Abfragen von:
- Einzelgewinde oder Gewinde-Bereichen
- Vorspannkräfte für Schaft- und Dehnschrauben
- Geometrische Gewindedaten
- VDI 2230-Berechnungsdokumentation

Automatische Features:
- Erkennung Regel-/Feingewinde
- Reihen-Warnsystem (bevorzugt Reihe 1)
- Optimierte Markdown-Ausgabe
- VDI 2230-konforme Berechnungen

Normen: DIN 13-1 bis DIN 13-11, DIN 13-6, VDI 2230, ISO 262""",
        "tags": ["DIN 13", "VDI 2230", "schrauben"],

        "has_solving": "none",
        "parameters": {
            FUNCTION_PARAM_GEWINDE_NAME: {
                "type": "string",
                "description": FUNCTION_PARAM_GEWINDE_DESC,
                "default": ""
            },
            FUNCTION_PARAM_GEWINDE_BEREICH_NAME: {
                "type": "object",
                "description": FUNCTION_PARAM_GEWINDE_BEREICH_DESC,
                "default": {}
            },
            FUNCTION_PARAM_SCHRAUBENTYP_NAME: {
                "type": "string",
                "description": FUNCTION_PARAM_SCHRAUBENTYP_DESC,
                "default": FUNCTION_PARAM_SCHRAUBENTYP_EXAMPLE
            },
            FUNCTION_PARAM_FESTIGKEITSKLASSE_NAME: {
                "type": "string",
                "description": FUNCTION_PARAM_FESTIGKEITSKLASSE_DESC,
                "default": ""
            },
            FUNCTION_PARAM_REIBBEIWERT_NAME: {
                "type": "string",
                "description": FUNCTION_PARAM_REIBBEIWERT_DESC,
                "default": "alle"
            },
            FUNCTION_PARAM_MIN_VORSPANNKRAFT_NAME: {
                "type": "string",
                "description": FUNCTION_PARAM_MIN_VORSPANNKRAFT_DESC,
                "default": ""
            }
        },
        "examples": [
            {
                "description": "Vollständige Analyse eines Gewindes",
                "parameters": {FUNCTION_PARAM_GEWINDE_NAME: FUNCTION_PARAM_GEWINDE_EXAMPLE, FUNCTION_PARAM_AUSGABE_DETAIL_NAME: "vollständig", FUNCTION_PARAM_BERECHNUNG_ZEIGEN_NAME: True},
                "result": "Komplette Schraubendaten mit Berechnungsdokumentation"
            },
            {
                "description": "Bereichssuche mit Vorspannkraft-Filter",
                "parameters": {FUNCTION_PARAM_GEWINDE_BEREICH_NAME: {"von": "M16", "bis": "M30"}, FUNCTION_PARAM_MIN_VORSPANNKRAFT_NAME: FUNCTION_PARAM_MIN_VORSPANNKRAFT_EXAMPLE},
                "result": "Übersicht aller Gewinde im Bereich mit ausreichender Vorspannkraft"
            },
            {
                "description": "Vergleich Schaft- vs Dehnschrauben",
                "parameters": {FUNCTION_PARAM_GEWINDE_NAME: "M20", FUNCTION_PARAM_SCHRAUBENTYP_NAME: "beide"},
                "result": "Vergleichstabelle beider Schraubentypen"
            }
        ]
    }

def calculate(**kwargs) -> Dict:
    """
    Führt Schrauben-Datenbankabfrage durch.
    
    Args:
        **kwargs: Alle Parameter für die Datenbankabfrage
        
    Returns:
        Dict: Schrauben-Datenbank Ergebnisse
    """
    return schrauben_datenbank(**kwargs)

# 🎯 METADATA
if __name__ == "__main__":
    # Test-Beispiele
    print("=== Schrauben-Datenbank Template Tests ===")
    
    # Test 1: Einzelgewinde
    result1 = schrauben_datenbank(gewinde="M10")
    print("Test 1 - M10 Einzelgewinde:")
    if 'gewinde_daten' in result1:
        print(result1['gewinde_daten'][:300] + "...")
    else:
        print(result1)
    
    print("\n" + "="*50)
    
    # Test 2: Bereich
    result2 = schrauben_datenbank(gewinde_bereich={"von": "M10", "bis": "M16"})
    print("Test 2 - Bereichsabfrage:")
    if 'gewinde_uebersicht' in result2:
        print(result2['gewinde_uebersicht'][:300] + "...")
    else:
        print(result2) 