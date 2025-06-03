#!/usr/bin/env python3
"""
Tag-Definitionen für Engineering MCP Server

Diese Datei enthält alle verfügbaren Tag-Kategorien mit ihren Beschreibungen.
Neue Tags können hier einfach hinzugefügt werden.
"""

from typing import Dict, Any

# Verfügbare Tag-Kategorien
TAG_DEFINITIONS = {
    "meta": {
        "name": "meta",
        "description": "Discovery und Workflow-Tools für Tool-Exploration",
        "tools": [],
        "tool_count": 0
    },
    "elementar": {
        "name": "elementar", 
        "description": "Grundlegende geometrische und mathematische Berechnungen",
        "tools": [],
        "tool_count": 0
    },
    "mechanik": {
        "name": "mechanik",
        "description": "Spezialisierte Formeln aus Mechanik und Maschinenbau", 
        "tools": [],
        "tool_count": 0
    },
    "tabellenwerk": {
        "name": "tabellenwerk",
        "description": "Tabellen-basierte Nachschlagewerke und Normwerte ohne Berechnungen",
        "tools": [],
        "tool_count": 0
    },
    "schrauben": {
        "name": "schrauben",
        "description": "Schraubenverbindungen, Durchgangslöcher und Gewindeberechnungen",
        "tools": [],
        "tool_count": 0
    },
    "normwerte": {
        "name": "normwerte", 
        "description": "DIN-, ISO- und andere Normwerte für Engineering-Anwendungen",
        "tools": [],
        "tool_count": 0
    }
}

def get_tag_definitions() -> Dict[str, Dict[str, Any]]:
    """
    Gibt eine Kopie der Tag-Definitionen zurück.
    
    Returns:
        Dict: Tag-Definitionen mit leeren Tool-Listen (werden zur Laufzeit gefüllt)
        
    Verwendung:
        tags = get_tag_definitions()
        available_tags = list(tags.keys())
        description = tags[tag_name]["description"]
    """
    import copy
    return copy.deepcopy(TAG_DEFINITIONS)

# Beispiel für zukünftige Tag-Erweiterungen:
# Einfach hier im TAG_DEFINITIONS dict hinzufügen:
# 
# "thermodynamik": {
#     "name": "thermodynamik",
#     "description": "Wärmeübertragung, Zustandsänderungen und thermische Berechnungen",
#     "tools": [],
#     "tool_count": 0
# } 