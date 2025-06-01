"""
Test script to verify MCP endpoints
"""
import requests
import json
from time import sleep

# Base URLs
LOCAL_URL = "http://localhost:8080"
RAILWAY_URL = "https://web-production-3666.up.railway.app"

def test_endpoint(base_url, path):
    """Test a single endpoint"""
    url = f"{base_url}{path}"
    print(f"\n📍 Testing: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
            except:
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_mcp_protocol(base_url):
    """Test MCP protocol initialization"""
    url = f"{base_url}/mcp"
    print(f"\n🔧 Testing MCP Protocol at: {url}")
    
    # MCP initialization request
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
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
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    # Test local if running
    print("=" * 50)
    print("🧪 ENDPOINT TESTS")
    print("=" * 50)
    
    # Test Railway deployment
    print("\n🚀 Testing Railway deployment...")
    
    endpoints = ["/", "/health", "/mcp/", "/sse/", "/mcp", "/sse"]
    
    for endpoint in endpoints:
        test_endpoint(RAILWAY_URL, endpoint)
        sleep(0.5)  # Avoid rate limiting
    
    # Test MCP protocol
    test_mcp_protocol(RAILWAY_URL)

if __name__ == "__main__":
    main() 