"""MCP-specific exceptions."""


class MCPError(Exception):
    """Base exception for MCP-related errors."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class MCPConnectionError(MCPError):
    """Exception raised when MCP connection fails."""
    pass


class MCPToolError(MCPError):
    """Exception raised when MCP tool execution fails."""
    pass


class MCPTimeoutError(MCPError):
    """Exception raised when MCP request times out."""
    pass


class MCPValidationError(MCPError):
    """Exception raised when MCP response validation fails."""
    pass
