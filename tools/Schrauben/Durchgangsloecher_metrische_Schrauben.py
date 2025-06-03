"""
Engineering Tool: Durchgangslöcher für metrische Schrauben
===========================================================

Dieses Tool stellt Standardwerte für Durchgangslöcher metrischer Schrauben bereit.
Die Werte basieren auf DIN-Normen und Industriestandards.

WICHTIG: Dieses Tool führt KEINE symbolische Berechnungen durch!
Es handelt sich um eine reine Tabellen-Abfrage mit festen Normwerten.

Eingabeparameter:
- screw_size: Schraubengröße (z.B. "M6", "M10", "M20")
- hole_class: Lochklasse ("fein", "mittel", "grob")

Ausgabe:
- diameter: Durchmesser des Durchgangslochs in mm

Verfügbare Schraubengrößen: M6 bis M150
Verfügbare Lochklassen: fein, mittel, grob
"""

from typing import Dict, Any, Optional, List
from pint import Quantity
import json

try:
    # Wenn als Modul importiert
    from ..units_utils import parse_unit_input, format_quantity, ureg
except ImportError:
    # Wenn direkt ausgeführt - vereinfachte Implementierung
    print("⚠️ Wird direkt ausgeführt - vereinfachte Pint-Implementierung")
    import pint
    ureg = pint.UnitRegistry()

# ===== TABELLE FÜR DURCHGANGSLÖCHER =====
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

def get_metadata() -> Dict[str, Any]:
    """
    Engineering Tool Metadaten für MCP-Server Registration
    """
    return {
        "tool_name": "durchgangsloecher_metrische_schrauben",
        "category": "schrauben",
        "tags": ["tabellenwerk", "schrauben", "normwerte"],
        "short_description": "Durchgangslöcher für metrische Schrauben (M6-M150)",
        "description": (
            "Stellt Normwerte für Durchgangslöcher metrischer Schrauben bereit. "
            "WICHTIG: Keine symbolische Berechnung - reine Tabellen-Abfrage mit festen DIN-Normwerten. "
            "Verfügbare Schraubengrößen: M6 bis M150. Verfügbare Lochklassen: fein, mittel, grob. "
            "ERWEITERT: Unterstützt 'all' für komplette Tabellen-Übersichten."
        ),
        "version": "1.1.0",
        "parameters": {
            "screw_size": {
                "type": "string",
                "description": "Schraubengröße (z.B. 'M6', 'M10', 'M20') oder 'all' für alle Größen",
                "example": "M10",
                "allowed_values": list(DURCHGANGSLOCH_TABELLE.keys()) + ["all"]
            },
            "hole_class": {
                "type": "string", 
                "description": "Lochklasse ('fein', 'mittel', 'grob') oder 'all' für alle Klassen",
                "example": "mittel",
                "allowed_values": ["fein", "mittel", "grob", "all"]
            }
        },
        "output": {
            "diameter": {
                "type": "Quantity or Dict",
                "description": "Durchmesser des Durchgangslochs oder Tabelle mit mehreren Werten",
                "unit": "mm"
            }
        },
        "examples": [
            {
                "title": "Einzelner Wert: M10 Schraube, mittlere Lochklasse",
                "input": {"screw_size": "M10", "hole_class": "mittel"},
                "output": {"diameter": "11.0 mm"}
            },
            {
                "title": "Alle Lochklassen für M20",
                "input": {"screw_size": "M20", "hole_class": "all"},
                "output": {"table": {"M20": {"fein": "21.0 mm", "mittel": "22.0 mm", "grob": "24.0 mm"}}}
            },
            {
                "title": "Alle Schraubengrößen für mittlere Lochklasse",
                "input": {"screw_size": "all", "hole_class": "mittel"},
                "output": {"table": {"M6": "6.6 mm", "M8": "9.0 mm", "M10": "11.0 mm"}}
            },
            {
                "title": "Komplette Tabelle",
                "input": {"screw_size": "all", "hole_class": "all"},
                "output": {"table": "Vollständige DIN-Normwerte-Tabelle"}
            }
        ],
        "mathematical_foundation": (
            "Basiert auf DIN-Normen und Industriestandards für Durchgangslöcher metrischer Schrauben. "
            "Die Werte berücksichtigen Fertigungstoleranzen und Montageanforderungen."
        ),
        "assumptions": [
            "Standardmäßige DIN-Normen",
            "Normale Montagebedingungen",
            "Übliche Werkstoffe für Schraubenverbindungen"
        ],
        "limitations": [
            "Keine symbolische Berechnung möglich",
            "Nur Tabellen-Lookup verfügbar",
            "Begrenzt auf M6 bis M150",
            "Nur drei Lochklassen verfügbar"
        ],
        "calculation_type": "table_lookup",  # KEIN sympy!
        "has_symbolic_solving": False,  # Explizit keine symbolische Lösung
        "reference_units": {
            "diameter": "mm"
        }
    }

def calculate(**kwargs) -> Dict[str, Any]:
    """
    Abfrage von Durchgangsloch-Durchmessern für metrische Schrauben
    
    WICHTIG: Dies ist eine reine Tabellen-Abfrage, KEINE Berechnung!
    
    ERWEITERT: Unterstützt jetzt auch "all" für Tabellen-Übersichten:
    - screw_size="all", hole_class="mittel" → Alle Schrauben für mittlere Klasse
    - screw_size="M10", hole_class="all" → Alle Klassen für M10
    - screw_size="all", hole_class="all" → Komplette Tabelle
    
    Args:
        screw_size (str): Schraubengröße (z.B. "M10") oder "all"
        hole_class (str): Lochklasse ("fein", "mittel", "grob") oder "all"
        
    Returns:
        Dict mit Durchgangsloch-Durchmesser(n)
        
    Raises:
        ValueError: Bei ungültigen Eingabeparametern
    """
    
    # Parameter validieren
    required_params = ["screw_size", "hole_class"]
    for param in required_params:
        if param not in kwargs:
            raise ValueError(f"Pflichtparameter '{param}' fehlt")
    
    screw_size = kwargs["screw_size"].strip().lower()
    hole_class = kwargs["hole_class"].strip().lower()
    
    # === TABELLEN-ABFRAGEN (mit "all") ===
    
    if screw_size == "all" and hole_class == "all":
        # Komplette Tabelle zurückgeben
        complete_table = {}
        for size, classes in DURCHGANGSLOCH_TABELLE.items():
            complete_table[size] = {
                cls: f"{diameter} mm" for cls, diameter in classes.items()
            }
        
        return {
            "table": complete_table,
            "query_type": "complete_table",
            "total_entries": len(DURCHGANGSLOCH_TABELLE) * 3,
            "screw_sizes": list(DURCHGANGSLOCH_TABELLE.keys()),
            "hole_classes": ["fein", "mittel", "grob"],
            "source": "DIN-Normwerte",
            "calculation_type": "table_lookup",
            "note": "Komplette DIN-Normwerte-Tabelle für alle Schraubengrößen und Lochklassen"
        }
    
    elif screw_size == "all" and hole_class in ["fein", "mittel", "grob"]:
        # Alle Schraubengrößen für eine Lochklasse
        size_table = {}
        for size, classes in DURCHGANGSLOCH_TABELLE.items():
            diameter_value = classes[hole_class]
            size_table[size] = f"{diameter_value} mm"
        
        return {
            "table": size_table,
            "query_type": "all_sizes_one_class",
            "hole_class": hole_class,
            "total_entries": len(DURCHGANGSLOCH_TABELLE),
            "source": "DIN-Normwerte",
            "calculation_type": "table_lookup",
            "note": f"Alle Schraubengrößen für Lochklasse '{hole_class}'"
        }
    
    elif screw_size.upper() in DURCHGANGSLOCH_TABELLE and hole_class == "all":
        # Alle Lochklassen für eine Schraubengröße
        screw_size_upper = screw_size.upper()
        classes_table = {}
        for cls, diameter_value in DURCHGANGSLOCH_TABELLE[screw_size_upper].items():
            classes_table[cls] = f"{diameter_value} mm"
        
        return {
            "table": {screw_size_upper: classes_table},
            "query_type": "one_size_all_classes", 
            "screw_size": screw_size_upper,
            "total_entries": 3,
            "source": "DIN-Normwerte",
            "calculation_type": "table_lookup",
            "note": f"Alle Lochklassen für Schraubengröße {screw_size_upper}"
        }
    
    # === EINZELWERT-ABFRAGEN (original) ===
    
    else:
        # Original-Verhalten: Einzelwert-Abfrage
        screw_size_upper = screw_size.upper()
        
        # Schraubengröße validieren
        if screw_size_upper not in DURCHGANGSLOCH_TABELLE:
            available_sizes = ", ".join(sorted(DURCHGANGSLOCH_TABELLE.keys(), 
                                             key=lambda x: int(x[1:])))  # Nach Nummer sortieren
            raise ValueError(
                f"Unbekannte Schraubengröße: {screw_size_upper}. "
                f"Verfügbare Größen: {available_sizes} oder 'all'"
            )
        
        # Lochklasse validieren
        if hole_class not in ["fein", "mittel", "grob"]:
            raise ValueError(
                f"Unbekannte Lochklasse: {hole_class}. "
                f"Verfügbare Klassen: fein, mittel, grob oder 'all'"
            )
        
        # Durchmesser aus Tabelle holen
        diameter_value = DURCHGANGSLOCH_TABELLE[screw_size_upper][hole_class]
        
        # Als Quantity mit Einheit erstellen
        diameter = diameter_value * ureg.mm
        
        return {
            "diameter": diameter,
            "query_type": "single_value",
            "input_parameters": {
                "screw_size": screw_size_upper,
                "hole_class": hole_class
            },
            "source": "DIN-Normwerte",
            "calculation_type": "table_lookup",
            "note": f"Durchgangsloch für {screw_size_upper} Schraube, Klasse '{hole_class}'"
        }

def get_available_screw_sizes() -> List[str]:
    """Gibt alle verfügbaren Schraubengrößen zurück"""
    return sorted(DURCHGANGSLOCH_TABELLE.keys(), key=lambda x: int(x[1:]))

def get_available_hole_classes() -> List[str]:
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

if __name__ == "__main__":
    # Test der Funktion
    print("🔧 Test: Durchgangslöcher metrische Schrauben")
    print("=" * 50)
    
    # Test-Fälle für Einzelwerte
    test_cases = [
        {"screw_size": "M10", "hole_class": "mittel"},
        {"screw_size": "M20", "hole_class": "grob"},
        {"screw_size": "M6", "hole_class": "fein"},
        {"screw_size": "M150", "hole_class": "grob"}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case}")
        try:
            result = calculate(**test_case)
            print(f"✅ Erfolg: {result['diameter']}")
            print(f"   Note: {result['note']}")
        except Exception as e:
            print(f"❌ Fehler: {e}")
    
    # Erweiterte Tests für "all"-Funktionalität
    print(f"\n🔧 ERWEITERTE TESTS: 'all'-Unterstützung")
    print("=" * 50)
    
    # Test: Alle Klassen für M20
    print(f"\nTest: Alle Klassen für M20")
    try:
        result = calculate(screw_size="M20", hole_class="all")
        print(f"✅ Tabelle: {result['table']}")
        print(f"   Typ: {result['query_type']}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    # Test: Alle Größen für mittlere Klasse (erste 5)
    print(f"\nTest: Alle Größen für mittlere Klasse")
    try:
        result = calculate(screw_size="all", hole_class="mittel")
        first_5 = dict(list(result['table'].items())[:5])
        print(f"✅ Erste 5: {first_5}")
        print(f"   Gesamt: {result['total_entries']} Einträge")
        print(f"   Typ: {result['query_type']}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    # Test: Komplette Tabelle (nur Struktur)
    print(f"\nTest: Komplette Tabelle")
    try:
        result = calculate(screw_size="all", hole_class="all")
        print(f"✅ Tabellenstruktur:")
        print(f"   Schraubengrößen: {len(result['table'])}")
        print(f"   Beispiel M6: {result['table']['M6']}")
        print(f"   Beispiel M150: {result['table']['M150']}")
        print(f"   Gesamt Einträge: {result['total_entries']}")
        print(f"   Typ: {result['query_type']}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    # Verfügbare Größen anzeigen
    print(f"\n📋 Verfügbare Schraubengrößen: {len(get_available_screw_sizes())}")
    print(f"📋 Durchmesser-Bereich: {get_diameter_range()}")
    print(f"\n✅ ALLE TESTS ABGESCHLOSSEN") 