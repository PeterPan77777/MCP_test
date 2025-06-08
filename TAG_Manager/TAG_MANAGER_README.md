# Engineering Tool Tag Manager - Web Interface

Ein komfortables Web-GUI für die Verwaltung von Tool-Tags im Engineering MCP Server.

## 🚀 Schnellstart

```bash
# 1. In das TAG_Manager Verzeichnis wechseln
cd TAG_Manager/

# 2. Tag Manager starten (installiert automatisch Abhängigkeiten)
python start_tag_manager.py

# 3. Browser öffnen
# → http://localhost:5000
```

## 📋 Features

### 🏠 Dashboard (Hauptseite)
- **Tool-Übersicht**: Alle Engineering-Tools mit aktuellen Tags
- **Filterung**: Nach Kategorie, Tags oder Suchtext
- **Sortierung**: Nach Name, Kategorie, Anzahl Tags oder Tag-Namen
- **Ansichten**: Tabellen- oder Karten-Ansicht
- **Bulk-Auswahl**: Mehrere Tools gleichzeitig auswählen
- **Statistiken**: Live-Übersicht über Tools und Tags

### ✏️ Einzelne Tool-Bearbeitung
- **Tag-Editor**: Intuitive Tag-Verwaltung pro Tool
- **Tag-Vorschläge**: Alle verfügbaren Tags mit Beschreibungen
- **Neue Tags**: Direkte Eingabe neuer Tags möglich
- **Vorschau**: Änderungen vor dem Speichern anzeigen
- **Backup**: Automatische Backup-Erstellung

### 📦 Bulk-Bearbeitung
- **Mehrere Tools**: Gleichzeitige Bearbeitung ausgewählter Tools
- **Drei Operationen**:
  - **Hinzufügen**: Tags zu bestehenden hinzufügen
  - **Entfernen**: Bestimmte Tags von allen Tools entfernen
  - **Ersetzen**: Alle Tags durch neue ersetzen (⚠️ Achtung!)
- **Gemeinsame Tags**: Anzeige der in allen Tools vorhandenen Tags
- **Vorschau**: Detaillierte Übersicht aller Änderungen
- **Batch-Backup**: Backups für alle geänderten Dateien

### 📖 Tag-Definitionen
- **Übersicht**: Alle Tags mit Beschreibungen und Verwendung
- **Status-Anzeige**: 
  - ✅ **Definiert**: Hat Beschreibung in `TAG_DESCRIPTIONS`
  - ⚠️ **Undefiniert**: Wird verwendet, aber keine Beschreibung
  - 📊 **Ungenutzt**: Hat Beschreibung, wird aber nicht verwendet
- **Filter**: Nach Status oder Suchtext
- **Tool-Zuordnung**: Welche Tools verwenden welchen Tag

### 💾 Backup-Verwaltung
- **Backup-Übersicht**: Alle automatisch erstellten Backups
- **Metadaten**: Erstellungszeit, Dateigröße, ursprüngliches Tool
- **Aktionen**: Anzeigen, Herunterladen, Löschen
- **Cleanup**: Automatisches Löschen alter Backups
- **Bulk-Löschung**: Mehrere Backups gleichzeitig löschen

## 🔧 Installation & Setup

### Automatische Installation
```bash
# Startet automatisch und installiert Abhängigkeiten bei Bedarf
python start_tag_manager.py
```

### Manuelle Installation
```bash
# Web-Abhängigkeiten installieren
pip install -r requirements_web.txt

# Tag Manager direkt starten
python tag_manager_web.py
```

### Abhängigkeiten
- **Flask 3.0.0**: Web-Framework
- **Bootstrap 5.3**: Frontend-Framework (über CDN)
- **Bootstrap Icons**: Icon-Set (über CDN)

## 📁 Dateistruktur

```
TAG_Manager/
├── tag_manager_web.py          # Haupt-Flask-Anwendung
├── start_tag_manager.py        # Start-Script mit Auto-Installation
├── requirements_web.txt        # Web-Abhängigkeiten
├── templates/                  # HTML-Templates
│   ├── base.html              # Basis-Template mit Navigation
│   ├── index.html             # Dashboard/Hauptseite
│   ├── edit_tool.html         # Einzelnes Tool bearbeiten
│   ├── bulk_edit.html         # Bulk-Bearbeitung
│   ├── tag_definitions.html   # Tag-Definitionen verwalten
│   └── backups.html           # Backup-Verwaltung
├── backups/                   # Automatische Backups (wird erstellt)
└── TAG_MANAGER_README.md      # Diese Dokumentation
```

## 🎯 Workflow-Beispiele

### Neues Tag zu mehreren Tools hinzufügen
1. **Dashboard** → Tools auswählen → **"Bearbeiten"**
2. **Bulk-Edit** → Operation: **"Tags hinzufügen"**
3. **Tag auswählen** oder **neuen Tag eingeben**
4. **Vorschau** → **"Jetzt anwenden"**

### Tool-Tags bereinigen
1. **Dashboard** → **einzelnes Tool** → **"Bearbeiten"**
2. **Ungewünschte Tags** mit ❌ entfernen
3. **Neue Tags** aus Vorschlägen hinzufügen
4. **Vorschau** → **"Speichern"**

### Tag-System validieren
1. **Tag-Definitionen** → **Undefinierte Tags** finden
2. **tag_definitions.py** bearbeiten → Beschreibungen hinzufügen
3. **Tag Manager** → **"Aktualisieren"**

## ⚙️ Konfiguration

### Server-Einstellungen
```python
# In tag_manager_web.py anpassen:
app.run(
    host='0.0.0.0',    # Alle IPs (LAN-Zugriff)
    port=5000,         # Port ändern falls belegt
    debug=True         # Produktiv: False
)
```

### Backup-Verhalten
```python
# Backup-Verzeichnis ändern:
BACKUP_DIR = os.path.join(PROJECT_ROOT, 'meine_backups')

# Automatische Backups deaktivieren:
create_backup_flag = False  # In API-Calls
```

## 🔒 Sicherheitshinweise

- **Entwicklungsmodus**: Debug-Modus nur für Entwicklung
- **Lokaler Zugriff**: Standardmäßig nur localhost
- **Backup-Schutz**: Backups vor Änderungen erstellen
- **Netzwerk**: Firewall beachten bei LAN-Zugriff

## 🐛 Fehlerbehebung

### Flask nicht gefunden
```bash
pip install Flask
# oder
python start_tag_manager.py  # Auto-Installation
```

### Templates nicht gefunden
```bash
# Sicherstellen dass Sie im richtigen Verzeichnis sind:
cd TAG_Manager/
python tag_manager_web.py
```

### Port bereits belegt
```python
# In tag_manager_web.py Port ändern:
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Tools werden nicht erkannt
```bash
# Prüfen ob tools/ Verzeichnis existiert:
ls ../tools/

# Tag-Discovery testen:
python list_tools_with_tags.py
```

## 📊 API-Endpunkte

Das Web-Interface bietet folgende REST-API-Endpunkte:

- `GET /api/tools` - Tool-Liste mit Filterung/Sortierung
- `POST /api/update_tool` - Einzelnes Tool aktualisieren
- `POST /api/bulk_update` - Bulk-Update für mehrere Tools
- `GET /api/available_tags` - Verfügbare Tags abrufen

## 🔄 Integration mit CLI-Tools

Das Web-Interface nutzt die bestehenden CLI-Module:
- `manage_tool_tags.py` - Tag-Operationen
- `list_tools_with_tags.py` - Tool-Discovery
- `tag_definitions.py` - Tag-Definitionen

## 📈 Zukünftige Erweiterungen

- **Tag-Kategorien**: Hierarchische Tag-Struktur
- **Import/Export**: Tag-Konfigurationen teilen
- **Versionierung**: Tag-Änderungen verfolgen
- **Benutzer-Rollen**: Multi-User-Support
- **API-Dokumentation**: OpenAPI/Swagger
- **Tag-Validierung**: Automatische Überprüfungen

## 📞 Support

Bei Problemen oder Fragen:
1. **README** nochmals durchlesen
2. **Konsolen-Output** prüfen für Fehlermeldungen
3. **CLI-Tools** testen: `python list_tools_with_tags.py`
4. **Backup-Wiederherstellung** falls nötig

---

**Engineering Tool Tag Manager** - Komfortable Web-Verwaltung für Ihre Tool-Tags! 🏷️✨ 