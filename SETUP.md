# Clinical Trial Site Selection Demo - Complete Setup Guide

This package contains a partial implementation. Follow these steps to complete the setup.

## What's Included

### ✅ Complete Files
- Patient Demographics MCP Server (TypeScript)
  - ✅ types.ts
  - ✅ data.ts  
  - ✅ tools.ts
  - ✅ server.ts
  - ✅ index.ts
  - ✅ package.json
  - ✅ tsconfig.json
  - ✅ Dockerfile

- Project Configuration
  - ✅ docker-compose.yml
  - ✅ .env.example
  - ✅ .gitignore
  - ✅ README.md

### 📝 Files to Create

You'll need to create the following files using the specification document provided:

1. **Site Performance MCP Server** (mcp-servers/site-performance/src/)
   - Copy structure from patient-demographics server
   - Implement 3 tools: search_sites, get_site_capabilities, get_enrollment_history
   - Use mock data provided in specification

2. **LangGraph Agent** (agent/src/)
   - Create agent.py with LangGraph workflow
   - Create MCP client wrapper
   - Create node implementations

## Quick Start (Patient Demographics Server Only)

```bash
# 1. Navigate to patient demographics server
cd mcp-servers/patient-demographics

# 2. Install dependencies
npm install

# 3. Build
npm run build

# 4. Run
npm start
```

The server will start on http://localhost:3001

## Testing the Demographics Server

```bash
# List tools
curl -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# Search patient pools
curl -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "search_patient_pools",
      "arguments": {
        "disease": "Type 2 Diabetes",
        "region": "US-Northeast"
      }
    }
  }'
```

## Creating the Site Performance Server

The site performance server follows the same pattern as the patient demographics server:

1. Copy the entire `patient-demographics` directory to `site-performance`
2. Update package.json name to "site-performance-mcp-server"
3. Change PORT to 3002 in index.ts
4. Replace tools.ts with site-specific tools (see specification)
5. Replace data.ts with site data (see specification)
6. Update types.ts with site-related interfaces

## Creating the LangGraph Agent

```python
# agent/pyproject.toml
[tool.poetry]
name = "clinical-trial-agent"
version = "1.0.0"

[tool.poetry.dependencies]
python = "^3.11"
langgraph = "^0.2.0"
langchain-anthropic = "^0.2.0"
httpx = "^0.27.0"
pydantic = "^2.0.0"

# agent/src/agent.py
from langgraph.graph import StateGraph, END
from .state import TrialSiteSelectionState
from .nodes import (
    parse_requirements,
    query_demographics,
    query_performance,
    analyze_rank,
    generate_report
)

def create_agent():
    workflow = StateGraph(TrialSiteSelectionState)
    
    # Add nodes
    workflow.add_node("parse_requirements", parse_requirements)
    workflow.add_node("query_demographics", query_demographics)
    workflow.add_node("query_performance", query_performance)
    workflow.add_node("analyze_rank", analyze_rank)
    workflow.add_node("generate_report", generate_report)
    
    # Add edges
    workflow.set_entry_point("parse_requirements")
    workflow.add_edge("parse_requirements", "query_demographics")
    workflow.add_edge("query_demographics", "query_performance")
    workflow.add_edge("query_performance", "analyze_rank")
    workflow.add_edge("analyze_rank", "generate_report")
    workflow.add_edge("generate_report", END)
    
    return workflow.compile()
```

## Environment Setup

```bash
# Create .env file
cp .env.example .env

# Edit .env and add:
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Docker Deployment

Once all files are created:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Next Steps

1. Complete the site-performance MCP server implementation
2. Implement the LangGraph agent
3. Test end-to-end workflow
4. Add error handling and logging
5. Implement authentication (production)

## Reference Documentation

- MCP TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- LangGraph: https://langchain-ai.github.io/langgraph/
- Anthropic API: https://docs.anthropic.com

## Support

Refer to the software specification document for detailed implementation guidance.
