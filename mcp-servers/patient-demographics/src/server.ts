import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import {
  SearchPatientPoolsSchema,
  GetDemographicsByRegionSchema,
  searchPatientPools,
  getDemographicsByRegion,
} from "./tools.js";
import { zodToJsonSchema } from "zod-to-json-schema";

export function createServer() {
  const server = new Server(
    {
      name: "patient-demographics-server",
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
        name: "search_patient_pools",
        description:
          "Search for anonymized patient populations matching disease and geographic criteria. Returns aggregated demographic data and disease prevalence information.",
        inputSchema: zodToJsonSchema(SearchPatientPoolsSchema) as any,
      },
      {
        name: "get_demographics_by_region",
        description:
          "Get detailed demographic breakdown for a specific geographic region, including healthcare access, enrollment velocity, and socioeconomic indicators.",
        inputSchema: zodToJsonSchema(GetDemographicsByRegionSchema) as any,
      },
    ];

    return { tools };
  });

  // Handle tool calls
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
      switch (name) {
        case "search_patient_pools": {
          const params = SearchPatientPoolsSchema.parse(args);
          const result = searchPatientPools(params);
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        }

        case "get_demographics_by_region": {
          const params = GetDemographicsByRegionSchema.parse(args);
          const result = getDemographicsByRegion(params);
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
