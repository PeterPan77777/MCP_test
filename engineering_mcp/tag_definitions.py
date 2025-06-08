#!/usr/bin/env python3
"""
Tag-Definitionen für Engineering MCP Server

Dynamisches Tag-System:
- Tags werden automatisch aus allen Tools im /tools Verzeichnis gesammelt
- Beschreibungen werden zentral hier gepflegt
- Unbekannte Tags werden automatisch erkannt und gemeldet
"""

from typing import Dict, Any, Set, List
import os
import sys
import importlib.util
import inspect
import ast
import re

# ===== ZENTRALE TAG-BESCHREIBUNGEN =====
# Hier werden NUR die Beschreibungen gepflegt!
TAG_DESCRIPTIONS = {
    # Meta-Tags
    "meta": "Discovery und Workflow-Tools für Tool-Exploration",
    
    # Engineering-Kategorien
    "elementar": "Grundlegende geometrische und mathematische Berechnungen, Flächen, Volumen, Umfang, etc.",
    "mechanik": "Spezialisierte Formeln aus Mechanik und Maschinenbau",
    "tabellenwerk": "Tabellen-basierte Nachschlagewerke und Normwerte ohne Berechnungen",
    "schrauben": "Schraubenverbindungen, Durchgangslöcher und Gewindeberechnungen",

    "wissen": "Context- und Dokumentations-Tools ohne Parameter für Wissensvermittlung",
    
    
    # Spezifische Kategorien

     "druckbehaelter": "Berechnungen für Druckbehälter und Kesselformeln",
    
    # Normen und Standards
    "DIN 13": "Schrauben- und Gewindeberechnungen nach DIN 13",
    "VDI 2230": "Schraubenverbindungs-Berechnungen nach VDI 2230",
    
    
    # Physikalische Bereiche (für zukünftige Erweiterungen)

}

# Cache für entdeckte Tags
_discovered_tags_cache = None
_unknown_tags_cache = set()

def clear_tag_cache():
    """
    Leert den Tag-Discovery-Cache, um Änderungen zu erkennen.
    """
    global _discovered_tags_cache, _unknown_tags_cache
    _discovered_tags_cache = None
    _unknown_tags_cache = set()

def discover_all_tags_robust() -> Dict[str, Set[str]]:
    """
    Robuste Version: Parst Python-Dateien direkt ohne sie zu importieren.
    Funktioniert auch bei Import-Fehlern.
    
    Returns:
        Dict: Mapping von Tag zu Set von Tool-Namen die diesen Tag verwenden
    """
    tag_to_tools = {}
    tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools')
    
    # Durchsuche alle Python-Dateien im tools Verzeichnis
    for root, dirs, files in os.walk(tools_dir):
        # Überspringe __pycache__ und andere System-Verzeichnisse
        dirs[:] = [d for d in dirs if not d.startswith('__') and not d.startswith('.')]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                
                try:
                    # Lese Datei-Inhalt
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Einfachere Methode: Suche direkt im Code mit Regex
                    # Tool name - suche in get_metadata() oder TOOL_METADATA
                    tool_match = re.search(r'"tool_name"\s*:\s*"([^"]+)"', content)
                    if not tool_match:
                        tool_match = re.search(r'"name"\s*:\s*"([^"]+)"', content)
                    tool_name = tool_match.group(1) if tool_match else file[:-3]
                    
                    # Tags - suche nach tags Array oder tool_tags
                    tags_found = False
                    
                    # Methode 1: "tags": [...]
                    tags_match = re.search(r'"tags"\s*:\s*\[(.*?)\]', content, re.DOTALL)
                    if tags_match:
                        tags_str = tags_match.group(1)
                        tags = re.findall(r'["\']([^"\']+)["\']', tags_str)
                        tags_found = True
                    
                    # Methode 2: "tool_tags": TOOL_TAGS oder TOOL_TAGS = [...]
                    if not tags_found:
                        tool_tags_match = re.search(r'"tool_tags"\s*:\s*TOOL_TAGS', content)
                        if tool_tags_match:
                            # Suche nach TOOL_TAGS = [...]
                            tool_tags_def = re.search(r'TOOL_TAGS\s*=\s*\[(.*?)\]', content, re.DOTALL)
                            if tool_tags_def:
                                tags_str = tool_tags_def.group(1)
                                tags = re.findall(r'["\']([^"\']+)["\']', tags_str)
                                tags_found = True
                    
                    if tags_found:
                        # Füge Tool zu jedem Tag hinzu
                        for tag in tags:
                            if tag not in tag_to_tools:
                                tag_to_tools[tag] = set()
                            tag_to_tools[tag].add(tool_name)
                            
                            # Prüfe ob Tag unbekannt ist
                            if tag not in TAG_DESCRIPTIONS:
                                _unknown_tags_cache.add(tag)
                                        
                except Exception as e:
                    # Fehler beim Parsen ignorieren
                    pass
    
    return tag_to_tools

def discover_all_tags() -> Dict[str, Set[str]]:
    """
    Durchsucht alle Tools im /tools Verzeichnis und sammelt deren Tags.
    Versucht zuerst Import, dann robustes Parsing.
    
    Returns:
        Dict: Mapping von Tag zu Set von Tool-Namen die diesen Tag verwenden
    """
    global _discovered_tags_cache
    
    # Cache verwenden wenn verfügbar
    if _discovered_tags_cache is not None:
        return _discovered_tags_cache
    
    # Versuche zuerst die Import-Methode
    tag_to_tools = {}
    import_failed_files = []
    tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools')
    
    # Durchsuche alle Python-Dateien im tools Verzeichnis
    for root, dirs, files in os.walk(tools_dir):
        # Überspringe __pycache__ und andere System-Verzeichnisse
        dirs[:] = [d for d in dirs if not d.startswith('__') and not d.startswith('.')]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                
                try:
                    # Lade Modul dynamisch
                    spec = importlib.util.spec_from_file_location("temp_module", file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Suche nach get_metadata Funktion (Engineering-Tools)
                        if hasattr(module, 'get_metadata'):
                            metadata = module.get_metadata()
                            
                            # Extrahiere Tags - unterstütze sowohl "tags" als auch "tool_tags"
                            tags = metadata.get('tags', []) or metadata.get('tool_tags', [])
                            tool_name = metadata.get('tool_name', file[:-3])  # Fallback zu Dateiname
                            
                            # Füge Tool zu jedem Tag hinzu
                            for tag in tags:
                                if tag not in tag_to_tools:
                                    tag_to_tools[tag] = set()
                                tag_to_tools[tag].add(tool_name)
                                
                                # Prüfe ob Tag unbekannt ist
                                if tag not in TAG_DESCRIPTIONS:
                                    _unknown_tags_cache.add(tag)
                        
                        # Suche nach TOOL_METADATA (Meta-Tools)
                        elif hasattr(module, 'TOOL_METADATA'):
                            meta_data = module.TOOL_METADATA
                            
                            # Extrahiere Tags aus TOOL_METADATA
                            tags = meta_data.get('tags', [])
                            tool_name = meta_data.get('name', file[:-3])  # Fallback zu Dateiname
                            
                            # Füge Tool zu jedem Tag hinzu
                            for tag in tags:
                                if tag not in tag_to_tools:
                                    tag_to_tools[tag] = set()
                                tag_to_tools[tag].add(tool_name)
                                
                                # Prüfe ob Tag unbekannt ist
                                if tag not in TAG_DESCRIPTIONS:
                                    _unknown_tags_cache.add(tag)
                                    
                except Exception as e:
                    # Merke Datei für robustes Parsing
                    import_failed_files.append(file_path)
    
    # Wenn Dateien beim Import fehlgeschlagen sind, verwende robustes Parsing
    if import_failed_files:
        robust_tags = discover_all_tags_robust()
        # Merge Ergebnisse
        for tag, tools in robust_tags.items():
            if tag not in tag_to_tools:
                tag_to_tools[tag] = set()
            tag_to_tools[tag].update(tools)
    
    # Cache aktualisieren
    _discovered_tags_cache = tag_to_tools
    
    return tag_to_tools

def get_unknown_tags() -> Set[str]:
    """
    Gibt alle entdeckten Tags zurück, die keine Beschreibung haben.
    
    Returns:
        Set[str]: Menge der unbekannten Tags
    """
    discover_all_tags()  # Stelle sicher dass Discovery gelaufen ist
    return _unknown_tags_cache.copy()

def get_tag_definitions() -> Dict[str, Dict[str, Any]]:
    """
    Gibt dynamisch generierte Tag-Definitionen zurück.
    Kombiniert entdeckte Tags mit zentral verwalteten Beschreibungen.
    
    Returns:
        Dict: Tag-Definitionen mit Tool-Listen und Beschreibungen
    """
    tag_to_tools = discover_all_tags()
    definitions = {}
    
    # Erstelle Definitionen für alle entdeckten Tags
    all_tags = set(TAG_DESCRIPTIONS.keys()) | set(tag_to_tools.keys())
    
    for tag in sorted(all_tags):
        tools = sorted(list(tag_to_tools.get(tag, set())))
        
        # Hole Beschreibung oder generiere Warnung
        if tag in TAG_DESCRIPTIONS:
            description = TAG_DESCRIPTIONS[tag]
        else:
            description = f"⚠️ UNBEKANNTER TAG - Bitte Beschreibung in tag_definitions.py hinzufügen!"
            print(f"WARNING: Unbekannter Tag '{tag}' gefunden in Tools: {tools}")
        
        definitions[tag] = {
            "name": tag,
            "description": description,
            "tools": tools,
            "tool_count": len(tools),
            "is_known": tag in TAG_DESCRIPTIONS
        }
    
    return definitions

def get_tag_statistics() -> Dict[str, Any]:
    """
    Gibt Statistiken über das Tag-System zurück.
    
    Returns:
        Dict: Statistiken über Tags und Tools
    """
    tag_to_tools = discover_all_tags()
    unknown_tags = get_unknown_tags()
    
    # Zähle Tools
    all_tools = set()
    for tools in tag_to_tools.values():
        all_tools.update(tools)
    
    # Finde Tools ohne Tags
    # TODO: Das müsste man implementieren wenn nötig
    
    return {
        "total_tags": len(tag_to_tools),
        "known_tags": len(TAG_DESCRIPTIONS),
        "unknown_tags": len(unknown_tags),
        "unknown_tag_list": sorted(list(unknown_tags)),
        "total_tools": len(all_tools),
        "tags_per_tool": {
            # Könnte man berechnen wenn nötig
        },
        "most_used_tags": sorted(
            [(tag, len(tools)) for tag, tools in tag_to_tools.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
    }

def validate_tag_system() -> List[str]:
    """
    Validiert das Tag-System und gibt Warnungen zurück.
    
    Returns:
        List[str]: Liste von Warnungen
    """
    warnings = []
    unknown_tags = get_unknown_tags()
    
    if unknown_tags:
        warnings.append(f"⚠️ {len(unknown_tags)} unbekannte Tags gefunden: {sorted(unknown_tags)}")
        warnings.append("   → Bitte Beschreibungen in TAG_DESCRIPTIONS hinzufügen!")
    
    # Prüfe auf nicht verwendete Tag-Beschreibungen
    tag_to_tools = discover_all_tags()
    unused_descriptions = set(TAG_DESCRIPTIONS.keys()) - set(tag_to_tools.keys())
    
    if unused_descriptions:
        warnings.append(f"ℹ️ {len(unused_descriptions)} Tag-Beschreibungen ohne Tools: {sorted(unused_descriptions)}")
        warnings.append("   → Diese Tags werden aktuell von keinem Tool verwendet")
    
    return warnings

# ===== LEGACY SUPPORT =====

def get_tag_descriptions_legacy():
    """
    Legacy-Funktion: Gibt verfügbare Tool-Tags mit Beschreibungen zurück.
    
    HINWEIS: Diese Funktion ist überholt. Verwende stattdessen get_tag_definitions()
    """
    # Generiere aus neuer Struktur
    definitions = get_tag_definitions()
    legacy_dict = {}
    
    for tag, info in definitions.items():
        legacy_dict[tag] = info['description']
    
    return legacy_dict

# ===== INITIALISIERUNG =====

# Beim Import: Validiere das System einmal
# DEAKTIVIERT: Vermeidet mehrfaches Laden aller Tools beim Server-Start
# if __name__ != "__main__":
#     # Nur wenn als Modul importiert
#     try:
#         warnings = validate_tag_system()
#         if warnings:
#             print("\n🏷️ TAG-SYSTEM VALIDIERUNG:")
#             for warning in warnings:
#                 print(warning)
#             print("")
#     except Exception as e:
#         # Fehler beim Validieren sollten nicht das System blockieren
#         print(f"⚠️ Tag-System Validierung fehlgeschlagen: {e}")
        
# ===== TEST-FUNKTION =====

if __name__ == "__main__":
    # Test das System
    print("🏷️ TAG-SYSTEM TEST")
    print("=" * 50)
    
    # Zeige alle Tags
    definitions = get_tag_definitions()
    print(f"\n📊 Gefundene Tags: {len(definitions)}")
    
    for tag, info in definitions.items():
        status = "✅" if info['is_known'] else "⚠️"
        print(f"{status} {tag}: {info['tool_count']} Tools")
        print(f"   → {info['description']}")
        if info['tools']:
            print(f"   → Tools: {', '.join(info['tools'][:5])}")
            if len(info['tools']) > 5:
                print(f"            ... und {len(info['tools']) - 5} weitere")
        print()
    
    # Zeige Statistiken
    print("\n📈 STATISTIKEN:")
    stats = get_tag_statistics()
    print(f"Gesamt Tags: {stats['total_tags']}")
    print(f"Bekannte Tags: {stats['known_tags']}")
    print(f"Unbekannte Tags: {stats['unknown_tags']}")
    if stats['unknown_tag_list']:
        print(f"   → {stats['unknown_tag_list']}")
    print(f"Gesamt Tools: {stats['total_tools']}")
    
    print("\n🔝 TOP 10 TAGS:")
    for tag, count in stats['most_used_tags']:
        print(f"   {tag}: {count} Tools")
    
    # Zeige Warnungen
    warnings = validate_tag_system()
    if warnings:
        print("\n⚠️ WARNUNGEN:")
        for warning in warnings:
            print(warning) 