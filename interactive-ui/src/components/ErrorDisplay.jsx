import { AlertCircle, RefreshCw, ExternalLink } from 'lucide-react'
import './ErrorDisplay.css'

function ErrorDisplay({ error }) {
  const handleRetry = () => {
    window.location.reload()
  }

  const is401 = error.response && error.response.status === 401
  const authUrl = is401 && error.response.headers ? error.response.headers.get('x-auth-redirect-url') : null
  const handleOAuth = () => {
    if (authUrl) {
      window.open(authUrl, '_blank')
    }
  }

  // if error.response.status is 403 show different message that user lacks permissions to use the service
  const is403 = error.response && error.response.status === 403
  if (is403) {
    return (
      <div className="card error-display fade-in">
        <div className="error-header">
          <AlertCircle size={32} className="error-icon" />
          <div>
            <h3 className="error-title">Access Forbidden</h3>
            <p className="error-subtitle">You do not have permission to access this service.</p>
          </div>
        </div>

        <div className="error-help">
          <p className="error-help-title">Troubleshooting:</p>
          <ul className="error-help-list">
            <li>Ensure your account has the necessary permissions</li>
            <li>Contact your administrator for access</li>
          </ul>
        </div>
      </div>
    )
  }

  return (
    <div className="card error-display fade-in">
      {/* <div className="error-header">
        <AlertCircle size={32} className="error-icon" />
        <div>
          <h3 className="error-title">Unable to Complete Request</h3>
          <p className="error-subtitle">{error.message}</p>
        </div>
      </div> */}

      {error.details && (
        <div className="error-details">
          <p className="error-details-title">Details:</p>
          <p className="error-details-text">{error.details}</p>
        </div>
      )}

      {authUrl && (
        <div className="error-oauth">
          <p className="error-oauth-title">Authorization Required:</p>
          <p className="error-oauth-text">
            You need to authorize access to the query service. Click the button below to start the OAuth flow in a new tab.
          </p>
          <button onClick={handleOAuth} className="btn btn-auth">
            <ExternalLink size={20} />
            Authorize Access
          </button>
          <p className="error-oauth-instruction">
            After completing authorization, return here and click "Try Again" to retry your request.
          </p>
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
          <li>Ensure required permissions are available</li>
          <li>Ensure Agent's Keys are configured</li>
          <li>Review the agent logs for error details</li>
        </ul>
      </div>
    </div>
  )
}

export default ErrorDisplay
