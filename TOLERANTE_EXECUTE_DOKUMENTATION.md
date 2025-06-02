# 🔧 Tolerante MCP Execute-Tool Implementierung

## 📋 Übersicht

Diese Implementierung erweitert den hierarchischen MCP-Server um eine **tolerante Tool-Ausführung**, die automatisch typische LLM-Syntax-Fehler repariert. Das System verwendet ein **3-Layer-Ansatz** für maximale Robustheit.

## 🎯 Kernkonzept

**Problem**: LLMs produzieren oft inkonsistente Tool-Parameter-Formate:
- Python-dict-Syntax statt JSON: `{key=value}` statt `{"key": "value"}`
- Einfache statt doppelte Anführungszeichen: `{'key': 'value'}`
- Code-Fence-wrapping: ` ```json {"key": "value"} ``` `
- Python-bool/None: `True`, `False`, `None` statt `true`, `false`, `null`
- Unquoted Keys: `{key: value}` statt `{"key": "value"}`

**Lösung**: Server-seitige automatische Reparatur mit Fallback-Strategien.

## 🏗️ Architektur: 3-Layer-System

### Layer 1: Strenge Validierung ✅
```python
# Versuche normale Pydantic-Validierung
validated = ExecuteSchema(tool_name=tool_name, parameters=parameters)
```
- Normale JSON/dict-Parameter → Direkte Verarbeitung
- Keine Reparatur nötig → Maximale Performance

### Layer 2: Heuristische Reparatur 🔧  
```python
# Bei ValidationError → Automatische Reparatur
repaired = _repair_arguments({"tool_name": tool_name, "parameters": parameters})
validated = ExecuteSchema(**repaired)
```
- Regex-basierte Syntax-Reparatur
- Multiple Fallback-Strategien
- Intelligente Type-Konvertierung

### Layer 3: Kontrollierte Fehlantwort ❌
```python
# Wenn alle Reparaturversuche fehlschlagen
return {
    "error": "Schema-Validierung fehlgeschlagen",
    "original_error": str(e),
    "expected_format": {...},
    "hint": "Verwende format: execute_tool(...)"
}
```
- Detaillierte Fehlermeldungen
- Hilfreiche Format-Beispiele
- Keine Server-Abstürze

## 🛠️ Reparatur-Strategien

### 1. Code-Fence-Entfernung
```python
def _strip_codefence(txt: str) -> str:
    # Entfernt ```json ... ``` und ``` ... ```
    if txt.startswith("```"):
        lines = txt.splitlines()
        return "\n".join(lines[1:-1])
```

### 2. Regex-basierte Syntax-Reparatur
```python
# Python assignment → JSON
py_like = re.sub(r"([A-Za-z_][A-Za-z0-9_]*)\s*=", r'"\1":', py_like)

# Unquoted keys → quoted keys  
py_like = re.sub(r"([A-Za-z_][A-Za-z0-9_]*)\s*:", r'"\1":', py_like)

# Anführungszeichen normalisieren
py_like = py_like.replace("'", '"')

# Python-Literale → JSON
py_like = py_like.replace("True", "true").replace("False", "false").replace("None", "null")
```

### 3. ast.literal_eval Fallback
```python
# Wenn JSON-Parsing fehlschlägt → Python literal_eval
py_eval = raw.replace("true", "True").replace("false", "False").replace("null", "None")
raw = ast.literal_eval(py_eval)
```

### 4. Minimaler Dict-Parser
```python
# Letzter Ausweg: Regex-basierter Key-Value-Extraktor
pairs = re.findall(r'([A-Za-z_][A-Za-z0-9_]*)\s*[:=]\s*([^,}]+)', content)
for key, value in pairs:
    # Intelligente Type-Konvertierung
    if value.isdigit(): raw[key] = int(value)
    elif re.match(r'^\d+\.\d+$', value): raw[key] = float(value)
    # ... weitere Type-Checks
```

## 📊 Test-Ergebnisse

### ✅ Erfolgreich reparierte Formate:

| Format | Beispiel | Status |
|--------|----------|--------|
| **Normale JSON** | `{"p": 10, "d": 100}` | ✅ Direkt verarbeitet |
| **Python Assignment** | `{p=10, d=100}` | ✅ Automatisch repariert |
| **Einfache Quotes** | `{'p': 10, 'd': 100}` | ✅ Automatisch repariert |
| **Unquoted Keys** | `{p: 10, d: 100}` | ✅ Automatisch repariert |
| **Code-Fence JSON** | ` ```json{"p":10}``` ` | ✅ Automatisch repariert |
| **JSON-String** | `'{"p": 10, "d": 100}'` | ✅ Automatisch repariert |
| **Mixed Syntax** | `{p=10, diameter: 100}` | ✅ Automatisch repariert |

### ❌ Erwartete Fehler:
- **Komplett invalide Syntax**: `"This is not JSON"` → Kontrollierte Fehlantwort
- **Falsche Parameter-Namen**: Werden durch Engineering-Tool abgefangen
- **Nicht-aktivierte Tools**: Domain-Prüfung verhindert Ausführung

## 🚀 Integration ins MCP-System

### Enhanced Execute-Tool Signature
```python
@mcp.tool(
    name="execute_tool",
    description="🔧 Tolerante Tool-Ausführung - Repariert automatisch LLM-Syntax-Fehler",
    tags=["executor", "engineering", "tolerant"]
)
async def execute_tool(
    tool_name: str,
    parameters: Union[Dict[str, Any], str],  # ← Erweitert für String-Input
    ctx: Context = None
) -> Dict:
```

### Zusätzliche Metadaten in Antworten
```python
result.update({
    "execution_status": "success",
    "tolerant_parsing": True,      # ← Indikator für Reparatur
    "tool_executed": tool_name
})
```

## 🔄 Workflow-Integration

### Normaler Workflow (keine Reparatur nötig):
1. **LLM**: `execute_tool("pressure.solve_kesselformel", {"p": 10, "d": 100, "sigma": 160})`
2. **Layer 1**: Pydantic-Validierung ✅
3. **Server**: Tool-Ausführung
4. **Response**: Ergebnis + `"tolerant_parsing": True`

### Reparatur-Workflow:
1. **LLM**: `execute_tool("pressure.solve_kesselformel", "{p=10, d=100, sigma=160}")`
2. **Layer 1**: Pydantic-Validierung ❌
3. **Layer 2**: Automatische Reparatur → `{"p": 10, "d": 100, "sigma": 160}` ✅
4. **Server**: Tool-Ausführung
5. **Response**: Ergebnis + Reparatur-Metadaten

### Fehler-Workflow:
1. **LLM**: `execute_tool("invalid", "completely broken syntax")`
2. **Layer 1**: Pydantic-Validierung ❌  
3. **Layer 2**: Reparatur-Versuche ❌
4. **Layer 3**: Kontrollierte Fehlantwort mit Hilfe-Informationen

## 🔧 Konfiguration und Erweiterung

### Neue Reparatur-Pattern hinzufügen:
```python
def _repair_arguments(raw: Any) -> dict:
    if isinstance(raw, str):
        # Neue Pattern hier hinzufügen:
        raw = raw.replace("special_llm_syntax", "json_syntax")
        # ... rest der Reparatur-Pipeline
```

### Error-Handling anpassen:
```python
# In Layer 3 - Erweiterte Fehlermeldungen
return {
    "error": "Schema-Validierung fehlgeschlagen",
    "suggestions": ["Try format X", "Check parameter Y"],
    "documentation_link": "https://docs.example.com/tools"
}
```

## 📈 Performance-Optimierungen

1. **Layer 1 First**: Normale Inputs haben keine Performance-Penalty
2. **Cached Patterns**: Regex-Kompilierung nur einmal
3. **Early Exit**: Bei erfolgreichem JSON-Parsing → keine weiteren Versuche
4. **Minimal Logging**: Nur bei Reparatur-Versuchen

## 🛡️ Security-Überlegungen

- **ast.literal_eval**: Sicher für Python-Literale (keine Code-Ausführung)
- **JSON-Parsing**: Standard-Bibliothek ohne Security-Risiken  
- **Regex-Limits**: Pattern sind auf dict-Syntax beschränkt
- **Input-Länge**: Schutz vor extremen Eingaben durch String-Trunkierung

## 📝 Fazit

Die tolerante Execute-Tool-Implementierung macht den MCP-Server **robust gegen LLM-Eigenarten** ohne das offizielle MCP-Protokoll zu verletzen:

- ✅ **Offizielles Protokoll unverändert**
- ✅ **Server-seitige Reparatur transparent**  
- ✅ **Graceful Degradation bei Fehlern**
- ✅ **Performance-optimiert für normale Inputs**
- ✅ **Erweiterbar für neue LLM-Patterns**

**Ergebnis**: LLMs können Tools mit ihrer "natürlichen" Syntax aufrufen, während der Server robust und protokoll-konform bleibt. 