#!/usr/bin/env python3
"""
Test script for OAuth 2.0 JWT token validation.
"""

import os
import sys
import json
import jwt
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from main import validate_token
from fastapi.security import HTTPAuthorizationCredentials

def create_test_jwt():
    """Create a test JWT token."""
    # Mock JWKS key
    private_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJTUt9Us8cKB
sQ9Q0h1P8SvpLx7QJr8YQgDgWQXv7g7cM8r2kHfW8I2I5mOQgFgHj3Kf8zQk8J
...
-----END PRIVATE KEY-----"""

    # For simplicity, let's use a simple secret for testing
    secret = "test-secret-key"
    kid = "test-key-id"

    payload = {
        "iss": "test-issuer",
        "sub": "test-user",
        "aud": "test-audience",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "kid": kid
    }

    token = jwt.encode(payload, secret, algorithm="HS256", headers={"kid": kid})
    return token, secret, kid

def mock_jwks_response(kid, secret):
    """Create mock JWKS response."""
    # For HS256, we need to encode the secret as base64
    import base64
    key_data = base64.urlsafe_b64encode(secret.encode()).decode().rstrip('=')

    jwks = {
        "keys": [
            {
                "kty": "oct",
                "k": key_data,
                "kid": kid,
                "alg": "HS256",
                "use": "sig"
            }
        ]
    }
    return jwks

def test_token_validation():
    """Test the token validation function."""
    print("Testing JWT token validation...")

    # Create test token
    token, secret, kid = create_test_jwt()
    print(f"Created test token: {token[:50]}...")

    # Mock JWKS response
    jwks = mock_jwks_response(kid, secret)

    # Temporarily set JWKS URL to a mock
    original_jwks_url = os.environ.get("JWKS_URL")
    os.environ["JWKS_URL"] = "http://mock-jwks-url"

    # Mock requests.get
    original_get = requests.get
    def mock_get(url):
        class MockResponse:
            def __init__(self, json_data):
                self.json_data = json_data
            def json(self):
                return self.json_data
            def raise_for_status(self):
                pass
        return MockResponse(jwks)

    requests.get = mock_get

    try:
        # Create credentials object
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Test validation
        payload = validate_token(credentials)

        print("✅ Token validation successful!")
        print(f"Decoded payload: {payload}")

        # Test with invalid token
        print("\nTesting invalid token...")
        invalid_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.here")
        try:
            validate_token(invalid_credentials)
            print("❌ Should have failed with invalid token")
        except Exception as e:
            print(f"✅ Correctly rejected invalid token: {e}")

    finally:
        # Restore original functions
        requests.get = original_get
        if original_jwks_url:
            os.environ["JWKS_URL"] = original_jwks_url
        else:
            os.environ.pop("JWKS_URL", None)

if __name__ == "__main__":
    test_token_validation()