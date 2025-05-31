#!/usr/bin/env python3
"""
Entry point für DigitalOcean Deployment
"""
from app.main import mcp
import uvicorn

if __name__ == "__main__":
    # FastMCP direkt mit streamable-http Transport starten
    # Port 8080 für DigitalOcean
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8080
    ) 