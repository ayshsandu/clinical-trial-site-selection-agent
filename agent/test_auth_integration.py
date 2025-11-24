#!/usr/bin/env python3
"""
Test script for auth_sdk integration.

This script tests the basic functionality of the auth_adapter module
to ensure the auth_sdk integration is working correctly.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    try:
        from src.auth_adapter import (
            validate_token,
            set_jwks_url,
            get_jwks_url,
            AgentOAuthProvider,
            set_agent_oauth_provider,
            get_agent_token,
            get_token_for_mcp,
            get_token_for_user_context,
            get_final_token
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_jwks_configuration():
    """Test JWKS URL configuration."""
    print("\nTesting JWKS configuration...")
    try:
        from src.auth_adapter import set_jwks_url, get_jwks_url
        
        # Test setting JWKS URL
        test_url = "https://test.example.com/.well-known/jwks.json"
        test_issuer = "https://test.example.com"
        test_audience = "test-audience"
        
        set_jwks_url(test_url, test_issuer, test_audience)
        
        # Test getting JWKS URL
        configured_url = get_jwks_url()
        
        if configured_url == test_url:
            print(f"✓ JWKS URL configured correctly: {configured_url}")
            return True
        else:
            print(f"✗ JWKS URL mismatch: expected {test_url}, got {configured_url}")
            return False
    except Exception as e:
        print(f"✗ JWKS configuration failed: {e}")
        return False


def test_token_management():
    """Test token management functions."""
    print("\nTesting token management...")
    try:
        from src.auth_adapter import get_final_token, get_token_for_mcp, get_token_for_user_context
        
        # Test with user token only
        payload1 = {"token": "user_token_123"}
        result1 = get_final_token(payload1, prefer_agent_token=False)
        if result1 == "user_token_123":
            print("✓ User token selection works")
        else:
            print(f"✗ User token selection failed: got {result1}")
            return False
        
        # Test with agent token preference
        payload2 = {"token": "user_token_123", "agent_token": "agent_token_456"}
        result2 = get_token_for_mcp(payload2)
        if result2 == "agent_token_456":
            print("✓ Agent token preference works")
        else:
            print(f"✗ Agent token preference failed: got {result2}")
            return False
        
        # Test with user token preference
        result3 = get_token_for_user_context(payload2)
        if result3 == "user_token_123":
            print("✓ User token preference works")
        else:
            print(f"✗ User token preference failed: got {result3}")
            return False
        
        # Test anonymous access
        payload3 = {"anonymous": True}
        result4 = get_final_token(payload3)
        if result4 is None:
            print("✓ Anonymous access handling works")
        else:
            print(f"✗ Anonymous access handling failed: got {result4}")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Token management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_provider_creation():
    """Test AgentOAuthProvider creation."""
    print("\nTesting AgentOAuthProvider creation...")
    try:
        from src.auth_adapter import AgentOAuthProvider, set_agent_oauth_provider
        
        # Test provider creation
        provider = AgentOAuthProvider(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_url="http://localhost/callback",
            agent_id="test_agent_id",
            agent_password="test_agent_password",
            token_endpoint="https://test.example.com/oauth2/token"
        )
        
        print("✓ AgentOAuthProvider created successfully")
        
        # Test setting provider
        set_agent_oauth_provider(provider)
        print("✓ AgentOAuthProvider set successfully")
        
        return True
    except Exception as e:
        print(f"✗ AgentOAuthProvider test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_provider_validation():
    """Test AgentOAuthProvider validation."""
    print("\nTesting AgentOAuthProvider validation...")
    try:
        from src.auth_adapter import AgentOAuthProvider
        
        # Test missing required parameters
        try:
            provider = AgentOAuthProvider(
                client_id="test_client_id",
                # Missing agent_id and agent_password
            )
            print("✗ AgentOAuthProvider should require agent_id and agent_password")
            return False
        except ValueError as e:
            print(f"✓ AgentOAuthProvider validation works: {e}")
            return True
    except Exception as e:
        print(f"✗ AgentOAuthProvider validation test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 80)
    print("Auth SDK Integration Tests")
    print("=" * 80)
    
    tests = [
        ("Imports", test_imports),
        ("JWKS Configuration", test_jwks_configuration),
        ("Token Management", test_token_management),
        ("Agent Provider Creation", test_agent_provider_creation),
        ("Agent Provider Validation", test_agent_provider_validation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
