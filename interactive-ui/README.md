# Clinical Trial Site Selection UI

Modern React web interface for the Clinical Trial Site Selection Agent.

## Overview

This is a professional, production-ready React UI that provides an intuitive interface to interact with the Trial Site Advisor Agent running on `http://localhost:8010`.

## Features

- 🎨 **Modern UI Design**: Clean, professional interface with smooth animations
- 🚀 **Real-time Updates**: Live feedback during agent processing
- 📊 **Rich Data Visualization**: Score bars, metrics, and comprehensive site details
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- 🔍 **Example Queries**: Pre-built examples to get started quickly
- 📜 **Audit Trail**: Complete transparency of agent workflow
- ⚡ **Fast & Lightweight**: Built with Vite for optimal performance

## Screenshots

### Query Interface
- Natural language query input
- Example queries for quick start
- Real-time loading indicators

### Results Display
- Site rankings with match scores
- Key strengths and considerations
- Patient pool and historical performance metrics
- Complete audit trail

## Prerequisites

- Node.js 18+ and npm
- Trial Site Advisor Agent running on `http://localhost:8010/api/query`
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Usage

### Development Mode

```bash
npm run dev
```

The UI will be available at `http://localhost:3000`

### Production Build

```bash
# Build
npm run build

# Preview
npm run preview

# Or serve with any static file server
npx serve dist
```

## Configuration

### Agent Endpoint

The UI connects to the agent at `http://localhost:8010/api/query`. If your agent is running on a different URL, update the endpoint in `src/App.jsx`:

```javascript
const response = await fetch('http://your-agent-url:port/api/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ query }),
})
```

### Proxy Configuration

The Vite config includes a proxy for development:

```javascript
// vite.config.js
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8010',
        changeOrigin: true,
      }
    }
  }
})
```

## Project Structure

```
clinical-trial-ui/
├── index.html              # HTML entry point
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration
├── src/
│   ├── main.jsx           # React entry point
│   ├── App.jsx            # Main app component
│   ├── App.css            # App-level styles
│   ├── index.css          # Global styles and utilities
│   └── components/
│       ├── Header.jsx              # App header
│       ├── Header.css
│       ├── QueryForm.jsx           # Query input form
│       ├── QueryForm.css
│       ├── ExampleQueries.jsx      # Example query cards
│       ├── ExampleQueries.css
│       ├── LoadingState.jsx        # Loading indicator
│       ├── LoadingState.css
│       ├── ErrorDisplay.jsx        # Error messages
│       ├── ErrorDisplay.css
│       ├── ResultsDisplay.jsx      # Results presentation
│       └── ResultsDisplay.css
└── README.md              # This file
```

## Components

### Header
- Application branding
- Status indicator (agent active)
- Responsive navigation

### QueryForm
- Text area for natural language queries
- Submit button with loading state
- Helpful tips and examples

### ExampleQueries
- Pre-built query examples
- Click to populate query form
- Covers common use cases

### LoadingState
- Multi-stage progress indicator
- Shows agent workflow steps
- Animated loading animations

### ErrorDisplay
- User-friendly error messages
- Troubleshooting tips
- Retry functionality

### ResultsDisplay
- Trial requirements summary
- Ranked site recommendations
- Score visualization with color coding
- Key strengths and considerations
- Patient pool and performance metrics
- Audit trail of agent actions

## API Integration

### Request Format

```javascript
POST http://localhost:8010/api/query

{
  "query": "Find sites for a Phase III Type 2 Diabetes trial..."
}
```

### Expected Response Format

```javascript
{
  "trial_requirements": {
    "disease": "Type 2 Diabetes",
    "phase": "Phase III",
    "target_enrollment": 200,
    "geographic_preferences": ["US-Northeast"],
    "therapeutic_area": "Endocrinology"
  },
  "recommended_sites": [
    {
      "rank": 1,
      "site_id": "SITE-001",
      "site_name": "Massachusetts General Hospital CRC",
      "score": 0.92,
      "reasoning": "Excellent match...",
      "key_strengths": ["...", "..."],
      "concerns": ["..."],
      "patient_pool_match": {
        "estimated_eligible_patients": 45000,
        "region": "Boston Metropolitan Area"
      },
      "historical_performance": {
        "avg_enrollment_rate": 1.08,
        "retention_rate": 0.89,
        "completed_trials": 34
      }
    }
  ],
  "analysis_summary": "Overall analysis...",
  "audit_trail": [
    {
      "timestamp": "2025-11-18T07:00:00Z",
      "node": "parse_requirements",
      "action": "Parse trial requirements",
      "results_summary": "Extracted 5 fields"
    }
  ]
}
```

## Customization

### Theming

Colors are defined in `src/index.css` using CSS custom properties:

```css
:root {
  --primary-blue: #0066cc;
  --success-green: #10b981;
  --warning-orange: #f59e0b;
  --error-red: #ef4444;
  /* ... */
}
```

### Adding New Features

1. Create new component in `src/components/`
2. Add corresponding CSS file
3. Import and use in `App.jsx`
4. Update this README

## Troubleshooting

### "Failed to fetch" Error

**Cause**: Agent not running or wrong URL

**Solution**:
```bash
# Check agent is running
curl http://localhost:8010/api/query

# Start the agent if needed
cd ../clinical-trial-agent
poetry run python main.py
```

### Blank Screen

**Cause**: Build or runtime error

**Solution**:
```bash
# Check browser console for errors
# Rebuild the app
npm run build
npm run preview
```

### Styling Issues

**Cause**: CSS not loading correctly

**Solution**:
```bash
# Clear cache and rebuild
rm -rf node_modules dist
npm install
npm run dev
```

## Performance Optimization

- **Code Splitting**: Vite automatically splits code
- **Asset Optimization**: Images and fonts optimized
- **Lazy Loading**: Components loaded on demand
- **Caching**: Static assets cached by browser

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

### Code Style

- ESLint for code quality
- Prettier for formatting (optional)
- Consistent naming conventions

### Adding Components

```bash
# Create new component
touch src/components/NewComponent.jsx
touch src/components/NewComponent.css
```

### Running Linter

```bash
npm run lint
```

## Deployment

### Static Hosting

Deploy to any static hosting service:

```bash
# Build
npm run build

# Deploy dist/ folder to:
# - Vercel
# - Netlify
# - GitHub Pages
# - AWS S3
# - Any static host
```



## Future Enhancements

- [ ] Query history sidebar
- [ ] Save/export results as PDF
- [ ] Advanced filtering and sorting
- [ ] Site comparison view
- [ ] Real-time collaboration
- [ ] Dark mode toggle
- [ ] Multi-language support

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

MIT

## Support

For issues or questions:
- Check the browser console for errors
- Verify the agent is running and accessible
- Review this README for troubleshooting steps

## Acknowledgments

- Built with React and Vite
- Icons from Lucide React
- Design inspired by modern healthcare applications

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Status**: Production Ready
