# Grundsätzliche Informationen

Achte strikt darauf, eine übersichtliche Projektstruktu zu erhalten.
Wir wollen keine einzelnen großen, monolithischen Dateien erzeugen, sondern immer kleine, gut wartbare Dateien.

**WICHTIG: Alle Tools verwenden einheitlich den symbolischen Ansatz mit lösbaren Variablen.**

# Projektziel: Modularer MCP-Server für Ingenieurberechnungen (Konsolidiert)

**Datum:** 25. Mai 2025  
**Status:** Produktionsreif - Alle Komponenten verfügbar  
**Architektur-Prinzip:** Modulare, kleine, wartbare Dateien mit einheitlicher symbolischer Variablen-Auflösung

---

## 🎯 Projektübersicht

Entwicklung eines modularen MCP-Servers für Ingenieurberechnungen mit **FastMCP 2.5.1**, der **symbolische Gleichungsauflösung** mit **flexibler Variablen-Discovery** über das Model Context Protocol bereitstellt.

### Zentrale Anforderungen
- **Einheitlicher symbolischer Ansatz**: Alle Tools lösen Formeln nach verschiedenen Variablen auf
- **Modularer Aufbau**: Jedes Tool in eigener Datei mit Template-Konformität
- **Variablen-Discovery**: LLM erhält Information über lösbare Variablen pro Tool
- **Skalierung**: Bis 400 parallele Verbindungen
- **Kategorisierung**: Tag-basierte Tool-Discovery mit symbolischen Metadaten
- **Deployment**: Lokal (FastMCP CLI) → Produktiv (DigitalOcean)
- **Agent-Integration**: OpenAI Agent SDK für komplexe Workflows

### Symbolische Tool-Philosophie
**Jedes Engineering-Tool implementiert EINE Formel und kann diese nach VERSCHIEDENEN Variablen auflösen:**
- ✅ `solve_kesselformel`: σ = p·d/(2·s) → löst nach [sigma, p, d, s]
- ✅ `solve_circle_area`: A = π·r² → löst nach [area, radius]
- ✅ `solve_cylinder_volume`: V = π·r²·h → löst nach [volume, radius, height]

---

## 🛠️ Technologie-Stack (Finalisiert)

### Core-Framework
- **Language & Runtime:** Python 3.10+
- **MCP-Framework:** FastMCP 2.5.1 (aktuellste stabile Version)
- **Package Manager:** UV (moderner, schneller als Poetry)
- **Agent-Framework:** OpenAI Agent SDK v0.0.16
- **Symbolische Mathematik:** SymPy 1.13+ (aktuellste Version)
- **Numerische Routinen:** NumPy 1.26+, SciPy 1.11+

### Deployment-Stack
- **Lokal:** `fastmcp dev` / `fastmcp install`
- **Produktiv:** DigitalOcean App Platform
- **Container:** Python 3.10-slim + UV
- **Konfiguration:** `.env` für Umgebungsvariablen

### Dependencies (UV-Format)
```toml
[project]
name = "mcp-engineering-server"
version = "0.1.0"
description = "Modularer MCP-Server für Ingenieurberechnungen"
requires-python = ">=3.10"
dependencies = [
    "fastmcp>=2.5.1",
    "sympy>=1.13",
    "numpy>=1.26",
    "scipy>=1.11",
    "python-dotenv>=1.0",
    "openai-agents>=0.0.16",
    "pydantic>=2.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "black>=23.0",
    "ruff>=0.1"
]
```

---

## 🏗️ Projektarchitektur (Optimiert für Symbolische Tools)

### Verzeichnisstruktur
```
mcp-engineering-server/
├── .env                    # SERVER_NAME, DEBUG, API_KEYS
├── pyproject.toml          # UV Dependencies + Scripts
├── app.py                  # FastMCP Entry-Point + Discovery-Tools
├── TOOL_TEMPLATE.md        # Symbolisches Template für neue Tools
├── mcp/
│   ├── __init__.py
│   ├── config.py           # Server-Konfiguration
│   └── registry.py         # Tool-Discovery & Variablen-Extraktion
└── tools/                  # Thematische Tool-Gruppen (Symbolisch)
    ├── __init__.py
    ├── materials/          # Werkstoffdaten
    │   ├── __init__.py
    │   ├── solve_material_stress.py      # @mcp.tool(tags=["materials", "symbolic"])
    │   └── solve_yield_strength.py       # Lösbare Variablen: [stress, yield, safety]
    ├── geometry/           # Flächen & Volumen
    │   ├── __init__.py
    │   ├── solve_circle_area.py          # Lösbare Variablen: [area, radius]
    │   ├── solve_rectangle_area.py       # Lösbare Variablen: [area, width, height]
    │   └── solve_cylinder_volume.py      # Lösbare Variablen: [volume, radius, height]
    └── pressure/           # Druckberechnungen
        ├── __init__.py
        ├── solve_kesselformel.py         # Lösbare Variablen: [sigma, p, d, s]
        ├── solve_thin_wall.py            # Lösbare Variablen: [stress, pressure, radius, thickness]
        └── solve_thick_wall.py           # Lösbare Variablen: [stress_inner, stress_outer, pressure, radius_inner, radius_outer]
```

**Prinzipien:**
- ✅ **Ein Tool = Eine Formel = Ein Datei**
- ✅ **Symbolische SymPy-Auflösung für alle Tools**
- ✅ **Tool-Namen mit `solve_` Prefix**
- ✅ **Lösbare Variablen explizit dokumentiert**
- ✅ **Discovery-Integration für LLM-Orchestrierung**

---

## 💻 Symbolische Tool-Implementation (Standard-Template)

### Template-Struktur für alle Tools
```python
"""
[Tool Name] Tool für MCP Engineering Server

Löst die Formel [FORMEL] nach verschiedenen Variablen auf.
Lösbare Variablen: [var1, var2, var3, ...]
Template für alle weiteren Engineering Tools.
"""

from typing import Dict, Optional
from fastmcp import FastMCP, Context
from sympy import symbols, Eq, solve, pi  # weitere SymPy-Funktionen nach Bedarf
from pydantic import BaseModel, field_validator

# MCP-Instanz für Tool-Registration
mcp = FastMCP("EngineersCalc")

class ToolInput(BaseModel):
    """Input-Validierung für Tool-Parameter"""
    var1: Optional[float] = None  # Beschreibung [Einheit]
    var2: Optional[float] = None  # Beschreibung [Einheit]
    
    @field_validator('var1', 'var2')
    @classmethod
    def must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Alle Werte müssen positiv sein")
        return v

@mcp.tool(
    name="solve_formula_name",
    description="Löst [FORMEL] nach verschiedenen Variablen auf. Lösbare Variablen: [var1, var2]",
    tags=["kategorie", "engineering", "symbolic"]
)
async def solve_formula_name(
    var1: Optional[float] = None,
    var2: Optional[float] = None,
    ctx: Context = None
) -> Dict:
    """Symbolische Formel-Auflösung nach unbekannter Variable"""
    
    # 1. Context-Logging
    if ctx:
        await ctx.info("Starte symbolische Berechnung...")
    
    # 2. Input-Validierung
    inputs = ToolInput(var1=var1, var2=var2)
    provided_params = {k: v for k, v in inputs.model_dump().items() if v is not None}
    solvable_vars = ['var1', 'var2']
    
    if len(provided_params) != len(solvable_vars) - 1:
        raise ValueError(f"Genau {len(solvable_vars) - 1} von {len(solvable_vars)} Parametern müssen angegeben werden")
    
    # 3. Symbolische Hauptberechnung
    var1_sym, var2_sym = symbols('var1 var2', positive=True)
    formula = Eq(var1_sym, var2_sym)  # Beispiel-Formel
    
    unknown_var = next(k for k in solvable_vars if k not in provided_params)
    target_symbol = {'var1': var1_sym, 'var2': var2_sym}[unknown_var]
    
    solution_expr = solve(formula, target_symbol)[0]
    result_value = float(solution_expr.subs(provided_params))
    
    # 4. Strukturierte Rückgabe
    return {
        "unknown_variable": unknown_var,
        "result": result_value,
        "unit": "Einheit",
        "formula": str(formula),
        "solution_expression": str(solution_expr),
        "input_parameters": provided_params,
        "solvable_variables": solvable_vars,
        "calculation_steps": f"[FORMEL] → {unknown_var} = {solution_expr}"
    }
```

---

## 🔍 Discovery-System für LLM-Orchestrierung

### Automatische Variablen-Extraktion
```python
# mcp/registry.py
def get_tool_info_for_llm(mcp_instance: Any) -> List[Dict]:
    """Extrahiert lösbare Variablen aus Tool-Beschreibungen"""
    for tool in all_tools:
        # Parse: "Lösbare Variablen: [sigma, p, d, s]"
        solvable_vars = extract_solvable_variables(tool.description)
        
        tool_info.append({
            "name": tool.name,
            "description": tool.description,
            "solvable_variables": solvable_vars,
            "is_symbolic": "symbolic" in tool.tags
        })
```

### LLM-Discovery Tools (app.py)
```python
@mcp.tool(name="list_engineering_tools")
async def list_engineering_tools(category: Optional[str] = None) -> List[Dict]:
    """Listet alle Tools mit lösbaren Variablen für LLM-Discovery"""

@mcp.tool(name="suggest_tool_for_variables")  
async def suggest_tool_for_variables(known_variables: List[str], unknown_variable: str) -> List[Dict]:
    """Schlägt passende Tools für gegebene Variable-Kombination vor"""

@mcp.tool(name="get_symbolic_tools_overview")
async def get_symbolic_tools_overview() -> Dict:
    """Erstellt kategorisierte Übersicht aller symbolischen Tools"""
```

---

## 🚀 Entry-Point & Discovery-Integration

### app.py (Erweitert um Discovery)
```python
# Globale MCP-Instanz mit eingebauten Discovery-Tools
mcp = FastMCP("EngineersCalc")

# Discovery-Tools automatisch registriert:
# - list_engineering_tools
# - suggest_tool_for_variables  
# - get_symbolic_tools_overview

async def setup_server():
    """Lädt alle symbolischen Tools + Discovery-Tools"""
    engineering_tools = await discover_tools(mcp)  # Symbolische Tools
    discovery_tools = 3  # Fest eingebaute Discovery-Tools
    
    total_tools = engineering_tools + discovery_tools
    print(f"✅ {total_tools} Tools bereit ({engineering_tools} symbolisch + {discovery_tools} discovery)")
```

---

## 📝 Entwicklungsworkflow für neue Tools

### 1. Template-basierte Erstellung
```bash
# Kopiere TOOL_TEMPLATE.md
cp TOOL_TEMPLATE.md tools/geometry/solve_triangle_area.py

# Anpassen:
# - Formel: A = (1/2) * base * height  
# - Lösbare Variablen: [area, base, height]
# - Tags: ["geometry", "engineering", "symbolic", "area"]
```

### 2. Automatische Discovery
- Tool wird automatisch erkannt via `discover_tools()`
- Lösbare Variablen werden aus Beschreibung extrahiert
- LLM erhält strukturierte Tool-Info über Discovery-APIs

### 3. Testing
```bash
# Tool-Discovery testen
fastmcp dev app.py
# → Rufe list_engineering_tools() auf
# → Prüfe solvable_variables Array
```

---

## 🎯 Beispiel: LLM-Orchestrierung

### Szenario: "Berechne Wanddicke für Druckbehälter"
```python
# 1. LLM ruft Discovery auf
tools = await list_engineering_tools(category="pressure")
# → Findet: solve_kesselformel mit solvable_variables: [sigma, p, d, s]

# 2. LLM identifiziert passende Variablen
# Gegeben: p=10, d=100, sigma=200
# Gesucht: s

# 3. LLM ruft suggestion auf  
suggestions = await suggest_tool_for_variables(
    known_variables=["p", "d", "sigma"],
    unknown_variable="s"
)
# → Schlägt solve_kesselformel vor

# 4. LLM führt Berechnung aus
result = await solve_kesselformel(p=10, d=100, sigma=200)
# → result["unknown_variable"] = "s"
# → result["result"] = 2.5
# → result["calculation_steps"] = "σ = p·d/(2·s) → s = p*d/(2*sigma)"
```

---

## 🔧 Best Practices für symbolische Tools

### 1. Tool-Naming Convention
- ✅ **Prefix:** Immer `solve_` verwenden
- ✅ **Beschreibung:** Formel + "Lösbare Variablen: [...]"
- ✅ **Tags:** Mindestens ["kategorie", "engineering", "symbolic"]

### 2. Variable-Validation
- ✅ **Anzahl:** Genau n-1 von n Variablen gegeben
- ✅ **Werte:** Positive Zahlen (falls physikalisch sinnvoll)
- ✅ **Namen:** Konsistent mit mathematischen Konventionen

### 3. Rückgabe-Format
- ✅ **solvable_variables:** Array für LLM-Discovery
- ✅ **unknown_variable:** Welche Variable wurde gelöst
- ✅ **calculation_steps:** Nachvollziehbare Formel-Umstellung

---

## 📊 Nächste Schritte: Tool-Erweiterung

### Phase 1: Geometrie-Tools (1 Woche)
- [ ] `solve_rectangle_area`: A = w·h → [area, width, height]
- [ ] `solve_triangle_area`: A = (1/2)·b·h → [area, base, height]  
- [ ] `solve_cylinder_volume`: V = π·r²·h → [volume, radius, height]
- [ ] `solve_sphere_volume`: V = (4/3)·π·r³ → [volume, radius]

### Phase 2: Material-Tools (1 Woche)  
- [ ] `solve_stress_strain`: σ = E·ε → [stress, modulus, strain]
- [ ] `solve_safety_factor`: σ_allow = σ_yield/SF → [allowable_stress, yield_stress, safety_factor]
- [ ] `solve_elongation`: ΔL = (σ·L)/E → [elongation, stress, length, modulus]

### Phase 3: Erweiterte Drucktools (2 Wochen)
- [ ] `solve_thin_wall_stress`: σ = p·r/t → [stress, pressure, radius, thickness]  
- [ ] `solve_thick_wall_lame`: Komplexe Lame-Gleichungen
- [ ] `solve_buckling_pressure`: Kritische Knickspannung

---

## ⚡ Fazit

**Status: ✅ SYMBOLISCHE ARCHITEKTUR IMPLEMENTIERT**

Die konsolidierte symbolische Architektur bietet:
- ✅ **Einheitlichkeit**: Alle Tools folgen symbolischem Template
- ✅ **Flexibilität**: Jede Formel nach verschiedenen Variablen auflösbar  
- ✅ **Discovery**: LLM erhält strukturierte Tool-Metadaten
- ✅ **Skalierbarkeit**: Template-basierte Tool-Entwicklung
- ✅ **Orchestrierung**: Intelligente Variable-zu-Tool-Zuordnung

**Nächster Schritt**: Weitere symbolische Tools nach Template erstellen 