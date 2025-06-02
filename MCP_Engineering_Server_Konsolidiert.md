# MCP Engineering Server - Konsolidierte Dokumentation

## Übersicht

Der MCP Engineering Server ist ein modularer Server für Ingenieurberechnungen mit einer **mehrstufigen Discovery-Architektur** basierend auf **Tags**. Diese Architektur minimiert die initiale Tool-Liste für LLMs und ermöglicht eine schrittweise Erkundung der verfügbaren Funktionen.

## Architektur-Prinzipien

### Mehrstufiger Discovery-Prozess

```
LLM Handshake
    ↓
4 Meta-Tools (kompakt)
    ↓
Tags erkunden → Tools mit Tags → Tool-Details → Tool ausführen
```

### Vorteile
- **Skalierbarkeit**: Hunderte von Tools ohne Überlastung beim Handshake
- **Progressive Discovery**: LLM erhält nur relevante Informationen
- **Tag-basierte Organisation**: Flexible Kategorisierung statt starrer Verzeichnisse
- **Flexible Erweiterung**: Neue Tools ohne Core-Änderungen

## Tag-System

### Verfügbare Tags
- **`meta`**: Discovery und Workflow-Tools für Tool-Exploration
- **`elementar`**: Grundlegende geometrische und mathematische Berechnungen
- **`mechanik`**: Spezialisierte Formeln aus Mechanik und Maschinenbau

### Tag-Vorteile
- **Flexibel**: Tools können mehrere Tags haben (derzeit auf 1 begrenzt)
- **Erweiterbar**: Neue Tags einfach in `tools/tag_definitions.py` hinzufügbar
- **Beschränkbar**: LLM-Zugriff kann auf bestimmte Tags limitiert werden

## Meta-Tools (beim Handshake sichtbar)

### 1. get_available_categories
```python
@mcp.tool(
    name="get_available_categories", 
    description="Gibt alle verfügbaren Engineering-Tool-Tags zurück"
)
```
**Zweck**: Einstiegspunkt - zeigt verfügbare Tags wie meta, elementar, mechanik.

### 2. list_engineering_tools
```python
@mcp.tool(
    name="list_engineering_tools",
    description="Listet alle Tools mit spezifischen Tags mit Kurzbeschreibungen auf"
)
```
**Zweck**: Zeigt Tools mit gewählten Tags, inkl. kompakter Beschreibung und lösbaren Variablen.

### 3. get_tool_details
```python
@mcp.tool(
    name="get_tool_details",
    description="Ruft detaillierte Informationen zu einem spezifischen Tool ab"
)
```
**Zweck**: Liefert vollständige Dokumentation eines Tools inkl. Input/Output-Format, Beispiele und Verwendungshinweise.

### 4. call_tool
```python
@mcp.tool(
    name="call_tool",
    description="Führt ein Engineering-Tool mit den angegebenen Parametern aus"
)
```
**Zweck**: Gateway zur eigentlichen Tool-Ausführung.

## Workflow für LLMs

### Schritt 1: Tags erkunden
```python
tags = await get_available_categories()
# Ergebnis: {"meta": {...}, "elementar": {...}, "mechanik": {...}}
```

### Schritt 2: Tools mit Tags auflisten
```python
tools = await list_engineering_tools(tags=["elementar"])
# Ergebnis: Liste mit Tool-Namen und Kurzbeschreibungen
```

### Schritt 3: Tool-Details abrufen (**PFLICHT vor Tool-Aufruf**)
```python
details = await get_tool_details(tool_name="solve_kesselformel")
# Ergebnis: Vollständige Dokumentation, Parameter, Beispiele
```

### Schritt 4: Tool ausführen
```python
result = await call_tool(
    tool_name="solve_kesselformel",
    parameters={"p": 10, "d": 100, "sigma": 160}
)
```

## Tool-Struktur

### Symbolischer Ansatz
Alle Engineering-Tools implementieren **eine Formel** und können diese nach **verschiedenen Variablen** auflösen:

```python
# Kesselformel: σ = p·d/(2·s)
# Lösbar nach: [sigma, p, d, s]
```

### Tool-Template
```python
"""
[Tool Name] - Kurzbeschreibung für list_engineering_tools

Löst die Formel [FORMEL] nach verschiedenen Variablen auf.
Lösbare Variablen: [var1, var2, var3]

Detaillierte Beschreibung:
[Ausführliche Erklärung der Formel, Anwendungsbereich, Einheiten etc.]

Beispiele:
1. Berechne var1 aus var2, var3:
   parameters = {"var2": 10, "var3": 20}
   
2. Berechne var2 aus var1, var3:
   parameters = {"var1": 5, "var3": 20}
"""

# ... Tool-Implementierung mit SymPy ...

TOOL_METADATA = {
    "name": "solve_tool_name",
    "short_description": "Kurze Beschreibung für Discovery",
    "description": "Vollständige Beschreibung mit Details",
    "tags": ["elementar"],  # Wähle: ["meta"] | ["elementar"] | ["mechanik"]
    "function": solve_tool_name,
    "examples": [...],
    "input_schema": {...},
    "output_schema": {...}
}
```

## Projektstruktur

```
MCP_server_TEST/
├── server.py              # Meta-Tools und MCP-Konfiguration
├── web.py                 # Railway-kompatibler Entry-Point
├── tools/                 # Engineering-Tools organisiert in Unterordnern
│   ├── tag_definitions.py # Tag-Schema und -Definitionen
│   ├── pressure/          # Druckberechnungen (Tag: mechanik)
│   │   └── kesselformel.py
│   └── geometry/          # Geometrische Berechnungen (Tag: elementar)
│       └── circle_area.py
└── TOOL_TEMPLATE.py       # Template für neue Tools
```

## Konfiguration

### Umgebungsvariablen
```bash
SERVER_NAME=EngineersCalc    # Name des MCP Servers
DEBUG=false                  # Debug-Modus
PORT=8080                   # Server-Port (Railway)
```

### Requirements
```txt
fastmcp>=2.5.1              # MCP Framework
sympy>=1.13                 # Symbolische Mathematik
pydantic>=2.0               # Input-Validierung
uvicorn[standard]           # ASGI Server
starlette                   # Web Framework
```

## Neue Tools hinzufügen

1. **Tool-Datei** nach `TOOL_TEMPLATE.py` erstellen
2. **Richtiges Tag** wählen: `["elementar"]`, `["mechanik"]` oder neues Tag in `tag_definitions.py`
3. **TOOL_METADATA** mit korrektem Tag definieren
4. **Server neu starten** - Tool wird automatisch entdeckt

## Best Practices

### Für Tool-Entwickler
- **Konsistente Metadaten**: Kurz- und Langbeschreibung trennen
- **Richtiges Tag**: `elementar` für Grundlagen, `mechanik` für Spezielles
- **Klare Variablennamen**: Mathematische Konventionen befolgen
- **Vollständige Beispiele**: Mindestens 2 Use-Cases dokumentieren
- **Robuste Validierung**: Alle physikalischen Constraints prüfen

### Für LLM-Integration
- **Immer mit Tags starten**: Nie direkt alle Tools laden
- **get_tool_details ist PFLICHT**: Vor jedem call_tool ausführen
- **Tag-basierte Filterung**: Nur relevante Tools laden
- **Fehlerbehandlung**: Status-Feld in Responses beachten
- **Einheiten beachten**: Immer in Tool-Details dokumentiert

## Deployment (Railway)

Der Server ist für Railway optimiert:
- Nutzt PORT-Umgebungsvariable
- Health-Check unter `/health`
- Automatische Tool-Discovery beim Start
- Tag-basierte Tool-Organisation

## Zusammenfassung

Der MCP Engineering Server bietet:
- ✅ **Kompakter Handshake**: Nur 4 Meta-Tools initial sichtbar
- ✅ **Progressive Discovery**: Schrittweise Tool-Erkundung über Tags
- ✅ **Tag-basierte Organisation**: Flexible Alternative zu Verzeichnissen
- ✅ **Symbolische Berechnung**: Flexible Variablen-Auflösung
- ✅ **Skalierbare Architektur**: Beliebig viele Tools und Tags möglich
- ✅ **Railway-kompatibel**: Läuft ohne Anpassungen 