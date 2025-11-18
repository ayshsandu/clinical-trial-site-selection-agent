import express from "express";
import { createServer } from "./server.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import cors from 'cors'; 

const PORT = process.env.PORT || 4001;
const app = express();

// Parse JSON bodies
app.use(express.json());

// Create MCP server
const mcpServer = createServer();

//handle CORS
app.use(
    cors({
        origin: '*', // Allow all origins for development; restrict in production (e.g., ['https://your-client-domain.com'])
        exposedHeaders: ['Mcp-Session-Id'],
    })
);

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({ status: "healthy", server: "patient-demographics" });
});
// MCP endpoint - StreamableHTTP transport
app.post("/mcp", async (req, res) => {
  try {
    console.log("Received MCP request:", JSON.stringify(req.body, null, 2));
    // console.log("Received MCP request:");
    
    // Create transport for this request
    const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: undefined,
        enableJsonResponse: true
    });
    await mcpServer.connect(transport);
    await transport.handleRequest(req, res, req.body);
    // Log response sent
    console.log("MCP response sent.", res.statusCode, res.getHeaders());
  } catch (error) {
    console.error("Error handling MCP request:", error);
    res.status(500).json({
      error: "Internal server error",
      message: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Patient Demographics MCP Server running on port ${PORT}`);
  console.log(`MCP endpoint: http://localhost:${PORT}/mcp`);
  console.log(`Health check: http://localhost:${PORT}/health`);
});
