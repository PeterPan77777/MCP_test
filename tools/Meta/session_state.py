#!/usr/bin/env python3
"""
Session State Management für Meta-Tools

Zentrales Session State Management für sicheres Whitelisting zwischen Meta-Tools.
"""

import time
from typing import Set, Dict, List
from collections import defaultdict

# Globaler Session State für alle Meta-Tools
_session_state = {
    "viewed_categories": set(),      # Angesehene Kategorien
    "viewed_functions": set(),       # Angesehene Funktionen  
    "whitelisted_tools": set(),      # Freigeschaltete Tools (nach get_tool_details)
    "call_timestamps": defaultdict(list)  # Rate-Limiting: {tool_name: [timestamp1, timestamp2, ...]}
}

def get_session_state() -> Dict:
    """Gibt den aktuellen Session State zurück"""
    return _session_state

def add_to_whitelist(tool_name: str) -> None:
    """Fügt ein Tool zur Whitelist hinzu"""
    _session_state["whitelisted_tools"].add(tool_name)
    _session_state["viewed_functions"].add(tool_name)

def is_whitelisted(tool_name: str) -> bool:
    """Prüft ob ein Tool in der Whitelist ist"""
    return tool_name in _session_state["whitelisted_tools"]

def get_whitelisted_tools() -> Set[str]:
    """Gibt alle gewhitelisteten Tools zurück"""
    return _session_state["whitelisted_tools"].copy()

def _cleanup_old_timestamps(tool_name: str, max_age_seconds: int = 60) -> None:
    """Entfernt Timestamps älter als max_age_seconds für ein Tool"""
    current_time = time.time()
    cutoff_time = current_time - max_age_seconds
    
    # Filtere nur Timestamps der letzten 60 Sekunden
    recent_timestamps = [
        ts for ts in _session_state["call_timestamps"][tool_name] 
        if ts > cutoff_time
    ]
    _session_state["call_timestamps"][tool_name] = recent_timestamps

def increment_call_count(tool_name: str) -> int:
    """Fügt einen neuen Call-Timestamp hinzu und gibt aktuelle Anzahl zurück (letzte 60 Sekunden)"""
    current_time = time.time()
    
    # Bereinige alte Timestamps vor dem Hinzufügen
    _cleanup_old_timestamps(tool_name)
    
    # Füge neuen Timestamp hinzu
    _session_state["call_timestamps"][tool_name].append(current_time)
    
    return len(_session_state["call_timestamps"][tool_name])

def get_call_count(tool_name: str) -> int:
    """Gibt Anzahl der Calls in den letzten 60 Sekunden zurück"""
    # Bereinige alte Timestamps vor der Abfrage
    _cleanup_old_timestamps(tool_name)
    
    return len(_session_state["call_timestamps"][tool_name]) 