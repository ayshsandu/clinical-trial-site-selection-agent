import { useState, useEffect } from 'react'
import { Database, Activity, Server, PlayCircle, RefreshCw } from 'lucide-react'
import { mcpServers } from '../config'
import { mcpClientManager } from '../utils/mcpClient'
import './MCPServerControls.css'

function MCPServerControls() {
  const [activeServer, setActiveServer] = useState('demographics')
  const [selectedTool, setSelectedTool] = useState('')
  const [toolParams, setToolParams] = useState({})
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [availableTools, setAvailableTools] = useState([])
  const [isLoadingTools, setIsLoadingTools] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState({
    demographics: false,
    performance: false
  })

  const currentServer = mcpServers[activeServer]

  // Load available tools when server changes
  useEffect(() => {
    loadAvailableTools()
  }, [activeServer])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mcpClientManager.disconnectAll()
    }
  }, [])

  const loadAvailableTools = async () => {
    setIsLoadingTools(true)
    setError(null)
    
    try {
      const tools = await mcpClientManager.listTools(currentServer.url)
      setAvailableTools(tools)
      setConnectionStatus(prev => ({
        ...prev,
        [activeServer]: true
      }))
    } catch (err) {
      console.error('Error loading tools:', err)
      setError({
        message: 'Failed to connect to MCP server',
        details: `Could not load tools from ${currentServer.name}. Please ensure the server is running on ${currentServer.url}`
      })
      setAvailableTools([])
      setConnectionStatus(prev => ({
        ...prev,
        [activeServer]: false
      }))
    } finally {
      setIsLoadingTools(false)
    }
  }

  const handleToolChange = (toolId) => {
    setSelectedTool(toolId)
    setToolParams({})
    setResult(null)
    setError(null)
  }

  const handleParamChange = (paramName, value, paramType) => {
    // Convert to appropriate type based on input type
    let parsedValue = value;
    if (paramType === 'number') {
      parsedValue = value === '' ? 0 : Number(value);
    }
    
    setToolParams(prev => ({
      ...prev,
      [paramName]: parsedValue
    }))
  }

  const handleExecute = async () => {
    if (!selectedTool) return

    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      // Call the tool using MCP SDK
      const response = await mcpClientManager.callTool(
        currentServer.url,
        selectedTool,
        toolParams
      )

      // Extract content from MCP response
      let resultData = response;
      
      // If the response has content array, extract the text
      if (response.content && Array.isArray(response.content)) {
        resultData = response.content.map(item => {
          if (item.type === 'text') {
            try {
              // Try to parse as JSON if possible
              return JSON.parse(item.text);
            } catch {
              return item.text;
            }
          }
          return item;
        });
        
        // If only one item, unwrap it
        if (resultData.length === 1) {
          resultData = resultData[0];
        }
      }

      setResult(resultData)
    } catch (err) {
      console.error('Error calling MCP tool:', err)
      setError({
        message: err.message || 'Failed to execute tool',
        details: `Error executing ${selectedTool} on ${currentServer.name}`
      })
    } finally {
      setIsLoading(false)
    }
  }

  const getToolParameters = (toolId) => {
    // Define parameters for each tool
    const toolParameters = {
      search_patient_pools: [
        { name: 'region', label: 'Region', type: 'text', placeholder: 'e.g., US-NE-001' },
        { name: 'min_population', label: 'Min Patients', type: 'number', placeholder: 'e.g., 100' },
        { name: 'disease', label: 'Condition', type: 'text', placeholder: 'e.g., Type 2 Diabetes' }
      ],
      get_demographics_by_region: [
        { name: 'region', label: 'Region', type: 'text', placeholder: 'e.g., US-NE-001' },
        { name: 'disease_filter', label: 'Condition Filter', type: 'text', placeholder: 'e.g., Hypertension' }
      ],
      search_sites: [
        { name: 'region', label: 'Location', type: 'text', placeholder: 'e.g., US-NE-001' },
        { name: 'therapeutic_area', label: 'Specialty', type: 'text', placeholder: 'e.g., Endocrinology' },
        { name: 'min_capacity', label: 'Min Capacity', type: 'number', placeholder: 'e.g., 50' }
      ],
      get_site_capabilities: [
        { name: 'site_id', label: 'Site ID', type: 'text', placeholder: 'e.g., SITE-001' }
      ],
      get_enrollment_history: [
        { name: 'site_id', label: 'Site ID', type: 'text', placeholder: 'e.g., SITE-001' },
        { name: 'year', label: 'Years', type: 'number', placeholder: 'e.g., 3' },
      ]
    }

    return toolParameters[toolId] || []
  }

  return (
    <div className="mcp-server-controls">
      <div className="mcp-header">
        <Server size={24} className="mcp-icon" />
        <div>
          <h2 className="mcp-title">MCP Server Controls</h2>
          <p className="mcp-subtitle">Direct access to MCP server tools using official SDK</p>
        </div>
        <button
          className="btn-refresh"
          onClick={loadAvailableTools}
          disabled={isLoadingTools}
          title="Refresh tools"
        >
          <RefreshCw size={18} className={isLoadingTools ? 'spinning' : ''} />
        </button>
      </div>

      {/* Connection Status */}
      <div className="connection-status">
        <div className={`status-indicator ${connectionStatus[activeServer] ? 'connected' : 'disconnected'}`}>
          <div className="status-dot"></div>
          <span className="status-text">
            {connectionStatus[activeServer] ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Server Selector */}
      <div className="server-selector">
        <button
          className={`server-tab ${activeServer === 'demographics' ? 'active' : ''}`}
          onClick={() => {
            setActiveServer('demographics')
            setSelectedTool('')
            setToolParams({})
            setResult(null)
            setError(null)
          }}
        >
          <Database size={18} />
          <div className="server-tab-content">
            <span className="server-tab-name">Demographics</span>
            <span className="server-tab-desc">{mcpServers.demographics.description}</span>
          </div>
        </button>
        <button
          className={`server-tab ${activeServer === 'performance' ? 'active' : ''}`}
          onClick={() => {
            setActiveServer('performance')
            setSelectedTool('')
            setToolParams({})
            setResult(null)
            setError(null)
          }}
        >
          <Activity size={18} />
          <div className="server-tab-content">
            <span className="server-tab-name">Performance</span>
            <span className="server-tab-desc">{mcpServers.performance.description}</span>
          </div>
        </button>
      </div>

      {/* Tool Selection */}
      <div className="tool-selection">
        <label htmlFor="tool-select" className="tool-label">
          Select Tool {isLoadingTools && <span className="loading-text">(Loading...)</span>}
        </label>
        <select
          id="tool-select"
          className="tool-select"
          value={selectedTool}
          onChange={(e) => handleToolChange(e.target.value)}
          disabled={isLoading || isLoadingTools}
        >
          <option value="">-- Choose a tool --</option>
          {/* Use tools from MCP server if available, otherwise fall back to config */}
          {(availableTools.length > 0 ? availableTools : currentServer.tools).map((tool) => (
            <option key={tool.id || tool.name} value={tool.name || tool.id}>
              {tool.name || tool.id}
              {tool.description && ` - ${tool.description}`}
            </option>
          ))}
        </select>
        {availableTools.length > 0 && (
          <div className="tool-count">
            {availableTools.length} tool{availableTools.length !== 1 ? 's' : ''} available
          </div>
        )}
      </div>

      {/* Tool Parameters */}
      {selectedTool && (
        <div className="tool-parameters">
          <h3 className="params-title">Parameters</h3>
          {getToolParameters(selectedTool).map((param) => (
            <div key={param.name} className="param-group">
              <label htmlFor={param.name} className="param-label">
                {param.label}
              </label>
              <input
                id={param.name}
                type={param.type}
                className="param-input"
                placeholder={param.placeholder}
                value={toolParams[param.name] || ''}
                onChange={(e) => handleParamChange(param.name, e.target.value, param.type)}
                disabled={isLoading}
              />
            </div>
          ))}

          <button
            className="btn btn-primary btn-execute"
            onClick={handleExecute}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="spinner" style={{ width: '20px', height: '20px' }}>
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" opacity="0.25"/>
                    <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="4" strokeLinecap="round"/>
                  </svg>
                </div>
                Executing...
              </>
            ) : (
              <>
                <PlayCircle size={20} />
                Execute Tool
              </>
            )}
          </button>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mcp-error">
          <div className="error-title">Error</div>
          <div className="error-message">{error.message}</div>
          <div className="error-details">{error.details}</div>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="mcp-result">
          <h3 className="result-title">Result</h3>
          <pre className="result-content">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

export default MCPServerControls
