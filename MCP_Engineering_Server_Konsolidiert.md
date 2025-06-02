# MCP Engineering Server - Konsolidierte Dokumentation

## Übersicht

Der MCP Engineering Server ist ein modularer Server für Ingenieurberechnungen mit einer **Progressive Tool Disclosure Architektur**. Diese Architektur stellt sicher, dass beim Handshake nur wenige Discovery-Tools sichtbar sind, während Engineering-Tools erst nach expliziter Freischaltung verfügbar werden.

## Architektur-Prinzipien

### Progressive Tool Disclosure Prozess

```
LLM Handshake
    ↓
4 Tools sichtbar (clock + 3 Discovery-Tools)
    ↓
Kategorien erkunden → Tools einer Kategorie → Tool-Details → FREISCHALTUNG → DIREKTER Tool-Aufruf
```

### Implementierung
- **Versteckte Registry**: Engineering-Tools werden in `_HIDDEN_ENGINEERING_TOOLS` gespeichert
- **Session State**: Freigeschaltete Tools in `_session_allowed_tools` Set
- **Dynamische Registrierung**: Tools werden erst nach `get_tool_details()` bei FastMCP registriert
- **Keine Handler-Override**: Nutzt einfache Session-basierte Logik statt komplexer MCP-Handler

### Vorteile
- **Minimaler Handshake**: Nur 4 Tools beim Start sichtbar
- **Schrittweise Freischaltung**: Tools werden progressiv verfügbar gemacht
- **Session-basiert**: Jede Session hat eigene freigeschaltete Tools
- **Einfache Implementation**: Keine komplexen MCP-Handler-Overrides nötig
- **Skalierbar**: Funktioniert auch bei 100+ Tools

## Discovery-Tools (beim Handshake sichtbar)

### 1. clock
```python
@mcp.tool()
def clock() -> str:
    """Aktuelle UTC-Zeit zurückgeben"""
```
**Zweck**: Utility-Tool für Zeitstempel

### 2. get_available_categories
```python
@mcp.tool(
    name="get_available_categories",
    description="Gibt alle verfügbaren Engineering-Tool-Kategorien zurück. IMMER ZUERST AUFRUFEN!",
    tags=["discovery", "categories", "meta"]
)
```
**Zweck**: Einstiegspunkt - zeigt verfügbare Kategorien wie pressure, geometry, materials etc.

### 3. list_engineering_tools
```python
@mcp.tool(
    name="list_engineering_tools", 
    description="Listet alle Tools einer spezifischen Kategorie mit Kurzbeschreibungen auf",
    tags=["discovery", "engineering", "meta"]
)
```
**Zweck**: Zeigt Tools einer Kategorie mit Status (🔒 LOCKED / 🔓 UNLOCKED)

### 4. get_tool_details
```python
@mcp.tool(
    name="get_tool_details",
    description="Ruft detaillierte Informationen zu einem Tool ab und SCHALTET ES FREI für direkten Aufruf",
    tags=["discovery", "engineering", "documentation", "meta", "unlock"]
)
```
**Zweck**: ⚡ **SCHALTET TOOLS FREI** - Registriert Tools dynamisch bei FastMCP für direkten Aufruf

## Progressive Discovery Workflow

### Schritt 1: Kategorien erkunden
```python
categories = await get_available_categories()
# Ergebnis: {"available_categories": ["pressure", "geometry", "materials", ...], 
#           "progressive_disclosure_status": {"hidden_tools_available": 2, "currently_unlocked": 0}}
```

### Schritt 2: Tools einer Kategorie auflisten
```python
tools = await list_engineering_tools(category="pressure")
# Ergebnis: {"tools": [{"name": "solve_kesselformel", "status": "🔒 LOCKED", ...}],
#           "unlocked_tools": 0, "locked_tools": 1}
```

### Schritt 3: Tool freischalten ⚡
```python
details = await get_tool_details(tool_name="solve_kesselformel") 
# ⚡ FREISCHALTUNG: Tool wird bei FastMCP registriert
# Ergebnis: {"unlock_status": {"unlocked": True, "direct_call_available": True}}
```

### Schritt 4: Tool DIREKT aufrufen ⭐
```python
# JETZT VERFÜGBAR:
result = await solve_kesselformel(p=10, d=100, sigma=160)
# Ergebnis: {"unknown_variable": "s", "result": 3.125, "unit": "mm"}
```

## Tool-Struktur

### Symbolischer Ansatz
Alle Engineering-Tools implementieren **eine Formel** und können diese nach **verschiedenen Variablen** auflösen:

```python
# Kesselformel: σ = p·d/(2·s)
# Lösbar nach: [sigma, p, d, s]
# Direkter Aufruf (nach Freischaltung): solve_kesselformel(p=10, d=100, sigma=160)
```

### Versteckte Registrierung
```python
# In engineering_mcp/registry.py:
_HIDDEN_ENGINEERING_TOOLS = {}  # Versteckte Registry

async def discover_engineering_tools(mcp_instance: Any, register_hidden: bool = False):
    """Tools werden NICHT bei MCP registriert, sondern nur in versteckter Registry gespeichert"""
    if register_hidden:
        _HIDDEN_ENGINEERING_TOOLS[tool_id] = {
            **metadata,
            'category': category,
            'function': tool_func
        }
        # KEIN mcp_instance.tool() Aufruf!
```

### Dynamische Freischaltung
```python
# In server.py:
async def register_engineering_tool_dynamically(tool_name: str):
    """Nach get_tool_details() wird Tool bei FastMCP registriert"""
    if tool_name in _HIDDEN_ENGINEERING_TOOLS:
        tool_metadata = _HIDDEN_ENGINEERING_TOOLS[tool_name]
        tool_func = tool_metadata.get('function')
        
        # JETZT erst bei FastMCP registrieren:
        mcp.tool(
            name=tool_name,
            description=tool_metadata.get('short_description'),
            tags=tool_metadata.get('tags', [])
        )(tool_func)
```

## Projektstruktur

```
MCP_server_TEST/
├── server.py                    # Progressive Tool Disclosure + Discovery-Tools
├── web.py                       # Railway-kompatibler Entry-Point
├── engineering_mcp/             # Core-Module
│   ├── config.py               # Server-Konfiguration
│   └── registry.py             # Versteckte Tool-Registry + Discovery
└── tools/                      # Engineering-Tools nach Kategorien
    ├── pressure/               # Druckberechnungen
    │   └── kesselformel.py     # Versteckt geladen, dynamisch freigeschaltet
    ├── geometry/               # Geometrische Berechnungen
    │   └── circle_area.py      # Versteckt geladen, dynamisch freigeschaltet
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
fastmcp>=2.5.1              # MCP Framework mit Tool-Support
sympy>=1.13                 # Symbolische Mathematik
pydantic>=2.0               # Input-Validierung
uvicorn[standard]           # ASGI Server
starlette                   # Web Framework
```

## Implementation Details

### Session State Management
```python
# Global Session State (vereinfacht, da keine Multi-Session bei Railway)
_session_allowed_tools = set()

# Nach Tool-Freischaltung:
_session_allowed_tools.add(tool_name)
await register_engineering_tool_dynamically(tool_name)
```

### Tool Status Tracking
```python
# In list_engineering_tools():
for tool in filtered_tools:
    is_unlocked = tool["name"] in _session_allowed_tools
    
    compact_tools.append({
        "name": tool["name"],
        "status": "🔓 UNLOCKED - Ready to call" if is_unlocked else "🔒 LOCKED - Call get_tool_details() to unlock",
        "call_example": f"{tool['name']}(...)" if is_unlocked else f"get_tool_details('{tool['name']}')",
        "unlock_hint": "Tool bereits freigeschaltet!" if is_unlocked else f"Nutze get_tool_details('{tool['name']}') um das Tool freizuschalten"
    })
```

## Neue Tools hinzufügen

1. **Kategorie-Ordner** erstellen (falls nicht vorhanden)
2. **Tool-Datei** nach Template erstellen
3. **TOOL_METADATA** mit allen Informationen definieren
4. **Server neu starten** - Tool wird automatisch in versteckter Registry geladen
5. **Zur Laufzeit**: Tool über `get_tool_details()` freischalten

## Best Practices

### Für Tool-Entwickler
- **Short_description**: Kompakt für initiale Discovery
- **Unlock_hints**: Klare Anweisungen zur Freischaltung
- **Direct_call Beispiele**: In examples mit konkreten Aufrufen nach Freischaltung
- **Robuste Validierung**: Alle physikalischen Constraints prüfen

### Für LLM-Integration
- **Discovery-Workflow**: Immer get_categories → list_tools → get_details → direkter Aufruf
- **Tool-Status beachten**: 🔒/🔓 Status in list_engineering_tools
- **Freischaltung zuerst**: Vor Tool-Aufruf immer get_tool_details() aufrufen
- **Einheiten beachten**: Immer in Tool-Details dokumentiert

## Beispiel: Kompletter LLM-Workflow

```python
# 1. Discovery Phase
categories = await get_available_categories()
# → ["pressure", "geometry", "materials"] + progressive_disclosure_status

tools = await list_engineering_tools(category="pressure") 
# → [{"name": "solve_kesselformel", "status": "🔒 LOCKED", ...}]

# 2. Tool-Freischaltung
details = await get_tool_details(tool_name="solve_kesselformel")
# → ⚡ Tool wird dynamisch bei FastMCP registriert
# → {"unlock_status": {"unlocked": True, "direct_call_available": True}}

# 3. Direkter Tool-Aufruf (JETZT möglich)
result = await solve_kesselformel(p=10, d=100, sigma=160)
# → {"unknown_variable": "s", "result": 3.125, "unit": "mm"}
```

## Deployment (Railway)

Der Server ist für Railway optimiert:
- Nutzt PORT-Umgebungsvariable
- Health-Check unter `/health`
- Automatische versteckte Tool-Discovery beim Start
- Progressive Tool Disclosure ohne Session-Persistence (bei Railway nicht nötig)
- Keine Änderungen am bestehenden Setup nötig

## Test Results

✅ **Progressive Tool Disclosure erfolgreich implementiert:**
- ✅ 2 Engineering-Tools in versteckter Registry geladen
- ✅ 4 Discovery-Tools beim Handshake sichtbar (clock + 3 Meta-Tools)
- ✅ Session-basierte Freischaltung funktioniert
- ✅ Dynamische Tool-Registrierung implementiert
- ✅ Tools bleiben versteckt bis zur Freischaltung

## Zusammenfassung

Der MCP Engineering Server bietet:
- ✅ **Minimaler Handshake**: Nur 4 Tools initial sichtbar
- ✅ **Progressive Freischaltung**: Tools werden nach Bedarf aktiviert
- ✅ **Session-basiert**: Einfache Zustandsverwaltung
- ✅ **Dynamische Registrierung**: FastMCP-konforme Tool-Registrierung
- ✅ **Railway-kompatibel**: Läuft ohne Anpassungen
- ✅ **Benutzerfreundlich**: Klare Status-Indikatoren und Workflow-Guidance

Die Progressive Tool Disclosure löst das ursprüngliche Problem: **Beim Handshake sind nur wenige Discovery-Tools sichtbar, Engineering-Tools werden erst nach expliziter Freischaltung verfügbar**. 