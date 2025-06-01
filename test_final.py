"""
Final test script for Railway MCP deployment
"""
import requests
import json
from time import sleep

BASE_URL = "https://web-production-3666.up.railway.app"

def test_endpoint(path, method="GET", data=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"
    print(f"\n📍 {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=data, headers=headers, timeout=5)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            if response.headers.get("content-type", "").startswith("application/json"):
                print(f"   Response: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"   Response: {response.text}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    print("=" * 60)
    print("🧪 FINAL MCP SERVER TEST")
    print("=" * 60)
    
    # Test 1: Health check (Railway requirement)
    test_endpoint("/health")
    sleep(0.5)
    
    # Test 2: Root endpoint
    test_endpoint("/")
    sleep(0.5)
    
    # Test 3: MCP initialization
    mcp_init_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "0.1.0",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    test_endpoint("/mcp", method="POST", data=mcp_init_data)
    
    print("\n" + "=" * 60)
    print("✅ If /health returns 'OK', Railway deployment is successful!")
    print("✅ If /mcp POST returns JSON-RPC response, MCP is working!")
    print("=" * 60)

if __name__ == "__main__":
    main() 