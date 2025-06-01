# MCP Engineering Server - Konsolidierte Dokumentation

## Übersicht

Der MCP Engineering Server ist ein modularer Server für Ingenieurberechnungen mit einer **mehrstufigen Discovery-Architektur**. Diese Architektur minimiert die initiale Tool-Liste für LLMs und ermöglicht eine schrittweise Erkundung der verfügbaren Funktionen.

## Architektur-Prinzipien

### Mehrstufiger Discovery-Prozess

```
LLM Handshake
    ↓
4 Meta-Tools (kompakt)
    ↓
Kategorien erkunden → Tools einer Kategorie → Tool-Details → Tool ausführen
```

### Vorteile
- **Skalierbarkeit**: Hunderte von Tools ohne Überlastung beim Handshake
- **Progressive Discovery**: LLM erhält nur relevante Informationen
- **Klare Organisation**: Tools nach Fachgebieten kategorisiert
- **Flexible Erweiterung**: Neue Tools ohne Core-Änderungen

## Meta-Tools (beim Handshake sichtbar)

### 1. get_available_categories
```python
@mcp.tool(
    name="get_available_categories",
    description="Gibt alle verfügbaren Engineering-Tool-Kategorien zurück"
)
```
**Zweck**: Einstiegspunkt - zeigt verfügbare Kategorien wie pressure, geometry, materials etc.

### 2. list_engineering_tools
```python
@mcp.tool(
    name="list_engineering_tools",
    description="Listet alle Tools einer spezifischen Kategorie mit Kurzbeschreibungen auf"
)
```
**Zweck**: Zeigt Tools einer Kategorie mit kompakter Beschreibung und lösbaren Variablen.

### 3. get_tool_details
```python
@mcp.tool(
    name="get_tool_details",
    description="Ruft detaillierte Informationen zu einem spezifischen Tool ab"
)
```
**Zweck**: Liefert vollständige Dokumentation eines Tools inkl. Input/Output-Format, Beispiele und Verwendungshinweise.

### 4. calculate_engineering
```python
@mcp.tool(
    name="calculate_engineering",
    description="Führt ein Engineering-Tool mit den angegebenen Parametern aus"
)
```
**Zweck**: Gateway zur eigentlichen Tool-Ausführung.

## Workflow für LLMs

### Schritt 1: Kategorien erkunden
```python
categories = await get_available_categories()
# Ergebnis: ["pressure", "geometry", "materials", ...]
```

### Schritt 2: Tools einer Kategorie auflisten
```python
tools = await list_engineering_tools(category="pressure")
# Ergebnis: Liste mit Tool-Namen und Kurzbeschreibungen
```

### Schritt 3: Tool-Details abrufen (optional)
```python
details = await get_tool_details(tool_name="solve_kesselformel")
# Ergebnis: Vollständige Dokumentation, Parameter, Beispiele
```

### Schritt 4: Tool ausführen
```python
result = await calculate_engineering(
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
    "tags": ["category", "engineering", "symbolic"],
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
├── engineering_mcp/       # Core-Module
│   ├── config.py         # Server-Konfiguration
│   └── registry.py       # Tool-Registry und Discovery
└── tools/                # Engineering-Tools nach Kategorien
    ├── pressure/         # Druckberechnungen
    │   └── kesselformel.py
    ├── geometry/         # Geometrische Berechnungen
    │   └── circle_area.py
    └── materials/        # Werkstoffberechnungen
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

1. **Kategorie-Ordner** erstellen (falls nicht vorhanden)
2. **Tool-Datei** nach Template erstellen
3. **TOOL_METADATA** mit allen Informationen definieren
4. **Server neu starten** - Tool wird automatisch entdeckt

## Best Practices

### Für Tool-Entwickler
- **Konsistente Metadaten**: Kurz- und Langbeschreibung trennen
- **Klare Variablennamen**: Mathematische Konventionen befolgen
- **Vollständige Beispiele**: Mindestens 2 Use-Cases dokumentieren
- **Robuste Validierung**: Alle physikalischen Constraints prüfen

### Für LLM-Integration
- **Immer mit Kategorien starten**: Nie direkt alle Tools laden
- **Tool-Details bei Bedarf**: Nur wenn Parameter unklar sind
- **Fehlerbehandlung**: Status-Feld in Responses beachten
- **Einheiten beachten**: Immer in Tool-Details dokumentiert

## Deployment (Railway)

Der Server ist für Railway optimiert:
- Nutzt PORT-Umgebungsvariable
- Health-Check unter `/health`
- Automatische Tool-Discovery beim Start
- Keine Änderungen am bestehenden Setup nötig

## Zusammenfassung

Der MCP Engineering Server bietet:
- ✅ **Kompakter Handshake**: Nur 4 Meta-Tools initial sichtbar
- ✅ **Progressive Discovery**: Schrittweise Tool-Erkundung
- ✅ **Symbolische Berechnung**: Flexible Variablen-Auflösung
- ✅ **Skalierbare Architektur**: Beliebig viele Tools möglich
- ✅ **Railway-kompatibel**: Läuft ohne Anpassungen 