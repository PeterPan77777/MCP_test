#!/usr/bin/env python3
"""
Test-Script für tolerante execute_tool Funktion
Testet automatische LLM-Fehler-Reparatur bei Tool-Aufrufen
"""

import asyncio
import json
from server import execute_tool, dispatch_engineering, _repair_arguments

async def test_tolerant_execute():
    """Testet verschiedene LLM-Fehler-Szenarien"""
    
    print("🧪 TEST: Tolerante Execute-Tool-Funktion")
    print("=" * 60)
    
    # Zuerst Pressure-Domain aktivieren
    print("\n1️⃣ Domain aktivieren...")
    activation = await dispatch_engineering("pressure", "activate")
    print(f"   ✅ {activation['message']}")
    
    # ===== TEST-SZENARIEN =====
    test_cases = [
        {
            "name": "✅ Normaler JSON-Call",
            "tool_name": "pressure.solve_kesselformel",
            "parameters": {"p": 10, "d": 100, "sigma": 160}
        },
        {
            "name": "🔧 Python-dict-Syntax (= statt :)",
            "tool_name": "pressure.solve_kesselformel", 
            "parameters": "{p=10, d=100, sigma=160}"
        },
        {
            "name": "🔧 Einfache Anführungszeichen",
            "tool_name": "pressure.solve_kesselformel",
            "parameters": "{'p': 10, 'd': 100, 'sigma': 160}"
        },
        {
            "name": "🔧 Python-Bools (ignoriert validate)",
            "tool_name": "pressure.solve_kesselformel",
            "parameters": {"p": 10, "d": 100, "s": 5}  # Nur gültige Parameter
        },
        {
            "name": "🔧 Code-Fence-wrapped JSON",
            "tool_name": "pressure.solve_kesselformel",
            "parameters": '```json\n{"p": 10, "d": 100, "sigma": 160}\n```'
        },
        {
            "name": "🔧 JSON-String als Parameter",
            "tool_name": "pressure.solve_kesselformel",
            "parameters": '{"p": 10, "d": 100, "sigma": 160}'
        },
        {
            "name": "🔧 Unquoted keys mit Doppelpunkt", 
            "tool_name": "pressure.solve_kesselformel",
            "parameters": "{p: 10, d: 100, sigma: 160}"
        },
        {
            "name": "🔧 Mixed Python/Assignment Syntax",
            "tool_name": "pressure.solve_kesselformel",
            "parameters": "{pressure=10, diameter: 100, sigma=160}"
        },
        {
            "name": "❌ Komplett invalide Parameter",
            "tool_name": "pressure.solve_kesselformel",
            "parameters": "This is not valid JSON or dict syntax at all!"
        },
        {
            "name": "❌ Nicht-aktiviertes Tool",
            "tool_name": "geometry.solve_circle_area",
            "parameters": {"radius": 10}
        }
    ]
    
    # Tests ausführen
    print(f"\n🧪 Führe {len(test_cases)} Test-Szenarien aus...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print(f"   Tool: {test_case['tool_name']}")
        print(f"   Params: {test_case['parameters']}")
        
        try:
            result = await execute_tool(
                tool_name=test_case['tool_name'],
                parameters=test_case['parameters']
            )
            
            # Ergebnis analysieren
            if "error" in result:
                print(f"   ❌ Fehler: {result['error']}")
                if "hint" in result:
                    print(f"   💡 Hinweis: {result['hint']}")
            else:
                print(f"   ✅ Erfolg!")
                if "result" in result:
                    print(f"   📊 Ergebnis: {result['result']} {result.get('unit', '')}")
                if "execution_status" in result:
                    print(f"   🔧 Status: {result['execution_status']}")
        
        except Exception as e:
            print(f"   💥 Exception: {e}")
        
        print()
    
    print("=" * 60)
    print("✅ Tolerante Execute-Tool Tests abgeschlossen!")

async def test_repair_function():
    """Testet die _repair_arguments Funktion direkt"""
    
    print("\n🔧 TEST: _repair_arguments Funktion")
    print("=" * 60)
    
    repair_tests = [
        {
            "name": "Python-dict mit =",
            "input": "{p=10, d=100, sigma=160}",
            "expected_keys": ["p", "d", "sigma"]
        },
        {
            "name": "Code-fence JSON",
            "input": "```json\n{\"radius\": 10}\n```",
            "expected_keys": ["radius"]
        },
        {
            "name": "Python-bool",
            "input": "{'active': True, 'debug': False, 'value': None}",
            "expected_keys": ["active", "debug", "value"]
        },
        {
            "name": "Einfache Anführungszeichen",
            "input": "{'key': 'value', 'number': 42}",
            "expected_keys": ["key", "number"]
        },
        {
            "name": "Unquoted keys mit Doppelpunkt",
            "input": "{p: 10, d: 100, sigma: 160}",
            "expected_keys": ["p", "d", "sigma"]
        },
        {
            "name": "Mixed unquoted/Python-bool",
            "input": "{active: True, count: 42, name: test}",
            "expected_keys": ["active", "count", "name"]
        },
        {
            "name": "Komplexer mixed case",
            "input": "{pressure=10, diameter: 100, sigma=160, validate: True}",
            "expected_keys": ["pressure", "diameter", "sigma", "validate"]
        }
    ]
    
    for i, test in enumerate(repair_tests, 1):
        print(f"{i}. {test['name']}")
        print(f"   Input: {test['input']}")
        
        try:
            repaired = _repair_arguments(test['input'])
            print(f"   Output: {repaired}")
            
            # Prüfe erwartete Keys
            has_keys = all(key in repaired for key in test['expected_keys'])
            print(f"   ✅ Keys vorhanden: {has_keys}")
            
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
        
        print()

async def main():
    """Hauptfunktion für alle Tests"""
    print("🧪 TOLERANTE MCP-SERVER TESTS")
    print("Testet automatische LLM-Fehler-Reparatur\n")
    
    # Reparatur-Funktion testen
    await test_repair_function()
    
    # Execute-Tool testen
    await test_tolerant_execute()

if __name__ == "__main__":
    asyncio.run(main()) 