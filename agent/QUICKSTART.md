# Quick Start Guide

Get the Clinical Trial Site Selection Agent running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.11+)
python --version

# Check MCP servers are running
curl http://localhost:4001/health
curl http://localhost:4002/health
```

Both health checks should return `{"status":"healthy","server":"..."}`.

## Step 1: Install Dependencies

### Option A: Using Poetry (Recommended)

```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

### Option B: Using pip

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Anthropic API key
nano .env  # or use your preferred editor
```

Your `.env` should look like:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
DEMOGRAPHICS_SERVER_URL=http://localhost:4001/mcp
PERFORMANCE_SERVER_URL=http://localhost:4002/mcp
LOG_LEVEL=INFO
```

## Step 3: Run Your First Query

### Using Poetry

```bash
poetry run python main.py --query "Find sites for Phase III Type 2 Diabetes trial in Northeast US"
```

### Using pip/venv

```bash
python main.py --query "Find sites for Phase III Type 2 Diabetes trial in Northeast US"
```

## Step 4: Try Interactive Mode

```bash
# With Poetry
poetry run python main.py

# With pip/venv
python main.py
```

Then enter your query at the prompt.

## Example Queries to Try

1. **Diabetes Trial**:
   ```
   Find sites for Phase III Type 2 Diabetes trial targeting 200 patients in the Northeast US
   ```

2. **Cancer Trial**:
   ```
   I need sites for Phase II lung cancer trial in California with PET imaging
   ```

3. **Rare Disease**:
   ```
   Looking for sites with metabolic disorder experience, any US location
   ```

4. **Cardiology Trial**:
   ```
   Find sites for Phase III hypertension study in major metropolitan areas
   ```

## Expected Output

You should see:

```
🔍 Analyzing your request...
⏳ This may take 30-60 seconds...

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
    [...]

✅ Analysis complete: 5 sites recommended
```

## Troubleshooting

### Error: "ANTHROPIC_API_KEY not set"

Solution:
```bash
# Check if .env file exists
cat .env

# Verify API key is set
echo $ANTHROPIC_API_KEY

# Set it manually if needed
export ANTHROPIC_API_KEY=sk-ant-your-key
```

### Error: "Connection refused"

Solution:
```bash
# Check if MCP servers are running
curl http://localhost:4001/health
curl http://localhost:4002/health

# If not running, start them
cd ../mcp-servers/patient-demographics && npm start &
cd ../mcp-servers/site-performance && npm start &
```

### Error: Module not found

Solution:
```bash
# Reinstall dependencies
poetry install  # or pip install -r requirements.txt

# Make sure you're in the right directory
pwd  # should end with /clinical-trial-agent
```

## Save Results to File

```bash
# Text format
poetry run python main.py \
  --query "Your query" \
  --output report.txt

# JSON format
poetry run python main.py \
  --query "Your query" \
  --json \
  --output results.json
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Explore different query patterns
- Check the audit trail to understand data flow
- Experiment with different trial types and regions

## Getting Help

- Check logs for detailed error messages (set `LOG_LEVEL=DEBUG` in .env)
- Verify MCP servers are running with `/health` endpoints
- Ensure Anthropic API key is valid
- Open an issue if you find bugs

Happy site selection! 🎉
