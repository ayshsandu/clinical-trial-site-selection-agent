import { useAuthContext } from '@asgardeo/auth-react'
import { LogIn, LogOut, User } from 'lucide-react'
import './AuthGuard.css'

function AuthGuard({ children }) {
  const { state, signIn, signOut } = useAuthContext()

  // Show loading state while authentication is initializing
  if (state.isLoading) {
    return (
      <div className="auth-loading">
        <div className="loading-spinner"></div>
        <p>Initializing authentication...</p>
      </div>
    )
  }

  // If user is not authenticated, show login screen
  if (!state.isAuthenticated) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>ClinicalCompass</h1>
            <p>Smart Site Selection for Clinical Trials</p>
          </div>
          <button className="auth-button sign-in" onClick={() => signIn()}>
            <LogIn size={20} />
            Sign In to Continue
          </button>
        </div>
      </div>
    )
  }

  // User is authenticated, show the app with a user info bar
  return (
    <>
      <div className="user-bar">
        <div className="user-info">
          <User size={18} />
          <span className="user-name">{state.displayName || state.username || state.email}</span>
        </div>
        <button className="auth-button sign-out" onClick={() => signOut()}>
          <LogOut size={18} />
          Sign Out
        </button>
      </div>
      {children}
    </>
  )
}

export default AuthGuard
