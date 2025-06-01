from fastmcp import FastMCP
import datetime

mcp = FastMCP(name="demo-mcp", instructions="Einfacher Test-Server")

@mcp.tool()
def echo(msg: str) -> str:
    "Gibt die Nachricht unverändert zurück"
    return msg

@mcp.tool()
def clock() -> str:
    "Aktuelle UTC-Zeit zurückgeben"
    return datetime.datetime.utcnow().isoformat() + "Z" 