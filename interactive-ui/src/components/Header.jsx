import { Activity } from 'lucide-react'
import './Header.css'

function Header() {
  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="header-logo">
            <Activity className="header-icon" size={32} />
            <div>
              <h1 className="header-title">ClinicalCompass: Clinical Trial Site Selection Demo</h1>
              <p className="header-subtitle">AI-Powered Site Recommendations</p>
            </div>
          </div>
          <div className="header-status">
            <div className="status-indicator">
              <div className="status-dot"></div>
              <span>Agent Active</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
