# Clinical Trial Site Selection Agent

LangGraph-based AI agent for intelligent clinical trial site selection using Google Gemini and Model Context Protocol (MCP) servers.

## Overview

This agent orchestrates data from multiple MCP servers to provide data-driven recommendations for clinical trial sites. It analyzes patient demographics, site capabilities, and historical performance to rank optimal sites.

## Architecture

```
┌─────────────────────────────────────┐
│   Trial Site Selection Agent        │
│        (LangGraph)                   │
│                                      │
│  ┌──────────────────────────────┐   │
│  │ 1. Parse Requirements        │   │
│  │ 2. Query Demographics        │───┼──→ Demographics MCP (4001)
│  │ 3. Query Performance         │───┼──→ Performance MCP (4002)
│  │ 4. Analyze & Rank            │   │
│  │ 5. Generate Report           │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

## Features

- 🤖 **AI-Powered Analysis**: Uses Google Gemini to understand queries and analyze data
- 🔄 **Multi-Source Data**: Integrates patient demographics and site performance
- 📊 **Data-Driven Ranking**: Scores sites based on multiple criteria
- 🔍 **Transparent Reasoning**: Provides clear explanations for recommendations
- 📝 **Audit Trail**: Complete tracking of all data access and decisions
- 🎯 **Flexible Queries**: Natural language interface for trial requirements

## Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Running MCP servers:
  - Patient Demographics Server (default: http://localhost:4001/mcp)
  - Site Performance Server (default: http://localhost:4002/mcp)
- Google API key for Gemini

## Installation

```bash
# Install dependencies

poetry install

# Or using pip
source venv/bin/activate && pip install -r requirements.txt
pip install -r requirements.txt
```

## Configuration

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
GOOGLE_API_KEY=your-google-api-key-here
DEMOGRAPHICS_SERVER_URL=http://localhost:4001/mcp
PERFORMANCE_SERVER_URL=http://localhost:4002/mcp
LOG_LEVEL=INFO
```

## Usage

### Interactive Mode

```bash
poetry run python main.py
```

Then enter your query when prompted.

### Direct Query

```bash
poetry run python main.py --query "Find sites for Phase III Type 2 Diabetes trial in Northeast US"
```

### JSON Output

```bash
poetry run python main.py \
  --query "Find sites for Phase II lung cancer trial in California" \
  --json \
  --output results.json
```

### Custom MCP Server URLs

```bash
poetry run python main.py \
  --query "Your query here" \
  --demographics-url http://localhost:4001/mcp \
  --performance-url http://localhost:4002/mcp
```

## Example Queries

```bash
# Type 2 Diabetes trial
"Find sites for a Phase III Type 2 Diabetes trial targeting 200 patients 
 in the Northeast US with strong endocrinology departments"

# Oncology trial
"I need 5 sites for a Phase II lung cancer trial in California, 
 preferably academic medical centers with PET imaging capabilities"

# Rare disease trial
"Looking for sites with experience in rare metabolic disorders, 
 any US location, need at least 50 potential patients per site"

# Cardiovascular trial
"Find sites for Phase III hypertension trial in major metropolitan areas 
 with proven track record in cardiology trials"
```

## Project Structure

```
clinical-trial-agent/
├── main.py                      # Entry point
├── pyproject.toml              # Poetry dependencies
├── .env.example                # Environment template
├── README.md                   # This file
└── src/
    ├── __init__.py
    ├── agent.py                # LangGraph workflow
    ├── state.py                # State definitions
    ├── mcp_client.py           # MCP client wrapper
    └── nodes/
        ├── __init__.py
        ├── parse_requirements.py    # Parse user query
        ├── query_demographics.py    # Query demographics MCP
        ├── query_performance.py     # Query performance MCP
        ├── analyze_and_rank.py      # LLM analysis & ranking
        └── generate_report.py       # Format final report
```

## Workflow

1. **Parse Requirements**: Extract structured trial parameters from natural language
2. **Query Demographics**: Search patient populations and regional health data
3. **Query Performance**: Retrieve site capabilities and historical performance
4. **Analyze & Rank**: Use LLM to analyze all data and score sites
5. **Generate Report**: Format recommendations with reasoning and audit trail

## Scoring Methodology

Sites are scored (0-1.0) based on:

- **Patient Population Match (40%)**: Availability of eligible patients
- **Historical Performance (30%)**: Enrollment rates, retention, quality
- **Site Capabilities (30%)**: Equipment, staff, certifications

## Output Format

### Text Report

```
================================================================================
CLINICAL TRIAL SITE SELECTION REPORT
================================================================================

Query: Find sites for Phase III Type 2 Diabetes trial in Northeast US

TRIAL REQUIREMENTS:
  Disease: Type 2 Diabetes
  Phase: Phase III
  Target Enrollment: 200
  Geographic Preferences: US-Northeast

RECOMMENDED SITES:

#1 - Massachusetts General Hospital CRC (Score: 0.92)
    Reasoning: Excellent match with 45K T2D patient pool nearby...
    Key Strengths:
      • Strong historical performance (34 completed trials)
      • High patient retention (89%)
      • Adequate capacity (8 available trial slots)
    Patient Pool:
      • Estimated Eligible: 45000
      • Region: Boston Metropolitan Area
    Historical Performance:
      • Enrollment Rate: 1.08
      • Retention Rate: 0.89
      • Completed Trials: 34

[Additional sites...]

AUDIT TRAIL: (15 entries)
  [2025-11-17T10:30:00] parse_requirements: Parse trial requirements
    → Extracted 5 fields
  [2025-11-17T10:30:05] query_demographics: Search patient pools
    → Found 3 pools
  [...]
```

### JSON Report

```json
{
  "user_query": "...",
  "trial_requirements": {...},
  "recommended_sites": [
    {
      "rank": 1,
      "site_id": "SITE-001",
      "site_name": "...",
      "score": 0.92,
      "reasoning": "...",
      "key_strengths": [...],
      "patient_pool_match": {...},
      "historical_performance": {...}
    }
  ],
  "analysis_summary": "...",
  "audit_trail": [...],
  "generated_at": "2025-11-17T10:35:00"
}
```

## Error Handling

The agent includes comprehensive error handling:

- MCP server connection failures
- LLM parsing errors
- Missing or invalid data
- API rate limits

Errors are logged and included in the audit trail.

## Logging

Configure logging level in `.env`:

```bash
LOG_LEVEL=DEBUG   # Detailed logs
LOG_LEVEL=INFO    # Standard logs (default)
LOG_LEVEL=WARNING # Warnings only
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Type Checking

```bash
poetry run mypy src/
```

### Formatting

```bash
poetry run black src/
poetry run ruff check src/
```

## Troubleshooting

### "GOOGLE_API_KEY not set"

Set your API key:
```bash
export GOOGLE_API_KEY=your-google-api-key
```

### "Connection refused" errors

Ensure MCP servers are running:
```bash
curl http://localhost:4001/health
curl http://localhost:4002/health
```

### "Failed to parse JSON from LLM"

This may indicate:
- Model returning unexpected format
- Rate limiting
- API issues

Check logs for details.

## Performance

Typical execution time: 30-60 seconds
- Parse requirements: ~2-3 seconds
- Query demographics: ~5-10 seconds
- Query performance: ~10-15 seconds
- Analysis & ranking: ~10-20 seconds

## Limitations

- Currently supports US sites only
- Mock data (not connected to real databases)
- Limited to ~10 sites per query for performance
- No caching (each run queries servers fresh)

## Future Enhancements

- [ ] Parallel MCP queries for faster execution
- [ ] Caching layer for frequently accessed data
- [ ] Web UI interface
- [ ] Streaming responses
- [ ] Multi-region support
- [ ] Budget optimization
- [ ] Competitive landscape analysis

## License

MIT

## Support

For issues or questions, please open a GitHub issue.

## Contributing

Contributions welcome! Please read the contributing guidelines first.
