import { AlertCircle, RefreshCw } from 'lucide-react'
import './ErrorDisplay.css'

function ErrorDisplay({ error }) {
  const handleRetry = () => {
    window.location.reload()
  }

  return (
    <div className="card error-display fade-in">
      <div className="error-header">
        <AlertCircle size={32} className="error-icon" />
        <div>
          <h3 className="error-title">Unable to Complete Request</h3>
          <p className="error-subtitle">{error.message}</p>
        </div>
      </div>

      {error.details && (
        <div className="error-details">
          <p className="error-details-title">Details:</p>
          <p className="error-details-text">{error.details}</p>
        </div>
      )}

      <div className="error-actions">
        <button onClick={handleRetry} className="btn btn-primary">
          <RefreshCw size={20} />
          Try Again
        </button>
      </div>

      <div className="error-help">
        <p className="error-help-title">Troubleshooting:</p>
        <ul className="error-help-list">
          <li>Verify the agent is running on http://localhost:8010</li>
          <li>Check that MCP servers are accessible</li>
          <li>Ensure your ANTHROPIC_API_KEY is configured</li>
          <li>Review the agent logs for error details</li>
        </ul>
      </div>
    </div>
  )
}

export default ErrorDisplay
