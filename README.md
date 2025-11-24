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

1. **LangGraph Agent** (Python) - Orchestrates site selection using Gemini. Includes a complete authentication SDK for secure API access.
2. **Patient Demographics MCP Server** (TypeScript) - Provides anonymized patient data with OAuth protection
3. **Site Performance MCP Server** (TypeScript) - Provides site capabilities and history with authentication
4. **Interactive UI** (React) - Web interface for visualizing agent progress and results, with direct MCP server access

## Prerequisites

- **Python 3.11+** - For the LangGraph agent (includes complete auth SDK)
- **Node.js 18+** - For MCP servers and React UI
- **Google Gemini API Key** - For AI-powered site selection
- **Authentication Server** (Optional) - Asgardeo or similar for OAuth (demo works without it)

## Quick Start

### Option 1: Automated Setup (Recommended)

For a streamlined setup experience, follow the individual component guides:

1. **Start MCP Servers** (see `mcp-servers/*/QUICKSTART.md`)
2. **Setup Agent** (see `agent/QUICKSTART.md`)
3. **Launch UI** (see `interactive-ui/QUICKSTART.md`)

### Option 2: Manual Setup

```bash
# 1. Configure environment variables
# Copy and update .env files for each component
cp .env.example .env  # Root config (optional)
cp agent/.env.example agent/.env
cp mcp-servers/patient-demographics/.env.example mcp-servers/patient-demographics/.env
cp mcp-servers/site-performance/.env.example mcp-servers/site-performance/.env
cp interactive-ui/.env.example interactive-ui/.env
# Edit the .env files with your actual configuration values

# 2. Start MCP Servers (in separate terminals)
cd mcp-servers/patient-demographics
npm install && npm run build && npm start &

cd ../site-performance
npm install && npm run build && npm start &

# 3. Start Agent (in new terminal)
cd ../../agent
pip install -r requirements.txt  # or poetry install
python main.py

# 4. Start Interactive UI (in new terminal)
cd ../interactive-ui
npm install && npm run dev
```

### First Test

1. Open `http://localhost:3000` in your browser
2. Try a query: "Find sites for Phase III diabetes trial in Northeast US"
3. Results should appear in 30-60 seconds

### Prerequisites Check

```bash
# Python 3.11+
python --version

# Node.js 18+
node --version

# Check MCP servers (after starting)
curl http://localhost:4001/health
curl http://localhost:4002/health
```

**📖 Detailed Setup Guides**: Each component has detailed setup instructions:
- `agent/QUICKSTART.md` - Agent setup and usage
- `interactive-ui/QUICKSTART.md` - UI setup
- `mcp-servers/*/QUICKSTART.md` - MCP server quick starts

## Project Structure

```
clinical-trial-demo/
├── agent/                      # LangGraph agent (self-contained with auth SDK)
│   ├── src/
│   │   ├── agent.py           # Main agent graph
│   │   ├── auth_sdk/          # Local authentication SDK
│   │   │   ├── core.py        # AuthSDK main class
│   │   │   ├── agent_auth.py  # Agent OAuth provider
│   │   │   ├── validator.py   # Token validation
│   │   │   └── ...            # Other auth modules
│   │   ├── state.py           # State definitions
│   │   ├── nodes/             # Graph nodes
│   │   └── mcp_client.py      # MCP client wrapper
│   ├── pyproject.toml
│   ├── main.py
│   ├── QUICKSTART.md          # Agent setup guide
│   └── README.md
├── mcp-servers/
│   ├── patient-demographics/  # Demographics MCP server
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── site-performance/      # Performance MCP server
│       ├── src/
│       ├── package.json
│       └── tsconfig.json
├── interactive-ui/            # React web interface
│   ├── src/
│   ├── package.json
│   ├── QUICKSTART.md          # UI setup guide
│   └── README.md
├── .env.example               # Root environment template
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

## Authentication

The agent includes a complete authentication SDK (`agent/src/auth_sdk/`) that handles:

- OAuth 2.0 On-Behalf-Of (OBO) flows
- JWT token validation with JWKS
- Agent identity authentication
- Session management
- Scope-based access control

This makes the agent **completely self-contained** - no external authentication dependencies required for development and testing.

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
# Google API Key (required)
# Get your API key from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your-api-key-here

# MCP Server URLs
DEMOGRAPHICS_SERVER_URL=http://localhost:4001/mcp
PERFORMANCE_SERVER_URL=http://localhost:4002/mcp

# OAuth 2.0 JWKS URL (required for API mode)
JWKS_URL=https://your-auth-server/.well-known/jwks.json

# Logging
LOG_LEVEL=DEBUG

# Token Validation Configuration
TOKEN_AUDIENCE=your-audience
TOKEN_ISSUER=https://your-auth-server/oauth2/token
REQUIRED_SCOPE=query_agent

# OBO (On-Behalf-Of) Flow Configuration
AUTHORIZATION_ENDPOINT=https://your-auth-server/oauth2/authorize
TOKEN_ENDPOINT=https://your-auth-server/oauth2/token
AGENT_REDIRECT_URI=http://localhost:8010/auth/callback
REQUESTING_SCOPES=openid profile email

# Agent Authentication (for agent identity)
AGENT_CLIENT_ID=your-agent-client-id
AGENT_CLIENT_SECRET=your-agent-client-secret
AGENT_REDIRECT_URL=http://localhost:8080/callback
AGENT_ID=your-agent-id
AGENT_PASSWORD=your-agent-password
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
# MCP Server URLs
VITE_DEMOGRAPHICS_SERVER_URL=http://localhost:4001/mcp
VITE_PERFORMANCE_SERVER_URL=http://localhost:4002/mcp

# Agent Resource Server URLs
VITE_AGENT_URL=http://localhost:8010

# Authentication Configuration
VITE_AUTH_CLIENT_ID=your-client-id

# Auth Server Base URL, for Asgardeo use https://api.asgardeo.io/t/<your-tenant>
VITE_AUTH_SERVER_BASE_URL=https://localhost:9443
VITE_AUTH_SIGN_IN_REDIRECT_URL=http://localhost:3000
VITE_AUTH_SIGN_OUT_REDIRECT_URL=http://localhost:3000
VITE_AUTH_SCOPE=openid,profile,email,query_agent
VITE_AUTH_RESOURCE_SERVER_URLS=[${VITE_DEMOGRAPHICS_SERVER_URL},${VITE_PERFORMANCE_SERVER_URL},${VITE_AGENT_URL}]

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

**Note:** MCP servers require authentication. Include a valid JWT bearer token in requests.

```bash
# List available tools
curl -X POST http://localhost:4001/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# Call a tool
curl -X POST http://localhost:4001/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
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

### Authentication Errors
- Ensure `.env` files are configured with correct auth server URLs
- Verify JWT tokens are valid and not expired
- Check that required scopes are present in tokens
- For direct API testing, obtain valid bearer tokens from your auth server

### Agent Connection Issues
- Verify MCP servers are running: `curl http://localhost:4001/health`
- Check environment variables in .env
- Ensure GOOGLE_API_KEY is valid
- Verify authentication is configured (JWKS_URL, client credentials)

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
- [x] Authentication & authorization (SDK included)
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
