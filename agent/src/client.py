"""MCP Client utility class for testing and interacting with MCP servers."""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)


class MCPClientTester:
    """Utility class for testing and interacting with MCP servers using LangChain MCP adapters."""

    def __init__(
        self,
        demographics_url: str = "http://localhost:4001/mcp",
        performance_url: str = "http://localhost:4002/mcp"
    ):
        """
        Initialize MCP client tester.

        Args:
            demographics_url: URL of demographics MCP server
            performance_url: URL of performance MCP server
        """
        self.demographics_url = demographics_url
        self.performance_url = performance_url
        self.client = None
        self.tools = []

    async def initialize(self) -> None:
        """Initialize the MCP client and load tools."""
        print("🔄 Initializing MCP client connection...")

        self.client = MultiServerMCPClient({
            "demographics": {
                "url": self.demographics_url,
                "transport": "streamable_http",
            },
            "site-data": {
                "url": self.performance_url,
                "transport": "streamable_http",
            }
        })

        try:
            self.tools = await self.client.get_tools()
            print(f"✅ Successfully loaded {len(self.tools)} tools from MCP servers")

            for tool in self.tools:
                print(f"  - {tool.name}: {tool.description}")

        except Exception as e:
            print(f"❌ Error initializing MCP client: {e}")
            raise

    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Call a specific tool by name with given parameters.

        Args:
            tool_name: Name of the tool to call
            parameters: Parameters to pass to the tool

        Returns:
            Tool execution result
        """
        if not self.tools:
            await self.initialize()

        # Find the tool
        tool = None
        for t in self.tools:
            if t.name == tool_name:
                tool = t
                break

        if not tool:
            available_tools = [t.name for t in self.tools]
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {available_tools}")

        print(f"\n🧪 Calling tool: {tool_name}")
        print(f"Description: {tool.description}")
        print(f"Parameters: {parameters}")

        try:
            result = await tool.ainvoke(parameters)
            print("✅ Tool execution successful!")
            return result
        except Exception as e:
            print(f"❌ Tool execution failed: {e}")
            raise

    async def list_available_tools(self) -> List[str]:
        """List all available tool names."""
        if not self.tools:
            await self.initialize()
        return [tool.name for tool in self.tools]

    async def test_search_sites(self, region: str = "US-Northeast", min_capacity: int = 0, therapeutic_area: str = "Endocrinology") -> Dict[str, Any]:
        """Test the search_sites tool with default parameters."""
        params = {
            "region": region,
            "min_capacity": min_capacity,
            "therapeutic_area": therapeutic_area
        }
        return await self.call_tool("search_sites", params)

    async def test_search_patient_pools(self, disease: str = "Type 2 Diabetes", region: str = "US-Northeast") -> Dict[str, Any]:
        """Test the search_patient_pools tool."""
        params = {
            "disease": disease,
            "region": region
        }
        return await self.call_tool("search_patient_pools", params)


async def main():
    """Main function for testing the MCP client."""
    print("Testing MCP Client Utility Class")
    print("=" * 50)

    tester = MCPClientTester()

    try:
        # Initialize and list tools
        await tester.initialize()

        # Test search_sites tool
        print("\n" + "=" * 50)
        print("Testing search_sites tool...")
        sites_result = await tester.test_search_sites()
        print(f"Sites result type: {type(sites_result)}")
        if isinstance(sites_result, dict):
            print("Sites found:", sites_result.get("total_count", 0))
            # Show first site if available
            sites = sites_result.get("sites", [])
            if sites:
                print(f"First site: {sites[0].get('site_name', 'Unknown')}")
        else:
            print("Sites result:", str(sites_result)[:200] + "..." if len(str(sites_result)) > 200 else str(sites_result))

        # Test search_patient_pools tool
        print("\n" + "=" * 50)
        print("Testing search_patient_pools tool...")
        pools_result = await tester.test_search_patient_pools()
        print(f"Pools result type: {type(pools_result)}")
        if isinstance(pools_result, dict):
            pools = pools_result.get("pools", [])
            print(f"Patient pools found: {len(pools)}")
            if pools:
                print(f"First pool region: {pools[0].get('region_name', 'Unknown')}")
        else:
            print("Pools result:", str(pools_result)[:200] + "..." if len(str(pools_result)) > 200 else str(pools_result))

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1

    print("\n" + "=" * 50)
    print("✅ All tests completed successfully!")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())