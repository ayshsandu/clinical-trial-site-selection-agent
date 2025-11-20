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

from .agent_auth import get_agent_token


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