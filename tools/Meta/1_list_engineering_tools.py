#!/usr/bin/env python3
"""
List Engineering Tools Meta-Tool

Listet verfügbare Engineering-Tools auf - der Einstiegspunkt für Tool-Discovery.
Erster Schritt im 3-stufigen Discovery-Workflow.
"""

from typing import Dict, List, Annotated
from pydantic import Field
import asyncio
from engineering_mcp.registry import get_tool_info_for_llm, discover_engineering_tools, _ENGINEERING_TOOLS_REGISTRY

# Tag-Definitionen werden LAZY geladen um Circular Imports zu vermeiden

def _get_available_tags() -> List[str]:
    """
    Dynamische Generierung aller verfügbaren Tags.
    
    Returns:
        List[str]: Alle verfügbaren Tags inklusive Spezial-Tags
    """
    try:
        # LAZY LOADING: Importiere erst hier
        from engineering_mcp.tag_definitions import get_tag_definitions
        
        # Hole Tag-Definitionen
        tag_definitions = get_tag_definitions()
        available_tags = list(tag_definitions.keys())
        
        # Spezial-Tags hinzufügen
        special_tags = ["all"]
        available_tags.extend(special_tags)
        
        # Entferne Duplikate und sortiere
        available_tags = sorted(list(set(available_tags)))
        
        return available_tags
    except Exception:
        # Fallback bei Circular Import oder anderen Problemen
        return ["all", "unknown"]

def _create_dynamic_tags_field():
    """
    Erstellt ein dynamisches Field mit Tag-Beschreibungen aus tag_definitions.py.
    Verwendet OpenAI-kompatiblen Hybrid-Ansatz: enum + separate Beschreibungen.
    
    Returns:
        Field: Pydantic Field mit dynamischen Tag-Constraints und Beschreibungen
    """
    try:
        # LAZY LOADING: Importiere erst hier, nicht beim Modul-Import
        from engineering_mcp.tag_definitions import get_tag_definitions
        
        # Hole Tag-Definitionen
        tag_definitions = get_tag_definitions()
        available_tags = ["all"] + sorted(tag_definitions.keys())
        
        # Erstelle Beschreibungs-Mapping ohne Emojis
        tag_descriptions = {
            "all": "Complete overview - Shows all available Engineering tools (full library overview)"
        }
        
        # Füge Tag-Beschreibungen aus tag_definitions.py hinzu
        for tag_name, tag_data in tag_definitions.items():
            tag_descriptions[tag_name] = tag_data['description']
        
        return Field(
            description="REQUIRED: Tags for filtering tools with detailed descriptions from tag_definitions.py",
            min_length=1,
            max_items=10,
            examples=[
                ["all"], 
                ["elementar"], 
                ["mechanik"], 
                ["schrauben"], 
                ["thermodynamik"],
                ["strömungslehre"]
            ],
            title="Engineering Tool Filter Tags",
            json_schema_extra={
                "items": {
                    "enum": available_tags,  # OpenAI-compatible: Standard enum
                    "type": "string"
                },
                "uniqueItems": True,
                "tag_descriptions": tag_descriptions,  # Complete descriptions separately
                "tag_count": len(available_tags),
                "description_extended": "Each tag has a detailed description available in 'tag_descriptions'",
                "format": "engineering-tag-list-with-descriptions",
                "usage_hint": "Use ['all'] for complete overview or specific tags for filtered search"
            }
        )
        
    except Exception as e:
        # Fallback für Circular Import oder andere Probleme
        return Field(
            description="REQUIRED: Tags for tool filtering (WARNING: tag_definitions.py not available)",
            min_length=1,
            max_items=10,
            examples=[["all"], ["unknown"]],
            title="Engineering Tool Filter Tags (Degraded Mode)",
            json_schema_extra={
                "items": {
                    "enum": ["all", "unknown"],
                    "type": "string"
                },
                "uniqueItems": True,
                "degraded_mode": True,
                "issue": f"Tag definitions not available: {str(e)}"
            }
        )

# LAZY FIELD: Wird erst zur Laufzeit erstellt, nicht beim Import
def _get_tags_field():
    """Lazy Field Creator - wird erst aufgerufen wenn benötigt"""
    return _create_dynamic_tags_field()

def list_engineering_tools(
    tags: Annotated[List[str], _create_dynamic_tags_field()]
) -> List[Dict]:
    """
    Listet Engineering-Tools auf - entweder nach spezifischen Tags oder alle verfügbaren Tools.
    
    Args:
        tags: Liste der gewünschten Tags (z.B. ["elementar"] oder ["all"])
        
    Returns:
        List[Dict]: Liste der Tools mit Metadaten oder Fehlermeldung
    """
    # REGISTRY-CHECK: Stelle sicher dass Tools geladen sind
    if len(_ENGINEERING_TOOLS_REGISTRY) == 0:
        try:
            # Führe Tool-Discovery aus falls Registry leer ist
            asyncio.run(discover_engineering_tools())
        except Exception as e:
            return [
                {
                    "error": "REGISTRY_INITIALIZATION_ERROR",
                    "problem": f"Engineering-Tools konnten nicht geladen werden: {str(e)}",
                    "suggestion": "Server neu starten oder Tool-Verzeichnisse prüfen",
                    "workflow_step": "1/3 - System-Fehler"
                }
            ]
    
    # VALIDATION: Prüfe ob tags-Parameter korrekt verwendet wird
    if not tags or len(tags) == 0:
        # DYNAMIC TAG GENERATION für Fehlermeldung
        try:
            # LAZY LOADING: Importiere erst hier
            from engineering_mcp.tag_definitions import get_tag_definitions
            
            tag_definitions = get_tag_definitions()
            available_tag_names = ["all"] + sorted(tag_definitions.keys())
            
            # Erstelle dynamische Beispiele für correct_usage
            dynamic_examples = ["list_engineering_tools(tags=['all'])"]
            for tag_name in sorted(tag_definitions.keys())[:4]:  # Top 4 Tags als Beispiele
                dynamic_examples.append(f"list_engineering_tools(tags=['{tag_name}'])")
            
            # COMPLETE Tag-Dictionary mit ALLEN Beschreibungen
            complete_tag_descriptions = {
                "all": "Complete overview - Shows all available Engineering tools (full library overview)"
            }
            
            for tag_name, tag_data in tag_definitions.items():
                complete_tag_descriptions[tag_name] = tag_data["description"]
            
            # Dynamische Tag-Beispiele für bessere Übersicht (begrenzt für Lesbarkeit)
            tag_info = []
            for tag_name in sorted(tag_definitions.keys())[:6]:  # Top 6 für Übersicht
                description = tag_definitions[tag_name]["description"]
                tag_info.append(f"'{tag_name}' - {description}")
                
        except Exception:
            # Kein Fallback - explizit "unknown" verwenden
            available_tag_names = ["all", "unknown"]
            dynamic_examples = [
                "list_engineering_tools(tags=['all'])",
                "list_engineering_tools(tags=['unknown'])"
            ]
            complete_tag_descriptions = {
                "all": "Complete overview - Shows all available tools",
                "unknown": "WARNING: Tools without tag classification (tag_definitions.py problem)"
            }
            tag_info = [
                "'all' - Complete overview - Shows all available tools",
                "'unknown' - WARNING: Tools without tag classification"
            ]
        
        return [
            {
                "error": "INVALID_TOOL_USAGE", 
                "problem": "list_engineering_tools() ohne tags-Parameter aufgerufen",
                "required_parameter": "tags-Liste ist PFLICHT",
                "available_tags": available_tag_names,  # Quick overview of tag names
                "tag_descriptions": complete_tag_descriptions,  # COMPLETE dictionary with ALL descriptions
                "tag_examples": tag_info,  # Formatted examples for readability
                "recommendation": "Verwenden Sie tags=['all'] für vollständige Tool-Übersicht",
                "correct_usage": dynamic_examples,  # Dynamic examples
                "workflow_step": "1/3 - Ungültige Verwendung", 
                "next_action": "Rufen Sie list_engineering_tools(tags=['all']) auf oder wählen Sie einen bestimmten Tag",
                "workflow_info": {
                    "current_step": "Tool Discovery",
                    "required_format": "list_engineering_tools(tags=[...])",
                    "tip": "ENTRY POINT: Start here - Tags are directly available!"
                }
            }
        ]
    
    # Hole alle Tools von der Registry
    all_tools = get_tool_info_for_llm(include_engineering=True)
    
    # Filtere Tools nach gewünschten Tags
    result_tools = []
    for tool in all_tools:
        tool_tags = tool.get('tags', [])
        
        # Spezialbehandlung für "all"
        if "all" in tags:
            result_tools.append(tool)
        else:
            # Prüfe ob Tool einen der gewünschten Tags hat
            if any(tag in tool_tags for tag in tags):
                result_tools.append(tool)
    
    # ADDITIONAL VALIDATION: Warnung bei 0 gefundenen Tools (außer bei leerem System)
    if len(result_tools) == 0 and len(all_tools) > 0:
        # Es gibt Tools, aber keine passen zu den Tags
        try:
            # LAZY LOADING: Importiere Tag-Definitionen für vollständige Liste
            from engineering_mcp.tag_definitions import get_tag_definitions
            
            tag_definitions = get_tag_definitions()
            available_tag_names = ["all"] + sorted(tag_definitions.keys())
            
            # COMPLETE Tag-Dictionary mit ALLEN Beschreibungen
            complete_tag_descriptions = {
                "all": "Complete overview - Shows all available Engineering tools (full library overview)"
            }
            
            for tag_name, tag_data in tag_definitions.items():
                complete_tag_descriptions[tag_name] = tag_data["description"]
            
            # Formatierte Tag-Liste für bessere Lesbarkeit
            tag_info = ["'all' - Complete overview - Shows all available Engineering tools"]
            for tag_name in sorted(tag_definitions.keys()):
                description = tag_definitions[tag_name]["description"]
                tag_info.append(f"'{tag_name}' - {description}")
                
        except Exception:
            # Fallback bei Problemen
            available_tag_names = ["all", "unknown"]
            complete_tag_descriptions = {
                "all": "Complete overview - Shows all available tools",
                "unknown": "WARNING: Tools without tag classification (tag_definitions.py problem)"
            }
            tag_info = [
                "'all' - Complete overview - Shows all available tools",
                "'unknown' - WARNING: Tools without tag classification"
            ]
        
        return [
            {
                "warning": "NO_TOOLS_FOUND",
                "tags_searched": tags,
                "total_tools_available": len(all_tools),
                "message": f"Keine Tools für Tags gefunden: {tags}",
                "available_tags": available_tag_names,  # Liste aller verfügbaren Tag-Namen
                "tag_descriptions": complete_tag_descriptions,  # VOLLSTÄNDIGES Dictionary mit allen Beschreibungen
                "tag_examples": tag_info,  # Formatierte Beispiele für Lesbarkeit
                "suggestion": "Versuchen Sie andere Tags oder verwenden Sie tags=['all']",
                "immediate_action": "Versuchen Sie: list_engineering_tools(tags=['all'])",
                "workflow_step": "1/3 - Keine Treffer",
                "workflow_info": {
                    "current_step": "Tool Discovery - Keine passenden Tools gefunden",
                    "available_options": f"{len(available_tag_names)} Tags verfügbar",
                    "tip": "Prüfen Sie die verfügbaren Tags in 'tag_descriptions'"
                }
            }
        ]
    
    # STATUS für Workflow-Optimierung
    if len(result_tools) > 0:
        status = "SUCCESS"
        step = "1/3",  # Aktualisiert auf 3-Stufen-Workflow
        message = f"{len(result_tools)} Tools gefunden"
        workflow_guidance = [
            "1. list_engineering_tools(tags=[...]) <- Aktueller Schritt ABGESCHLOSSEN",
            "2. get_tool_details(tool_name='...') <- Nächster Schritt: Details für bestimmtes Tool",
            "3. call_tool(tool_name='...', parameters={...}) <- Abschließend: Tool ausführen"
        ]
    else:
        status = "NO_TOOLS"
        step = "1/3"
        message = "Keine Tools im System gefunden"
        workflow_guidance = ["System scheint leer - Tool-Installation prüfen"]
    
    # Usage hint generieren
    if len(result_tools) > 0:
        usage_hint = f"ERFOLG: {len(result_tools)} Tools gefunden."
    else:
        usage_hint = "INFO: Keine Tools gefunden - andere Tags verwenden oder tags=['all']"
    
    # OPTIMIZE TOOL OUTPUT für 3-Stufen-Workflow: Nur Übersichtsinformationen
    tools_output = []
    for tool in result_tools:
        # Nur grundlegende Infos für Schritt 1 - Details in Schritt 2
        tool_summary = {
            "name": tool["name"],
            "short_description": tool.get("short_description", ""),
            "tags": tool.get("tags", []),
            "has_solving": tool.get("has_solving", "symbolic")
            # REMOVED: "description" - wird nur in get_tool_details gezeigt
            # REMOVED: "solvable_variables" - wird nur in get_tool_details gezeigt
        }
        tools_output.append(tool_summary)
    
    # Response mit Workflow-Info
    return [
        {
            "status": status,
            "message": message,
            "step": step,
            "usage_hint": usage_hint,
            "workflow_guidance": workflow_guidance,
            "tools": tools_output,
            "total_count": len(result_tools),
            "tags_used": tags
        }
    ]

# Tool-Metadaten für Registry
TOOL_METADATA = {
    "name": "1_list_engineering_tools",
    "description": """Tool Discovery: Complete overview of available Engineering tools

MAIN FUNCTION: Lists all available tools by category/tag for selection
WORKFLOW: Step 1/3 -> then 2_get_tool_details -> then 3_call_tool  
START HERE: This is the entry point for all Engineering calculations!
MANDATORY: Required at least once per conversation before any other tool execution!""",
    "tags": ["meta"]  # CORRECTED Meta-Tool Tag added
}

 