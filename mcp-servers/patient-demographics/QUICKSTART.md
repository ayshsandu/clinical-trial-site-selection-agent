# Quick Start Guide - Patient Demographics MCP Server

Get the Patient Demographics MCP server running in 2 minutes!

## Prerequisites Check

```bash
# Check Node.js version (need 18+)
node --version

# Check if port 4001 is available
lsof -i :4001 || echo "Port 4001 is available"
```

## Installation (2 steps)

```bash
# 1. Install dependencies
npm install

# 2. Build and start the server
npm run build && npm start
```

The server will start on port 4001 and show:
```
Patient Demographics MCP Server listening on port 4001
```

## Health Check

Verify the server is running:
```bash
curl http://localhost:4001/health
```

Should return:
```json
{
  "status": "healthy",
  "server": "patient-demographics"
}
```

## Available Tools

### search_patient_pools

Search for patient populations by disease and region.

**Parameters:**
- `disease` (string, optional): Disease or indication (e.g., "Type 2 Diabetes")
- `region` (string, optional): Geographic region (e.g., "US-Northeast")
- `min_population` (number, optional): Minimum patient population size

**Example Query:**
```json
{
  "disease": "Type 2 Diabetes",
  "region": "US-Northeast",
  "min_population": 1000
}
```

### get_demographics_by_region

Get detailed regional demographics and healthcare access data.

**Parameters:**
- `region_id` (string, required): Region identifier (e.g., "US-NE-001")
- `disease_filter` (string, optional): Optional disease filter

**Example Query:**
```json
{
  "region_id": "US-NE-001",
  "disease_filter": "Diabetes"
}
```

## Testing the Server

**Note:** The MCP server requires authentication. You'll need a valid JWT bearer token from your authentication server. For testing, you can obtain a token through your OAuth flow or use the agent's authentication system.

### List Available Tools
```bash
curl -X POST http://localhost:4001/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

### Call a Tool
```bash
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

### Getting a Test Token

For development/testing, you can:
1. Use the Clinical Trial Agent which handles authentication automatically
2. Obtain a token through your OAuth server (Asgardeo or similar)
3. Use a JWT token with the required scope (`query_agent`)

## Troubleshooting

### Error: "Port 4001 already in use"

Find and kill the process:
```bash
lsof -ti:4001 | xargs kill -9
```

### Error: "npm command not found"

Install Node.js from https://nodejs.org (version 18+ required)

### Error: "Build failed"

Clean and rebuild:
```bash
npm run clean
npm install
npm run build
```

### Error: "Module not found"

Reinstall dependencies:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Development Mode

For development with auto-restart:
```bash
npm run dev
```

## Configuration

The server uses environment variables from `.env`:
```bash
# Copy example config
cp .env.example .env

# Edit as needed
PORT=4001
AUTH_SERVER_BASE_URL=https://your-auth-server
ISSUER=https://your-auth-server/oauth2/token
```

## Next Steps

- Read README.md for detailed API documentation
- Check auth logs at `/auth-logs` endpoint
- Review source code in `src/` directory
- Test with the clinical trial agent

## Integration

This server provides patient data to the Clinical Trial Site Selection Agent. Make sure it's running before starting the agent.

Happy data serving! 📊