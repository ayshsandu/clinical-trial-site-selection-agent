// Asgardeo Authentication Configuration
// Update these values with your Asgardeo application details

export const authConfig = {
  // The Client ID of your OIDC application registered in Asgardeo
  clientID: import.meta.env.VITE_AUTH_CLIENT_ID || "Kp3gcfZCdOVmMqas5VnKjZtKYjoa",

  // Asgardeo server's host name along with your organization name
  // Format: https://api.asgardeo.io/t/<org_name>
  baseUrl: import.meta.env.VITE_AUTH_SERVER_BASE_URL || "https://localhost:9443",

  // The URL to redirect to after user login
  signInRedirectURL: import.meta.env.VITE_AUTH_SIGN_IN_REDIRECT_URL || "http://localhost:3000",

  // The URL to redirect to after user logout
  signOutRedirectURL: import.meta.env.VITE_AUTH_SIGN_OUT_REDIRECT_URL || "http://localhost:3000",

  // Requested scopes
  scope: (import.meta.env.VITE_AUTH_SCOPE || "openid,profile,email,query_agent").split(","),

  // Enable PKCE for additional security
  enablePKCE: true,

  // Resource server URLs that should have the access token attached
  resourceServerURLs: (import.meta.env.VITE_AUTH_RESOURCE_SERVER_URLS).split(",")
};

// MCP Server Configuration
export const mcpServers = {
  demographics: {
    url: import.meta.env.VITE_DEMOGRAPHICS_SERVER_URL || "http://localhost:4001/mcp",
    name: "Patient Demographics Database",
    description: "Provides anonymized patient population data by geography",
    tools: [
      { id: "search_patient_pools", name: "Search Patient Pools" },
      { id: "get_demographics_by_region", name: "Get Demographics by Region" }
    ]
  },
  performance: {
    url: import.meta.env.VITE_PERFORMANCE_SERVER_URL || "http://localhost:4002/mcp",
    name: "Site Performance & Capabilities",
    description: "Tracks historical site performance metrics",
    tools: [
      { id: "search_sites", name: "Search Sites" },
      { id: "get_site_capabilities", name: "Get Site Capabilities" },
      { id: "get_enrollment_history", name: "Get Enrollment History" }
    ]
  }
};

// Agent API Configuration
export const agentConfig = {
  baseUrl: import.meta.env.VITE_AGENT_URL || "http://localhost:8010",
  queryUrl: (import.meta.env.VITE_AGENT_URL || "http://localhost:8010") + "/api/query"
};
