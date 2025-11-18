# Asgardeo Authentication Setup Guide

This application now includes authentication via Asgardeo Auth React SDK.

## Configuration Steps

### 1. Register your application in Asgardeo

1. Go to [Asgardeo Console](https://console.asgardeo.io/)
2. Sign in and select your organization
3. Navigate to **Applications** → **New Application**
4. Choose **Single-Page Application** (SPA)
5. Enter an application name (e.g., "Clinical Trial Demo")
6. Add the following **Authorized redirect URLs**:
   - `http://localhost:5173`
   - `http://localhost:5173/` (if needed)
7. Add the following **Allowed origins**:
   - `http://localhost:5173`
8. Click **Register**

### 2. Update configuration file

After registering your app, update `src/config.js` with your app details:

```javascript
export const authConfig = {
  clientID: "YOUR_CLIENT_ID_FROM_ASGARDEO",
  baseUrl: "https://api.asgardeo.io/t/YOUR_ORG_NAME",
  signInRedirectURL: "http://localhost:5173",
  signOutRedirectURL: "http://localhost:5173",
  scope: ["openid", "profile", "email"],
  enablePKCE: true,
  resourceServerURLs: ["http://localhost:8010"]
};
```

**Required values:**
- `clientID`: Copy from your Asgardeo application details
- `baseUrl`: Replace `YOUR_ORG_NAME` with your Asgardeo organization name

### 3. Run the application

```bash
npm install
npm run dev
```

## Features Implemented

✅ **Authentication Flow**
- Login with Asgardeo (OAuth 2.0 / OpenID Connect)
- Secure logout
- Automatic token management

✅ **Protected Routes**
- App content only accessible to authenticated users
- Login screen for unauthenticated users
- User info displayed in header

✅ **API Security**
- Access tokens automatically included in API requests
- Bearer token authentication header

✅ **User Experience**
- Loading states during authentication
- User display name/email shown in UI
- Sign out button in header

## Architecture

### Components
- **AuthProvider** (main.jsx): Wraps the entire app with auth context
- **AuthGuard** (AuthGuard.jsx): Protects routes and shows login UI
- **App** (App.jsx): Uses auth context to include tokens in API calls

### Authentication Flow
1. User visits app → AuthGuard checks authentication status
2. Not authenticated → Shows login screen
3. User clicks "Sign In" → Redirects to Asgardeo
4. User authenticates → Redirects back to app
5. App receives auth code → Exchanges for tokens
6. User is authenticated → App content loads

## Troubleshooting

**Issue**: "Invalid redirect URI"
- Ensure redirect URLs in Asgardeo match exactly (including trailing slashes)
- Check that port 5173 is being used

**Issue**: CORS errors
- Add `http://localhost:5173` to allowed origins in Asgardeo
- Verify `resourceServerURLs` in config.js includes your API URL

**Issue**: Token not included in API requests
- Ensure backend API is configured to accept Bearer tokens
- Check that `resourceServerURLs` in config matches your API

## Security Notes

- PKCE (Proof Key for Code Exchange) is enabled by default for enhanced security
- Access tokens are stored securely by the SDK
- Tokens are automatically refreshed when expired
- Sign out clears all local session data

## Backend Integration

If you need to validate tokens on your backend:

1. Extract the Bearer token from the Authorization header
2. Validate the JWT token using Asgardeo's public keys
3. Verify the token's signature, expiration, and issuer
4. Extract user info from token claims

Example token validation endpoint: `https://api.asgardeo.io/t/YOUR_ORG_NAME/oauth2/jwks`

## Additional Resources

- [Asgardeo Documentation](https://wso2.com/asgardeo/docs/)
- [Asgardeo Auth React SDK](https://github.com/asgardeo/asgardeo-auth-react-sdk)
- [OpenID Connect Specification](https://openid.net/connect/)
