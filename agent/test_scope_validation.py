#!/usr/bin/env python3
"""
Test script for auth_sdk scope validation functionality.

This script tests the enhanced scope validation features that have been
moved to the auth_sdk.
"""

import os
import sys
from pathlib import Path

# Add auth_sdk to path
auth_sdk_path = Path.home() / "AI" / "Antigravity" / "src"
if auth_sdk_path.exists():
    sys.path.insert(0, str(auth_sdk_path))

def test_scope_validation_imports():
    """Test that scope validation classes can be imported."""
    print("Testing scope validation imports...")
    try:
        from auth_sdk.validator import (
            TokenValidator,
            TokenValidationError,
            TokenExpiredError,
            InvalidTokenError,
            ScopeValidationError
        )
        print("✓ All scope validation imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_validator_creation():
    """Test creating a TokenValidator with scope validation."""
    print("\nTesting TokenValidator creation...")
    try:
        from auth_sdk import TokenConfig
        from auth_sdk.validator import TokenValidator
        
        config = TokenConfig(
            issuer="https://test.example.com",
            audience="test-audience",
            jwks_url="https://test.example.com/.well-known/jwks.json",
            authorization_endpoint="https://test.example.com/oauth2/authorize",
            token_endpoint="https://test.example.com/oauth2/token",
            client_id="test-client",
            ssl_verify=False,
            log_level="INFO"
        )
        
        validator = TokenValidator(config)
        print("✓ TokenValidator created successfully")
        
        # Check that validator has the new methods
        if hasattr(validator, 'validate_with_scope'):
            print("✓ validate_with_scope method exists")
        else:
            print("✗ validate_with_scope method not found")
            return False
        
        return True
    except Exception as e:
        print(f"✗ TokenValidator creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exception_hierarchy():
    """Test that exception classes have correct hierarchy."""
    print("\nTesting exception hierarchy...")
    try:
        from auth_sdk.validator import (
            TokenValidationError,
            TokenExpiredError,
            InvalidTokenError,
            ScopeValidationError
        )
        
        # Check inheritance
        if issubclass(TokenExpiredError, TokenValidationError):
            print("✓ TokenExpiredError inherits from TokenValidationError")
        else:
            print("✗ TokenExpiredError inheritance incorrect")
            return False
        
        if issubclass(InvalidTokenError, TokenValidationError):
            print("✓ InvalidTokenError inherits from TokenValidationError")
        else:
            print("✗ InvalidTokenError inheritance incorrect")
            return False
        
        if issubclass(ScopeValidationError, TokenValidationError):
            print("✓ ScopeValidationError inherits from TokenValidationError")
        else:
            print("✗ ScopeValidationError inheritance incorrect")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Exception hierarchy test failed: {e}")
        return False


def test_auth_sdk_exports():
    """Test that auth_sdk exports the new classes."""
    print("\nTesting auth_sdk exports...")
    try:
        from auth_sdk import (
            TokenValidator,
            TokenValidationError,
            TokenExpiredError,
            InvalidTokenError,
            ScopeValidationError
        )
        print("✓ All classes exported from auth_sdk")
        return True
    except ImportError as e:
        print(f"✗ Export test failed: {e}")
        return False


def test_adapter_uses_sdk_exceptions():
    """Test that auth_adapter uses SDK exceptions."""
    print("\nTesting auth_adapter uses SDK exceptions...")
    try:
        # Add agent path
        agent_path = Path(__file__).parent
        sys.path.insert(0, str(agent_path))
        
        from src.auth_sdk.auth_adapter import validate_token
        
        # Check that the module imports the SDK exceptions
        import src.auth_sdk.auth_adapter as adapter_module
        
        # Get the source code to verify imports
        import inspect
        source = inspect.getsource(adapter_module)
        
        if "TokenExpiredError" in source and "ScopeValidationError" in source:
            print("✓ auth_adapter imports SDK exception classes")
        else:
            print("✗ auth_adapter doesn't import SDK exception classes")
            return False
        
        if "AuthSDK" in source:
            print("✓ auth_adapter uses AuthSDK")
        else:
            print("✗ auth_adapter doesn't use AuthSDK")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Adapter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 80)
    print("Auth SDK Scope Validation Tests")
    print("=" * 80)
    
    tests = [
        ("Scope Validation Imports", test_scope_validation_imports),
        ("TokenValidator Creation", test_validator_creation),
        ("Exception Hierarchy", test_exception_hierarchy),
        ("Auth SDK Exports", test_auth_sdk_exports),
        ("Adapter Uses SDK Exceptions", test_adapter_uses_sdk_exceptions),
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
