from fastmcp import FastMCP, Context
import datetime
from typing import Dict, List, Any
from engineering_mcp.registry import (
    discover_engineering_tools,
    get_tool_info_for_llm, 
    call_engineering_tool,
    get_tool_details as get_tool_details_from_registry
)

# Session State wird jetzt zentral in tools.Meta.session_state verwaltet

# MCP Server mit ausführlichen Instructions für LLMs
mcp = FastMCP(
    name="EngineersCalc", 
    instructions="""
Engineering Calculation Server - Berechnungstools und Informationen für Ingenieure

🎯 SYSTEMÜBERSICHT:
Dieser Server bietet Zugriff auf eine spezialisierte Engineering-Tool-Bibliothek mit symbolischen und numerischen Berechnungstools für den Bereich Maschinenbau. Ebenso werden normkonforme Berechnungen nach DIN und weiteren Normen, sowie Tabellenwerke bereitgestellt.

🔬 BERECHNUNGSARTEN (has_solving Parameter):
• "symbolic" - Alle Parameter analytisch lösbar durch geschlossene Formeln (SymPy-basiert, schnell & exakt)
• "numeric" - Alle Parameter numerisch lösbar durch Iterationsverfahren (mit Fehlerabschätzung & Konvergenzprüfung)
• "symbolic/numeric" - Gemischte Methoden: verschiedene Parameter verwenden unterschiedliche Berechnungsarten
• "none" - Keine Berechnungslogik, nur Information/Datenbank-Zugriff (Tabellen, Normwerte, etc.)

Du erkennst die Berechnungsart jedes Tools an dem Parameter "has_solving" in der Tool-Dokumentation.

🔄 3-STUFIGER WORKFLOW:
Der Server implementiert einen Discovery-to-Execution-Workflow:

1. 📋 DISCOVERY: '1_list_engineering_tools(tags=[...])' ← EINSTIEGSPUNKT
   🎯 ÜBERSICHTSMODUS: Zeigt name, short_description, tags pro Tool
   ❌ KEINE vollständigen Beschreibungen oder Parameter (→ 2_get_tool_details)
   
   📋 TAG-FILTER BEISPIELE:
   - tags=["all"] für vollständige Tool-Übersicht
    ...

   💡 WORKFLOW-PFLICHT: Muss mindestens einmal pro Konversation ausgeführt werden, um verfügbare Toolnamen zu erhalten. Immer hier starten!

2. 📖 DOKUMENTATION: '2_get_tool_details(tool_name)'
   - MANDATORY vor jeder Tool-Ausführung
   - Aktiviert Tool für Ausführung (Whitelist-System)
   - Liefert vollständige Parameter-Dokumentation
   - Zeigt Anwendungsbeispiele und Einheiten-Anforderungen

   💡 WORKFLOW-PFLICHT: Muss mindestens einmal pro Konversation jeweils pro Tool ausgeführt werden, um die verfügbaren Tooldetails zu erhalten und das entsprechende Tool für die Benutzung freizuschalten.
    Führe dieses Tool ebenso aus, wenn Du bei der Benutzung von 3_call_tool() eine Fehlermeldung erhältst.

3. ⚙️ EXECUTION: '3_call_tool(tool_name, parameters)'

    - Mit diesem Tool führst Du Berechnungen aus, oder fragst Informationen ab !

   - Nur freigeschaltete Tools können ausgeführt werden
   - Fehlertolerante Parameter-Eingabe mit automatischer Reparatur
   - Unterstützt JSON, Python-dict-Syntax und Code-Fence-wrapped Parameter

⚠️ KRITISCHE TECHNISCHE ANFORDERUNGEN:

🔢 SYMBOLISCHE BERECHNUNG:
- Tools verwenden vollständige Parameter-Sets mit Zielparameter-Kennzeichnung
- ALLE Parameter sind required: bekannte Werte + Zielparameter = "target"
- Beispiel: Kesselformel σ = p·d/(2·s) → {"pressure": "100 bar", "diameter": "500 mm", "wall_thickness": "target", "allowable_stress": "200 MPa"}
- Der Zielparameter wird symbolisch aufgelöst und numerisch berechnet
- Verwende IMMER SymPy-kompatible symbolische Eingaben

📐 EINHEITEN-OBLIGATION:
- ALLE numerischen Parameter MÜSSEN physikalische Einheiten enthalten
- Format: "Wert Einheit" (z.B. "100 bar", "50 mm", "200 MPa")
- Keine einheitenlosen Zahlen erlaubt bei Engineering-Berechnungen

🔒 SICHERHEITS-ARCHITEKTUR:
- Whitelist-basiertes Freischaltungssystem
- Rate-Limiting (max. 10 Aufrufe pro Tool/Minute)
- Tools bleiben ohne 2_get_tool_details() deaktiviert

🔧 PARAMETER-EINGABE FÜR 3_call_tool:
⚠️ KRITISCHES PARAMETER-FORMAT - STRIKT EINHALTEN:

ZWINGEND ERFORDERLICHES FORMAT:
```json
{
  "tool_name": "solve_kesselformel",
  "parameters": {
    "pressure": "100 bar",
    "wall_thickness": "target",
    "diameter": "500 mm", 
    "allowable_stress": "200 MPa"
  }
}
```
❌ VERBOTENES FORMAT:
```json
{
  "tool_name": "solve_kesselformel", 
  "parameters": "pressure='100 bar', wall_thickness='target', diameter='500 mm'"
}
```


WICHTIGE REGELN:
• Alle Parameter MÜSSEN als Key-Value-Pairs im "parameters"-Objekt definiert werden
• Ein Parameter muss den Wert "target" haben (zu berechnende Variable)
• Andere Parameter müssen Werte mit Einheiten enthalten
• NIEMALS Parameter als String-Verkettung verwenden

🔄 BATCH-BERECHNUNGEN (NEU 2025):
Alle Engineering-Tools mit dem Parameter "has_solving" = "symbolic" oder "numeric" oder beide unterstützen jetzt Batch-Verarbeitung für Massenberechnungen!
Du kannst viele Paramtersätze auf einmal berechnen (hunderte ... tausende). Du kannst dies zum Beispiel verwenden, wenn Datentabellen / Diagrammdaten oder ähnliches benötigt wird.

⚠️ KRITISCHE BATCH-REGELN:
• ALLE Parameter müssen Listen gleicher Länge sein
• Jeder Index repräsentiert einen vollständigen Parametersatz
• Jeder Parametersatz braucht genau einen 'target'
• Keine Mischung von Listen und Einzelwerten erlaubt

✅ KORREKTES BATCH-FORMAT:
```json
{
  "tool_name": "kreis_flaeche",
  "parameters": {
    "flaeche": ["target", "50 cm²", "target"],
    "radius": ["5 cm", "10 cm", "15 cm"],
    "durchmesser": ["10 cm", "target", "30 cm"]
  }
}
```
Dies berechnet 3 separate Kreise:
- Index 0: flaeche=target, radius=5cm, durchmesser=10cm
- Index 1: flaeche=50cm², radius=10cm, durchmesser=target
- Index 2: flaeche=target, radius=15cm, durchmesser=30cm

❌ FALSCHE BATCH-FORMATE:
```json
// FALSCH: Gemischte Listen und Einzelwerte
{
  "flaeche": "target",
  "radius": ["5 cm", "10 cm"],
  "durchmesser": "20 cm"
}

// FALSCH: Unterschiedliche Listenlängen
{
  "flaeche": ["target", "target"],
  "radius": ["5 cm", "10 cm", "15 cm"],
  "durchmesser": ["20 cm"]
}
```

BATCH-ANTWORT-FORMAT:
```json
{
  "batch_mode": true,
  "total_calculations": 3,
  "successful": 3,
  "failed": 0,
  "results": [
    {
      "batch_index": 0,
      "input_combination": {...},
      "📊 ANALYTICAL SOLUTION": "...",
      "ergebnis": {...}
    },
    // ... weitere Ergebnisse
  ]
}
```



✅ KORREKTE TARGET-WORKFLOW BEISPIELE:
• Wanddicke berechnen: {"pressure": "100 bar", "wall_thickness": "target", "diameter": "500 mm", "allowable_stress": "200 MPa"}
• Durchmesser berechnen: {"pressure": "15 bar", "wall_thickness": "8 mm", "diameter": "target", "allowable_stress": "160 MPa"}
• Druck berechnen: {"pressure": "target", "wall_thickness": "10 mm", "diameter": "800 mm", "allowable_stress": "140 MPa"}

"""
)

# ===== DIREKTE META-TOOL-REGISTRIERUNG =====

# Import der Meta-Tool-Module (mit importlib für numerische Präfixe)
import importlib
import tools.Meta.clock as clock_module
list_engineering_tools_module = importlib.import_module("tools.Meta.1_list_engineering_tools")
get_tool_details_module = importlib.import_module("tools.Meta.2_get_tool_details")
call_tool_module = importlib.import_module("tools.Meta.3_call_tool")

# Registriere Clock-Tool (automatische Metadaten-Extraktion)
@mcp.tool(
    name=clock_module.TOOL_METADATA["name"],
    description=clock_module.TOOL_METADATA["description"]
)
def clock_tool() -> str:
    return clock_module.clock()

# Registriere List Engineering Tools
@mcp.tool(
    name=list_engineering_tools_module.TOOL_METADATA["name"],
    description=list_engineering_tools_module.TOOL_METADATA["description"]
)
async def list_engineering_tools_tool(tags: List[str], ctx: Context = None) -> Dict:
    # Diese Funktion braucht nur tags Parameter
    return list_engineering_tools_module.list_engineering_tools(tags=tags)

# Registriere Get Tool Details
@mcp.tool(
    name=get_tool_details_module.TOOL_METADATA["name"],
    description=get_tool_details_module.TOOL_METADATA["description"]
)
async def get_tool_details_tool(tool_name: str = "", ctx: Context = None) -> Dict:
    # Reine Weiterleitung - alle Logik in Meta-Tool
    return await get_tool_details_module.get_tool_details(tool_name=tool_name)

# Registriere Call Tool
@mcp.tool(
    name=call_tool_module.TOOL_METADATA["name"],
    description=call_tool_module.TOOL_METADATA["description"]
)
async def call_tool_tool(tool_name: str = "", parameters: Dict[str, Any] = {}, ctx: Context = None) -> Dict:
    # Reine Weiterleitung - alle Logik in Meta-Tool
    return await call_tool_module.call_tool(tool_name=tool_name, parameters=parameters)

async def init_all_tools():
    """Initialisiert Engineering-Tools"""
    
    # Entdecke Engineering-Tools (bleiben in separater Registry)
    engineering_count = await discover_engineering_tools()
    
    # Tag-System validieren (nach Discovery, um Circular Imports zu vermeiden)
    try:
        from engineering_mcp.tag_definitions import validate_tag_system, get_tag_statistics, get_tag_definitions, clear_tag_cache
        
        # Cache leeren um aktuelle Änderungen zu erkennen
        clear_tag_cache()
        
        print("\n🏷️ TAG-SYSTEM ANALYSE:")
        print("=" * 50)
        
        # Hole detaillierte Statistiken
        stats = get_tag_statistics()
        print(f"📊 STATISTIKEN:")
        print(f"   Gesamt Tags im System: {stats['total_tags']}")
        print(f"   Bekannte Tag-Beschreibungen: {stats['known_tags']}")
        print(f"   Unbekannte Tags: {stats['unknown_tags']}")
        print(f"   Gesamt Tools kategorisiert: {stats['total_tools']}")
        
        # Zeige TOP Tags
        print(f"\n🔝 TOP VERWENDETE TAGS:")
        for tag, count in stats['most_used_tags'][:8]:  # Top 8 zeigen
            print(f"   {tag}: {count} Tools")
        
        # Hole Tag-Definitionen für Details
        definitions = get_tag_definitions()
        
        # Zeige aktive Tag-Kategorien
        active_tags = {tag: info for tag, info in definitions.items() if info['tool_count'] > 0}
        print(f"\n📂 AKTIVE TAG-KATEGORIEN ({len(active_tags)}):")
        for tag, info in sorted(active_tags.items(), key=lambda x: x[1]['tool_count'], reverse=True):
            tools_preview = ', '.join(info['tools'][:3])
            if len(info['tools']) > 3:
                tools_preview += f" ... (+{len(info['tools'])-3} weitere)"
            print(f"   ✅ {tag} ({info['tool_count']}): {tools_preview}")
        
        # Validierungswarnungen
        warnings = validate_tag_system()
        if warnings:
            print(f"\n⚠️ VALIDIERUNG:")
            for warning in warnings:
                print(f"   {warning}")
        else:
            print(f"\n✅ VALIDIERUNG: Alle Tags korrekt definiert")
        
        print("")  # Leerzeile für bessere Lesbarkeit
        
    except Exception as e:
        print(f"⚠️ Tag-System Analyse fehlgeschlagen: {e}")
    
    # Meta-Tools sind bereits bei Import registriert worden
    meta_count = 4  # clock, list_engineering_tools, get_tool_details, call_tool
    
    # Zeige Gesamtübersicht
    total_tools = meta_count + engineering_count
    print(f"✅ {meta_count} Meta-Tools direkt registriert")
    print(f"✅ {engineering_count} Engineering-Tools entdeckt")
    print(f"🎯 Server bereit: {total_tools} Tools verfügbar")
    print(f"   • {meta_count} Meta-Tools (direkt verfügbar)")
    print(f"   • {engineering_count} Engineering-Tools (über call_tool)")
    print(f"🎯 3-stufiger Discovery-Workflow aktiviert:")
    print(f"   1. 1_list_engineering_tools")  
    print(f"   2. 2_get_tool_details")
    print(f"   3. 3_call_tool")
    
    return total_tools

# Server-Initialisierung
if __name__ == "__main__":
    import asyncio
    asyncio.run(init_all_tools()) 