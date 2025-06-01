# MCP Engineering Server - Vollständiges Manual

## Übersicht

Der MCP Engineering Server ist ein spezialisierter Server für Ingenieurberechnungen, der eine innovative **zweistufige Architektur** implementiert. Diese Architektur trennt Meta-Tools (für die Discovery) von den eigentlichen Engineering-Tools, um eine bessere Skalierbarkeit und Organisation zu erreichen.

## Inhaltsverzeichnis

1. [Architektur-Konzept](#architektur-konzept)
2. [Projektstruktur](#projektstruktur)
3. [Zweistufige Tool-Architektur](#zweistufige-tool-architektur)
4. [Registry-System](#registry-system)
5. [Tool-Implementierung](#tool-implementierung)
6. [Kesselformel-Beispiel](#kesselformel-beispiel)
7. [Workflow für LLMs](#workflow-für-llms)
8. [Erweiterung des Systems](#erweiterung-des-systems)

## Architektur-Konzept

### Kernprinzip: Trennung von Discovery und Execution

```
┌─────────────────────┐
│   Externe LLMs      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   5 Meta-Tools      │ ◀── Was LLMs direkt sehen
├─────────────────────┤
│ • list_engineering  │
│ • get_categories    │
│ • suggest_tool      │
│ • calculate         │
│ • get_overview      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Engineering Registry│ ◀── Separate Tool-Sammlung
├─────────────────────┤
│ • Kesselformel      │
│ • Kreisberechnung   │
│ • Balkenberechnung  │
│ • ...               │
└─────────────────────┘
```

### Vorteile dieser Architektur

1. **Skalierbarkeit**: Hunderte von Engineering-Tools ohne MCP-Überladung
2. **Organisation**: Klare Kategorisierung nach Fachgebieten
3. **Discovery**: LLMs können gezielt nach Tools suchen
4. **Wartbarkeit**: Neue Tools ohne Core-Änderungen hinzufügen

## Projektstruktur

```
mcp-engineering-server/
├── app.py                     # Haupteinstiegspunkt mit Meta-Tools
├── engineering_mcp/
│   ├── __init__.py
│   ├── config.py             # Server-Konfiguration
│   └── registry.py           # Tool-Discovery und Registry
├── tools/                    # Engineering-Tools nach Kategorien
│   ├── __init__.py
│   ├── pressure/            # Druckberechnungen
│   │   ├── __init__.py
│   │   └── kesselformel.py
│   ├── geometry/            # Geometrische Berechnungen
│   │   ├── __init__.py
│   │   └── circle_area.py
│   ├── materials/           # Werkstoffkennwerte
│   └── statics/             # Statik-Berechnungen
└── tests/                   # Test-Skripte
```

## Zweistufige Tool-Architektur

### 1. Meta-Tools (bei MCP registriert)

Diese 5 Tools sind die einzigen, die externe LLMs direkt sehen:

#### list_engineering_tools
```python
@mcp.tool(
    name="list_engineering_tools",
    description="Listet alle verfügbaren Engineering-Tools mit lösbaren Variablen auf",
    tags=["discovery", "engineering", "meta"]
)
async def list_engineering_tools(
    category: Optional[str] = None,
    ctx: Context = None
) -> List[Dict]
```

**Zweck**: Haupteinstiegspunkt für Tool-Discovery. Liefert alle verfügbaren Engineering-Tools mit ihren lösbaren Variablen.

#### get_available_categories
```python
@mcp.tool(
    name="get_available_categories",
    description="Gibt alle verfügbaren Engineering-Tool-Kategorien zurück",
    tags=["discovery", "categories", "meta"]
)
async def get_available_categories(
    ctx: Context = None
) -> Dict
```

**Zweck**: Zeigt verfügbare Kategorien (pressure, geometry, materials, etc.) mit Beschreibungen.

#### suggest_tool_for_variables
```python
@mcp.tool(
    name="suggest_tool_for_variables",
    description="Schlägt passende Tools basierend auf gegebenen/gesuchten Variablen vor",
    tags=["discovery", "engineering", "recommendation"]
)
async def suggest_tool_for_variables(
    known_variables: List[str],
    unknown_variable: str,
    ctx: Context = None
) -> List[Dict]
```

**Zweck**: Intelligente Tool-Empfehlung basierend auf bekannten und gesuchten Variablen.

#### calculate_engineering
```python
@mcp.tool(
    name="calculate_engineering",
    description="Führt Engineering-Berechnungen über die separate Tool-Registry aus",
    tags=["engineering", "execution", "gateway"]
)
async def calculate_engineering(
    tool_name: str,
    parameters: Dict,
    ctx: Context = None
) -> Dict
```

**Zweck**: Gateway-Funktion zur Ausführung der eigentlichen Engineering-Tools.

#### get_symbolic_tools_overview
```python
@mcp.tool(
    name="get_symbolic_tools_overview",
    description="Gibt eine Übersicht aller symbolischen Tools zurück",
    tags=["discovery", "engineering", "symbolic", "meta"]
)
async def get_symbolic_tools_overview(
    ctx: Context = None
) -> Dict
```

**Zweck**: Strukturierte Übersicht über alle symbolischen Tools mit ihren Formeln.

### 2. Engineering-Tools (in separater Registry)

Diese Tools werden NICHT direkt bei MCP registriert, sondern in einer separaten Registry gespeichert:

```python
# Globale Engineering-Tool-Registry
_ENGINEERING_TOOLS_REGISTRY: Dict[str, Dict] = {}
```

## Registry-System

### Tool-Discovery

Die `discover_engineering_tools()` Funktion durchsucht automatisch das `tools/` Verzeichnis:

```python
async def discover_engineering_tools() -> int:
    """
    Entdeckt Engineering-Tools und speichert sie in separater Registry.
    REGISTRIERT NICHT bei MCP - nur interne Speicherung!
    """
    global _ENGINEERING_TOOLS_REGISTRY
    _ENGINEERING_TOOLS_REGISTRY.clear()
    
    # Dynamischer Import aller Tool-Module
    import tools
    
    # Iteriere durch alle Submodule in tools/
    for category_finder, category_name, ispkg in pkgutil.iter_modules(tools.__path__, tools.__name__ + "."):
        if ispkg:
            # Importiere Kategorie-Modul (z.B. tools.pressure)
            category_module = importlib.import_module(category_name)
            
            # Importiere alle Tool-Module in der Kategorie
            for tool_finder, tool_name, _ in pkgutil.iter_modules(
                category_module.__path__, 
                category_name + "."
            ):
                # Importiere das Tool-Modul
                tool_module = importlib.import_module(tool_name)
                
                # Suche nach TOOL_METADATA
                if hasattr(tool_module, 'TOOL_METADATA'):
                    metadata = tool_module.TOOL_METADATA
                    tool_func = metadata.get('function')
                    
                    if tool_func and callable(tool_func):
                        # Speichere in separater Registry
                        tool_id = metadata.get('name', tool_func.__name__)
                        _ENGINEERING_TOOLS_REGISTRY[tool_id] = {
                            **metadata,
                            'category': category_name.split('.')[-1]
                        }
```

### Tool-Informationen für LLMs

Die `get_tool_info_for_llm()` Funktion bereitet Tool-Informationen strukturiert auf:

```python
def get_tool_info_for_llm(include_engineering: bool = True) -> List[Dict]:
    """
    Erstellt strukturierte Tool-Informationen für LLM-Discovery.
    
    Returns:
        List[Dict]: Tool-Informationen mit solvable_variables
    """
    tool_info = []
    
    for tool_name, tool_data in _ENGINEERING_TOOLS_REGISTRY.items():
        # Extrahiere lösbare Variablen aus der Beschreibung
        solvable_vars = []
        description = tool_data.get('description', '')
        if 'Lösbare Variablen:' in description:
            # Parse: "Lösbare Variablen: [var1, var2, var3]"
            match = re.search(r'Lösbare Variablen:\s*\[([^\]]+)\]', description)
            if match:
                vars_str = match.group(1)
                solvable_vars = [var.strip() for var in vars_str.split(',')]
        
        tool_info.append({
            "name": tool_name,
            "description": description,
            "tags": tool_data.get('tags', []),
            "category": tool_data.get('category', 'unknown'),
            "solvable_variables": solvable_vars,
            "is_symbolic": "symbolic" in tool_data.get('tags', []),
            "source": "engineering_registry"
        })
```

## Tool-Implementierung

### Struktur eines Engineering-Tools

Jedes Engineering-Tool folgt diesem Muster:

```python
"""
Tool-Name für MCP Engineering Server

Löst die Formel [FORMEL] nach verschiedenen Variablen auf.
Lösbare Variablen: [var1, var2, var3]
"""

from typing import Dict, Optional
from fastmcp import Context
from sympy import symbols, Eq, solve, N
from pydantic import BaseModel, field_validator

# 1. Input-Validierung
class ToolNameInput(BaseModel):
    """Input-Validierung für Tool-Parameter"""
    param1: Optional[float] = None
    param2: Optional[float] = None
    # ... weitere Parameter
    
    @field_validator('param1', 'param2')
    @classmethod
    def must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Alle Werte müssen positiv sein")
        return v

# 2. Tool-Funktion
async def solve_tool_name(
    param1: Optional[float] = None,
    param2: Optional[float] = None,
    ctx: Context = None
) -> Dict:
    """
    Löst die Formel symbolisch nach der unbekannten Variable.
    """
    # Context-Logging
    if ctx:
        await ctx.info("Starte Berechnung...")
    
    # Input-Validierung
    inputs = ToolNameInput(param1=param1, param2=param2)
    provided_params = {k: v for k, v in inputs.model_dump().items() if v is not None}
    
    # Symbolische Berechnung mit SymPy
    # ... (siehe Kesselformel-Beispiel)
    
    return {
        "unknown_variable": unknown_var,
        "result": result_value,
        "unit": "...",
        "formula": str(formula),
        "solution_expression": str(solution_expr),
        "input_parameters": provided_params,
        "solvable_variables": ["param1", "param2", ...],
        "calculation_steps": "..."
    }

# 3. Tool-Metadaten für Registry
TOOL_METADATA = {
    "name": "solve_tool_name",
    "description": "Löst [FORMEL] nach verschiedenen Variablen auf. Lösbare Variablen: [var1, var2, ...]",
    "tags": ["category", "engineering", "symbolic"],
    "function": solve_tool_name
}
```

## Kesselformel-Beispiel

Die Kesselformel ist ein perfektes Beispiel für ein symbolisches Engineering-Tool:

### Formel
```
σ = p·d/(2·s)
```

- **σ** (sigma): Zulässige Spannung [N/mm²]
- **p**: Innendruck [N/mm²]
- **d**: Außendurchmesser [mm]
- **s**: Wanddicke [mm]

### Implementierung

```python
async def solve_kesselformel(
    p: Optional[float] = None,
    d: Optional[float] = None,
    s: Optional[float] = None,
    sigma: Optional[float] = None,
    ctx: Context = None
) -> Dict:
    """
    Löst die Kesselformel σ = p·d/(2·s) symbolisch nach der unbekannten Variable.
    """
    # 1. Input-Validierung: Genau 3 von 4 Parametern müssen angegeben werden
    inputs = KesselformelInput(p=p, d=d, s=s, sigma=sigma)
    provided_params = {k: v for k, v in inputs.model_dump().items() if v is not None}
    
    if len(provided_params) != 3:
        raise ValueError("Genau 3 von 4 Parametern müssen angegeben werden")
    
    # 2. SymPy-Symbole definieren
    p_sym, d_sym, s_sym, sigma_sym = symbols('p d s sigma', positive=True)
    formula = Eq(sigma_sym, (p_sym * d_sym) / (2 * s_sym))
    
    # 3. Unbekannte Variable identifizieren
    unknown_var = next(k for k in ['p', 'd', 's', 'sigma'] if k not in provided_params)
    target_symbol = {'p': p_sym, 'd': d_sym, 's': s_sym, 'sigma': sigma_sym}[unknown_var]
    
    # 4. Symbolische Lösung
    solution_expr = solve(formula, target_symbol)[0]
    
    # 5. Robuste Substitution
    symbol_mapping = {
        p_sym: provided_params.get('p'),
        d_sym: provided_params.get('d'),
        s_sym: provided_params.get('s'), 
        sigma_sym: provided_params.get('sigma')
    }
    symbol_mapping = {k: v for k, v in symbol_mapping.items() if v is not None}
    
    # 6. Numerische Auswertung
    substituted_expr = solution_expr.subs(symbol_mapping)
    result_value = float(N(substituted_expr))
    
    return {
        "unknown_variable": unknown_var,
        "result": result_value,
        "unit": "N/mm²" if unknown_var in ['p', 'sigma'] else "mm",
        "formula": str(formula),
        "solution_expression": str(solution_expr),
        "input_parameters": provided_params,
        "solvable_variables": ["sigma", "p", "d", "s"],
        "calculation_steps": f"σ = p·d/(2·s) → {unknown_var} = {solution_expr}"
    }
```

### Verwendungsbeispiele

#### Beispiel 1: Wanddicke berechnen
```python
result = await calculate_engineering(
    tool_name="solve_kesselformel",
    parameters={"p": 10, "d": 100, "sigma": 160}
)
# Ergebnis: s = 3.125 mm
```

#### Beispiel 2: Innendruck berechnen
```python
result = await calculate_engineering(
    tool_name="solve_kesselformel",
    parameters={"d": 100, "s": 5, "sigma": 160}
)
# Ergebnis: p = 16.0 N/mm²
```

## Workflow für LLMs

### Überblick: Sequenzieller Discovery-Prozess

Der MCP Engineering Server erfordert einen **strukturierten, sequenziellen Ablauf** für die Tool-Discovery:

```
1. Kategorien abrufen → 2. Tools der Kategorie abrufen → 3. Tool auswählen → 4. Tool ausführen
```

### 1. Discovery-Phase

#### Schritt 1: Verfügbare Kategorien abrufen (PFLICHT)
```python
# IMMER ZUERST: Welche Kategorien gibt es?
categories = await get_available_categories()

# Beispiel-Response:
{
    "available_categories": ["pressure", "geometry", "materials", "statics"],
    "category_details": {
        "pressure": {
            "name": "pressure",
            "tools": ["solve_kesselformel", "..."],
            "tool_count": 3,
            "description": "Druckbehälter, Kesselformeln, Druckberechnungen"
        },
        "geometry": {
            "name": "geometry", 
            "tools": ["solve_circle_area", "..."],
            "tool_count": 5,
            "description": "Flächenberechnungen, Volumen, geometrische Formeln"
        }
        // ... weitere Kategorien
    }
}
```

#### Schritt 2: Tools einer spezifischen Kategorie abrufen
```python
# NUR NACH SCHRITT 1: Jetzt kennen wir die Kategorien
# Beispiel: Wir brauchen ein Druck-Tool
pressure_tools = await list_engineering_tools(category="pressure")

# Beispiel-Response:
[
    {
        "name": "solve_kesselformel",
        "description": "Löst σ = p·d/(2·s) nach verschiedenen Variablen auf. Lösbare Variablen: [sigma, p, d, s]",
        "tags": ["pressure", "engineering", "symbolic", "vessels"],
        "category": "pressure",
        "solvable_variables": ["sigma", "p", "d", "s"],
        "is_symbolic": true
    }
    // ... weitere Tools
]
```

#### Schritt 3: Passendes Tool auswählen

**Option A: Direkte Auswahl** (wenn Tool bekannt)
```python
# Wir wissen, wir brauchen die Kesselformel
selected_tool = "solve_kesselformel"
```

**Option B: Tool basierend auf Variablen finden**
```python
# Wir haben: Druck (p), Durchmesser (d), Spannung (sigma)
# Wir suchen: Wanddicke (s)
suggestions = await suggest_tool_for_variables(
    known_variables=["p", "d", "sigma"],
    unknown_variable="s"
)

# Response:
[
    {
        "tool_name": "solve_kesselformel",
        "description": "Löst σ = p·d/(2·s) nach verschiedenen Variablen auf...",
        "solvable_variables": ["sigma", "p", "d", "s"],
        "reason": "Kann s aus ['p', 'd', 'sigma'] berechnen",
        "confidence": "high"
    }
]
```

### 2. Execution-Phase

#### Schritt 4: Tool ausführen
```python
# Tool mit den bekannten Parametern aufrufen
result = await calculate_engineering(
    tool_name="solve_kesselformel",
    parameters={
        "p": 10,        # Innendruck: 10 N/mm²
        "d": 100,       # Durchmesser: 100 mm
        "sigma": 160    # Zul. Spannung: 160 N/mm²
    }
)

# Response:
{
    "tool_name": "solve_kesselformel",
    "parameters": {"p": 10, "d": 100, "sigma": 160},
    "result": {
        "unknown_variable": "s",
        "result": 3.125,
        "unit": "mm",
        "formula": "Eq(sigma, d*p/(2*s))",
        "solution_expression": "d*p/(2*sigma)",
        "calculation_steps": "σ = p·d/(2·s) → s = d*p/(2*sigma)"
    },
    "status": "success"
}
```

### Wichtige Regeln für LLMs

1. **NIEMALS** direkt `list_engineering_tools()` ohne Kategorie aufrufen (zu viele Tools!)
2. **IMMER** erst `get_available_categories()` aufrufen
3. **DANN** mit einer spezifischen Kategorie `list_engineering_tools(category="...")` aufrufen
4. **OPTIONAL** `suggest_tool_for_variables()` für intelligente Tool-Auswahl nutzen
5. **ZULETZT** `calculate_engineering()` mit Tool-Name und Parametern aufrufen

### Beispiel: Kompletter Workflow

```python
# Ein LLM möchte die Wanddicke eines Druckbehälters berechnen

# 1. Was gibt es für Kategorien?
categories = await get_available_categories()
# → Findet "pressure" Kategorie

# 2. Welche Druck-Tools gibt es?
tools = await list_engineering_tools(category="pressure")
# → Findet "solve_kesselformel"

# 3. Ist das das richtige Tool?
suggestion = await suggest_tool_for_variables(
    known_variables=["p", "d", "sigma"],
    unknown_variable="s"
)
# → Bestätigt: solve_kesselformel ist richtig

# 4. Tool ausführen
result = await calculate_engineering(
    tool_name="solve_kesselformel",
    parameters={"p": 10, "d": 100, "sigma": 160}
)
# → Ergebnis: s = 3.125 mm
```

### Alternative: Übersicht aller symbolischen Tools

Für spezielle Fälle kann auch eine Gesamtübersicht abgerufen werden:

```python
overview = await get_symbolic_tools_overview()
# Liefert strukturierte Übersicht ALLER symbolischen Tools
# Nützlich für: Dokumentation, Überblick, spezielle Suchen
```

## Erweiterung des Systems

### Neues Tool hinzufügen

1. **Kategorie-Verzeichnis erstellen** (falls noch nicht vorhanden):
   ```
   tools/neue_kategorie/__init__.py
   ```

2. **Tool-Datei erstellen**:
   ```
   tools/neue_kategorie/mein_tool.py
   ```

3. **Tool implementieren** (siehe Tool-Struktur oben)

4. **Server neu starten** - das Tool wird automatisch entdeckt!

### Neue Kategorie definieren

In `app.py` die Kategorie-Beschreibungen erweitern:

```python
category_descriptions = {
    "pressure": "Druckbehälter, Kesselformeln, Druckberechnungen",
    "geometry": "Flächenberechnungen, Volumen, geometrische Formeln",
    "materials": "Werkstoffkennwerte, Festigkeitsberechnungen",
    "neue_kategorie": "Beschreibung der neuen Kategorie"  # NEU
}
```

### Best Practices

1. **Konsistente Beschreibungen**: Immer "Lösbare Variablen: [...]" im Format angeben
2. **Positive Validierung**: Alle physikalischen Größen sollten positiv sein
3. **Einheiten dokumentieren**: Immer Einheiten in Kommentaren und Rückgaben angeben
4. **Robuste Substitution**: Verwende SymPy-Symbole als Schlüssel, nicht Strings
5. **Aussagekräftige Tags**: Mindestens Kategorie + "engineering" + "symbolic" (falls zutreffend)

## Zusammenfassung

Der MCP Engineering Server implementiert eine innovative zweistufige Architektur, die es ermöglicht, hunderte von spezialisierten Engineering-Tools zu verwalten, ohne das MCP-System zu überlasten. Durch die Trennung von Meta-Tools (Discovery) und Engineering-Tools (Execution) erreichen wir:

- **Skalierbarkeit**: Beliebig viele Tools ohne Performance-Einbußen
- **Organisation**: Klare Struktur nach Fachgebieten
- **Flexibilität**: Neue Tools ohne Core-Änderungen
- **Intelligenz**: LLMs können gezielt nach passenden Tools suchen

Die symbolische Berechnung mit SymPy ermöglicht es, Formeln nach beliebigen Variablen aufzulösen - ein mächtiges Werkzeug für Ingenieurberechnungen! 