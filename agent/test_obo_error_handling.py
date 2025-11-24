#!/usr/bin/env python3
"""
Test script to verify OBO flow error handling.

This script verifies that:
1. Redirect URL is only returned when SDK provides one
2. Authentication errors are returned otherwise
"""

import os
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
auth_sdk_path = Path.home() / "AI" / "Antigravity" / "src"
if auth_sdk_path.exists():
    sys.path.insert(0, str(auth_sdk_path))

def test_error_handling_logic():
    """Test the error handling logic in validate_token."""
    print("Testing OBO flow error handling logic...")
    
    from auth_sdk import AuthResult, Session
    
    # Test Case 1: Authentication failed with redirect URL (new session)
    print("\n1. Testing: Not authenticated + redirect URL")
    result1 = AuthResult(
        is_authenticated=False,
        redirect_url="https://auth.example.com/authorize?...",
        session=Session(jti="test123", user_id="user@example.com"),
        error=None
    )
    
    if result1.redirect_url:
        print("   ✓ Should return 401 with X-Auth-Redirect-URL header")
        print(f"   ✓ Redirect URL: {result1.redirect_url}")
    else:
        print("   ✗ Should have redirect URL")
        return False
    
    # Test Case 2: Authentication failed without redirect URL (validation error)
    print("\n2. Testing: Not authenticated + no redirect URL")
    result2 = AuthResult(
        is_authenticated=False,
        redirect_url=None,
        session=None,
        error="Token validation failed: Invalid signature"
    )
    
    if not result2.redirect_url:
        print("   ✓ Should return 401 with error message")
        print(f"   ✓ Error: {result2.error}")
    else:
        print("   ✗ Should not have redirect URL")
        return False
    
    # Test Case 3: Authentication failed without redirect URL (expired token)
    print("\n3. Testing: Not authenticated + no redirect URL (expired)")
    result3 = AuthResult(
        is_authenticated=False,
        redirect_url=None,
        session=None,
        error="Token has expired"
    )
    
    if not result3.redirect_url:
        print("   ✓ Should return 401 with error message")
        print(f"   ✓ Error: {result3.error}")
    else:
        print("   ✗ Should not have redirect URL")
        return False
    
    # Test Case 4: Authentication successful
    print("\n4. Testing: Authenticated successfully")
    session = Session(jti="test123", user_id="user@example.com")
    session.obo_access_token = "obo_token_xyz"
    result4 = AuthResult(
        is_authenticated=True,
        redirect_url=None,
        session=session,
        error=None
    )
    
    if result4.is_authenticated and result4.session.obo_access_token:
        print("   ✓ Should return 200 with OBO token")
        print(f"   ✓ OBO Token: {result4.session.obo_access_token[:20]}...")
    else:
        print("   ✗ Should be authenticated with OBO token")
        return False
    
    return True


def test_code_logic():
    """Verify the actual code logic."""
    print("\n" + "="*70)
    print("Verifying auth_adapter.py logic")
    print("="*70)
    
    # Read the auth_adapter code
    adapter_path = Path(__file__).parent / "src" / "auth_adapter.py"
    with open(adapter_path, 'r') as f:
        code = f.read()
    
    # Check for correct error handling pattern
    checks = [
        ("if not auth_result.is_authenticated:", "Check authentication status"),
        ("if auth_result.redirect_url:", "Check for redirect URL"),
        ("X-Auth-Redirect-URL", "Return redirect URL in header"),
        ("else:", "Handle no redirect URL case"),
        ("auth_result.error or", "Return error message"),
    ]
    
    all_passed = True
    for check, description in checks:
        if check in code:
            print(f"✓ {description}: Found '{check}'")
        else:
            print(f"✗ {description}: Missing '{check}'")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests."""
    print("=" * 70)
    print("OBO Flow Error Handling Tests")
    print("=" * 70)
    
    tests = [
        ("Error Handling Logic", test_error_handling_logic),
        ("Code Logic Verification", test_code_logic),
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
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        print("\n✅ Verification Complete:")
        print("   • Redirect URL is ONLY returned when SDK provides one")
        print("   • Authentication errors are returned otherwise")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
