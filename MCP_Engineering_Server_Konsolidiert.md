# MCP Engineering Server - Konsolidierte Dokumentation

## Übersicht

Der MCP Engineering Server ist ein modularer Server für Ingenieurberechnungen mit einer **eleganten Hybrid-Discovery-Architektur**. Diese Architektur kombiniert kompakte Discovery-Tools mit direkten Tool-Aufrufen für optimale LLM-Erfahrung.

## Architektur-Prinzipien

### Hybrid-Discovery-Prozess

```
LLM Handshake
    ↓
3 Discovery-Tools (kompakt)
    ↓
Kategorien erkunden → Tools einer Kategorie → Tool-Details → DIREKTER Tool-Aufruf
```

### Vorteile
- **Kompakter Handshake**: Nur 3 Discovery-Tools beim Start sichtbar
- **Direkte Tool-Aufrufe**: `solve_kesselformel(p=10, d=100, sigma=160)` statt Gateway
- **Progressive Discovery**: LLM lernt Tools schrittweise kennen
- **Native MCP**: Echte Tool-Registrierung, keine Indirektion
- **Skalierbar**: Funktioniert auch bei 100+ Tools

## Discovery-Tools (beim Handshake sichtbar)

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
**Zweck**: Zeigt Tools einer Kategorie mit Namen und lösbaren Variablen.

### 3. get_tool_details
```python
@mcp.tool(
    name="get_tool_details",
    description="Ruft detaillierte Informationen zu einem spezifischen Tool ab"
)
```
**Zweck**: Liefert vollständige Dokumentation mit direkten Aufruf-Beispielen.

## Workflow für LLMs

### Schritt 1: Kategorien erkunden
```python
categories = await get_available_categories()
# Ergebnis: ["pressure", "geometry", "materials", ...]
```

### Schritt 2: Tools einer Kategorie auflisten
```python
tools = await list_engineering_tools(category="pressure")
# Ergebnis: Liste mit Tool-Namen und call_example
```

### Schritt 3: Tool-Details abrufen (optional)
```python
details = await get_tool_details(tool_name="solve_kesselformel")
# Ergebnis: Vollständige Dokumentation mit direkten Aufruf-Beispielen
```

### Schritt 4: Tool DIREKT aufrufen ⭐
```python
# DIREKT ohne Gateway:
result = await solve_kesselformel(p=10, d=100, sigma=160)
```

## Tool-Struktur

### Symbolischer Ansatz
Alle Engineering-Tools implementieren **eine Formel** und können diese nach **verschiedenen Variablen** auflösen:

```python
# Kesselformel: σ = p·d/(2·s)
# Lösbar nach: [sigma, p, d, s]
# Direkter Aufruf: solve_kesselformel(p=10, d=100, sigma=160)
```

### Automatische MCP-Registrierung
```python
# Tools werden automatisch bei MCP registriert:
TOOL_METADATA = {
    "name": "solve_tool_name",
    "short_description": "Kurze Beschreibung für MCP-Registrierung",
    "description": "Vollständige Beschreibung mit Lösbare Variablen: [var1, var2, var3]",
    "tags": ["category", "engineering", "symbolic"],
    "function": solve_tool_name,
    "examples": [
        {
            "description": "Beispiel-Berechnung",
            "direct_call": "solve_tool_name(var1=10, var2=20)"
        }
    ]
}
```

## Projektstruktur

```
MCP_server_TEST/
├── server.py                    # Discovery-Tools und MCP-Konfiguration
├── web.py                       # Railway-kompatibler Entry-Point
├── engineering_mcp/             # Core-Module
│   ├── config.py               # Server-Konfiguration
│   └── registry.py             # Tool-Discovery und direkte MCP-Registrierung
└── tools/                      # Engineering-Tools nach Kategorien
    ├── pressure/               # Druckberechnungen
    │   └── kesselformel.py     # Automatisch bei MCP registriert
    ├── geometry/               # Geometrische Berechnungen
    │   └── circle_area.py      # Automatisch bei MCP registriert
    └── materials/              # Werkstoffberechnungen
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
4. **Server neu starten** - Tool wird automatisch bei MCP registriert

## Best Practices

### Für Tool-Entwickler
- **Short_description**: Kompakt für MCP-Registrierung
- **Klare Variablennamen**: Mathematische Konventionen befolgen
- **Direct_call Beispiele**: In examples mit konkreten Aufrufen
- **Robuste Validierung**: Alle physikalischen Constraints prüfen

### Für LLM-Integration
- **Discovery-Workflow**: Immer get_categories → list_tools → (details) → direkter Aufruf
- **Tool-Details nutzen**: Bei unklaren Parametern für Aufruf-Beispiele
- **Direkte Aufrufe**: Nach Discovery Tools direkt aufrufen
- **Einheiten beachten**: Immer in Tool-Details dokumentiert

## Beispiel: Kompletter LLM-Workflow

```python
# 1. Discovery
categories = await get_available_categories()
tools = await list_engineering_tools(category="pressure")
details = await get_tool_details(tool_name="solve_kesselformel")

# 2. LLM lernt: solve_kesselformel ist verfügbar
# 3. Direkter Aufruf:
result = await solve_kesselformel(p=10, d=100, sigma=160)
# → Ergebnis: s = 3.125 mm
```

## Deployment (Railway)

Der Server ist für Railway optimiert:
- Nutzt PORT-Umgebungsvariable
- Health-Check unter `/health`
- Automatische Tool-Discovery und MCP-Registrierung beim Start
- Keine Änderungen am bestehenden Setup nötig

## Zusammenfassung

Der MCP Engineering Server bietet:
- ✅ **Kompakter Handshake**: Nur 3 Discovery-Tools initial sichtbar
- ✅ **Direkte Tool-Aufrufe**: Keine Gateway-Indirektion
- ✅ **Progressive Discovery**: Schrittweise Tool-Erkundung
- ✅ **Native MCP**: Echte Tool-Registrierung
- ✅ **Elegante Architektur**: Das Beste aus beiden Welten
- ✅ **Railway-kompatibel**: Läuft ohne Anpassungen 