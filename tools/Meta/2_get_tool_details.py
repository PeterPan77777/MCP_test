#!/usr/bin/env python3
"""
Get Tool Details Meta-Tool

Ruft detaillierte Informationen zu einem spezifischen Tool ab und schaltet es frei.
Dritter Schritt im Discovery-Workflow.
"""

from typing import Dict, Annotated, Optional
from pydantic import Field
from engineering_mcp.registry import get_tool_details as get_tool_details_from_registry
from tools.Meta.session_state import add_to_whitelist, get_call_count, increment_call_count

def _create_dynamic_tool_name_field():
    """
    Erstellt ein dynamisches Field für Tool-Namen mit erweiterten Constraints.
    
    Returns:
        Field: Pydantic Field mit Tool-Name-Validierung
    """
    return Field(
        description="REQUIRED: Name of the Engineering tool for detailed information (e.g. 'solve_kesselformel', 'solve_rechteck', 'durchgangsloecher_metrische_schrauben')",
        min_length=1,
        max_length=100,
        examples=["solve_kesselformel", "solve_rechteck", "area_rectangle", "volume_cylinder", "durchgangsloecher_metrische_schrauben"],
        title="Tool Name",
        json_schema_extra={
            "pattern": r"^[a-z_][a-z0-9_]*$",  # Snake-case Pattern
            "format": "tool-identifier",
            "description_extended": "Tool name must be in snake_case format (lowercase letters, numbers, underscores only)"
        }
    )

async def get_tool_details(
    tool_name: Annotated[str, _create_dynamic_tool_name_field()]
) -> Dict:
    """
    Ruft detaillierte Informationen zu einem spezifischen Tool ab und schaltet es für die Ausführung frei.
    
    Args:
        tool_name: Name des Tools für das Details abgerufen werden sollen
        
    Returns:
        Dict: Detaillierte Tool-Informationen oder Fehlermeldung
    """
    # VALIDATION: Prüfe ob tool_name-Parameter korrekt verwendet wird
    if not tool_name or tool_name.strip() == "":
        return {
            "error": "INVALID_TOOL_USAGE",
            "problem": "get_tool_details() called without tool_name parameter",
            "required_parameter": "tool_name is MANDATORY",
            "workflow_violation": "You may have skipped Step 1!",
            "correct_workflow": [
                "1. FIRST: list_engineering_tools(tags=['all']) -> Overview of all tools",
                "2. THEN: get_tool_details(tool_name='...') -> Details for specific tool",
                "3. FINALLY: call_tool(tool_name='...', parameters={...}) -> Execute tool"
            ],
            "immediate_action": "Call NOW: list_engineering_tools(tags=['all'])",
            "workflow_step": "2/3 - Invalid Usage",
            "why_list_first": "list_engineering_tools() shows you all available tools with tags and descriptions - so you can choose the right tool",
            "workflow_info": {
                "current_step": "Tool Documentation (skipped)",
                "missing_step": "Tool Discovery not performed",
                "tip": "ALWAYS discover tools first, then get details!"
            }
        }
    
    # Rate Limiting Check
    call_count = get_call_count(tool_name)
    if call_count >= 50:
        return {
            "error": "Rate Limit reached",
            "tool_name": tool_name,
            "limit_info": "Too many calls for this tool (max. 50 per minute)",
            "retry_after": "Wait until next minute"
        }
    
    try:
        details = await get_tool_details_from_registry(tool_name)
        
        # WHITELIST TOOL für call_tool
        add_to_whitelist(tool_name)
        increment_call_count(tool_name)
        
        # Erweitere Details um Ausführungs-Info
        details.update({
            "execution_unlocked": True,
            "next_step": f"Use call_tool(tool_name='{tool_name}', parameters={{...}}) for execution",
            "session_info": "Tool is now unlocked for this session",
            "workflow_step": "2/3"
        })
        
        # Füge Batch-Mode Informationen prominent hinzu, wenn unterstützt
        if details.get('batch_mode', {}).get('supported'):
            details['batch_mode_notice'] = {
                "feature": "🔄 BATCH-MODUS VERFÜGBAR",
                "benefit": "Verarbeitung mehrerer Parametersätze in einem Aufruf",
                "quick_tip": "Alle Parameter als Listen gleicher Länge → unbegrenzte Massenberechnungen",
                "see_details": "Weitere Informationen unter 'batch_mode' in den Tool-Details"
            }
        
        return details
        
    except ValueError as e:
        # Hilfreiche Fehlermeldung mit verfügbaren Tools
        from engineering_mcp.registry import get_tool_info_for_llm
        available_tools = list(get_tool_info_for_llm(include_engineering=True))
        tool_names = [tool["name"] for tool in available_tools]
        
        return {
            "error": str(e),
            "tool_name": tool_name,
            "hint": "Use list_engineering_tools(tags=['...']) to see available tools",
            "workflow_reminder": "1. list_engineering_tools -> 2. get_tool_details -> 3. call_tool"
        }

# Tool-Metadaten für Registry
TOOL_METADATA = {
    "name": "2_get_tool_details",
    "description": """
    Detailinformationen zu einem spezifischen Engineering‑Tool und Tool‑Freischaltung.
    Bevor Du ein Tool verwenden kannst, musst Du mindestens einmal pro Konversation 2_get_tool_details für dieses Tool aufrufen, um es freizuschalten.
""",
    "tags": ["meta"]
}

 