#!/usr/bin/env python3
"""
Server Informations Meta-Tool

Stellt umfassende Informationen über die korrekte Verwendung des MCP Engineering Servers bereit.
Einstiegspunkt für neue Benutzer und Referenz für den korrekten Workflow.
"""

from typing import Dict

def server_informations() -> Dict:
    """
    Gibt vollständige Serverinformationen und Nutzungsanweisungen zurück.
    
    Returns:
        Dict: Umfassende Serverdokumentation mit Workflow-Anweisungen
    """
    
    server_info = """# Engineering Calculation Server - geprüfte Berechnungstools, Tabellenwerke und Informationen für Ingenieure

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

  Wenn Dir der Toolname und die Tool-Details eines Tools bekannt sind, so kannst Du dieses Tool mehrfach direkt hintereinander aufrufen (parallele Aufrufe), ohne dass du andere Tools verwenden musst. Beachte jedoch, dass alle Berechnungstools die Batch-Verarbeitung zur Berechnung mehrerer Ergebnissätze unterstützten. Die Batchverarbeitung ist immer dem parallelen Toolaufruf vorzuziehen. Fordert der Benutzer explizit parallele Toolaufrufe, so führe diese aus."""

    return {
        "status": "SUCCESS",
        "server_documentation": server_info,
        "quick_start_guide": {
            "step_1": "Verwende 1_list_engineering_tools(tags=['']) um alle verfügbaren Tags zu sehen",
            "step_2": "Dann 1_list_engineering_tools(tags=['all']) für vollständige Tool-Übersicht",
            "step_3": "Wähle ein Tool und rufe 2_get_tool_details(tool_name='...') auf",
            "step_4": "Führe das Tool mit 3_call_tool(tool_name='...', parameters={...}) aus"
        },
        "critical_reminders": [
            "Alle Parameter brauchen Einheiten (z.B. '100 bar', '50 mm')",
            "Genau ein Parameter muss 'target' sein",
            "Tools müssen vor Ausführung freigeschaltet werden",
            "Batch-Mode für Massenberechnungen verfügbar"
        ],
        "tool_type": "meta",
        "workflow_position": "0/3 - Serverinformationen und Einstiegshilfe"
    }

# Tool-Metadaten für Registry
TOOL_METADATA = {
    "name": "0_Server_Informations",
    "description": """MCP Engineering Server - Vollständige Nutzungsanleitung

    Dieses Tool muss zu Beginn jeder Konversation mindestens einmal aufgerufen werden, um die korrekte Verwendung des Servers zu erfahren!

Umfassende Dokumentation der korrekten Server-Verwendung
Rufe dieses Tool zu Beginn jeder Konversation mindestens einmal auf, um die korrekte Verwendung des Servers zu erfahren.
Wenn Du dieses Tool bereits aufgerufen hast und der Inhalt noch in Deinem Gedächtnis ist, rufe dieses Tool nicht erneut auf.
AUFRUF: Parameterlos - server_informations()""",
    "tags": ["meta"]
}
