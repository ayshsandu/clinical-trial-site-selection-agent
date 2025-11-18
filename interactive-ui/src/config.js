// Asgardeo Authentication Configuration
// Update these values with your Asgardeo application details

export const authConfig = {
  // The Client ID of your OIDC application registered in Asgardeo
  clientID: "8kqkhQVQV1SRKYJyJ8KK_XNInHQa",
  
  // Asgardeo server's host name along with your organization name
  // Format: https://api.asgardeo.io/t/<org_name>
  baseUrl: "https://localhost:9443",
  
  // The URL to redirect to after user login
  signInRedirectURL: "http://localhost:3000",
  
  // The URL to redirect to after user logout
  signOutRedirectURL: "http://localhost:3000",
  
  // Requested scopes
  scope: ["openid", "profile", "email"],
  
  // Enable PKCE for additional security
  enablePKCE: true,
  
  // Resource server URLs that should have the access token attached
  resourceServerURLs: ["http://localhost:8010"]
};
