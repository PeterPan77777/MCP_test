#!/usr/bin/env python3
"""
Clock Meta-Tool - UTC-Zeitstempel

Stellt aktuelle UTC-Zeit im ISO-Format bereit.
"""

import datetime

def clock() -> str:
    """
    Gibt aktuellen UTC-Zeitstempel zurück.
    
    Returns:
        str: UTC-Zeitstempel im ISO-Format (z.B. "2024-01-15T14:30:25.123456Z")
    """
    return datetime.datetime.utcnow().isoformat() + "Z"

# Tool-Metadaten für Registry
TOOL_METADATA = {
    "name": "clock",
    "description": """Gibt die aktuelle UTC-Zeit im ISO-Format zurück.

Nützlich für:
- Zeitstempel in Berechnungen
- Logging und Dokumentation  
- Zeitbasierte Validierungen

Keine Parameter erforderlich.

Format: YYYY-MM-DDTHH:MM:SS.ssssssZ""",
    "tags": ["meta"]
}

 