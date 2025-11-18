"""MCP client for communicating with MCP servers via HTTP."""

import httpx
import logging
from typing import Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for communicating with MCP servers over HTTP (StreamableHTTP transport)."""
    
    def __init__(self, server_url: str, timeout: float = 30.0):
        """
        Initialize MCP client.
        
        Args:
            server_url: Base URL of the MCP server (e.g., http://localhost:4001/mcp)
            timeout: Request timeout in seconds
        """
        self.server_url = server_url
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        self._request_id = 0
        
    def _get_next_id(self) -> int:
        """Get next request ID."""
        self._request_id += 1
        return self._request_id
    
    def list_tools(self) -> list[dict[str, Any]]:
        """
        List available tools from the MCP server.
        
        Returns:
            List of tool definitions
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "tools/list"
        }
        
        logger.info(f"Listing tools from {self.server_url}")
        
        try:
            response = self.client.post(self.server_url, json=request)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise Exception(f"MCP error: {result['error']}")
            
            tools = result.get("result", {}).get("tools", [])
            logger.info(f"Found {len(tools)} tools")
            return tools
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error listing tools: {e}")
            raise
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            raise
    
    def call_tool(
        self, 
        tool_name: str, 
        arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool result as dictionary
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "tools/call",
            "params": {
            "name": tool_name,
            "arguments": arguments
            }
        }
        
        headers = {
            "Accept": "application/json, text/event-stream"
        }
        
        logger.info(f"Calling tool {tool_name} on {self.server_url}")
        logger.debug(f"Arguments: {arguments}")
        
        try:
            response = self.client.post(self.server_url, json=request, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise Exception(f"MCP error: {result['error']}")
            
            # Extract content from MCP response
            content = result.get("result", {}).get("content", [])
            
            if not content:
                logger.warning(f"No content in response from {tool_name}")
                return {}
            
            # Parse the text content as JSON
            import json
            text_content = content[0].get("text", "{}")
            parsed_result = json.loads(text_content)
            
            logger.info(f"Tool {tool_name} returned successfully")
            return parsed_result
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling tool {tool_name}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from {tool_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise
    
    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self) -> "MCPClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


class MCPClientManager:
    """Manager for multiple MCP clients."""
    
    def __init__(
        self,
        demographics_url: str,
        performance_url: str,
        timeout: float = 30.0
    ):
        """
        Initialize MCP client manager.
        
        Args:
            demographics_url: URL of demographics MCP server
            performance_url: URL of performance MCP server
            timeout: Request timeout in seconds
        """
        self.demographics_client = MCPClient(demographics_url, timeout)
        self.performance_client = MCPClient(performance_url, timeout)
        
        logger.info("MCP Client Manager initialized")
        logger.info(f"Demographics server: {demographics_url}")
        logger.info(f"Performance server: {performance_url}")
    
    def close(self) -> None:
        """Close all clients."""
        self.demographics_client.close()
        self.performance_client.close()
    
    def __enter__(self) -> "MCPClientManager":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
