#!/usr/bin/env python3
"""
Engineering Tool Tag Manager - Web Interface

Ein komfortables Web-GUI für die Verwaltung von Tool-Tags.

Features:
- Tag-Übersicht aller Engineering-Tools
- Einzelne und Bulk-Tag-Bearbeitung
- Sortierung und Filterung
- Preview-Modus vor Änderungen
- Backup-Funktionalität

Usage:
    python tag_manager_web.py
    # Öffnet http://localhost:5000
"""

import os
import sys
import json
import shutil
import re
from datetime import datetime
from typing import Dict, List, Set, Any, Tuple
from pathlib import Path

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

# Füge das Projekt-Root zum Python-Pfad hinzu
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from engineering_mcp.tag_definitions import discover_all_tags, get_tag_definitions, TAG_DESCRIPTIONS
except ImportError as e:
    print(f"ERROR: Kann Engineering MCP Module nicht importieren: {e}")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'engineering_tag_manager_2025'

# Globale Konfiguration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(PROJECT_ROOT, 'tools')
BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'backups')

def ensure_backup_dir():
    """Stelle sicher dass das Backup-Verzeichnis existiert."""
    os.makedirs(BACKUP_DIR, exist_ok=True)

def create_backup(file_path: str) -> str:
    """
    Erstellt ein Backup einer Datei.
    
    Returns:
        str: Pfad zur Backup-Datei
    """
    ensure_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rel_path = os.path.relpath(file_path, PROJECT_ROOT)
    backup_name = f"{rel_path.replace(os.sep, '_')}_{timestamp}.bak"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    shutil.copy2(file_path, backup_path)
    return backup_path

def find_python_files(directory: str) -> List[str]:
    """
    Findet alle Python-Dateien in einem Verzeichnis.
    
    Args:
        directory: Verzeichnis zum Durchsuchen
        
    Returns:
        List[str]: Liste der Python-Dateipfade
    """
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Überspringe __pycache__ etc.
        dirs[:] = [d for d in dirs if not d.startswith('__')]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def parse_tool_tags_from_file(file_path: str) -> Tuple[List[str], int, int]:
    """
    Extrahiert TOOL_TAGS aus einer Python-Datei.
    
    Args:
        file_path: Pfad zur Python-Datei
        
    Returns:
        Tuple[List[str], int, int]: (tags, start_line, end_line)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Suche nach TOOL_TAGS = [...]
        in_tool_tags = False
        start_line = -1
        end_line = -1
        tags = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if 'TOOL_TAGS' in stripped and '=' in stripped:
                start_line = i + 1  # 1-basiert
                in_tool_tags = True
                
                # Prüfe ob alles in einer Zeile steht
                if '[' in stripped and ']' in stripped:
                    # Einzeilige Definition
                    end_line = i + 1
                    tag_content = stripped.split('=', 1)[1].strip()
                    tags = extract_tags_from_string(tag_content)
                    break
                elif '[' in stripped:
                    # Mehrzeilige Definition beginnt
                    continue
            
            elif in_tool_tags:
                if ']' in stripped:
                    # Ende der mehrzeiligen Definition
                    end_line = i + 1
                    break
        
        # Wenn mehrzeilig, extrahiere alle Tags
        if start_line != -1 and end_line != -1 and start_line != end_line:
            tag_lines = lines[start_line-1:end_line]
            tag_content = ' '.join(tag_lines)
            tags = extract_tags_from_string(tag_content)
        
        return tags, start_line, end_line
        
    except Exception as e:
        print(f"Fehler beim Parsen von {file_path}: {e}")
        return [], -1, -1

def extract_tags_from_string(content: str) -> List[str]:
    """
    Extrahiert Tags aus einem String wie 'TOOL_TAGS = ["tag1", "tag2"]'.
    
    Args:
        content: String-Inhalt
        
    Returns:
        List[str]: Extrahierte Tags
    """
    try:
        # Entferne TOOL_TAGS = und finde die Liste
        if 'TOOL_TAGS' in content:
            content = content.split('=', 1)[1]
        
        # Finde alle Strings in Anführungszeichen
        pattern = r'["\']([^"\']+)["\']'
        matches = re.findall(pattern, content)
        
        return [match.strip() for match in matches if match.strip()]
        
    except Exception as e:
        print(f"Fehler beim Extrahieren der Tags: {e}")
        return []

def update_tool_tags_in_file(file_path: str, new_tags: List[str], dry_run: bool = False) -> bool:
    """
    Aktualisiert TOOL_TAGS in einer Python-Datei.
    
    Args:
        file_path: Pfad zur Python-Datei
        new_tags: Neue Tags
        dry_run: Nur simulieren, nicht schreiben
        
    Returns:
        bool: Erfolg
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        current_tags, start_line, end_line = parse_tool_tags_from_file(file_path)
        
        # Formatiere neue Tags
        if new_tags:
            new_tag_line = f'TOOL_TAGS = {json.dumps(new_tags, ensure_ascii=False)}'
        else:
            new_tag_line = 'TOOL_TAGS = []'
        
        if start_line != -1 and end_line != -1:
            # Ersetze bestehende TOOL_TAGS
            new_lines = lines[:start_line-1] + [new_tag_line] + lines[end_line:]
        else:
            # Füge TOOL_TAGS hinzu (nach Imports, vor ersten Funktionen)
            insert_pos = find_insert_position(lines)
            new_lines = lines[:insert_pos] + ['', new_tag_line, ''] + lines[insert_pos:]
        
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
        
        return True
        
    except Exception as e:
        print(f"Fehler beim Aktualisieren von {file_path}: {e}")
        return False

def find_insert_position(lines: List[str]) -> int:
    """
    Findet die beste Position zum Einfügen von TOOL_TAGS.
    
    Args:
        lines: Zeilen der Datei
        
    Returns:
        int: Position zum Einfügen
    """
    # Suche nach dem Ende der Imports
    last_import = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(('import ', 'from ')) and not stripped.startswith('#'):
            last_import = i
    
    # Füge nach Imports ein, aber vor ersten Funktionen/Klassen
    if last_import != -1:
        return last_import + 1
    
    # Fallback: Nach Docstring/Kommentaren am Anfang
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
            return i
    
    return 0

def parse_tool_metadata_from_file(file_path: str) -> Dict[str, Any]:
    """
    Extrahiert alle Metadaten aus einer Tool-Datei.
    
    Args:
        file_path: Pfad zur Python-Datei
        
    Returns:
        Dict[str, Any]: Extrahierte Metadaten
    """
    metadata = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Metadaten-Pattern definieren
        patterns = {
            'tool_metadata': r'TOOL_METADATA\s*=\s*(\{.*?\})',
            'tool_description': r'TOOL_DESCRIPTION\s*=\s*["\']([^"\']*)["\']',
            'tool_category': r'TOOL_CATEGORY\s*=\s*["\']([^"\']*)["\']',
            'has_solving': r'HAS_SOLVING\s*=\s*["\']([^"\']*)["\']',
            'norm_foundation': r'NORM_FOUNDATION\s*=\s*["\']([^"\']*)["\']',
            'knowledge_foundation': r'KNOWLEDGE_FOUNDATION\s*=\s*["\']([^"\']*)["\']'
        }
        
        # Extrahiere einfache String-Metadaten
        for key, pattern in patterns.items():
            if key == 'tool_metadata':
                continue  # Spezialbehandlung für TOOL_METADATA
                
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                metadata[key] = match.group(1).strip()
        
        # Spezialbehandlung für TOOL_METADATA (Dictionary)
        tool_metadata_match = re.search(patterns['tool_metadata'], content, re.MULTILINE | re.DOTALL)
        if tool_metadata_match:
            try:
                # Versuche das Dictionary zu parsen
                metadata_str = tool_metadata_match.group(1)
                # Einfache Extraktion der Key-Value-Paare
                dict_content = extract_dict_content(metadata_str)
                metadata.update(dict_content)
            except Exception as e:
                metadata['tool_metadata_raw'] = tool_metadata_match.group(1)
        
        # Zusätzliche Pattern für andere Metadaten
        additional_patterns = {
            'version': r'__version__\s*=\s*["\']([^"\']*)["\']',
            'author': r'__author__\s*=\s*["\']([^"\']*)["\']',
            'date': r'__date__\s*=\s*["\']([^"\']*)["\']'
        }
        
        for key, pattern in additional_patterns.items():
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                metadata[key] = match.group(1).strip()
                
    except Exception as e:
        print(f"Fehler beim Extrahieren der Metadaten aus {file_path}: {e}")
    
    return metadata

def extract_dict_content(dict_str: str) -> Dict[str, Any]:
    """
    Extrahiert Key-Value-Paare aus einem Dictionary-String.
    
    Args:
        dict_str: String-Repräsentation eines Dictionary
        
    Returns:
        Dict[str, Any]: Extrahierte Key-Value-Paare
    """
    result = {}
    
    try:
        # Entferne äußere Klammern
        dict_str = dict_str.strip()
        if dict_str.startswith('{'):
            dict_str = dict_str[1:]
        if dict_str.endswith('}'):
            dict_str = dict_str[:-1]
        
        # Einfache Extraktion von "key": "value" Paaren
        pairs = re.findall(r'["\']([^"\']+)["\']\s*:\s*["\']([^"\']+)["\']', dict_str)
        for key, value in pairs:
            result[key] = value
        
        # Extraktion von "key": non-string values
        non_string_pairs = re.findall(r'["\']([^"\']+)["\']\s*:\s*([^,}]+)', dict_str)
        for key, value in non_string_pairs:
            value = value.strip()
            if value not in result.get(key, ''):  # Vermeide Duplikate
                if value.isdigit():
                    result[key] = int(value)
                elif value.lower() in ('true', 'false'):
                    result[key] = value.lower() == 'true'
                elif not any(char in value for char in ['"', "'"]):  # Kein String
                    result[key] = value
                    
    except Exception as e:
        print(f"Fehler beim Parsen des Dictionary-Strings: {e}")
    
    return result

def update_tool_metadata_in_file(file_path: str, new_metadata: Dict[str, Any], dry_run: bool = False) -> bool:
    """
    Aktualisiert Metadaten in einer Python-Datei.
    
    Args:
        file_path: Pfad zur Python-Datei
        new_metadata: Neue Metadaten
        dry_run: Nur simulieren, nicht schreiben
        
    Returns:
        bool: Erfolg
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        modified = False
        
        # Aktualisiere jedes Metadaten-Feld
        for key, value in new_metadata.items():
            if key in ['tool_metadata_raw']:
                continue  # Überspringe interne Felder
                
            # Pattern für das spezifische Feld
            if key == 'tool_metadata':
                # Spezialbehandlung für TOOL_METADATA Dictionary
                pattern = r'(TOOL_METADATA\s*=\s*)\{.*?\}'
                replacement = f'\\1{format_metadata_dict(value)}'
            else:
                # Standard String-Felder
                field_name = key.upper()
                pattern = f'({field_name}\\s*=\\s*)["\'][^"\']*["\']'
                replacement = f'\\1"{value}"'
            
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            if new_content != content:
                content = new_content
                modified = True
        
        if modified and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return modified
        
    except Exception as e:
        print(f"Fehler beim Aktualisieren der Metadaten in {file_path}: {e}")
        return False

def format_metadata_dict(metadata: Dict[str, Any]) -> str:
    """
    Formatiert Metadaten als Python-Dictionary-String.
    
    Args:
        metadata: Metadaten-Dictionary
        
    Returns:
        str: Formatierter Dictionary-String
    """
    items = []
    for key, value in metadata.items():
        if isinstance(value, str):
            items.append(f'    "{key}": "{value}"')
        elif isinstance(value, bool):
            items.append(f'    "{key}": {str(value).lower()}')
        elif isinstance(value, (int, float)):
            items.append(f'    "{key}": {value}')
        else:
            items.append(f'    "{key}": "{str(value)}"')
    
    return "{\n" + ",\n".join(items) + "\n}"

def get_all_tools_with_details() -> Dict[str, Dict]:
    """
    Sammelt alle Tool-Details aus dem /tools Verzeichnis.
    
    Returns:
        Dict: tool_name -> tool_details
    """
    tools_data = {}
    
    # Durchsuche alle Python-Dateien
    for root, dirs, files in os.walk(TOOLS_DIR):
        # Überspringe __pycache__ etc.
        dirs[:] = [d for d in dirs if not d.startswith('__')]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, PROJECT_ROOT)
                
                # Extrahiere aktuelle Tags
                current_tags, start_line, end_line = parse_tool_tags_from_file(file_path)
                
                # Extrahiere Metadaten
                metadata = parse_tool_metadata_from_file(file_path)
                
                # Bestimme Kategorie aus Pfad (inklusive Unterordner)
                path_parts = Path(rel_path).parts
                if len(path_parts) > 2:
                    # Erstelle vollständigen Kategorie-Pfad: tools/geometry/Flaechen/tool.py -> geometry/Flaechen
                    category_parts = path_parts[1:-1]  # Alles außer 'tools' am Anfang und 'tool.py' am Ende
                    category = '/'.join(category_parts)
                else:
                    category = 'unknown'
                
                # Erstelle eindeutigen Tool-Namen
                base_name = file[:-3]  # Entferne .py
                
                # Bei Namenskonflikten: verwende Kategorie als Präfix
                if base_name in tools_data:
                    # Konflikt! Erstelle eindeutige Namen
                    existing_tool = tools_data[base_name]
                    existing_category = existing_tool['category'].replace('/', '_')
                    current_category = category.replace('/', '_')
                    
                    # Benenne existierendes Tool um
                    old_key = base_name
                    new_existing_key = f"{existing_category}_{base_name}"
                    tools_data[new_existing_key] = existing_tool
                    tools_data[new_existing_key]['name'] = new_existing_key
                    tools_data[new_existing_key]['display_name'] = f"{base_name} ({existing_tool['category']})"
                    del tools_data[old_key]
                    
                    # Neuer Name für aktuelles Tool
                    tool_name = f"{current_category}_{base_name}"
                    display_name = f"{base_name} ({category})"
                else:
                    tool_name = base_name
                    display_name = base_name
                
                tools_data[tool_name] = {
                    'name': tool_name,
                    'display_name': display_name,
                    'base_name': base_name,
                    'file_path': file_path,
                    'relative_path': rel_path,
                    'category': category,
                    'current_tags': current_tags,
                    'has_tool_tags': start_line != -1,
                    'metadata': metadata,
                    'line_info': {
                        'start': start_line,
                        'end': end_line
                    }
                }
    
    return tools_data

def get_all_available_tags() -> Dict[str, str]:
    """
    Gibt alle verfügbaren Tags mit Beschreibungen zurück.
    
    Returns:
        Dict: tag_name -> description
    """
    # Hole definierte Tags
    defined_tags = TAG_DESCRIPTIONS.copy()
    
    # Hole aktuelle Tags aus Tools
    discovered_tags = discover_all_tags()
    
    # Kombiniere
    all_tags = {}
    for tag in set(defined_tags.keys()) | set(discovered_tags.keys()):
        description = defined_tags.get(tag, "⚠️ Keine Beschreibung vorhanden")
        all_tags[tag] = description
    
    return all_tags

@app.route('/')
def index():
    """Haupt-Dashboard mit Tool-Übersicht."""
    try:
        tools_data = get_all_tools_with_details()
        available_tags = get_all_available_tags()
        
        # Statistiken berechnen
        stats = {
            'total_tools': len(tools_data),
            'tools_with_tags': len([t for t in tools_data.values() if t['current_tags']]),
            'tools_without_tags': len([t for t in tools_data.values() if not t['current_tags']]),
            'total_tags': len(available_tags),
            'categories': len(set(t['category'] for t in tools_data.values()))
        }
        
        return render_template('index.html', 
                             tools=tools_data, 
                             available_tags=available_tags,
                             stats=stats)
    except Exception as e:
        flash(f'Fehler beim Laden der Tool-Daten: {str(e)}', 'error')
        return render_template('index.html', tools={}, available_tags={}, stats={})

@app.route('/api/tools')
def api_tools():
    """API-Endpoint für Tool-Daten (für AJAX)."""
    try:
        tools_data = get_all_tools_with_details()
        
        # Sortierung
        sort_by = request.args.get('sort', 'name')
        sort_order = request.args.get('order', 'asc')
        
        # Filter
        category_filter = request.args.get('category', '')
        tag_filter = request.args.get('tag', '')
        
        # Filtern
        filtered_tools = tools_data.copy()
        
        if category_filter:
            filtered_tools = {
                name: data for name, data in filtered_tools.items()
                if data['category'] == category_filter
            }
        
        if tag_filter:
            filtered_tools = {
                name: data for name, data in filtered_tools.items()
                if tag_filter in data['current_tags']
            }
        
        # Sortieren
        def sort_key(item):
            name, data = item
            if sort_by == 'name':
                return name.lower()
            elif sort_by == 'category':
                return data['category'].lower()
            elif sort_by == 'tags':
                return len(data['current_tags'])
            elif sort_by == 'tag_names':
                return ', '.join(sorted(data['current_tags'])).lower()
            return name.lower()
        
        sorted_items = sorted(filtered_tools.items(), key=sort_key, 
                            reverse=(sort_order == 'desc'))
        
        # Konvertiere zurück zu Dict aber behalte Reihenfolge
        result = {name: data for name, data in sorted_items}
        
        return jsonify({
            'tools': result,
            'count': len(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/edit/<tool_name>')
def edit_tool(tool_name):
    """Einzelnes Tool bearbeiten."""
    try:
        tools_data = get_all_tools_with_details()
        
        if tool_name not in tools_data:
            flash(f'Tool "{tool_name}" nicht gefunden', 'error')
            return redirect(url_for('index'))
        
        tool_data = tools_data[tool_name]
        available_tags = get_all_available_tags()
        
        return render_template('edit_tool.html', 
                             tool=tool_data, 
                             available_tags=available_tags)
    except Exception as e:
        flash(f'Fehler beim Laden von Tool "{tool_name}": {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/bulk_edit')
def bulk_edit():
    """Bulk-Editor für mehrere Tools."""
    try:
        # Tool-Namen aus Query-Parameter
        tool_names = request.args.getlist('tools')
        
        if not tool_names:
            flash('Keine Tools für Bulk-Bearbeitung ausgewählt', 'warning')
            return redirect(url_for('index'))
        
        tools_data = get_all_tools_with_details()
        selected_tools = {
            name: tools_data[name] for name in tool_names 
            if name in tools_data
        }
        
        if not selected_tools:
            flash('Keine gültigen Tools für Bulk-Bearbeitung gefunden', 'error')
            return redirect(url_for('index'))
        
        available_tags = get_all_available_tags()
        
        # Gemeinsame Tags finden
        common_tags = set()
        if selected_tools:
            tool_values = list(selected_tools.values())
            common_tags = set(tool_values[0]['current_tags'])
            for tool_data in tool_values[1:]:
                common_tags &= set(tool_data['current_tags'])
        
        return render_template('bulk_edit.html', 
                             tools=selected_tools,
                             available_tags=available_tags,
                             common_tags=sorted(common_tags))
    except Exception as e:
        flash(f'Fehler beim Bulk-Editor: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/update_tool', methods=['POST'])
def api_update_tool():
    """API-Endpoint zum Aktualisieren eines einzelnen Tools."""
    try:
        data = request.get_json()
        tool_name = data.get('tool_name')
        new_tags = data.get('tags', [])
        create_backup_flag = data.get('create_backup', True)
        
        if not tool_name:
            return jsonify({'error': 'Tool-Name fehlt'}), 400
        
        tools_data = get_all_tools_with_details()
        if tool_name not in tools_data:
            return jsonify({'error': f'Tool "{tool_name}" nicht gefunden'}), 404
        
        tool_data = tools_data[tool_name]
        file_path = tool_data['file_path']
        
        # Backup erstellen
        backup_path = None
        if create_backup_flag:
            backup_path = create_backup(file_path)
        
        # Tags aktualisieren
        success = update_tool_tags_in_file(file_path, new_tags, dry_run=False)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Tags für "{tool_name}" erfolgreich aktualisiert',
                'backup_path': backup_path,
                'old_tags': tool_data['current_tags'],
                'new_tags': new_tags
            })
        else:
            return jsonify({'error': 'Fehler beim Aktualisieren der Tags'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bulk_update', methods=['POST'])
def api_bulk_update():
    """API-Endpoint für Bulk-Updates."""
    try:
        data = request.get_json()
        tool_names = data.get('tool_names', [])
        operation = data.get('operation')  # 'add', 'remove', 'replace'
        tags = data.get('tags', [])
        create_backup_flag = data.get('create_backup', True)
        
        if not tool_names:
            return jsonify({'error': 'Keine Tools ausgewählt'}), 400
        
        if not operation or not tags:
            return jsonify({'error': 'Operation und Tags sind erforderlich'}), 400
        
        tools_data = get_all_tools_with_details()
        results = []
        
        for tool_name in tool_names:
            if tool_name not in tools_data:
                results.append({
                    'tool': tool_name,
                    'success': False,
                    'error': 'Tool nicht gefunden'
                })
                continue
            
            tool_data = tools_data[tool_name]
            file_path = tool_data['file_path']
            current_tags = set(tool_data['current_tags'])
            
            # Berechne neue Tags basierend auf Operation
            if operation == 'add':
                new_tags = list(current_tags | set(tags))
            elif operation == 'remove':
                new_tags = list(current_tags - set(tags))
            elif operation == 'replace':
                new_tags = tags
            else:
                results.append({
                    'tool': tool_name,
                    'success': False,
                    'error': 'Unbekannte Operation'
                })
                continue
            
            # Backup erstellen
            backup_path = None
            if create_backup_flag:
                try:
                    backup_path = create_backup(file_path)
                except Exception as e:
                    results.append({
                        'tool': tool_name,
                        'success': False,
                        'error': f'Backup-Fehler: {str(e)}'
                    })
                    continue
            
            # Tags aktualisieren
            success = update_tool_tags_in_file(file_path, new_tags, dry_run=False)
            
            results.append({
                'tool': tool_name,
                'success': success,
                'old_tags': list(current_tags),
                'new_tags': new_tags,
                'backup_path': backup_path,
                'error': None if success else 'Fehler beim Aktualisieren'
            })
        
        successful_updates = len([r for r in results if r['success']])
        
        return jsonify({
            'success': True,
            'message': f'{successful_updates} von {len(tool_names)} Tools erfolgreich aktualisiert',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/edit_metadata/<tool_name>')
def edit_metadata(tool_name):
    """Metadaten eines einzelnen Tools bearbeiten."""
    try:
        tools_data = get_all_tools_with_details()
        
        if tool_name not in tools_data:
            flash(f'Tool "{tool_name}" nicht gefunden', 'error')
            return redirect(url_for('index'))
        
        tool_data = tools_data[tool_name]
        
        return render_template('edit_metadata.html', 
                             tool=tool_data)
    except Exception as e:
        flash(f'Fehler beim Laden der Metadaten von Tool "{tool_name}": {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/bulk_edit_metadata')
def bulk_edit_metadata():
    """Bulk-Editor für Metadaten mehrerer Tools."""
    try:
        # Tool-Namen aus Query-Parameter
        tool_names = request.args.getlist('tools')
        
        if not tool_names:
            flash('Keine Tools für Bulk-Metadaten-Bearbeitung ausgewählt', 'warning')
            return redirect(url_for('index'))
        
        tools_data = get_all_tools_with_details()
        selected_tools = {
            name: tools_data[name] for name in tool_names 
            if name in tools_data
        }
        
        if not selected_tools:
            flash('Keine gültigen Tools für Bulk-Metadaten-Bearbeitung gefunden', 'error')
            return redirect(url_for('index'))
        
        # Gemeinsame Metadaten-Schlüssel finden
        common_metadata_keys = set()
        if selected_tools:
            tool_values = list(selected_tools.values())
            if tool_values[0]['metadata']:
                common_metadata_keys = set(tool_values[0]['metadata'].keys())
                for tool_data in tool_values[1:]:
                    if tool_data['metadata']:
                        common_metadata_keys &= set(tool_data['metadata'].keys())
        
        return render_template('bulk_edit_metadata.html', 
                             tools=selected_tools,
                             common_metadata_keys=sorted(common_metadata_keys))
    except Exception as e:
        flash(f'Fehler beim Bulk-Metadaten-Editor: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/update_metadata', methods=['POST'])
def api_update_metadata():
    """API-Endpoint zum Aktualisieren der Metadaten eines einzelnen Tools."""
    try:
        data = request.get_json()
        tool_name = data.get('tool_name')
        new_metadata = data.get('metadata', {})
        create_backup_flag = data.get('create_backup', True)
        
        if not tool_name:
            return jsonify({'error': 'Tool-Name fehlt'}), 400
        
        tools_data = get_all_tools_with_details()
        if tool_name not in tools_data:
            return jsonify({'error': f'Tool "{tool_name}" nicht gefunden'}), 404
        
        tool_data = tools_data[tool_name]
        file_path = tool_data['file_path']
        
        # Backup erstellen
        backup_path = None
        if create_backup_flag:
            backup_path = create_backup(file_path)
        
        # Metadaten aktualisieren
        success = update_tool_metadata_in_file(file_path, new_metadata, dry_run=False)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Metadaten für "{tool_name}" erfolgreich aktualisiert',
                'backup_path': backup_path,
                'old_metadata': tool_data['metadata'],
                'new_metadata': new_metadata
            })
        else:
            return jsonify({'error': 'Fehler beim Aktualisieren der Metadaten'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bulk_update_metadata', methods=['POST'])
def api_bulk_update_metadata():
    """API-Endpoint für Bulk-Updates von Metadaten."""
    try:
        data = request.get_json()
        tool_names = data.get('tool_names', [])
        operation = data.get('operation')  # 'update', 'add_field', 'remove_field'
        metadata = data.get('metadata', {})
        create_backup_flag = data.get('create_backup', True)
        
        if not tool_names:
            return jsonify({'error': 'Keine Tools ausgewählt'}), 400
        
        if not operation:
            return jsonify({'error': 'Operation ist erforderlich'}), 400
        
        tools_data = get_all_tools_with_details()
        results = []
        
        for tool_name in tool_names:
            if tool_name not in tools_data:
                results.append({
                    'tool': tool_name,
                    'success': False,
                    'error': 'Tool nicht gefunden'
                })
                continue
            
            tool_data = tools_data[tool_name]
            file_path = tool_data['file_path']
            current_metadata = tool_data['metadata'] or {}
            
            # Berechne neue Metadaten basierend auf Operation
            if operation == 'update':
                new_metadata = {**current_metadata, **metadata}
            elif operation == 'add_field':
                new_metadata = {**current_metadata, **metadata}
            elif operation == 'remove_field':
                new_metadata = {k: v for k, v in current_metadata.items() 
                              if k not in metadata.keys()}
            else:
                results.append({
                    'tool': tool_name,
                    'success': False,
                    'error': 'Unbekannte Operation'
                })
                continue
            
            # Backup erstellen
            backup_path = None
            if create_backup_flag:
                try:
                    backup_path = create_backup(file_path)
                except Exception as e:
                    results.append({
                        'tool': tool_name,
                        'success': False,
                        'error': f'Backup-Fehler: {str(e)}'
                    })
                    continue
            
            # Metadaten aktualisieren
            success = update_tool_metadata_in_file(file_path, new_metadata, dry_run=False)
            
            results.append({
                'tool': tool_name,
                'success': success,
                'old_metadata': current_metadata,
                'new_metadata': new_metadata,
                'backup_path': backup_path,
                'error': None if success else 'Fehler beim Aktualisieren'
            })
        
        successful_updates = len([r for r in results if r['success']])
        
        return jsonify({
            'success': True,
            'message': f'{successful_updates} von {len(tool_names)} Tools erfolgreich aktualisiert',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/available_tags')
def api_available_tags():
    """API-Endpoint für verfügbare Tags."""
    try:
        available_tags = get_all_available_tags()
        return jsonify(available_tags)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tag_stats')
def api_tag_stats():
    """API-Endpoint für Tag-Statistiken in der Navigation."""
    try:
        available_tags = get_all_available_tags()
        tag_usage = discover_all_tags()
        
        total_tags = len(available_tags)
        defined_tags = len([tag for tag in available_tags.keys() if tag in TAG_DESCRIPTIONS])
        undefined_tags = len([tag for tag in available_tags.keys() if tag not in TAG_DESCRIPTIONS])
        unused_tags = len([tag for tag in available_tags.keys() if tag not in tag_usage or len(tag_usage.get(tag, set())) == 0])
        
        return jsonify({
            'success': True,
            'total': total_tags,
            'defined': defined_tags,
            'undefined': undefined_tags,
            'unused': unused_tags
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/tag_definitions')
def tag_definitions():
    """Tag-Definitionen verwalten."""
    try:
        available_tags = get_all_available_tags()
        tag_usage = discover_all_tags()
        
        # Kombiniere Informationen
        tag_info = {}
        for tag, description in available_tags.items():
            tools_using_tag = list(tag_usage.get(tag, set()))
            tag_info[tag] = {
                'name': tag,
                'description': description,
                'tools': tools_using_tag,
                'usage_count': len(tools_using_tag),
                'is_defined': tag in TAG_DESCRIPTIONS
            }
        
        return render_template('tag_definitions.html', tags=tag_info)
    except Exception as e:
        flash(f'Fehler beim Laden der Tag-Definitionen: {str(e)}', 'error')
        return render_template('tag_definitions.html', tags={})

@app.route('/backups')
def backups():
    """Backup-Verwaltung."""
    try:
        ensure_backup_dir()
        backup_files = []
        
        if os.path.exists(BACKUP_DIR):
            for file in os.listdir(BACKUP_DIR):
                if file.endswith('.bak'):
                    file_path = os.path.join(BACKUP_DIR, file)
                    stat = os.stat(file_path)
                    backup_files.append({
                        'name': file,
                        'path': file_path,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'modified': datetime.fromtimestamp(stat.st_mtime)
                    })
        
        # Sortiere nach Erstellungsdatum (neueste zuerst)
        backup_files.sort(key=lambda x: x['created'], reverse=True)
        
        return render_template('backups.html', backups=backup_files)
    except Exception as e:
        flash(f'Fehler beim Laden der Backups: {str(e)}', 'error')
        return render_template('backups.html', backups=[])

if __name__ == '__main__':
    print("🏷️ Engineering Tool Tag Manager - Web Interface")
    print("=" * 60)
    print(f"📁 Tools-Verzeichnis: {TOOLS_DIR}")
    print(f"💾 Backup-Verzeichnis: {BACKUP_DIR}")
    print("🌐 Web-Interface startet auf: http://localhost:5000")
    print("=" * 60)
    
    # Entwicklungsmodus
    app.run(host='0.0.0.0', port=5000, debug=True) 