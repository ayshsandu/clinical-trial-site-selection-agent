"""
Authentication utilities for OAuth 2.0 Bearer token validation.
"""

import os
import time
import secrets
import hashlib
import base64
import json
from venv import logger
import jwt
import requests
import urllib3
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# Suppress SSL warnings when verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Global JWKS URL - can be set at startup
_jwks_url = None


def set_jwks_url(url: str):
    """Set the JWKS URL for token validation."""
    global _jwks_url
    _jwks_url = url


def get_jwks_url() -> str:
    """Get the configured JWKS URL."""
    if _jwks_url:
        return _jwks_url
    return os.getenv("JWKS_URL")


# Global agent OAuth provider - can be set at startup
_agent_provider = None


def set_agent_oauth_provider(provider: "AgentOAuthProvider"):
    """Set the agent OAuth provider for acquiring agent tokens."""
    global _agent_provider
    _agent_provider = provider


# Global cached agent token
_agent_token = None


def get_agent_token() -> str:
    """Get the cached agent token, acquiring it if necessary."""
    global _agent_token
    if _agent_token and _is_token_valid(_agent_token):
        return _agent_token["access_token"]
    if _agent_provider:
        try:
            _agent_token = _agent_provider.acquire_agent_tokens()
            return _agent_token["access_token"]
        except Exception as e:
            logger.warning(f"Failed to acquire agent token: {e}")
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


# Security scheme
security = HTTPBearer()


def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate OAuth 2.0 Bearer token using JWKS.

    Args:
        credentials: HTTP authorization credentials containing the bearer token

    Returns:
        dict: Decoded JWT payload with 'token' key containing the original token

    Raises:
        HTTPException: If token is invalid, expired, or JWKS fetch fails
    """
    # Check if authentication is required
    jwks_url = get_jwks_url()
    if not jwks_url:
        # No authentication required
        return {"anonymous": True, "token": None}

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    token = credentials.credentials

    try:
        # Decode header to get kid
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing key ID"
            )

        # Fetch JWKS
        # Note: verify=False disables SSL certificate verification
        # This allows self-signed certificates but reduces security
        # In production, use proper certificates and set verify=True
        logger.info(f"Fetching JWKS from {jwks_url}")
        response = requests.get(jwks_url, timeout=10, verify=False)
        
        response.raise_for_status()
        jwks = response.json()

        # Find the key
        key = None
        for jwk_key in jwks.get("keys", []):
            if jwk_key.get("kid") == kid:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk_key)
                break

        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: key not found"
            )

        # Verify token
        logger.info("Decoding token")
        payload = jwt.decode(token, key=key, algorithms=["RS256"], options={"verify_aud": False})

        # Return payload with original token
        payload["token"] = token

        # Get cached agent token if available
        agent_token = get_agent_token()
        if agent_token:
            payload["agent_token"] = agent_token
            logger.debug("Using cached agent token")
        else:
            logger.debug("No agent token available")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch JWKS: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )


class AgentOAuthProvider:
    """
    OAuth provider for agent authentication flow.
    """

    def __init__(self, client_id: str, client_secret: str = None, redirect_url: str = None, agent_id: str = None, agent_password: str = None, token_endpoint: str = None):
        if not (client_id and agent_id and agent_password):
            raise ValueError("client_id, agent_id, and agent_password are required")
        
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_url = redirect_url or "http://localhost/callback"
        self._agent_id = agent_id
        self._agent_password = agent_password
        self._token_endpoint = token_endpoint
        self._code_verifier = self._generate_code_verifier()
        self._code_challenge = self._generate_code_challenge(self._code_verifier)

    def _generate_code_verifier(self) -> str:
        """Generate a random code verifier."""
        return secrets.token_urlsafe(32)

    def _generate_code_challenge(self, verifier: str) -> str:
        """Generate code challenge from verifier using S256."""
        sha256 = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(sha256).decode().rstrip('=')

    def _get_token_endpoint(self) -> str:
        """Get the token endpoint URL."""
        return self._token_endpoint

    def acquire_agent_tokens(self) -> dict:
        """
        Acquire tokens using the special agent authentication flow.

        Returns:
            dict: OAuth tokens
        """
        try:
            logger.info('AgentOAuthProvider: Starting agent authentication flow')

            # Step 1: Initiate authorization with direct response mode
            auth_response = self._initiate_agent_authorization()
            logger.info(f'AgentOAuthProvider: Authorization initiated, flowId: {auth_response["flowId"]}')

            # Step 2: Authenticate with agent credentials
            code_response = self._authenticate_agent(auth_response['flowId'])
            logger.info('AgentOAuthProvider: Agent authentication successful, received authorization code')

            # Step 3: Exchange code for tokens
            tokens = self._exchange_agent_code_for_tokens(code_response['authData']['code'])
            logger.info('AgentOAuthProvider: Token exchange completed successfully')

            return tokens
        except Exception as error:
            logger.error(f'AgentOAuthProvider: Agent authentication failed: {error}')
            raise error

    def _initiate_agent_authorization(self) -> dict:
        """
        Step 1: Initiate authorization request with direct response mode.
        """
        token_endpoint = self._get_token_endpoint()
        base_url = token_endpoint.replace('/oauth2/token', '')
        auth_url = f"{base_url}/oauth2/authorize"

        logger.info(f'AgentOAuthProvider: Initiating authorization request to {auth_url}')
        body = {
            'client_id': self._client_id,
            'response_type': 'code',
            'redirect_uri': self._redirect_url,
            'scope': 'openid',
            'response_mode': 'direct',
            'code_challenge': self._code_challenge,
            'code_challenge_method': 'S256'
        }

        response = requests.post(auth_url, data=body, headers={
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }, verify=False)  # Disable SSL verification for dev mode

        if not response.ok:
            raise Exception(f"Authorization initiation failed: {response.status_code} {response.reason}")

        auth_data = response.json()
        logger.info(f'AgentOAuthProvider: Authorization initiated: {auth_data}')  
        return auth_data

    def _authenticate_agent(self, flow_id: str) -> dict:
        """
        Step 2: Authenticate with agent credentials.
        """
        token_endpoint = self._get_token_endpoint()
        base_url = token_endpoint.replace('/oauth2/token', '')
        authn_url = f"{base_url}/oauth2/authn"

        body = {
            'flowId': flow_id,
            'selectedAuthenticator': {
                'authenticatorId': "QmFzaWNBdXRoZW50aWNhdG9yOkxPQ0FM",  # Basic Authenticator ID
                'params': {
                    'username': f"AGENT/{self._agent_id or self._client_id}",  # Use agent ID if available, otherwise fallback to client_id
                    'password': self._agent_password or self._client_secret,  # Use agent password if available, otherwise fallback to client_secret
                }
            }
        }

        response = requests.post(authn_url, json=body, headers={
            'Content-Type': 'application/json',
        }, verify=False)  # Disable SSL verification for dev mode

        if not response.ok:
            raise Exception(f"Agent authentication failed: {response.status_code} {response.reason}")

        authn_data = response.json()
        return authn_data

    def _exchange_agent_code_for_tokens(self, code: str) -> dict:
        """
        Step 3: Exchange authorization code for tokens.
        """
        token_endpoint = self._get_token_endpoint()

        body = {
            'grant_type': 'authorization_code',
            'client_id': self._client_id,
            'code': code,
            'code_verifier': self._code_verifier,
            'redirect_uri': self._redirect_url,
        }

        response = requests.post(token_endpoint, data=body, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        }, verify=False)  # Disable SSL verification for dev mode

        if not response.ok:
            raise Exception(f"Token exchange failed: {response.status_code} {response.reason}")

        token_data = response.json()

        tokens = {
            'access_token': token_data['access_token'],
            'token_type': token_data.get('token_type', 'Bearer'),
            'expires_in': token_data.get('expires_in'),
            'refresh_token': token_data.get('refresh_token'),
            'scope': token_data.get('scope'),
        }

        # Store obtained time for agent tokens
        tokens['obtained_at'] = int(time.time() * 1000)

        # Save agent identity tokens
        self.save_tokens(tokens)

        return tokens

    def save_tokens(self, tokens: dict):
        """
        Save the obtained tokens. Override this method to implement custom saving logic.
        """
        # Default implementation: do nothing
        pass