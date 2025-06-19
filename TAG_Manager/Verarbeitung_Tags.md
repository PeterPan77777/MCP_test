# Tag-System: Verarbeitung und Architektur

## 📋 Übersicht

Das Tag-System des Engineering MCP Servers ermöglicht die kategorische Organisation und das Filtern von Engineering-Tools. Es funktioniert über ein mehrstufiges Discovery- und Validierungs-System.

## 🏗️ Architektur-Übersicht

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Tools/*.py    │────│ tag_definitions  │────│ 1_list_tools    │
│  (Tag-Quelle)   │    │   .discover()    │    │  (Tag-Filter)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                        │                        │
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   registry.py   │    │  server.py       │    │  Meta-Tools     │
│ (Tool-Registry) │    │ (Initialisierung)│    │  (Workflow)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🎯 Tag-Definition in Tools

### 1. **Direkte Tag-Definition in Engineering-Tools**

Engineering-Tools definieren Tags über die `TOOL_TAGS` Konstante:

```python
# Beispiel: tools/geometry/Flaechen/circle_area.py
TOOL_TAGS = ["elementar"]
```

### 2. **Tag-Übertragung via get_metadata()**

Tags werden über die `get_metadata()` Funktion an das System übertragen:

```python
def get_metadata():
    return {
        "tool_name": TOOL_NAME,
        "tags": TOOL_TAGS,  # ← Hier werden Tags übertragen
        # ... weitere Metadaten
    }
```

### 3. **Meta-Tools (TOOL_METADATA)**

Meta-Tools verwenden das `TOOL_METADATA` Dictionary:

```python
# Beispiel: tools/Meta/1_list_engineering_tools.py
TOOL_METADATA = {
    "name": "1_list_engineering_tools",
    "tags": ["meta"]  # ← Meta-Tool Tag
}
```

## 🔍 Tag-Discovery-Prozess

### **Schritt 1: Automatische Tag-Sammlung**

**Datei:** `engineering_mcp/tag_definitions.py`

**Hauptfunktion:** `discover_all_tags()`

```python
def discover_all_tags() -> Dict[str, Set[str]]:
    """
    Durchsucht alle Tools im /tools Verzeichnis und sammelt deren Tags.
    Versucht zuerst Import, dann robustes Parsing.
    """
```

**Zwei Methoden:**

1. **Import-Methode** (bevorzugt):
   - Lädt Python-Module dynamisch
   - Ruft `get_metadata()` oder `TOOL_METADATA` auf
   - Extrahiert Tags aus `metadata.get('tags', [])`

2. **Robustes Parsing** (Fallback):
   - Parst Python-Dateien mit Regex
   - Sucht `"tags": [...]` oder `TOOL_TAGS = [...]`
   - Funktioniert auch bei Import-Fehlern

### **Schritt 2: Tag-Beschreibungen-Abgleich**

**Zentrale Beschreibungen:** `TAG_DESCRIPTIONS` Dictionary

```python
TAG_DESCRIPTIONS = {
    "meta": "Discovery und Workflow-Tools für Tool-Exploration",
    "elementar": "Grundlegende geometrische und mathematische Berechnungen",
    "mechanik": "Spezialisierte formeln aus Mechanik und Maschinenbau",
    "schrauben": "Schraubenverbindungen, Durchgangslöcher und Gewindeberechnungen",
    # ...
}
```

### **Schritt 3: Tag-Definitionen erstellen**

**Funktion:** `get_tag_definitions()`

- Kombiniert entdeckte Tags mit Beschreibungen
- Erstellt vollständiges Tag-Mapping: `Tag → {description, tools, tool_count}`
- Identifiziert unbekannte Tags

## 📊 Registry-Integration

### **Engineering-Tools Registry**

**Datei:** `engineering_mcp/registry.py`

**Funktion:** `discover_engineering_tools()`

```python
# Tag-Extraktion bei Tool-Discovery
tool_tags = metadata.get('tags', []) or metadata.get('tool_tags', [])
if not tool_tags:
    tool_tags = ['unknown']  # Fallback für Tools ohne Tags
```

**Registry-Struktur:**
```python
_ENGINEERING_TOOLS_REGISTRY[tool_id] = {
    'name': tool_id,
    'tags': tool_tags,  # ← Tags werden hier gespeichert
    'function': calculate_func,
    # ... weitere Daten
}
```

## 🎛️ Tag-Filter-System

### **1_list_engineering_tools.py**

**Hauptfunktion für Tag-basierte Tool-Suche:**

```python
def list_engineering_tools(tags: List[str]) -> List[Dict]:
    """
    Listet Engineering-Tools nach Tags auf
    """
```

**Tag-Filter-Logik:**
```python
for tool in all_tools:
    tool_tags = tool.get('tags', [])
    
    if "all" in tags:
        result_tools.append(tool)  # Zeige alle Tools
    else:
        # Prüfe ob Tool einen der gewünschten Tags hat
        if any(tag in tool_tags for tag in tags):
            result_tools.append(tool)
```

**Dynamische Tag-Field-Erstellung:**
- Lädt verfügbare Tags aus `tag_definitions.py`
- Erstellt OpenAI-kompatible Enum-Constraints
- Fügt Tag-Beschreibungen hinzu

## 🖥️ Server-Integration

### **server.py Initialisierung**

```python
async def init_all_tools():
    # 1. Engineering-Tools entdecken
    engineering_count = await discover_engineering_tools()
    
    # 2. Tag-System validieren
    from engineering_mcp.tag_definitions import validate_tag_system, get_tag_statistics
    
    stats = get_tag_statistics()
    print(f"Gesamt Tags im System: {stats['total_tags']}")
    print(f"Bekannte Tag-Beschreibungen: {stats['known_tags']}")
```

## ⚠️ Fehlerbehandlung & Validierung

### **Unbekannte Tags**

**Problem:** Tool verwendet Tag ohne Beschreibung in `TAG_DESCRIPTIONS`

**Erkennung:**
```python
if tag not in TAG_DESCRIPTIONS:
    _unknown_tags_cache.add(tag)
    print(f"WARNING: Unbekannter Tag '{tag}' gefunden")
```

**Validierung:**
```python
def validate_tag_system() -> List[str]:
    warnings = []
    unknown_tags = get_unknown_tags()
    
    if unknown_tags:
        warnings.append(f"⚠️ {len(unknown_tags)} unbekannte Tags gefunden")
```

### **Fallback-Strategien**

1. **Import-Fehler:** Robustes Regex-Parsing
2. **Fehlende Tags:** Zuweisung von `['unknown']`
3. **Cache-Invalidierung:** `clear_tag_cache()` Funktion

## 🔄 3-Stufiger Workflow mit Tags

### **Schritt 1: Tool Discovery**
```python
list_engineering_tools(tags=['elementar'])  # Nach spezifischen Tags filtern
list_engineering_tools(tags=['all'])        # Alle Tools anzeigen
```

### **Schritt 2: Tool Details**
```python
get_tool_details(tool_name='kreis_flaeche')  # Detaillierte Infos + Freischaltung
```

### **Schritt 3: Tool Execution**
```python
call_tool(tool_name='kreis_flaeche', parameters={...})  # Tool ausführen
```

## 📝 Tag-Kategorien im System

### **Meta-Tags**
- `meta` - Discovery und Workflow-Tools

### **Engineering-Kategorien**
- `elementar` - Grundlegende geometrische Berechnungen
- `mechanik` - Spezialisierte Maschinenbau-Formeln
- `schrauben` - Schraubenverbindungen und Gewindeberechnungen
- `tabellenwerk` - Tabellen-basierte Nachschlagewerke
- `druckbehaelter` - Druckbehälter und Kesselformeln

### **Normen-Tags**
- `DIN 13` - Schrauben- und Gewindeberechnungen nach DIN 13
- `VDI 2230` - Schraubenverbindungs-Berechnungen nach VDI 2230

### **Kontext-Tags**
- `wissen` - Context- und Dokumentations-Tools

## 🛠️ Erweiterte Funktionen

### **Tag-Statistiken**
```python
def get_tag_statistics() -> Dict[str, Any]:
    return {
        "total_tags": len(tag_to_tools),
        "known_tags": len(TAG_DESCRIPTIONS),
        "unknown_tags": len(unknown_tags),
        "most_used_tags": [...] # Top 10 meist verwendete Tags
    }
```

### **Cache-System**
- `_discovered_tags_cache` - Cache für entdeckte Tags
- `_unknown_tags_cache` - Cache für unbekannte Tags
- `clear_tag_cache()` - Cache-Invalidierung bei Änderungen

### **Batch-Tag-Processing**
- Unterstützung für mehrere Tags gleichzeitig
- OR-Logik: Tool wird angezeigt wenn es mindestens einen der Tags hat
- Spezial-Tag `"all"` zeigt alle verfügbaren Tools

## 🔧 Wartung und Erweiterung

### **Neue Tags hinzufügen**

1. **Tag-Beschreibung** in `TAG_DESCRIPTIONS` hinzufügen:
```python
TAG_DESCRIPTIONS = {
    # ... bestehende Tags
    "neuer_tag": "Beschreibung des neuen Tags"
}
```

2. **Tag in Tools** verwenden:
```python
TOOL_TAGS = ["elementar", "neuer_tag"]
```

3. **Cache leeren** (wenn Server läuft):
```python
from engineering_mcp.tag_definitions import clear_tag_cache
clear_tag_cache()
```

### **Tag-System debuggen**

```bash
# Tag-System direkt testen
python engineering_mcp/tag_definitions.py
```

**Ausgabe:**
- Alle gefundenen Tags
- Tag-Statistiken  
- Warnungen bei unbekannten Tags
- Top 10 meist verwendete Tags

## 📈 Performance-Optimierungen

1. **Lazy Loading:** Tags werden erst bei Bedarf geladen
2. **Caching:** Entdeckte Tags werden zwischengespeichert
3. **Robustes Parsing:** Fallback bei Import-Fehlern
4. **Batch-Discovery:** Alle Tools in einem Durchgang analysiert

---

**💡 Fazit:** Das Tag-System ermöglicht eine strukturierte, erweiterbare und fehlertolerante Kategorisierung der Engineering-Tools mit automatischer Discovery und Validierung. 