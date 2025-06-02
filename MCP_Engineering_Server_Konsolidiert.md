# MCP Engineering Server - Konsolidierte Dokumentation

## Übersicht

Der MCP Engineering Server nutzt ein **hierarchisches Tool-Schema** mit echtem Tool-Hiding. Beim Handshake sind nur 3 Tools sichtbar, während Engineering-Tools komplett versteckt bleiben und nur über einen Dispatcher/Executor ausgeführt werden können.

## Architektur-Prinzipien

### Hierarchisches Tool-Schema

```
LLM Handshake
    ↓
3 Tools sichtbar (clock, dispatch_engineering, execute_tool)
    ↓
Domain wählen → Domain aktivieren → Tool über execute_tool ausführen
```

### Implementierung
- **Versteckte Registry**: Engineering-Tools in `_ENGINEERING_TOOLS` Dictionary (NICHT bei MCP registriert!)
- **Session State**: Aktivierte Domain und erlaubte Tools in `_session_state`
- **Dispatcher**: `dispatch_engineering` für Domain-Auswahl und Aktivierung
- **Executor**: `execute_tool` für indirekte Tool-Ausführung

### Vorteile
- **Minimaler Handshake**: Nur 3 Tools beim Start sichtbar
- **Echtes Tool-Hiding**: Engineering-Tools sind NICHT bei MCP registriert
- **Domain-basierte Kontrolle**: Tools nur nach Domain-Aktivierung nutzbar
- **Skalierbar**: Beliebig viele versteckte Tools ohne Handshake-Bloat
- **OpenAI-konform**: Löst das 64-Tools-Limit elegant

## Sichtbare Tools (beim Handshake)

### 1. clock
```python
@mcp.tool()
def clock() -> str:
    """Aktuelle UTC-Zeit zurückgeben"""
```
**Zweck**: Utility-Tool für Zeitstempel

### 2. dispatch_engineering
```python
@mcp.tool(
    name="dispatch_engineering",
    description="Wählt eine Engineering-Domain und aktiviert deren Tools. Domains: pressure, geometry, materials"
)
```
**Zweck**: Dispatcher für Domain-Auswahl und Tool-Aktivierung
- `action="info"`: Zeigt alle verfügbaren Domains
- `action="list"`: Listet Tools einer Domain mit Details
- `action="activate"`: Aktiviert Domain für execute_tool

### 3. execute_tool
```python
@mcp.tool(
    name="execute_tool",
    description="Führt ein aktiviertes Engineering-Tool mit den gegebenen Parametern aus"
)
```
**Zweck**: Executor für versteckte Engineering-Tools nach Domain-Aktivierung

## Hierarchischer Workflow

### Schritt 1: Domain-Informationen abrufen
```python
result = await dispatch_engineering(domain="pressure", action="info")
# Ergebnis: {"available_domains": ["pressure", "geometry", "materials"], ...}
```

### Schritt 2: Domain aktivieren
```python
result = await dispatch_engineering(domain="pressure", action="activate")
# Ergebnis: {"domain_activated": "pressure", "tools_available": ["pressure.solve_kesselformel"], ...}
```

### Schritt 3: Tool ausführen über execute_tool
```python
result = await execute_tool(
    tool_name="pressure.solve_kesselformel",
    parameters={"p": 10, "d": 100, "sigma": 160}
)
# Ergebnis: {"unknown_variable": "s", "result": 3.125, "unit": "mm", ...}
```

## Versteckte Engineering-Tools

### Tool-Struktur
Engineering-Tools sind NICHT bei MCP registriert, sondern in einer internen Registry:

```python
_ENGINEERING_TOOLS = {
    "pressure.solve_kesselformel": {
        "function": _solve_kesselformel,  # Async function
        "description": "Kesselformel σ = p·d/(2·s) - Löst nach einer der 4 Variablen auf",
        "parameters": {
            "sigma": "Spannung [N/mm²] (optional)",
            "p": "Innendruck [bar] (optional)",
            "d": "Innendurchmesser [mm] (optional)",
            "s": "Wandstärke [mm] (optional)"
        }
    },
    "geometry.solve_circle_area": {
        "function": _solve_circle_area,
        "description": "Kreisfläche A = π·r² - Berechnet Fläche aus Radius oder umgekehrt",
        "parameters": {
            "area": "Kreisfläche [m²] (optional)",
            "radius": "Kreisradius [m] (optional)"
        }
    }
}
```

### Implementierte Tools

#### pressure.solve_kesselformel
- **Formel**: σ = p·d/(2·s)
- **Lösbare Variablen**: [sigma, p, d, s]
- **Verwendung**: Druckbehälter-Berechnungen nach AD2000

#### geometry.solve_circle_area
- **Formel**: A = π·r²
- **Lösbare Variablen**: [area, radius]
- **Verwendung**: Kreisflächen-Berechnungen

## Session State Management

```python
_session_state = {
    "active_domain": None,      # Aktuell aktivierte Domain
    "allowed_tools": set()      # Erlaubte Tool-Namen
}
```

Nach Domain-Aktivierung werden die Domain-Tools in `allowed_tools` hinzugefügt.
`execute_tool` prüft vor Ausführung, ob das Tool erlaubt ist.

## Beispiel: Kompletter LLM-Workflow

```python
# 1. Domain-Übersicht
info = await dispatch_engineering(domain="pressure", action="info")
# → Zeigt verfügbare Domains und Status

# 2. Tools einer Domain anzeigen
tools = await dispatch_engineering(domain="pressure", action="list")
# → {"tools": [{"name": "pressure.solve_kesselformel", "parameters": {...}}]}

# 3. Domain aktivieren
activate = await dispatch_engineering(domain="pressure", action="activate")
# → {"domain_activated": "pressure", "examples": [...]}

# 4. Tool ausführen
result = await execute_tool(
    tool_name="pressure.solve_kesselformel",
    parameters={"p": 10, "d": 100, "sigma": 160}
)
# → {"unknown_variable": "s", "result": 3.125, "unit": "mm"}
```

## Projektstruktur

```
MCP_server_TEST/
├── server.py                    # Hierarchisches Tool-Schema mit versteckten Tools
├── web.py                       # Railway-kompatibler Entry-Point  
├── engineering_mcp/             # (Nicht mehr benötigt für Tool-Hiding)
└── tools/                       # (Nicht mehr benötigt - Tools direkt in server.py)
```

## Neue Tools hinzufügen

1. **Tool-Funktion** als async function implementieren:
```python
async def _solve_new_tool(param1: float = None, param2: float = None, ctx: Context = None) -> Dict:
    """Interne Tool-Implementierung"""
    # Berechnung...
    return {"result": ...}
```

2. **In Registry eintragen**:
```python
_ENGINEERING_TOOLS["domain.tool_name"] = {
    "function": _solve_new_tool,
    "description": "Tool-Beschreibung",
    "parameters": {
        "param1": "Beschreibung [Einheit] (optional)",
        "param2": "Beschreibung [Einheit] (optional)"
    }
}
```

3. **Domain-Zuordnung** in `dispatch_engineering`:
```python
domain_tools = {
    "domain": ["domain.tool_name"],  # Tool zur Domain hinzufügen
    # ...
}
```

## Konfiguration

### Umgebungsvariablen
```bash
SERVER_NAME=EngineersCalc    # Name des MCP Servers
PORT=8080                   # Server-Port (Railway)
```

### Requirements
```txt
fastmcp>=2.5.1              # MCP Framework
sympy>=1.13                 # Symbolische Mathematik
pydantic>=2.0               # Input-Validierung (optional)
uvicorn[standard]           # ASGI Server
starlette                   # Web Framework
```

## Best Practices

### Für Tool-Entwickler
- **Klare Namenskonvention**: `domain.tool_name` Format
- **Ausführliche Parameter-Beschreibungen**: Mit Einheiten und optional-Markierung
- **Robuste Fehlerbehandlung**: Validierung in Tool-Funktionen
- **Konsistente Rückgabe-Struktur**: Domain, Tool, Result, Unit

### Für LLM-Integration
- **Hierarchischer Workflow**: Immer dispatch → activate → execute
- **Domain-Aktivierung zuerst**: Vor execute_tool immer Domain aktivieren
- **Parameter als Dictionary**: execute_tool erwartet parameters als Dict
- **Fehlerbehandlung**: execute_tool gibt strukturierte Fehler zurück

## Deployment (Railway)

Der Server ist für Railway optimiert:
- Nutzt PORT-Umgebungsvariable
- Health-Check unter `/health`
- Keine externen Dependencies für Tool-Registry
- Keine Änderungen am bestehenden Setup nötig

## Test-Ergebnisse

✅ **Hierarchisches Tool-Schema erfolgreich implementiert:**
- ✅ Nur 3 Tools beim Handshake sichtbar
- ✅ Engineering-Tools komplett versteckt (nicht bei MCP registriert)
- ✅ Domain-basierte Tool-Aktivierung funktioniert
- ✅ Tool-Ausführung über execute_tool funktioniert
- ✅ Session State Management aktiv

## Zusammenfassung

Der MCP Engineering Server bietet:
- ✅ **Minimaler Handshake**: Nur 3 Tools sichtbar (clock, dispatcher, executor)
- ✅ **Echtes Tool-Hiding**: Engineering-Tools sind NICHT bei MCP registriert
- ✅ **Hierarchisches Schema**: Skaliert auf beliebig viele Tools
- ✅ **OpenAI-konform**: Umgeht das 64-Tools-Limit elegant
- ✅ **Domain-Organisation**: Klare Strukturierung der Tools
- ✅ **Railway-kompatibel**: Läuft ohne Anpassungen

Das hierarchische Tool-Schema löst das ursprüngliche Problem vollständig: **Beim Handshake sind nur 3 Tools sichtbar, Engineering-Tools bleiben komplett versteckt und werden nur über den Dispatcher/Executor-Mechanismus ausgeführt**. 