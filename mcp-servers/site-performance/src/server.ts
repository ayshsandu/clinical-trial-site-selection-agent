import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import {
  SearchSitesSchema,
  GetSiteCapabilitiesSchema,
  GetEnrollmentHistorySchema,
  searchSites,
  getSiteCapabilities,
  getEnrollmentHistory,
} from "./tools.js";
import { zodToJsonSchema } from "zod-to-json-schema";

export function createServer() {
  const server = new Server(
    {
      name: "site-performance-server",
      version: "1.0.0",
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // List available tools
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    const tools: Tool[] = [
      {
        name: "search_sites",
        description:
          "Search for clinical trial sites matching geographic and therapeutic area criteria. Returns site information including location, capacity, and therapeutic expertise.",
        inputSchema: zodToJsonSchema(SearchSitesSchema) as any,
      },
      {
        name: "get_site_capabilities",
        description:
          "Get detailed capabilities and certifications for a specific clinical trial site, including equipment, staff qualifications, and accreditations.",
        inputSchema: zodToJsonSchema(GetSiteCapabilitiesSchema) as any,
      },
      {
        name: "get_enrollment_history",
        description:
          "Get historical enrollment performance for a specific site, including past trial outcomes, enrollment rates, and quality metrics.",
        inputSchema: zodToJsonSchema(GetEnrollmentHistorySchema) as any,
      },
    ];

    return { tools };
  });

  // Handle tool calls
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
      switch (name) {
        case "search_sites": {
          const params = SearchSitesSchema.parse(args);
          const result = searchSites(params);
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        }

        case "get_site_capabilities": {
          const params = GetSiteCapabilitiesSchema.parse(args);
          const result = getSiteCapabilities(params);
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        }

        case "get_enrollment_history": {
          const params = GetEnrollmentHistorySchema.parse(args);
          const result = getEnrollmentHistory(params);
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        }

        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    } catch (error) {
      if (error instanceof Error) {
        return {
          content: [
            {
              type: "text",
              text: `Error: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
      throw error;
    }
  });

  return server;
}