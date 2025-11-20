# Clinical Trial Site Selection Agent Demo

AI-powered clinical trial site selection system using LangGraph and Model Context Protocol (MCP) servers.

## Overview

This demonstration system helps identify optimal clinical trial sites by analyzing:
- Patient demographics and disease prevalence
- Site capabilities and certifications
- Historical enrollment performance

## Architecture

```
┌─────────────────────────────────┐
│         Interactive UI          │
│            (React)              │
└─┬──────────────┬──────────────┬─┘
  │              │              │
  │              ▼              │
  │     ┌─────────────────┐     │
  │     │ Trial Site Agent│     │
  │     │   (LangGraph)   │     │
  │     └────────┬────────┘     │
  │              │              │
  │       ┌──────┴──────┐       │
  │       │             │       │
  ▼       ▼             ▼       ▼
┌────────────┐   ┌──────────────┐
│ Patient    │   │    Site      │
│Demographics│   │ Performance  │
│MCP Server  │   │ MCP Server   │
└────────────┘   └──────────────┘
```

## Components

1. **LangGraph Agent** (Python) - Orchestrates site selection using Gemini
2. **Patient Demographics MCP Server** (TypeScript) - Provides anonymized patient data
3. **Site Performance MCP Server** (TypeScript) - Provides site capabilities and history
4. **Interactive UI** (React) - Web interface for visualizing agent progress and results, and directly calling MCP servers

## Prerequisites

- Python 3.11+
- Node.js 18+
- API key for LLM provider (Google Gemini)
- Authentication server (Asgardeo or similar) for OAuth

## Quick Start

### Manual Setup

```bash
# 0. Configure environment variables
# Copy and update .env files for each component
cp agent/.env.example agent/.env
cp mcp-servers/patient-demographics/.env.example mcp-servers/patient-demographics/.env
cp mcp-servers/site-performance/.env.example mcp-servers/site-performance/.env
# Edit the .env files with your actual configuration values

# 1. Start MCP Servers
cd mcp-servers/patient-demographics
npm install && npm run build && npm start &

cd ../site-performance
npm install && npm run build && npm start &

# 2. Start Agent
cd ../../agent
pip install -r requirements.txt  # or poetry install
python main.py

# 3. Start Interactive UI
cd ../interactive-ui
npm install && npm run dev
```

## Project Structure

```
clinical-trial-demo/
├── agent/                      # LangGraph agent
│   ├── src/
│   │   ├── agent.py           # Main agent graph
│   │   ├── state.py           # State definitions
│   │   ├── nodes/             # Graph nodes
│   │   └── mcp_client.py      # MCP client wrapper
│   ├── pyproject.toml
│   └── main.py
├── mcp-servers/
│   ├── patient-demographics/  # Demographics MCP server
│   └── site-performance/      # Performance MCP server
├── interactive-ui/            # React web interface
├── .env.example
└── README.md
```

## Example Queries

```
"Find sites for a Phase III Type 2 Diabetes trial targeting 200 patients 
 in the Northeast US with strong endocrinology departments"

"I need 5 sites for a Phase II lung cancer trial in California, 
 preferably academic medical centers with PET imaging capabilities"

"Looking for sites with experience in rare metabolic disorders, 
 any US location, need at least 50 potential patients per site"
```

## API Endpoints

### Patient Demographics Server (Port 4001)
- `POST /mcp` - MCP protocol endpoint
- `GET /health` - Health check

### Site Performance Server (Port 4002)
- `POST /mcp` - MCP protocol endpoint
- `GET /health` - Health check

## MCP Tools

### Patient Demographics Server

**search_patient_pools**
- Search for patient populations by disease and region
- Returns: Population size, demographics, prevalence rates

**get_demographics_by_region**
- Get detailed regional demographics
- Returns: Healthcare access, enrollment velocity, socioeconomic data

### Site Performance Server

**search_sites**
- Find sites by region and therapeutic area
- Returns: Site info, capacity, therapeutic expertise

**get_site_capabilities**
- Get site certifications and equipment
- Returns: Certifications, imaging/lab equipment, staff qualifications

**get_enrollment_history**
- Get historical trial performance
- Returns: Past trials, enrollment rates, quality metrics

## Configuration

### Environment Variables

All critical configurations are read from `.env` files in each component directory. Copy the provided `.env.example` files and update them with your actual values.

#### Agent Configuration (`agent/.env`)
```bash
# API Key for LLM (Google Gemini)
GOOGLE_API_KEY=your-api-key-here

# MCP Server URLs
DEMOGRAPHICS_SERVER_URL=http://localhost:4001/mcp
PERFORMANCE_SERVER_URL=http://localhost:4002/mcp

# Authentication Configuration
JWKS_URL=https://your-auth-server/jwks
AGENT_CLIENT_ID=your-agent-client-id
AGENT_CLIENT_SECRET=your-agent-client-secret
AGENT_REDIRECT_URL=http://localhost:8010/callback
AGENT_ID=your-agent-id
AGENT_PASSWORD=your-agent-password
TOKEN_ENDPOINT=https://your-auth-server/oauth2/token
REQUIRED_SCOPE=query_agent

# Logging
LOG_LEVEL=INFO
```

#### MCP Servers Configuration (`mcp-servers/*/env`)
```bash
# Auth Server URLs
AUTH_SERVER_BASE_URL=https://localhost:9443
ISSUER=https://localhost:9443/oauth2/token

# Server Ports
PORT=4001  # or 4002 for site-performance

# Logging
LOG_LEVEL=info

# For Development Only
NODE_TLS_REJECT_UNAUTHORIZED=0
```

#### Interactive UI Configuration (`interactive-ui/.env`)
```bash
# Authentication Configuration
VITE_AUTH_CLIENT_ID=your-client-id
VITE_AUTH_BASE_URL=https://localhost:9443
VITE_AUTH_SIGN_IN_REDIRECT_URL=http://localhost:3000
VITE_AUTH_SIGN_OUT_REDIRECT_URL=http://localhost:3000
VITE_AUTH_SCOPE=openid,profile,email,query_agent
VITE_AUTH_RESOURCE_SERVER_URLS=http://localhost:8010

# MCP Server URLs
VITE_DEMOGRAPHICS_SERVER_URL=http://localhost:4001/mcp
VITE_PERFORMANCE_SERVER_URL=http://localhost:4002/mcp

# Agent API Configuration
VITE_AGENT_URL=http://localhost:8010
AGENT_RESOURCE_URL=http://localhost:8010/api/query
```

### Setup Instructions

1. Copy `.env.example` files to `.env` in each component directory:
   ```bash
   # Agent
   cp agent/.env.example agent/.env

   # MCP Servers
   cp mcp-servers/patient-demographics/.env.example mcp-servers/patient-demographics/.env
   cp mcp-servers/site-performance/.env.example mcp-servers/site-performance/.env

   # Interactive UI
   cp interactive-ui/.env.example interactive-ui/.env
   ```

2. Update the `.env` files with your actual configuration values.

## Development

### Running Tests

```bash
# MCP Servers
cd mcp-servers/patient-demographics
npm test

# Agent
cd agent
poetry run pytest
```

### Building

```bash
# MCP Servers
npm run build

# Agent
poetry build
```

## Testing MCP Servers

```bash
# List available tools
curl -X POST http://localhost:4001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# Call a tool
curl -X POST http://localhost:4001/mcp \
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

## Troubleshooting

### MCP Server Not Starting
- Check if ports 4001/4002 are available
- Verify Node.js version (18+)

### Agent Connection Issues
- Verify MCP servers are running: `curl http://localhost:4001/health`
- Check environment variables in .env
- Ensure GOOGLE_API_KEY is valid

### Import Errors
- Run `npm install` in MCP server directories
- Run `poetry install` in agent directory
- Check Python version (3.11+)

## Security Notes

- All patient data is anonymized and aggregated
- No PII/PHI stored or transmitted
- Audit trail captures all data access
- Production deployment requires additional security measures

## Future Enhancements

- [ ] Real database integration
- [ ] Authentication & authorization
- [x] Web UI dashboard
- [ ] Budget estimation integration
- [ ] ML-based site performance prediction
- [ ] Real-time enrollment tracking

## License

Apache License 2.0

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For questions or issues, please open a GitHub issue.
