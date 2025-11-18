import { useState } from 'react'
import { CheckCircle, MapPin, Users, TrendingUp, Award, AlertTriangle, Clock, FileText } from 'lucide-react'
import './ResultsDisplay.css'

function ResultsDisplay({ results }) {
  const [selectedSite, setSelectedSite] = useState(null)

  console.log('Rendering ResultsDisplay with results:', results);
  // Extract data from results
  const resultsData = results.result || {}
  const trialRequirements = resultsData.trial_requirements || {}
  const recommendedSites = resultsData.recommended_sites || []
  const analysisSummary = resultsData.analysis_summary || ''
  const auditTrail = resultsData.audit_trail || []
  const getScoreColor = (score) => {
    if (score >= 0.8) return 'high'
    if (score >= 0.6) return 'medium'
    return 'low'
  }

  const getScoreLabel = (score) => {
    if (score >= 0.8) return 'Excellent Match'
    if (score >= 0.6) return 'Good Match'
    return 'Fair Match'
  }

  return (
    <div className="results-display fade-in">
      {/* Summary Card */}
      <div className="card summary-card">
        <div className="summary-header">
          <CheckCircle size={24} className="summary-icon" />
          <div>
            <h2 className="summary-title">Analysis Complete</h2>
            <p className="summary-subtitle">
              Found {recommendedSites.length} recommended sites
            </p>
          </div>
        </div>

        {/* Trial Requirements */}
        {Object.keys(trialRequirements).length > 0 && (
          <div className="trial-requirements">
            <h3 className="section-title">Trial Requirements</h3>
            <div className="requirements-grid">
              {trialRequirements.disease && (
                <div className="requirement-item">
                  <span className="requirement-label">Disease:</span>
                  <span className="requirement-value">{trialRequirements.disease}</span>
                </div>
              )}
              {trialRequirements.phase && (
                <div className="requirement-item">
                  <span className="requirement-label">Phase:</span>
                  <span className="requirement-value">{trialRequirements.phase}</span>
                </div>
              )}
              {trialRequirements.target_enrollment && (
                <div className="requirement-item">
                  <span className="requirement-label">Target Enrollment:</span>
                  <span className="requirement-value">{trialRequirements.target_enrollment}</span>
                </div>
              )}
              {trialRequirements.geographic_preferences && (
                <div className="requirement-item">
                  <span className="requirement-label">Region:</span>
                  <span className="requirement-value">
                    {trialRequirements.geographic_preferences.join(', ')}
                  </span>
                </div>
              )}
              {trialRequirements.therapeutic_area && (
                <div className="requirement-item">
                  <span className="requirement-label">Therapeutic Area:</span>
                  <span className="requirement-value">{trialRequirements.therapeutic_area}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Analysis Summary */}
        {analysisSummary && (
          <div className="analysis-summary">
            <h3 className="section-title">Analysis Summary</h3>
            <p className="summary-text">{analysisSummary}</p>
          </div>
        )}
      </div>

      {/* Recommended Sites */}
      <div className="sites-section">
        <h2 className="sites-title">Recommended Sites</h2>
        
        <div className="sites-grid">
          {recommendedSites.map((site, index) => (
            <div key={index} className="card site-card">
              <div className="site-header">
                <div className="site-rank">#{site.rank}</div>
                <div className="site-info">
                  <h3 className="site-name">{site.site_name}</h3>
                  <p className="site-id">{site.site_id}</p>
                </div>
              </div>

              <div className="site-score">
                <div className="score-header">
                  <span className="score-label">Match Score</span>
                  <span className="score-value">{(site.score * 100).toFixed(0)}%</span>
                </div>
                <div className={`score-bar ${getScoreColor(site.score)}`}>
                  <div 
                    className="score-bar-fill"
                    style={{ width: `${site.score * 100}%` }}
                  ></div>
                </div>
                <span className={`score-badge badge-${getScoreColor(site.score)}`}>
                  {getScoreLabel(site.score)}
                </span>
              </div>

              <div className="site-reasoning">
                <p>{site.reasoning}</p>
              </div>

              {/* Key Strengths */}
              {site.key_strengths && site.key_strengths.length > 0 && (
                <div className="site-section">
                  <h4 className="section-subtitle">
                    <Award size={16} />
                    Key Strengths
                  </h4>
                  <ul className="strength-list">
                    {site.key_strengths.map((strength, idx) => (
                      <li key={idx}>{strength}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Concerns */}
              {site.concerns && site.concerns.length > 0 && (
                <div className="site-section">
                  <h4 className="section-subtitle concerns">
                    <AlertTriangle size={16} />
                    Considerations
                  </h4>
                  <ul className="concern-list">
                    {site.concerns.map((concern, idx) => (
                      <li key={idx}>{concern}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Patient Pool */}
              {site.patient_pool_match && (
                <div className="site-metrics">
                  <div className="metric-item">
                    <Users size={16} className="metric-icon" />
                    <div className="metric-content">
                      <span className="metric-label">Estimated Eligible</span>
                      <span className="metric-value">
                        {site.patient_pool_match.estimated_eligible_patients?.toLocaleString() || 'N/A'}
                      </span>
                    </div>
                  </div>
                  {site.patient_pool_match.region && (
                    <div className="metric-item">
                      <MapPin size={16} className="metric-icon" />
                      <div className="metric-content">
                        <span className="metric-label">Region</span>
                        <span className="metric-value">{site.patient_pool_match.region}</span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Historical Performance */}
              {site.historical_performance && (
                <div className="site-metrics">
                  <div className="metric-item">
                    <TrendingUp size={16} className="metric-icon" />
                    <div className="metric-content">
                      <span className="metric-label">Enrollment Rate</span>
                      <span className="metric-value">
                        {site.historical_performance.avg_enrollment_rate?.toFixed(2) || 'N/A'}x
                      </span>
                    </div>
                  </div>
                  <div className="metric-item">
                    <CheckCircle size={16} className="metric-icon" />
                    <div className="metric-content">
                      <span className="metric-label">Retention Rate</span>
                      <span className="metric-value">
                        {((site.historical_performance.retention_rate || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <div className="metric-item">
                    <FileText size={16} className="metric-icon" />
                    <div className="metric-content">
                      <span className="metric-label">Completed Trials</span>
                      <span className="metric-value">
                        {site.historical_performance.completed_trials || 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Audit Trail */}
      {auditTrail && auditTrail.length > 0 && (
        <div className="card audit-trail">
          <div className="audit-header">
            <Clock size={20} />
            <h3 className="audit-title">Audit Trail</h3>
          </div>
          <div className="audit-list">
            {auditTrail.slice(0, 10).map((entry, index) => (
              <div key={index} className="audit-item">
                <div className="audit-timestamp">
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </div>
                <div className="audit-content">
                  <div className="audit-node">{entry.node}</div>
                  <div className="audit-action">{entry.action}</div>
                  {entry.results_summary && (
                    <div className="audit-result">{entry.results_summary}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ResultsDisplay
