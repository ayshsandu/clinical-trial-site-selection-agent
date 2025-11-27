import { useState } from 'react'
import { Send, Sparkles } from 'lucide-react'
import './QueryForm.css'

function QueryForm({ onSubmit, isLoading }) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim() && !isLoading) {
      onSubmit(query.trim())
    }
  }

  return (
    <div className="card query-form-card">
      <div className="query-form-header">
        <Sparkles size={24} className="query-icon" />
        <div>
          <h2 className="query-form-title">Trial Feasibility Assessment</h2>
          <p className="query-form-subtitle">
            Describe your protocol requirements to identify optimal sites
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="query-form">
        <div className="form-group">
          <label htmlFor="query" className="form-label">
            Protocol Parameters
          </label>
          <textarea
            id="query"
            className="form-textarea"
            placeholder="Example: Identify sites for a Phase III Type 2 Diabetes study requiring 200 patients in the Northeast US. Sites must have endocrinology expertise and recent experience with similar protocols."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
            rows={4}
          />
          <div className="query-help">
            <p>
              💡 <strong>Tips:</strong> Include trial phase, therapeutic area, target enrollment,
              geographic preferences, and specific inclusion/exclusion criteria.
            </p>
          </div>
        </div>

        <button
          type="submit"
          className="btn btn-primary btn-submit"
          disabled={!query.trim() || isLoading}
        >
          {isLoading ? (
            <>
              <div className="spinner" style={{ width: '20px', height: '20px' }}>
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" opacity="0.25" />
                  <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
                </svg>
              </div>
              Analyzing...
            </>
          ) : (
            <>
              <Send size={20} />
              Analyze Sites
            </>
          )}
        </button>
      </form>
    </div>
  )
}

export default QueryForm
