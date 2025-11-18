# Site Performance MCP Server

MCP server providing clinical trial site performance and capabilities data.

## Installation
```bash
npm install
npm run build
```

## Running
```bash
npm start
# or for development
npm run dev
```

The server will start on port 3002 (or PORT environment variable).

## Available Tools

### search_sites

Search for clinical trial sites matching criteria.

**Parameters:**
- `region` (string, required): Geographic region
- `therapeutic_area` (string, optional): Therapeutic area expertise
- `min_capacity` (number, optional): Minimum patient enrollment capacity

**Example:**
```json
{
  "region": "US-Northeast",
  "therapeutic_area": "Endocrinology",
  "min_capacity": 400
}
```

### get_site_capabilities

Get detailed capabilities for a specific site.

**Parameters:**
- `site_id` (string, required): Site identifier (e.g., "SITE-001")

**Example:**
```json
{
  "site_id": "SITE-001"
}
```

### get_enrollment_history

Get historical enrollment performance for a site.

**Parameters:**
- `site_id` (string, required): Site identifier
- `years` (number, optional): Number of years of history (default: 3)

**Example:**
```json
{
  "site_id": "SITE-001",
  "years": 5
}
```

## Testing
```bash
curl -X POST http://localhost:3002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```