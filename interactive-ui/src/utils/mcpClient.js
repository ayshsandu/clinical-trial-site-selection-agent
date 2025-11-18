import { Client } from '@modelcontextprotocol/sdk/client/index.js';
// import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js';
// import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';

/**
 * MCP Client Manager
 * Handles connections to MCP servers and tool execution
 */
class MCPClientManager {
  constructor() {
    this.clients = new Map();
  }

  /**
   * Get or create an MCP client for a specific server
   * @param {string} serverUrl - The MCP server URL
   * @returns {Promise<Client>} The MCP client instance
   */
  async getClient(serverUrl) {
    // Return existing client if already connected
    if (this.clients.has(serverUrl)) {
      return this.clients.get(serverUrl);
    }

    // Create new client with SSE transport
    const transport = new StreamableHTTPClientTransport(new URL(serverUrl));
    const client = new Client(
      {
        name: 'clinical-trial-ui',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Connect to the server
    await client.connect(transport);

    // Store the client for reuse
    this.clients.set(serverUrl, client);

    return client;
  }

  /**
   * List available tools from an MCP server
   * @param {string} serverUrl - The MCP server URL
   * @returns {Promise<Array>} List of available tools
   */
  async listTools(serverUrl) {
    try {
      const client = await this.getClient(serverUrl);
      const response = await client.listTools();
      return response.tools || [];
    } catch (error) {
      console.error(`Error listing tools from ${serverUrl}:`, error);
      throw new Error(`Failed to list tools: ${error.message}`);
    }
  }

  /**
   * Call a tool on an MCP server
   * @param {string} serverUrl - The MCP server URL
   * @param {string} toolName - The name of the tool to call
   * @param {Object} args - The arguments to pass to the tool
   * @returns {Promise<Object>} The tool execution result
   */
  async callTool(serverUrl, toolName, args = {}) {
    try {
      const client = await this.getClient(serverUrl);
      
      const response = await client.callTool({
        name: toolName,
        arguments: args,
      });

      return response;
    } catch (error) {
      console.error(`Error calling tool ${toolName}:`, error);
      throw new Error(`Failed to call tool: ${error.message}`);
    }
  }

  /**
   * Disconnect from a specific server
   * @param {string} serverUrl - The MCP server URL
   */
  async disconnect(serverUrl) {
    const client = this.clients.get(serverUrl);
    if (client) {
      await client.close();
      this.clients.delete(serverUrl);
    }
  }

  /**
   * Disconnect from all servers
   */
  async disconnectAll() {
    const disconnectPromises = Array.from(this.clients.entries()).map(
      async ([url, client]) => {
        try {
          await client.close();
        } catch (error) {
          console.error(`Error disconnecting from ${url}:`, error);
        }
      }
    );

    await Promise.all(disconnectPromises);
    this.clients.clear();
  }

  /**
   * Check if connected to a server
   * @param {string} serverUrl - The MCP server URL
   * @returns {boolean} True if connected
   */
  isConnected(serverUrl) {
    return this.clients.has(serverUrl);
  }
}

// Export singleton instance
export const mcpClientManager = new MCPClientManager();

// Export for direct use if needed
export default MCPClientManager;
