import { useState } from 'react'
import { useAuthContext } from '@asgardeo/auth-react'
import './App.css'
import QueryForm from './components/QueryForm'
import ResultsDisplay from './components/ResultsDisplay'
import LoadingState from './components/LoadingState'
import ErrorDisplay from './components/ErrorDisplay'
import Header from './components/Header'
import ExampleQueries from './components/ExampleQueries'
import AuthGuard from './components/AuthGuard'
import MCPServerControls from './components/MCPServerControls'
import ArchitectView from './components/ArchitectView'
import { agentConfig } from './config'

function App() {
  const [currentView, setCurrentView] = useState('query') // 'query' or 'architect'
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [queryHistory, setQueryHistory] = useState([])
  const { getAccessToken } = useAuthContext()

  const handleQuery = async (query) => {
    setIsLoading(true)
    setError(null)
    setResults(null)

    try {
      // Get the access token to include in the API request
      const accessToken = await getAccessToken()

      // Set up timeout for the fetch request
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 120000) // 120 second timeout

      const response = await fetch(agentConfig.queryUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Include the access token in the Authorization header
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ query }),
        signal: controller.signal,
      })

      clearTimeout(timeoutId) // Clear timeout if request completes

      if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`)
        error.response = response
        throw error
      }

      const data = await response.json()
      console.log('Received data:', data);
      setResults(data)

      // Add to query history
      setQueryHistory(prev => [
        { query, timestamp: new Date(), results: data },
        ...prev.slice(0, 9) // Keep last 10
      ])

    } catch (err) {
      console.error('Error querying agent:', err)
      if (err.name === 'AbortError') {
        setError({
          message: 'Request timed out',
          details: 'The query took too long to respond. Please try again or check if the agent is running.'
        })
      } else {
        const error = new Error(`HTTP error! status: ${err.status}`)
        error.response = err
        setError(err)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleExampleQuery = (exampleQuery) => {
    handleQuery(exampleQuery)
  }

  const handleHistoryQuery = (historyItem) => {
    setResults(historyItem.results)
    setError(null)
  }

  return (
    <AuthGuard>
      <div className="app">
        <Header />

        {/* Navigation Tabs */}
        <div className="view-navigation">
          <div className="container">
            <div className="nav-tabs">
              <button
                className={`nav-tab ${currentView === 'query' ? 'nav-tab-active' : ''}`}
                onClick={() => setCurrentView('query')}
              >
                <svg className="nav-tab-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                Query Agent
              </button>
              <button
                className={`nav-tab ${currentView === 'architect' ? 'nav-tab-active' : ''}`}
                onClick={() => setCurrentView('architect')}
              >
                <svg className="nav-tab-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
                Architecture
              </button>
            </div>
          </div>
        </div>

        {/* Conditional View Rendering */}
        {currentView === 'query' ? (
          <main className="container">
            <div className="main-content">
              {/* MCP Server Controls */}
              <MCPServerControls />

              <div className="query-section">
                <QueryForm
                  onSubmit={handleQuery}
                  isLoading={isLoading}
                />

                {!isLoading && !results && !error && (
                  <ExampleQueries onSelectExample={handleExampleQuery} />
                )}
              </div>

              {isLoading && <LoadingState />}

              {error && <ErrorDisplay error={error} />}

              {results && !isLoading && (
                <ResultsDisplay
                  results={results}
                  queryHistory={queryHistory}
                  onSelectHistory={handleHistoryQuery}
                />
              )}
            </div>
          </main>
        ) : (
          <ArchitectView />
        )}

        <footer className="footer">
          <div className="container">
            <p>Clinical Trial Site Selection Agent • Powered by Asgardeo</p>
          </div>
        </footer>
      </div>
    </AuthGuard>
  )
}

export default App
