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
    try:
        # Check if authentication is required
        jwks_url = get_jwks_url()
        if not jwks_url:
            logger.info("No JWKS URL configured - allowing anonymous access")
            return {"anonymous": True, "token": None}

        if not credentials:
            logger.warning("No authorization credentials provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing"
            )

        token = credentials.credentials
        logger.debug("Received token for validation")

        # Decode header to get kid
        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            if not kid:
                logger.warning("Token missing key ID (kid) in header")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing key ID"
                )
        except Exception as e:
            logger.error(f"Failed to decode token header: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token header: {str(e)}"
            )

        # Fetch JWKS
        try:
            logger.info(f"Fetching JWKS from {jwks_url}")
            response = requests.get(jwks_url, timeout=10, verify=False)
            response.raise_for_status()
            jwks = response.json()
            logger.debug("JWKS fetched successfully")
        except requests.RequestException as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch JWKS: {str(e)}"
            )
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JWKS response: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid JWKS response: {str(e)}"
            )

        # Find the key
        key = None
        for jwk_key in jwks.get("keys", []):
            if jwk_key.get("kid") == kid:
                try:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk_key)
                    break
                except Exception as e:
                    logger.error(f"Failed to create key from JWK: {e}")
                    continue

        if not key:
            logger.warning(f"Key with kid '{kid}' not found in JWKS")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: key not found"
            )

        # Verify token
        try:
            logger.info("Decoding and verifying token")
            payload = jwt.decode(token, key=key, algorithms=["RS256"], options={"verify_aud": False})
            logger.debug("Token decoded successfully")
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during token decoding: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token decoding error: {str(e)}"
            )

        # Check for required scope
        try:
            required_scope = os.getenv("REQUIRED_SCOPE", "query_agent")
            token_scopes = payload.get("scope") or payload.get("scp")
            
            logger.debug(f"Checking for required scope: {required_scope}")
            logger.debug(f"Token scopes: {token_scopes}")
            
            if not token_scopes:
                logger.warning(f"Token missing scope claim - required scope: {required_scope}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: required scope '{required_scope}' not found in token (no scope claim present)"
                )
            
            # Handle both string and array formats
            if isinstance(token_scopes, str):
                scopes_list = token_scopes.split()
            elif isinstance(token_scopes, list):
                scopes_list = token_scopes
            else:
                logger.warning(f"Invalid scope format in token: {type(token_scopes)} - required scope: {required_scope}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: invalid scope format in token - required scope '{required_scope}'"
                )
            
            logger.debug(f"Parsed scopes list: {scopes_list}")
            
            if required_scope not in scopes_list:
                logger.warning(f"Required scope '{required_scope}' not present in token scopes: {scopes_list}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: required scope '{required_scope}' not present in token scopes. Available scopes: {', '.join(scopes_list)}"
                )
            
            logger.info(f"Scope validation successful: {required_scope} found in token")
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error during scope validation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Scope validation error: {str(e)}"
            )

        # Return payload with original token
        payload["token"] = token

        # Get cached agent token if available
        try:
            agent_token = get_agent_token()
            if agent_token:
                payload["agent_token"] = agent_token
                logger.debug("Using cached agent token")
            else:
                logger.debug("No agent token available")
        except Exception as e:
            logger.warning(f"Error getting agent token: {e}")
            # Continue without agent token

        logger.info("Token validation completed successfully")
        return payload

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected authentication error: {e}", exc_info=True)
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