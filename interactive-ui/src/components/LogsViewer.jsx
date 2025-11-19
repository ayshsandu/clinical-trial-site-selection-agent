import { useState, useEffect } from 'react'
import { FileText, RefreshCw, Filter, X, ArrowLeft } from 'lucide-react'
import { useAuthContext } from '@asgardeo/auth-react'
import './LogsViewer.css'

function LogsViewer({ serverUrl, serverName, onClose }) {
  const [logs, setLogs] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [filterText, setFilterText] = useState('')
  const [filterToolName, setFilterToolName] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const { getAccessToken } = useAuthContext()

  useEffect(() => {
    fetchLogs()
  }, [serverUrl])

  const fetchLogs = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const token = await getAccessToken()
      const logsUrl = serverUrl.replace('/mcp', '/auth-logs')
      
      const response = await fetch(logsUrl, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      // Sort logs by timestamp descending (newest first)
      const sortedLogs = Array.isArray(data) ? data.sort((a, b) => 
        new Date(b.timestamp) - new Date(a.timestamp)
      ) : []
      setLogs(sortedLogs)
    } catch (err) {
      console.error('Error fetching logs:', err)
      setError({
        message: 'Failed to fetch logs',
        details: err.message
      })
    } finally {
      setIsLoading(false)
    }
  }

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
  }

  const formatArgs = (args) => {
    if (!args || Object.keys(args).length === 0) {
      return <span className="args-empty">No arguments</span>
    }
    return (
      <pre className="args-content">
        {JSON.stringify(args, null, 2)}
      </pre>
    )
  }

  const filteredLogs = logs.filter(log => {
    const matchesText = filterText === '' || 
      JSON.stringify(log).toLowerCase().includes(filterText.toLowerCase())
    const matchesTool = filterToolName === '' || 
      (log.toolName && log.toolName.toLowerCase().includes(filterToolName.toLowerCase()))
    return matchesText && matchesTool && log.toolName
  })

  // Group logs by user (sub) - only include logs with toolName
  const logsByUser = filteredLogs
    .filter(log => log.toolName)
    .reduce((acc, log) => {
      const sub = log.sub || 'unknown'
      if (!acc[sub]) {
        acc[sub] = []
      }
      acc[sub].push(log)
      return acc
    }, {})

  // Get unique tool names for filter
  const uniqueToolNames = [...new Set(logs.map(log => log.toolName).filter(Boolean))]

  return (
    <div className="logs-viewer">
      <div className="logs-header">
        <button className="btn-back" onClick={onClose} title="Back to MCP Controls">
          <ArrowLeft size={20} />
        </button>
        <FileText size={24} className="logs-icon" />
        <div className="logs-header-content">
          <h2 className="logs-title">Authentication & Activity Logs</h2>
          <p className="logs-subtitle">{serverName}</p>
        </div>
        <div className="logs-actions">
          <button
            className="btn-filter"
            onClick={() => setShowFilters(!showFilters)}
            title="Toggle filters"
          >
            <Filter size={18} />
            {showFilters && <X size={14} className="filter-close" />}
          </button>
          <button
            className="btn-refresh"
            onClick={fetchLogs}
            disabled={isLoading}
            title="Refresh logs"
          >
            <RefreshCw size={18} className={isLoading ? 'spinning' : ''} />
          </button>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="filters-panel">
          <div className="filter-group">
            <label htmlFor="filter-text">Search</label>
            <input
              id="filter-text"
              type="text"
              className="filter-input"
              placeholder="Search in logs..."
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
            />
          </div>
          <div className="filter-group">
            <label htmlFor="filter-tool">Tool Name</label>
            <select
              id="filter-tool"
              className="filter-select"
              value={filterToolName}
              onChange={(e) => setFilterToolName(e.target.value)}
            >
              <option value="">All tools</option>
              {uniqueToolNames.map(toolName => (
                <option key={toolName} value={toolName}>{toolName}</option>
              ))}
            </select>
          </div>
          {(filterText || filterToolName) && (
            <button
              className="btn-clear-filters"
              onClick={() => {
                setFilterText('')
                setFilterToolName('')
              }}
            >
              Clear filters
            </button>
          )}
        </div>
      )}

      {/* Stats Summary */}
      <div className="logs-stats">
        <div className="stat-item">
          <span className="stat-label">Total Logs:</span>
          <span className="stat-value">{filteredLogs.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Unique Requesters:</span>
          <span className="stat-value">{Object.keys(logsByUser).length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Tool Calls:</span>
          <span className="stat-value">{filteredLogs.filter(log => log.toolName).length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">By Agent:</span>
          <span className="stat-value">{filteredLogs.filter(log => log.sub == "fb0dba08-1621-49f6-82e4-d81094c5de54").length}</span>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="logs-error">
          <div className="error-title">Error</div>
          <div className="error-message">{error.message}</div>
          <div className="error-details">{error.details}</div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="logs-loading">
          <div className="spinner">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" opacity="0.25"/>
              <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="4" strokeLinecap="round"/>
            </svg>
          </div>
          <p>Loading logs...</p>
        </div>
      )}

      {/* Logs Display */}
      {!isLoading && !error && (
        <div className="logs-content">
          {filteredLogs.length === 0 ? (
            <div className="logs-empty">
              <FileText size={48} opacity={0.3} />
              <p>No logs found</p>
            </div>
          ) : (
            <div className="logs-table-container">
              <table className="logs-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Requester (Sub)</th>
                    {/* <th>Agent (Act)</th> */}
                    <th>Tool</th>
                    <th>Arguments</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredLogs.map((log, index) => (
                    <tr key={index} className={log.toolName ? 'log-tool-call' : 'log-auth'}>
                      <td className="timestamp-cell">
                        {formatTimestamp(log.timestamp)}
                      </td>
                      <td className="sub-cell">
                        <code>{log.sub ? log.sub.substring(0, 8) + '...' : 'N/A'}</code>
                      </td>
                      {/* <td className="act-cell">
                        <code>{log.act ? log.act.substring(0, 8) + '...' : 'N/A'}</code>
                      </td> */}
                      <td className="tool-cell">
                        {log.toolName ? (
                          <span className="tool-badge">{log.toolName}</span>
                        ) : (
                          <span className="na-badge">N/A</span>
                        )}
                      </td>
                      <td className="args-cell">
                        {formatArgs(log.args)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Grouped View Option */}
      {!isLoading && !error && filteredLogs.length > 0 && (
        <details className="grouped-view">
          <summary>View Logs Grouped by Requester</summary>
          <div className="grouped-content">
            {Object.entries(logsByUser).map(([sub, userLogs]) => (
              <div key={sub} className="user-group">
                <h4 className="user-group-header">
                  RequesterID: <code>{sub}</code>
                  <span className="user-log-count">({userLogs.length} events)</span>
                </h4>
                <div className="user-logs">
                  {userLogs.map((log, index) => (
                    <div key={index} className="user-log-item">
                      <span className="log-timestamp">{formatTimestamp(log.timestamp)}</span>
                      {log.act && <span className="log-act">Agent: <code>{log.act.substring(0, 8)}...</code></span>}
                      {log.toolName ? (
                        <>
                          <span className="tool-badge">{log.toolName}</span>
                          {log.args && Object.keys(log.args).length > 0 && (
                            <span className="log-args-summary">
                              {Object.keys(log.args).join(', ')}
                            </span>
                          )}
                        </>
                      ) : (
                        <span className="na-badge">N/A</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}

export default LogsViewer
