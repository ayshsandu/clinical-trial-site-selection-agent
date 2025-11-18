import { Loader2 } from 'lucide-react'
import './LoadingState.css'

function LoadingState() {
  const stages = [
    { name: 'Parsing Requirements', delay: 0 },
    { name: 'Querying Demographics', delay: 200 },
    { name: 'Querying Performance', delay: 400 },
    { name: 'Analyzing & Ranking', delay: 600 },
    { name: 'Generating Report', delay: 800 },
  ]

  return (
    <div className="card loading-state fade-in">
      <div className="loading-header">
        <Loader2 size={32} className="spinner loading-icon" />
        <div>
          <h3 className="loading-title">Analyzing Your Request</h3>
          <p className="loading-subtitle">This may take 30-60 seconds...</p>
        </div>
      </div>

      <div className="loading-progress">
        <div className="progress-bar">
          <div className="progress-bar-fill pulse"></div>
        </div>
      </div>

      <div className="loading-stages">
        <h4 className="stages-title">Agent Workflow:</h4>
        <ul className="stages-list">
          {stages.map((stage, index) => (
            <li 
              key={index} 
              className="stage-item"
              style={{ animationDelay: `${stage.delay}ms` }}
            >
              <div className="stage-indicator"></div>
              <span>{stage.name}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="loading-info">
        <p>🤖 The agent is orchestrating multiple data sources to provide comprehensive recommendations</p>
      </div>
    </div>
  )
}

export default LoadingState
