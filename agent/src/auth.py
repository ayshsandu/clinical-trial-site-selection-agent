"""
Authentication utilities for OAuth 2.0 Bearer token validation.
"""

import os
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