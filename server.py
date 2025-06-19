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
# Engineering Calculation Server - geprüfte Berechnungstools, Tabellenwerke und Informationen für Ingenieure

## SYSTEMÜBERSICHT:
Dieser Server bietet Zugriff auf eine spezialisierte Engineering-Tool-Bibliothek mit symbolischen und numerischen Berechnungstools für den Bereich Maschinenbau. Ebenso werden normkonforme Berechnungen nach DIN und weiteren Normen, sowie Tabellenwerke und Informationstexte bereitgestellt.

## 3-STUFIGER WORKFLOW:
Der Server implementiert einen Discovery-to-Execution-Workflow:

1. DISCOVERY: '1_list_engineering_tools(tags=[...])' ← EINSTIEGSPUNKT
   ÜBERSICHTSMODUS: Zeigt name, short_description, tags pro Tool
   KEINE vollständigen Beschreibungen oder Parameter (diese ist zu finden unter: 2_get_tool_details)
   
   TAG-FILTER BEISPIELE:
   - tags=[""] für eine vollständige Übersicht aller verfügbaren Tags.
   - tags=["all"] für vollständige Tool-Übersicht
   - tags=["elementar"] zeigt Tools einer Kategorie
   - tags=["elementar","meta"] Aufruf mit mehreren Tags möglich - zeigt Tools der angegebenen Tags/Kategorien
    

   WORKFLOW-PFLICHT: Muss mindestens einmal pro Konversation (zu Beginn) ausgeführt werden, um verfügbare Toolnamen zu erhalten. Dieses Tool kann nur mir korrekten TAG-Definitionen aufgerufen werden. Um alle verfügbaren Tags zu erhalten,  rufe dieses Tool ohne Parameter / bzw mit "leerem" Paramter auf (tags=[""]). Rate niemals TAGS, um dieses Tool aufzurufen. Du musst die verfügbaren Tags (erhältlich durch den Aufruf mit leerem Tag-Paramter) verwenden.

2. DOKUMENTATION: '2_get_tool_details(tool_name)'
   - PFLICHT vor jeder Tool-Ausführung (mindestens einmal pro Sitzung, zur Freischaltung des Tools)
   - Aktiviert Tool für Ausführung (Whitelist-System)
   - Liefert vollständige Parameter-Dokumentation
   - Zeigt Anwendungsbeispiele und Einheiten-Anforderungen

   WORKFLOW-PFLICHT: Muss mindestens einmal pro Konversation jeweils pro Tool ausgeführt werden, um die verfügbaren Tooldetails zu erhalten und das entsprechende Tool für die Benutzung freizuschalten.
   Führe dieses Tool ebenso aus, wenn Du bei der Benutzung von 3_call_tool() eine Fehlermeldung erhältst.

3. EXECUTION: '3_call_tool(tool_name, parameters)'
  
   - Mit diesem Tool führst Du Berechnungen aus, oder fragst Informationen ab !
   - Nur freigeschaltete Tools können ausgeführt werden
   - Bevor Du ein Tool mittels 3_call_tool(tool_name, parameters) verwendest, musst Du mindestens einmal pro Sitzung das tool 2_get_tool_details mit diesem Toolnamen verwenden, um es freizuschalten und Informationen zur Benutzung zu erhalten.
   - Berechnungstools mit has_solving= "symbolic", oder "numeric", oder "symbolic/numeric" verwendet einen Zielparameter, der mit "target" gekennzeichnet ist. Dieser Zielparameter wird symbolisch aufgelöst und numerisch berechnet. Hierdurch können die hinterlegten Formeln nach beliebigen Parametern aufgelöst werden. Du musst bei jedem Aufruf genau einen Zielparameter mit "target" kennzeichnen.
   - Berechnungstools mit has_solving= "symbolic", oder "numeric", oder "symbolic/numeric" bietet die Möglichkeit der Batchverarbeitung, um gleichzeitig mehrere Ergebnissätze zu berechnen. Siehe hierzu Kapitel: "Batchberechnung".



## BERECHNUNGSARTEN (has_solving Parameter):

  Alle Berechngstools verfügen über den Paramter "has_solving", mit folgenden Optionen:

  • "symbolic" - Alle Parameter analytisch lösbar durch geschlossene Formeln (SymPy-basiert, schnell & exakt)
  • "numeric" - Alle Parameter numerisch lösbar durch Iterationsverfahren (mit Fehlerabschätzung & Konvergenzprüfung)
  • "symbolic/numeric" - Gemischte Methoden: verschiedene Parameter verwenden unterschiedliche Berechnungsarten
  • "none" - Keine Berechnungslogik, nur Information/Datenbank-Zugriff (Tabellen, Normwerte, etc.)

  Du erkennst die Berechnungsart jedes Tools an dem Parameter "has_solving" in der Tool-Dokumentation.
  Jedes Berechnungstool mit has_solving= "symbolic", oder "numeric", oder "symbolic/numeric" bietet die Möglichkeit der Batchberechnung, um gleichzeitig mehrere Ergebnissätze zu berechnen. Siehe hierzu Kapitel: "Batchberechnung".
  Jedes Berechnungstools mit has_solving= "symbolic", oder "numeric", oder "symbolic/numeric" verwendet einen Zielparameter, der mit "target" gekennzeichnet ist. Dieser Zielparameter wird symbolisch aufgelöst und numerisch berechnet. Hierdurch können die hinterlegten Formeln nach beliebigen Parametern aufgelöst werden.

  KORREKTE TARGET-WORKFLOW BEISPIELE:
  • Wanddicke berechnen: {"pressure": "100 bar", "wall_thickness": "target", "diameter": "500 mm", "allowable_stress": "200 MPa"}
  • Durchmesser berechnen: {"pressure": "15 bar", "wall_thickness": "8 mm", "diameter": "target", "allowable_stress": "160 MPa"}
  • Druck berechnen: {"pressure": "target", "wall_thickness": "10 mm", "diameter": "800 mm", "allowable_stress": "140 MPa"}



## KRITISCHE TECHNISCHE ANFORDERUNGEN:

- Tools verwenden vollständige Parameter-Sets mit Zielparameter-Kennzeichnung (target)
- ALLE Parameter sind required: bekannte Werte + Zielparameter = "target"
- Beispiel: Kesselformel σ = p·d/(2·s) → {"pressure": "100 bar", "diameter": "500 mm", "wall_thickness": "target", "allowable_stress": "200 MPa"}
- Der Zielparameter wird symbolisch aufgelöst und numerisch berechnet
- Verwende IMMER SymPy-kompatible symbolische Eingaben

### EINHEITEN-OBLIGATION:
  - ALLE numerischen Parameter MÜSSEN physikalische Einheiten enthalten, es sei denn, in der Tool_description wird explizit auf einen Parameter OHNE Einheiten hingewiesen (zum Beispiel: "Anzahl Schrauben" - zu verwenden ohne Einheiten)
  - Format: "Wert Einheit" (z.B. "100 bar", "50 mm", "200 MPa")

### SICHERHEITS-ARCHITEKTUR:
  - Whitelist-basiertes Freischaltungssystem (Freischaltung des Tools durch 2_get_tool_details)
  - Rate-Limiting (max. 50 Aufrufe pro Tool/Minute)
  - Tools bleiben ohne 2_get_tool_details() deaktiviert

### PARAMETER-EINGABE FÜR 3_call_tool:
  KRITISCHES PARAMETER-FORMAT - STRIKT EINHALTEN:

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



## Batchberechnungen

  Alle Engineering-Tools mit dem Parameter "has_solving" = "symbolic" oder "numeric" oder beide unterstützen die Batch-Verarbeitung für Massenberechnungen! Du kannst viele Paramtersätze auf einmal berechnen (hunderte ... tausende).

  KRITISCHE BATCH-REGELN:
  • ALLE Parameter müssen Listen gleicher Länge sein
  • Jeder Index repräsentiert einen vollständigen Parametersatz
  • Jeder Parametersatz braucht genau einen 'target'
  • Keine Mischung von Listen und Einzelwerten erlaubt

  KORREKTES BATCH-FORMAT:
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


## Paralleler Toolaufruf

  Wenn Dir der Toolname und die Tool-Details eines Tools bekannt sind, so kannst Du dieses Tool mehrfach direkt hintereinander aufrufen (parallele Aufrufe), ohne dass du andere Tools verwenden musst. Beachte jedoch, dass alle Berechnungstools die Batch-Verarbeitung zur Berechnung mehrerer Ergebnissätze unterstützten. Die Batchverarbeitung ist immer dem parallelen Toolaufruf vorzuziehen. Fordert der Benutzer explizit parallele Toolaufrufe, so führe diese aus.


"""
)

# ===== DIREKTE META-TOOL-REGISTRIERUNG =====

# Import der Meta-Tool-Module (mit importlib für numerische Präfixe)
import importlib
import tools.Meta.clock as clock_module
server_informations_module = importlib.import_module("tools.Meta.0_Server_Informations")
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

# Registriere Server Informations Tool
@mcp.tool(
    name=server_informations_module.TOOL_METADATA["name"],
    description=server_informations_module.TOOL_METADATA["description"]
)
def server_informations_tool() -> Dict:
    return server_informations_module.server_informations()

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
    meta_count = 5  # clock, server_informations, list_engineering_tools, get_tool_details, call_tool
    
    # Zeige Gesamtübersicht
    total_tools = meta_count + engineering_count
    print(f"✅ {meta_count} Meta-Tools direkt registriert")
    print(f"✅ {engineering_count} Engineering-Tools entdeckt")
    print(f"🎯 Server bereit: {total_tools} Tools verfügbar")
    print(f"   • {meta_count} Meta-Tools (direkt verfügbar)")
    print(f"   • {engineering_count} Engineering-Tools (über call_tool)")
    print(f"🎯 3-stufiger Discovery-Workflow aktiviert:")
    print(f"   0. 0_Server_Informations (Serverdokumentation)")
    print(f"   1. 1_list_engineering_tools")  
    print(f"   2. 2_get_tool_details")
    print(f"   3. 3_call_tool")
    
    return total_tools

# Server-Initialisierung
if __name__ == "__main__":
    import asyncio
    asyncio.run(init_all_tools()) 