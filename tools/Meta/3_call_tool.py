#!/usr/bin/env python3
"""
Call Tool Meta-Tool

Führt Engineering-Tools aus mit ultra-toleranter Parameter-Reparatur.
Dritter und finaler Schritt im Discovery-Workflow.
"""

from typing import Dict, Any, Annotated, Optional, Union
from pydantic import Field, ValidationError
import json
import re
from engineering_mcp.registry import call_engineering_tool, _ENGINEERING_TOOLS_REGISTRY
from tools.Meta.session_state import is_whitelisted, increment_call_count, get_call_count

def _create_dynamic_tool_name_field():
    """
    Erstellt ein dynamisches Field für Tool-Namen.
    
    Returns:
        Field: Pydantic Field mit Tool-Name-Validierung
    """
    return Field(
        description="REQUIRED: Name of the Engineering tool to execute (e.g. 'solve_kesselformel', 'solve_rechteck', 'durchgangsloecher_metrische_schrauben')",
        min_length=1,
        max_length=100,
        examples=["solve_kesselformel", "solve_rechteck", "area_rectangle", "volume_cylinder"],
        title="Tool Name",
        json_schema_extra={
            "pattern": r"^[a-z_][a-z0-9_]*$",
            "format": "tool-identifier"
        }
    )

def _clean_parameter_value(value: Any) -> str:
    """
    Bereinigt Parameter-Werte von häufigen LLM-Syntax-Fehlern.
    
    Args:
        value: Roher Parameter-Wert
    
    Returns:
        str: Bereinigter Parameter-Wert
    """
    if value is None:
        return "target"
    
    # Konvertiere zu String
    str_value = str(value).strip()
    
    # Entferne Anführungszeichen
    str_value = str_value.strip("\"'")
    
    # Häufige Target-Varianten normalisieren
    target_variants = ["target", "TARGET", "Target", "null", "None", "undefined", ""]
    if str_value in target_variants:
        return "target"
    
    # Entferne überflüssige Leerzeichen
    str_value = re.sub(r'\s+', ' ', str_value)
    
    return str_value

def _repair_parameters(parameters: Dict[str, Any]) -> Dict[str, str]:
    """
    Repariert Parameter-Dictionary von häufigen LLM-Syntax-Fehlern.
    
    Args:
        parameters: Roh-Parameter vom LLM
        
    Returns:
        Dict[str, str]: Bereinigte Parameter
    """
    if not parameters:
        return {}
    
    repaired = {}
    for key, value in parameters.items():
        repaired[key] = _clean_parameter_value(value)
    
    return repaired

async def call_tool(
    tool_name: str,
    parameters: Dict[str, Any]
) -> Dict:
    """
    Führt Engineering-Tools mit ultra-toleranter Parameter-Reparatur aus.
    
    Args:
        tool_name: Name des auszuführenden Tools
        parameters: Tool-Parameter (werden automatisch repariert)
        
    Returns:
        Dict: Tool-Ergebnis oder Fehlermeldung
    """
    
    # VALIDATION 1: Prüfe auf fehlenden tool_name
    if not tool_name or tool_name.strip() == "":
        return {
            "error": "MISSING_TOOL_NAME", 
            "problem": "call_tool() called without tool_name parameter",
            "required_parameter": "tool_name is MANDATORY",
            "workflow_violation": "You may have skipped Step 1 and 2!",
            "correct_workflow": [
                "1. FIRST: list_engineering_tools(tags=['all']) -> Choose tool from list",
                "2. THEN: get_tool_details(tool_name='...') -> Get parameter info + unlock",
                "3. FINALLY: call_tool(tool_name='...', parameters={...}) -> Execute"
            ],
            "immediate_action": "Start with: list_engineering_tools(tags=['all'])",
            "workflow_step": "3/3 - Missing Tool Name",
            "helpful_hint": "Without tool discovery, no tool names are available"
        }
    
    # VALIDATION 2: Prüfe ob Tool existiert
    if tool_name not in _ENGINEERING_TOOLS_REGISTRY:
        available_tools = list(_ENGINEERING_TOOLS_REGISTRY.keys())
        # Suche nach ähnlichen Tool-Namen
        similar_tools = [t for t in available_tools if tool_name.lower() in t.lower() or t.lower() in tool_name.lower()]
        
        return {
            "error": "UNKNOWN_TOOL_NAME",
            "problem": f"Tool '{tool_name}' does not exist in the Engineering registry",
            "provided_tool_name": tool_name,
            "available_tools_count": len(available_tools),
            "similar_tools": similar_tools[:5] if similar_tools else [],
            "workflow_violation": "You may have skipped Step 1: Tool Discovery!",
            "required_step": "Call list_engineering_tools(tags=['all']) to see all available tools",
            "workflow_step": "3/3 - Invalid Tool Name",
            "correct_workflow": [
                "1. FIRST: list_engineering_tools(tags=['all']) -> Choose tool from list",
                "2. THEN: get_tool_details(tool_name='...') -> Get parameter info + unlock",
                "3. FINALLY: call_tool(tool_name='...', parameters={...}) -> Execute"
            ],
            "suggestion": "Use exact tool names from list_engineering_tools() output"
        }
    
    # VALIDATION 3: Prüfe auf fehlende oder leere parameters
    if not parameters or len(parameters) == 0:
        return {
            "error": "MISSING_PARAMETERS",
            "problem": "call_tool() called without parameters or with empty dictionary",
            "tool_name": tool_name,
            "required_parameter": "parameters dictionary is MANDATORY and must not be empty",
            "parameter_format": "All Engineering tools require parameters with units",
            "correct_format": f"call_tool(tool_name='{tool_name}', parameters={{'param1': 'target', 'param2': '100 unit'}})",
            "workflow_step": "3/3 - Missing Parameters",
            "help_action": f"Call get_tool_details(tool_name='{tool_name}') to see required parameters",
            "parameter_rules": [
                "All parameters must be provided",
                "Exactly one parameter set to 'target' (the value to solve for)",
                "All other parameters need units (e.g. '100 bar', '50 mm')"
            ]
        }
    
    # VALIDATION 4: Prüfe ob parameters ein Dictionary ist
    if not isinstance(parameters, dict):
        return {
            "error": "INVALID_PARAMETER_TYPE",
            "problem": f"Parameters must be a dictionary, got {type(parameters).__name__}",
            "tool_name": tool_name,
            "provided_parameters": parameters,
            "required_type": "dictionary (dict)",
            "correct_format": f"call_tool(tool_name='{tool_name}', parameters={{'param1': 'target', 'param2': '100 unit'}})",
            "workflow_step": "3/3 - Invalid Parameter Type",
            "help_action": f"Call get_tool_details(tool_name='{tool_name}') to see required parameters format",
            "format_examples": [
                "parameters={'pressure': 'target', 'diameter': '500 mm'}",
                "parameters={'area': 'target', 'width': '100 mm', 'height': '50 mm'}"
            ]
        }
    
    # Whitelist-Check
    if not is_whitelisted(tool_name):
        return {
            "error": "TOOL_NOT_UNLOCKED",
            "tool_name": tool_name,
            "problem": f"Tool '{tool_name}' not unlocked for execution",
            "required_step": f"Call get_tool_details(tool_name='{tool_name}') first to unlock tool",
            "security_reason": "Security measure: Tools must be explicitly unlocked before execution",
            "workflow_step": "3/3 - Security Block",
            "workflow_sequence": [
                "1. get_available_categories()",
                "2. list_engineering_tools(tags=['...'])",
                "3. get_tool_details(tool_name='...')",
                "4. call_tool(tool_name='...', parameters={...})"
            ]
        }
    
    # Rate Limiting
    call_count = get_call_count(tool_name)
    if call_count >= 20:  # Höher für call_tool da es der finale Schritt ist
        return {
            "error": "RATE_LIMIT_EXCEEDED",
            "tool_name": tool_name,
            "current_calls": call_count,
            "limit": 20,
            "retry_after": "Wait 60 seconds",
            "workflow_step": "3/3 - Rate Limited"
        }
    
    # Parameter-Reparatur
    repaired_parameters = _repair_parameters(parameters) if len(parameters) > 0 else {}
    
    # VALIDATION 5: Prüfe auf leere Parameter nach Reparatur
    if not repaired_parameters:
        return {
            "error": "EMPTY_PARAMETERS",
            "tool_name": tool_name,
            "problem": "Parameters provided but empty after processing",
            "original_parameters": parameters,
            "required": "All Engineering tools require meaningful parameters with units",
            "parameter_requirements": [
                "All parameters must be provided",
                "Exactly one parameter set to 'target' (the value to solve for)", 
                "All other parameters need units (e.g. '100 bar', '50 mm')"
            ],
            "correct_example": f"call_tool(tool_name='{tool_name}', parameters={{'param1': 'target', 'param2': '100 unit'}})",
            "help_action": f"Call get_tool_details(tool_name='{tool_name}') to see required parameters",
            "workflow_step": "3/3 - Empty Parameters"
        }
    
    try:
        # Führe Tool aus
        result = await call_engineering_tool(tool_name, repaired_parameters)
        increment_call_count(tool_name)
        
        # Erweitere Ergebnis um Ausführungs-Kontext
        if isinstance(result, dict):
            result.update({
                "execution_info": {
            "tool_name": tool_name,
                    "parameters_used": repaired_parameters,
                    "workflow_step": "3/3 - COMPLETED",
                    "status": "SUCCESS"
        }
            })
        
        return result
        
    except Exception as e:
        return {
            "error": "TOOL_EXECUTION_ERROR",
            "tool_name": tool_name,
            "message": str(e),
            "parameters_tried": repaired_parameters,
            "suggestion": f"Check parameter format - all values need units except 'target'",
            "workflow_step": "3/3 - Execution Error"
        }

# Tool-Metadaten für Registry
TOOL_METADATA = {
    "name": "3_call_tool",
    "description": """STEP 3/3: Executes Engineering tools with automatic parameter repair.

WORKFLOW: Final execution step after tool discovery and unlocking
SECURITY: Only executes tools unlocked via get_tool_details()
PARAMETER FORMAT: All values require units (e.g. "100 bar", "50 mm", "target")
USAGE: All parameters must be provided with exactly one set to "target" (the value to solve for)
HELP: For questions about tool usage, call get_tool_details() first to get parameter information""",
    "tags": ["meta"]
} 