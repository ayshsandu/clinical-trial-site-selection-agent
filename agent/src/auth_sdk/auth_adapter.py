"""
Authentication adapter for integrating auth_sdk into the agent project.

This module provides a compatibility layer between the auth_sdk and the agent's
authentication requirements, including:
- Token validation for incoming API requests
- Agent authentication for acquiring agent tokens
- Token management for MCP server communication
"""

import os
import sys
import time
import secrets
import hashlib
import base64
import requests
from typing import Optional, Dict, Any, Union
from pathlib import Path
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

# Import from local auth_sdk
# Import from local auth_sdk
try:
    from .models import TokenConfig, AuthResult, Session
    from .core import AuthSDK
    from .agent_auth import AgentOAuthProvider
    from .validator import (
        TokenValidator,
        TokenExpiredError,
        InvalidTokenError,
        ScopeValidationError
    )
    from .session import SessionManager
    from .logger import setup_logger
except ImportError as e:
    raise ImportError(f"Failed to import auth_sdk components. Error: {e}")


# Custom exception for OBO flow that needs redirect
class OAuthFlowRequiredException(HTTPException):
    """
    Custom exception for when OAuth flow is required.
    Carries the redirect URL in headers.
    """
    def __init__(self, redirect_url: str, session_jti: str = ""):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OAuth flow required",
            headers={
                "Access-Control-Expose-Headers": "X-Auth-Redirect-URL, X-Auth-Session-JTI",
                "X-Auth-Redirect-URL": redirect_url,
                "X-Auth-Session-JTI": session_jti
            }
        )
        self.redirect_url = redirect_url
        self.session_jti = session_jti


# Global configuration
_auth_sdk: Optional[AuthSDK] = None
_session_manager: Optional[SessionManager] = None
_agent_provider: Optional[AgentOAuthProvider] = None
_agent_token: Optional[Dict[str, Any]] = None
_logger = None
_required_scope: str = "query_agent"

# Security scheme for FastAPI
security = HTTPBearer()


def initialize_auth_sdk(
    jwks_url: str,
    issuer: str = None,
    audience: str = None,
    authorization_endpoint: str = None,
    token_endpoint: str = None,
    client_id: str = None,
    client_secret: str = None,
    redirect_uri: str = None,
    scope: str = None
):
    """
    Initialize the AuthSDK for OBO flow.
    
    Args:
        jwks_url: JWKS URL for token validation
        issuer: Token issuer
        audience: Token audience
        authorization_endpoint: OAuth authorization endpoint
        token_endpoint: OAuth token endpoint
        client_id: OAuth client ID
        client_secret: OAuth client secret (optional)
        redirect_uri: OAuth redirect URI
        scope: OAuth scope (default: "openid profile email")
    """
    global _auth_sdk, _session_manager, _logger
    
    # Derive issuer from JWKS URL if not provided
    if not issuer:
        issuer = os.getenv("TOKEN_ISSUER")
        if not issuer and jwks_url:
            from urllib.parse import urlparse
            parsed = urlparse(jwks_url)
            issuer = f"{parsed.scheme}://{parsed.netloc}"
    
    # Get other values from env if not provided
    audience = audience or os.getenv("TOKEN_AUDIENCE", "default")
    authorization_endpoint = authorization_endpoint or os.getenv("AUTHORIZATION_ENDPOINT", "")
    token_endpoint = token_endpoint or os.getenv("TOKEN_ENDPOINT", "")
    client_id = client_id or os.getenv("OBO_CLIENT_ID", "")
    client_secret = client_secret or os.getenv("OBO_CLIENT_SECRET")
    redirect_uri = redirect_uri or os.getenv("OBO_REDIRECT_URI", "http://localhost:8010/auth/callback")
    scope = scope or os.getenv("REQUIRED_SCOPE", "")
    
    config = TokenConfig(
        issuer=issuer,
        audience=audience,
        jwks_url=jwks_url,
        authorization_endpoint=authorization_endpoint,
        token_endpoint=token_endpoint,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        ssl_verify=False,  # Match the original auth_utils behavior
        log_level=os.getenv("LOG_LEVEL", "INFO")
    )
    
    _session_manager = SessionManager()
    _auth_sdk = AuthSDK(config, _session_manager)
    _logger = setup_logger(__name__, config.log_level)
    _logger.info(f"AuthSDK initialized with JWKS URL: {jwks_url}")


def set_jwks_url(url: str, issuer: str = None, audience: str = None):
    """
    Set the JWKS URL and initialize the AuthSDK.
    
    This is a compatibility function that initializes the full AuthSDK.
    
    Args:
        url: JWKS URL for token validation
        issuer: Token issuer (optional, defaults to env var or derived from JWKS URL)
        audience: Token audience (optional, defaults to env var)
    """
    initialize_auth_sdk(url, issuer, audience)


def get_jwks_url() -> Optional[str]:
    """Get the configured JWKS URL."""
    if _auth_sdk:
        return _auth_sdk.config.jwks_url
    return os.getenv("JWKS_URL")


def get_auth_sdk() -> Optional[AuthSDK]:
    """Get the initialized AuthSDK instance."""
    return _auth_sdk


def get_session_manager() -> Optional[SessionManager]:
    """Get the session manager instance."""
    return _session_manager


def set_required_scope(scope: str):
    """Set the required scope for token validation."""
    global _required_scope
    _required_scope = scope


async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Union[Dict[str, Any], JSONResponse]:
    """
    Validate OAuth 2.0 Bearer token using AuthSDK's process_request.
    
    This function implements the OBO flow:
    1. Validates the incoming token
    2. Checks for existing session
    3. If no session or no OBO token, returns 401 JSONResponse with redirect URL
    4. If session exists with OBO token, returns token payload dict
    
    Args:
        credentials: HTTP authorization credentials containing the bearer token
    
    Returns:
        Union[Dict[str, Any], JSONResponse]: Token payload dict if authenticated, 
                                              or JSONResponse with 401 status if auth required
    """
    global _logger, _auth_sdk, _required_scope
    
    if not _logger:
        import logging
        _logger = logging.getLogger(__name__)
    
    try:
        # Check if authentication is required
        jwks_url = get_jwks_url()
        if not jwks_url:
            _logger.info("No JWKS URL configured - allowing anonymous access")
            return {"anonymous": True, "token": None}
        
        if not credentials:
            _logger.warning("No authorization credentials provided")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header missing"}
            )
        
        # Initialize AuthSDK if not already done
        if not _auth_sdk:
            issuer = os.getenv("TOKEN_ISSUER", "")
            audience = os.getenv("TOKEN_AUDIENCE", "default")
            initialize_auth_sdk(jwks_url, issuer, audience)
        
        # Build request headers for AuthSDK
        request_headers = {
            "Authorization": f"Bearer {credentials.credentials}"
        }
        
        # Process request using AuthSDK
        # Note: process_request is synchronous, but that's fine in async function
        auth_result: AuthResult = _auth_sdk.process_request(request_headers)
        
        if not auth_result.is_authenticated:
            if auth_result.redirect_url:
                # OBO flow required - return 401 with redirect URL
                _logger.info(f"OBO flow required, redirect URL: {auth_result.redirect_url}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "OAuth flow required"},
                    headers={
                        "Access-Control-Expose-Headers": "X-Auth-Redirect-URL, X-Auth-Session-JTI",
                        "X-Auth-Redirect-URL": auth_result.redirect_url,
                        "X-Auth-Session-JTI": auth_result.session.jti if auth_result.session else ""
                    }
                )
            else:
                # Authentication failed - return 401 with error
                _logger.warning(f"Authentication failed: {auth_result.error}")
                
                # Check for scope validation error (403)
                if auth_result.error and "Access denied" in auth_result.error:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": auth_result.error}
                    )
                
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": auth_result.error or "Authentication failed"}
                )
        
        # Authentication successful - validate scope
        session = auth_result.session
        if not session or not session.obo_access_token:
            _logger.error("Authenticated but no OBO token available")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error: No OBO token"
            )
        
        # Build response payload
        payload = {
            "jti": session.jti,
            "sub": session.user_id,
            "obo_access_token": session.obo_access_token,
            "token": credentials.credentials,  # Original incoming token
            "session": session
        }
        
        # Get cached agent token if available
        try:
            agent_token = await get_agent_token()
            if agent_token:
                payload["agent_token"] = agent_token
                _logger.debug("Using cached agent token")
            else:
                _logger.debug("No agent token available")
        except Exception as e:
            _logger.warning(f"Error getting agent token: {e}")
            # Continue without agent token
        
        _logger.info("Token validation completed successfully with OBO token")
        return payload
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        _logger.error(f"Unexpected authentication error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )


def handle_oauth_callback(code: str, state: str) -> Dict[str, Any]:
    """
    Handle OAuth callback and complete the OBO flow.
    
    This function should be called from the OAuth callback endpoint.
    
    Args:
        code: Authorization code from OAuth provider
        state: State parameter for CSRF protection
    
    Returns:
        dict: Result with session information
        
    Raises:
        HTTPException: If callback handling fails
    """
    global _logger, _auth_sdk
    
    if not _logger:
        import logging
        _logger = logging.getLogger(__name__)
    
    if not _auth_sdk:
        _logger.error("AuthSDK not initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication system not initialized"
        )
    
    try:
        _logger.info(f"Handling OAuth callback with state: {state}")
        
        # Handle callback using AuthSDK
        auth_result: AuthResult = _auth_sdk.handle_callback(code, state)
        
        if not auth_result.is_authenticated:
            _logger.error(f"OAuth callback failed: {auth_result.error}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=auth_result.error or "OAuth callback failed"
            )
        
        session = auth_result.session
        if not session:
            _logger.error("OAuth callback succeeded but no session available")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error: No session"
            )
        
        _logger.info(f"OAuth callback completed successfully for JTI: {session.jti}")
        
        return {
            "success": True,
            "jti": session.jti,
            "user_id": session.user_id,
            "message": "Authentication successful"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        _logger.error(f"Unexpected error handling OAuth callback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback error: {str(e)}"
        )


# ============================================================================
# Agent Authentication (OAuth flow for agent identity)
# ============================================================================
# Note: AgentOAuthProvider is now imported from auth_sdk


def set_agent_oauth_provider(provider: AgentOAuthProvider):
    """Set the agent OAuth provider for acquiring agent tokens."""
    global _agent_provider
    _agent_provider = provider


async def get_agent_token() -> Optional[str]:
    """Get the cached agent token, acquiring it if necessary."""
    global _agent_token, _logger
    
    if not _logger:
        import logging
        _logger = logging.getLogger(__name__)
    
    # Check if we have a valid cached token
    if _agent_token and _is_token_valid(_agent_token):
        _logger.debug("Using cached agent token")
        return _agent_token.get("access_token")
    
    # Try to acquire a new token
    if _agent_provider:
        try:
            _logger.info("Acquiring new agent token from the SDK")
            tokens = await _agent_provider.acquire_agent_tokens()
            _agent_token = tokens
            return tokens.get("access_token")
        except Exception as e:
            _logger.warning(f"Failed to acquire agent token: {e}")
            return None
    
    return None


def _is_token_valid(token: dict) -> bool:
    """Check if the token is still valid (with some buffer time)."""
    if not token or "obtained_at" not in token or "expires_in" not in token:
        return False
    obtained_at = token["obtained_at"]
    expires_in = token["expires_in"]
    current_time = int(time.time() * 1000)
    # Consider token expired 5 minutes before actual expiry
    return current_time < (obtained_at + (expires_in * 1000) - 300000)


# ============================================================================
# Token Management
# ============================================================================

def get_final_token(token_payload: Dict[str, Any], prefer_obo_token: bool = True) -> Optional[str]:
    """
    Get the final token to use for authentication based on the token payload and preferences.
    
    With OBO flow, the priority is:
    1. OBO access token (if prefer_obo_token=True and available)
    2. Agent token (if available)
    3. Original user token
    
    Args:
        token_payload: The token validation payload
        prefer_obo_token: Whether to prefer OBO token (default: True)
    
    Returns:
        The final token to use for authentication, or None if no valid token is available
    """
    global _logger
    
    if not _logger:
        import logging
        _logger = logging.getLogger(__name__)
    
    # Handle anonymous access
    if token_payload.get("anonymous"):
        _logger.debug("Anonymous access - no token required")
        return None
    
    # Get available tokens
    obo_token = token_payload.get("obo_access_token")
    agent_token = token_payload.get("agent_token")
    user_token = token_payload.get("token")
    
    # Determine which token to use
    if prefer_obo_token and obo_token:
        _logger.debug("Using OBO access token (preferred)")
        return obo_token
    elif agent_token:
        _logger.debug("Using agent token")
        return agent_token
    elif user_token:
        _logger.debug("Using original user token")
        return user_token
    elif obo_token:
        _logger.debug("Using OBO access token (fallback)")
        return obo_token
    else:
        _logger.warning("No valid token available")
        return None


def get_token_for_mcp(token_payload: Dict[str, Any]) -> Optional[str]:
    """
    Get the appropriate token for MCP server authentication.
    
    For MCP servers, we prefer the OBO token as it represents the user's
    delegated access to the agent.
    
    Args:
        token_payload: The token validation payload
    
    Returns:
        The token to use for MCP authentication (OBO token preferred)
    """
    return get_final_token(token_payload, prefer_obo_token=True)


def get_token_for_user_context(token_payload: Dict[str, Any]) -> Optional[str]:
    """
    Get the token for user-specific operations.
    
    This function returns the OBO token which represents the user's
    delegated access.
    
    Args:
        token_payload: The token validation payload
    
    Returns:
        The OBO token, or original user token if OBO not available
    """
    # For user context, we want the OBO token or original user token
    # We do NOT want the agent token as that represents the agent's identity, not the user's
    obo_token = token_payload.get("obo_access_token")
    if obo_token:
        return obo_token
    
    return token_payload.get("token")
