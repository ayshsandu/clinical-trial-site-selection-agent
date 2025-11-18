import React from 'react'
import ReactDOM from 'react-dom/client'
import { AuthProvider } from '@asgardeo/auth-react'
import App from './App.jsx'
import './index.css'
import { authConfig } from './config.js'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider config={authConfig}>
      <App />
    </AuthProvider>
  </React.StrictMode>,
)
