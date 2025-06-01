"""
Server-Konfiguration für Engineering MCP
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """Zentrale Server-Konfiguration"""
    server_name: str = Field(default="EngineersCalc", description="Server-Name für MCP")
    debug: bool = Field(default=False, description="Debug-Modus aktivieren")
    port: int = Field(default=8080, description="Server-Port")
    host: str = Field(default="0.0.0.0", description="Server-Host")
    
    class Config:
        env_prefix = "MCP_"


def get_server_config() -> ServerConfig:
    """
    Lädt Server-Konfiguration aus Umgebungsvariablen.
    
    Returns:
        ServerConfig: Konfigurierte Server-Einstellungen
    """
    return ServerConfig(
        server_name=os.getenv("SERVER_NAME", "EngineersCalc"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        port=int(os.getenv("PORT", "8080")),
        host=os.getenv("HOST", "0.0.0.0")
    ) 