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
│   Trial Site Advisor Agent      │
│        (LangGraph)               │
└────────────┬────────────────────┘
             │
      ┌──────┴──────┐
      │             │
┌─────▼────┐  ┌────▼─────────┐
│ Patient  │  │    Site      │
│Demographics│  │ Performance │
│MCP Server│  │ MCP Server   │
└──────────┘  └──────────────┘
```

## Components

1. **LangGraph Agent** (Python) - Orchestrates site selection using Claude
2. **Patient Demographics MCP Server** (TypeScript) - Provides anonymized patient data
3. **Site Performance MCP Server** (TypeScript) - Provides site capabilities and history

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- Anthropic API key

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone and setup
cd clinical-trial-demo
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 2. Start all services
docker-compose up -d

# 3. Run agent
docker-compose exec agent python main.py
```

### Option 2: Manual Setup

```bash
# 1. Start MCP Servers
cd mcp-servers/patient-demographics
npm install && npm run build && npm start &

cd ../site-performance
npm install && npm run build && npm start &

# 2. Start Agent
cd ../../agent
poetry install
poetry run python main.py
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
├── docker-compose.yml
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

### Patient Demographics Server (Port 3001)
- `POST /mcp` - MCP protocol endpoint
- `GET /health` - Health check

### Site Performance Server (Port 3002)
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

```bash
# Agent
ANTHROPIC_API_KEY=sk-ant-...
DEMOGRAPHICS_SERVER_URL=http://localhost:3001/mcp
PERFORMANCE_SERVER_URL=http://localhost:3002/mcp

# MCP Servers
PORT_DEMOGRAPHICS=3001
PORT_PERFORMANCE=3002
LOG_LEVEL=info
```

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
curl -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# Call a tool
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

## Troubleshooting

### MCP Server Not Starting
- Check if ports 3001/3002 are available
- Verify Node.js version (18+)
- Check logs: `docker-compose logs demographics-server`

### Agent Connection Issues
- Verify MCP servers are running: `curl http://localhost:3001/health`
- Check environment variables in .env
- Ensure ANTHROPIC_API_KEY is valid

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
- [ ] Web UI dashboard
- [ ] Budget estimation integration
- [ ] ML-based site performance prediction
- [ ] Real-time enrollment tracking

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For questions or issues, please open a GitHub issue.
