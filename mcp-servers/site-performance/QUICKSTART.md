# Quick Start Guide - Site Performance MCP Server

Get the Site Performance MCP server running in 2 minutes!

## Prerequisites Check

```bash
# Check Node.js version (need 18+)
node --version

# Check if port 4002 is available
lsof -i :4002 || echo "Port 4002 is available"
```

## Installation (2 steps)

```bash
# 1. Install dependencies
npm install

# 2. Build and start the server
npm run build && npm start
```

The server will start on port 4002 and show:
```
Site Performance MCP Server listening on port 4002
```

## Health Check

Verify the server is running:
```bash
curl http://localhost:4002/health
```

Should return:
```json
{
  "status": "healthy",
  "server": "site-performance"
}
```

## Available Tools

### search_sites

Search for clinical trial sites by region and therapeutic area.

**Parameters:**
- `region` (string, required): Geographic region (e.g., "US-Northeast")
- `therapeutic_area` (string, optional): Therapeutic area expertise (e.g., "Endocrinology")
- `min_capacity` (number, optional): Minimum patient enrollment capacity

**Example Query:**
```json
{
  "region": "US-Northeast",
  "therapeutic_area": "Endocrinology",
  "min_capacity": 400
}
```

### get_site_capabilities

Get detailed capabilities and equipment for a specific site.

**Parameters:**
- `site_id` (string, required): Site identifier (e.g., "SITE-001")

**Example Query:**
```json
{
  "site_id": "SITE-001"
}
```

### get_enrollment_history

Get historical enrollment performance and trial data for a site.

**Parameters:**
- `site_id` (string, required): Site identifier
- `years` (number, optional): Number of years of history (default: 3)

**Example Query:**
```json
{
  "site_id": "SITE-001",
  "years": 5
}
```

## Testing the Server

**Note:** The MCP server requires authentication. You'll need a valid JWT bearer token from your authentication server. For testing, you can obtain a token through your OAuth flow or use the agent's authentication system.

### List Available Tools
```bash
curl -X POST http://localhost:4002/mcp \
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
curl -X POST http://localhost:4002/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "search_sites",
      "arguments": {
        "region": "US-Northeast",
        "therapeutic_area": "Endocrinology"
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

### Error: "Port 4002 already in use"

Find and kill the process:
```bash
lsof -ti:4002 | xargs kill -9
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
PORT=4002
AUTH_SERVER_BASE_URL=https://your-auth-server
ISSUER=https://your-auth-server/oauth2/token
```

## Next Steps

- Read README.md for detailed API documentation
- Check auth logs at `/auth-logs` endpoint
- Review source code in `src/` directory
- Test with the clinical trial agent

## Integration

This server provides site performance data to the Clinical Trial Site Selection Agent. Make sure it's running before starting the agent.

Happy site analysis! 🏥