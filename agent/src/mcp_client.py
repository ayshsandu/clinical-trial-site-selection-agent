"""MCP client for communicating with MCP servers via LangChain MCP adapters."""

import logging
import asyncio
from typing import Any, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for communicating with MCP servers using LangChain MCP adapters."""

    def __init__(self, server_url: str, bearer_token: Optional[str] = None):
        """
        Initialize MCP client.

        Args:
            server_url: Base URL of the MCP server (e.g., http://localhost:4001/mcp)
            bearer_token: Optional bearer token for authentication
        """
        self.server_url = server_url
        self.bearer_token = bearer_token
        self._tools = []
        self._initialized = False

    async def _ensure_initialized(self):
        """Ensure the client is initialized and tools are loaded."""
        if not self._initialized:
            # Create a MultiServerMCPClient with just this server
            config = {
                "server": {
                    "url": self.server_url,
                    "transport": "streamable_http",
                }
            }
            
            # Add authorization header if bearer token is provided
            if self.bearer_token:
                config["server"]["headers"] = {
                    "Authorization": f"Bearer {self.bearer_token}"
                }
            
            client = MultiServerMCPClient(config)
            self._tools = await client.get_tools()
            self._initialized = True
            logger.info(f"Loaded {len(self._tools)} tools from {self.server_url}")

    def list_tools(self) -> list[dict[str, Any]]:
        """
        List available tools from the MCP server.

        Returns:
            List of tool definitions
        """
        # Check if we're in an existing event loop
        try:
            asyncio.get_running_loop()
            # We're in an existing event loop, use nest_asyncio
            import nest_asyncio
            nest_asyncio.apply()
            
            async def _init_and_list():
                if not self._initialized:
                    await self._ensure_initialized()
                return self._tools
            
            tools = asyncio.run(_init_and_list())
            
        except RuntimeError:
            # No running event loop, use asyncio.run normally
            async def _init_and_list():
                if not self._initialized:
                    await self._ensure_initialized()
                return self._tools
            
            tools = asyncio.run(_init_and_list())

        tool_defs = []
        for tool in tools:
            tool_def = {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.args_schema.schema() if tool.args_schema else {}
            }
            tool_defs.append(tool_def)
        return tool_defs

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool result as dictionary
        """
        # Check if we're in an existing event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an existing event loop, use run_until_complete
            async def _init_and_call():
                if not self._initialized:
                    await self._ensure_initialized()
                
                tool = next((t for t in self._tools if t.name == tool_name), None)
                if not tool:
                    raise ValueError(f"Tool {tool_name} not found")

                logger.info(f"Calling tool {tool_name}")
                logger.debug(f"Arguments: {arguments}")
                
                result = await tool.ainvoke(arguments)
                
                # Parse JSON string result if needed
                if isinstance(result, str):
                    import json
                    try:
                        result = json.loads(result)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON result from {tool_name}: {e}")
                        # Return the string result as-is if parsing fails
                        pass
                
                logger.info(f"Tool {tool_name} returned successfully")
                return result
            
            # This will work even in a running event loop
            import nest_asyncio
            nest_asyncio.apply()
            return asyncio.run(_init_and_call())
            
        except RuntimeError:
            # No running event loop, use asyncio.run normally
            async def _init_and_call():
                if not self._initialized:
                    await self._ensure_initialized()
                
                tool = next((t for t in self._tools if t.name == tool_name), None)
                if not tool:
                    raise ValueError(f"Tool {tool_name} not found")

                logger.info(f"Calling tool {tool_name}")
                logger.debug(f"Arguments: {arguments}")
                
                result = await tool.ainvoke(arguments)
                
                # Parse JSON string result if needed
                if isinstance(result, str):
                    import json
                    try:
                        result = json.loads(result)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON result from {tool_name}: {e}")
                        # Return the string result as-is if parsing fails
                        pass
                
                logger.info(f"Tool {tool_name} returned successfully")
                return result
            
            return asyncio.run(_init_and_call())

    def close(self) -> None:
        """Close the client (no-op for LangChain MCP adapters)."""
        pass

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
        bearer_token: Optional[str] = None
    ):
        """
        Initialize MCP client manager.

        Args:
            demographics_url: URL of demographics MCP server
            performance_url: URL of performance MCP server
            bearer_token: Optional bearer token for authentication
        """
        self.demographics_client = MCPClient(demographics_url, bearer_token)
        self.performance_client = MCPClient(performance_url, bearer_token)

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
