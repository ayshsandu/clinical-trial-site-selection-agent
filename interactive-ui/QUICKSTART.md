# Quick Start Guide - Clinical Trial UI

Get the UI running in 3 minutes!

## Prerequisites Check

```bash
# Check Node.js version (need 18+)
node --version

# Check if agent is running
curl http://localhost:8010/api/query \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}'
```

## Installation (2 steps)

```bash
# 1. Install dependencies
npm install

# 2. Start development server
npm run dev
```

That's it! The UI will open at `http://localhost:3000`

## First Query

1. Open `http://localhost:3000` in your browser
2. Enter a query or click an example:
   - "Find sites for Phase III diabetes trial in Northeast US"
3. Click "Find Sites"
4. Wait 30-60 seconds for results

## Example Queries

Try these:

**Diabetes Trial**:
```
Find sites for a Phase III Type 2 Diabetes trial targeting 200 patients 
in the Northeast US with strong endocrinology departments
```

**Cancer Trial**:
```
I need 5 sites for a Phase II lung cancer trial in California, 
preferably academic medical centers with PET imaging capabilities
```

**Quick Test**:
```
Find sites for Phase III diabetes trial
```

## Troubleshooting

### Error: "Failed to fetch"

The agent isn't running. Start it:
```bash
cd ../clinical-trial-agent
poetry run python main.py
```

### Error: "npm command not found"

Install Node.js from https://nodejs.org

### Port 3000 Already in Use

Change the port in `vite.config.js`:
```javascript
export default defineConfig({
  server: {
    port: 4001, // Change this
  }
})
```

## Next Steps

- Read README.md for full documentation
- Explore all example queries
- Check the audit trail in results
- Review code in `src/` folder

## Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Serve with any static server
npx serve dist
```

## Tips

- Use natural language in queries
- Be specific about requirements
- Include trial phase, disease, location
- Check browser console for errors
- Results show in 30-60 seconds

Happy site selection! 🏥
