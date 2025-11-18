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

function App() {
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
      
      const response = await fetch('http://localhost:8010/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Include the access token in the Authorization header
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ query }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
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
      setError({
        message: err.message || 'Failed to query the agent',
        details: 'Please ensure the agent is running on http://localhost:8010'
      })
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

        <footer className="footer">
          <div className="container">
            <p>Clinical Trial Site Selection Agent • Powered by LangGraph & Claude</p>
          </div>
        </footer>
      </div>
    </AuthGuard>
  )
}

export default App
