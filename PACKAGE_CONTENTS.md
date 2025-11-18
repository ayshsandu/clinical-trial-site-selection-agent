# Clinical Trial Site Selection Demo - Package Contents

## 📦 What's in This Package

This is a **partial implementation** of the Clinical Trial Site Selection system. It includes:

### ✅ Fully Implemented: Patient Demographics MCP Server

A complete, working TypeScript MCP server that provides anonymized patient demographic data.

**Location**: `mcp-servers/patient-demographics/`

**Files**:
- `src/types.ts` - TypeScript interfaces for patient data
- `src/data.ts` - Mock database with 10 regions and diseases
- `src/tools.ts` - Two MCP tools implementation
- `src/server.ts` - MCP server setup  
- `src/index.ts` - Express HTTP server with StreamableHTTP transport
- `package.json` - Node.js dependencies
- `tsconfig.json` - TypeScript configuration
- `Dockerfile` - Container image definition

**Tools Provided**:
1. `search_patient_pools` - Search for patient populations by disease/region
2. `get_demographics_by_region` - Get detailed regional demographics

**Status**: ✅ Ready to run!

### 📋 Configuration Files

- `.env.example` - Environment variables template
- `.gitignore` - Git ignore rules
- `docker-compose.yml` - Multi-container Docker setup
- `README.md` - Project overview and quick start guide
- `SETUP.md` - Detailed setup and completion instructions

### 🔨 To Be Implemented

These components are described in the specification but not yet implemented:

1. **Site Performance MCP Server** (`mcp-servers/site-performance/`)
   - Similar structure to demographics server
   - 3 tools: search_sites, get_site_capabilities, get_enrollment_history
   - Mock data for 10 clinical trial sites

2. **LangGraph Agent** (`agent/`)
   - Python-based agent using LangGraph
   - Orchestrates both MCP servers
   - Implements site selection workflow
   - Returns ranked recommendations

## 🚀 Quick Start

### Run the Demographics Server

```bash
cd mcp-servers/patient-demographics
npm install
npm run build
npm start
```

Server runs on `http://localhost:3001`

### Test It

```bash
curl -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

## 📚 Complete the Implementation

See `SETUP.md` for detailed instructions on:
- Creating the Site Performance MCP server
- Implementing the LangGraph agent
- Running the complete system with Docker

## 📖 Reference

Refer to the software specification document (provided separately) for:
- Complete architecture details
- All data schemas
- Full implementation examples
- Tool specifications

## 🔑 Key Features of Included Server

- **StreamableHTTP Transport**: Uses HTTP instead of stdio for MCP communication
- **Mock Data**: 10 US regions with realistic demographic data
- **Multiple Diseases**: Type 2 Diabetes, Hypertension, Lung Cancer, Metabolic Disorders
- **Comprehensive Metrics**: Age distribution, ethnicity, healthcare access, enrollment velocity
- **Production-Ready Structure**: Proper TypeScript setup, Docker support, health checks

## 💡 Why Partial?

This partial implementation demonstrates:
1. Complete MCP server architecture
2. StreamableHTTP transport implementation  
3. Tool definition and implementation patterns
4. TypeScript best practices for MCP servers

You can use the demographics server as a template to build the performance server, then connect both to a LangGraph agent.

## 🎯 Next Steps

1. ✅ Test the demographics server
2. 📝 Clone it to create the performance server
3. 🤖 Build the LangGraph agent
4. 🚀 Deploy with Docker Compose

Happy building! 🎉
