# Clinical Trial Site Selection Demo - Package Contents

## 📦 What's in This Package

This is a **complete implementation** of the Clinical Trial Site Selection system. It includes:

### ✅ Fully Implemented Components

1.  **Patient Demographics MCP Server** (`mcp-servers/patient-demographics/`)
    *   Provides anonymized patient demographic data.
    *   Tools: `search_patient_pools`, `get_demographics_by_region`.

2.  **Site Performance MCP Server** (`mcp-servers/site-performance/`)
    *   Provides site capabilities and historical performance data.
    *   Tools: `search_sites`, `get_site_capabilities`, `get_enrollment_history`.

3.  **LangGraph Agent** (`agent/`)
    *   Python-based agent using LangGraph.
    *   Orchestrates both MCP servers.
    *   Implements site selection workflow (Parse -> Query Demographics -> Query Performance -> Analyze -> Report).

4.  **Interactive UI** (`interactive-ui/`)
    *   Modern React web interface.
    *   Visualizes agent progress and results.

### 📋 Configuration Files

- `.env.example` - Environment variables template
- `.gitignore` - Git ignore rules
- `README.md` - Project overview and quick start guide

## 🚀 Quick Start

### Manual Setup

```bash
cp .env.example .env
# Edit .env with your API keys
# Follow manual setup in README.md
```

See `README.md` for detailed manual setup instructions for each component.

## 📖 Reference

Refer to `agent/PROJECT_SUMMARY.md` for detailed architecture and implementation details.
