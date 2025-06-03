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
- **Ultra-tolerante LLM-Eingabe**: Automatische Reparatur von Parameter-Syntax-Fehlern

## Tag-System

### Verfügbare Tags
- **`meta`**: Discovery und Workflow-Tools für Tool-Exploration
- **`elementar`**: Grundlegende geometrische und mathematische Berechnungen
- **`mechanik`**: Spezialisierte Formeln aus Mechanik und Maschinenbau

### Tag-Unterstrukturen
- **`elementar + Fläche`**: Flächenberechnungen (Rechteck, Dreieck, Trapez, Kreis)
- **`elementar + Volumen`**: Volumenberechnungen (Quader, Zylinder, Kugel)

### Tag-Vorteile
- **Flexibel**: Tools können mehrere Tags haben
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
**Zweck**: Liefert vollständige Dokumentation eines Tools inkl. Input/Output-Format, Beispiele, Verwendungshinweise und **Parameter-Format-Hinweise**.

### 4. call_tool (Ultra-tolerant)
```python
@mcp.tool(
    name="call_tool",
    description="🔧 ULTRA-TOLERANTE Tool-Ausführung - Repariert automatisch LLM-Syntax-Fehler"
)
```
**Zweck**: Gateway zur Tool-Ausführung mit **automatischer Parameter-Reparatur**.

#### Unterstützte Parameter-Formate:
1. **Standard JSON**: `{"pressure": "100 bar", "wall_thickness": "50 mm"}`
2. **Python-Dict**: `{pressure="100 bar", wall_thickness="50 mm"}`  
3. **String-Parameter**: `'pressure="100 bar", wall_thickness="50 mm"'`
4. **Code-Fence**: ````json {"pressure": "100 bar"} ````
5. **n8n-Workflow-JSON**: Automatische Extraktion aus Workflow-Definitionen
6. **Verschachtelte Strukturen**: Intelligente Parameter-Suche

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
# Ergebnis: Vollständige Dokumentation + Parameter-Format-Hinweise
```
**Neue Features in Tool-Details:**
- **`parameter_format`**: Korrekte vs. falsche Parameter-Beispiele
- **`korrekte_aufruf_syntax`**: Spezifisches Beispiel für dieses Tool
- **`usage_hints`**: Variable Kombinationen für Berechnungen

### Schritt 4: Tool ausführen (Ultra-tolerant)
```python
# Alle diese Formate funktionieren:
result = await call_tool(
    tool_name="solve_kesselformel",
    parameters={"pressure": "100 bar", "wall_thickness": "50 mm", "allowable_stress": "200 MPa"}
)
# oder:
result = await call_tool(
    tool_name="solve_kesselformel", 
    parameters={pressure="100 bar", wall_thickness="50 mm", allowable_stress="200 MPa"}
)
```

## Engineering-Tools (Aktueller Stand: 9 Tools)

### Einheiten-System
Alle Tools verwenden **Pint** für automatische Einheiten-Konvertierung:
- **Eingabe**: Beliebige Einheiten ("100 bar", "5 mm", "25.5 cm²")
- **Verarbeitung**: Automatische SI-Konvertierung  
- **Ausgabe**: Optimierte Einheiten basierend auf Eingabe-Referenz

### Verfügbare Tools:

#### Mechanik (Tag: mechanik)
- **solve_kesselformel**: Druckbehälter-Berechnungen (pressure, wall_thickness, diameter, allowable_stress)

#### Geometrie - Flächen (Tags: elementar, Fläche)
- **solve_rechteck**: Rechteck-Fläche (area, length, width)
- **solve_dreieck**: Dreieck-Fläche (area, base, height)
- **solve_trapez**: Trapez-Fläche (area, side_a, side_c, height)
- **solve_circle_area**: Kreis-Fläche (area, radius, diameter)

#### Geometrie - Volumen (Tags: elementar, Volumen)
- **solve_quader**: Quader-Volumen (volume, length, width, height)
- **solve_zylinder**: Zylinder-Volumen (volume, radius, height)
- **solve_kugel**: Kugel-Volumen (volume, radius)

### Tool-Struktur

#### Symbolischer Ansatz
Alle Engineering-Tools implementieren **eine Formel** und können diese nach **verschiedenen Variablen** auflösen:

```python
# Kesselformel: p = (2 × σ_zul × s) / D
# Lösbare Variablen: pressure, wall_thickness, diameter, allowable_stress
```

#### n-1 Parameterprinzip
- Bei **n lösbaren Variablen** müssen **n-1 Parameter** gegeben werden
- **1 Variable** wird automatisch berechnet
- Flexible Variablen-Auflösung je nach gegebenen Parametern

### Tool-Template (Aktualisiert)
```python
"""
[Tool Name] - Kurzbeschreibung für list_engineering_tools

Löst die Formel [FORMEL] nach verschiedenen Variablen auf.
Lösbare Variablen: var1, var2, var3

Detaillierte Beschreibung:
[Ausführliche Erklärung der Formel, Anwendungsbereich, Einheiten etc.]
"""

# Einheiten-Import (aktualisiert)
from tools.units_utils import validate_inputs_have_units, optimize_output_unit, UnitsError, ureg

# Tool-Implementierung mit Pint-Einheiten
def solve_tool_name(var1: Optional[str] = None, ...):
    # Einheiten-Validierung
    params = validate_inputs_have_units(var1=var1, var2=var2, var3=var3)
    
    # SI-Konvertierung
    var1_si = params['var1']['si_value']
    
    # Berechnung
    result_si = formula_calculation(var1_si, ...)
    
    # Optimierte Ausgabe-Einheit
    result_quantity = result_si * ureg.meter
    result_optimized = optimize_output_unit(result_quantity, reference_unit)

TOOL_METADATA = {
    "name": "solve_tool_name",
    "short_description": "Kurze Beschreibung für Discovery",
    "description": """Löst [FORMEL] nach verschiedenen Variablen auf. Lösbare Variablen: var1, var2, var3

WICHTIG: Alle Parameter MÜSSEN mit Einheiten angegeben werden!
Format: "Wert Einheit" (z.B. "5.2 mm", "10 cm", "25.5 cm²")""",
    "tags": ["elementar", "Fläche"],  # oder ["mechanik"] 
    "function": solve_tool_name,
    "examples": [...]
}
```

## Projektstruktur

```
MCP_server_TEST/
├── server.py                    # Meta-Tools und MCP-Konfiguration (Ultra-tolerant)
├── web.py                       # Railway-kompatibler Entry-Point
├── engineering_mcp/
│   └── registry.py             # Tool-Registry mit Parameter-Format-Hinweisen
├── tools/                       # Engineering-Tools organisiert in Unterordnern
│   ├── units_utils.py          # Pint-basiertes Einheiten-System
│   ├── tag_definitions.py      # Tag-Schema und -Definitionen
│   ├── pressure/               # Druckberechnungen (Tag: mechanik)
│   │   └── kesselformel.py
│   └── geometry/               # Geometrische Berechnungen (Tag: elementar)
│       ├── circle_area.py
│       ├── Flaechen/          # Tag: elementar + Fläche
│       │   ├── rechteck.py
│       │   ├── dreieck.py
│       │   └── trapez.py
│       └── Volumen/           # Tag: elementar + Volumen
│           ├── quader.py
│           ├── zylinder.py
│           └── kugel.py
└── TOOL_TEMPLATE.py            # Aktualisiertes Template für neue Tools
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
pint>=0.23                  # Einheiten-System (NEU)
pydantic>=2.0               # Input-Validierung
uvicorn[standard]           # ASGI Server
starlette                   # Web Framework
```

## Neue Tools hinzufügen

1. **Tool-Datei** nach aktuellem `TOOL_TEMPLATE.py` erstellen
2. **Richtiges Tag** wählen: 
   - `["elementar", "Fläche"]` für Flächenberechnungen
   - `["elementar", "Volumen"]` für Volumenberechnungen
   - `["mechanik"]` für spezialisierte Maschinenbau-Formeln
3. **Lösbare Variablen** im Format `"Lösbare Variablen: var1, var2, var3"` definieren
4. **Einheiten-System** verwenden (`tools.units_utils`)
5. **Server neu starten** - Tool wird automatisch entdeckt

## Best Practices

### Für Tool-Entwickler
- **Konsistente Metadaten**: Kurz- und Langbeschreibung trennen
- **Richtiges Tag-Format**: `["elementar", "Fläche"]` statt nur `["elementar"]`
- **Einheiten-Pflicht**: Alle Parameter mit `validate_inputs_have_units()` prüfen
- **Optimierte Ausgabe**: `optimize_output_unit()` für benutzerfreundliche Einheiten
- **Vollständige Beispiele**: Mindestens 2 Use-Cases dokumentieren
- **Physikalische Constraints**: Alle Validierungen implementieren

### Für LLM-Integration
- **Immer mit Tags starten**: Nie direkt alle Tools laden
- **get_tool_details ist PFLICHT**: Vor jedem call_tool ausführen
- **Parameter-Format beachten**: Einheiten IMMER angeben `"100 bar"`
- **Tolerante Eingabe nutzen**: Server repariert viele Syntax-Fehler automatisch
- **Parameter-Format-Hinweise** aus Tool-Details verwenden
- **Fehlerbehandlung**: Status-Feld in Responses beachten

### Ultra-tolerante Eingabe-Features
- **n8n-Workflow-JSON**: Automatische Erkennung und Parameter-Extraktion
- **Python-Dict-Syntax**: `{param=value}` wird zu `{"param": value}` repariert
- **Code-Fence-Removal**: ````json ... ```` wird automatisch bereinigt
- **Bool/None-Konvertierung**: `True/False/None` ↔ `true/false/null`
- **Engineering-Parameter-Suche**: Intelligente Erkennung relevanter Parameter

## Deployment (Railway)

Der Server ist für Railway optimiert:
- Nutzt PORT-Umgebungsvariable
- Health-Check unter `/health`
- Automatische Tool-Discovery beim Start
- Tag-basierte Tool-Organisation
- Ultra-tolerante LLM-Parameter-Behandlung

## Zusammenfassung

Der MCP Engineering Server bietet:
- ✅ **Kompakter Handshake**: Nur 4 Meta-Tools initial sichtbar
- ✅ **Progressive Discovery**: Schrittweise Tool-Erkundung über Tags
- ✅ **Tag-basierte Organisation**: Flexible Alternative zu Verzeichnissen
- ✅ **Einheiten-System**: Automatische Konvertierung mit Pint
- ✅ **Ultra-tolerante LLM-Eingabe**: Automatische Parameter-Syntax-Reparatur
- ✅ **Parameter-Format-Hinweise**: Klare Anleitung in jeder Tool-Beschreibung
- ✅ **9 vollständige Engineering-Tools**: Mechanik + Geometrie (Flächen & Volumen)
- ✅ **n8n-Workflow-Kompatibilität**: Automatische JSON-Extraktion
- ✅ **Skalierbare Architektur**: Beliebig viele Tools und Tags möglich
- ✅ **Railway-kompatibel**: Läuft ohne Anpassungen 