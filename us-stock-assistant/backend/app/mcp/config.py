"""MCP configuration."""

from typing import Optional
from pydantic import BaseModel, Field


class MCPConfig(BaseModel):
    """Configuration for MCP client."""
    
    server_url: str = Field(..., description="MCP server URL")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    timeout: int = Field(10, description="Request timeout in seconds")
    retry_attempts: int = Field(2, description="Number of retry attempts")
    retry_delay: float = Field(0.5, description="Initial retry delay in seconds")
    max_retry_delay: float = Field(60.0, description="Maximum retry delay in seconds")
    pool_size: int = Field(10, description="Connection pool size")
    
    class Config:
        frozen = True
