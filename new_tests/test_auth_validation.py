"""
Test script to validate Better Auth with new secret
Tests database connection, signup, login, and JWT verification
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime, timedelta
from sqlmodel import Session, select
from jose import jwt
from src.database import engine, get_session
from src.config import get_settings
from src.models.user import User
from src.api.routes.auth import hash_password, verify_password, create_access_token

def test_environment_variables():
    """Test 1: Validate environment variables are loaded correctly"""
    print("\n=== Test 1: Environment Variables ===")
    settings = get_settings()

    print(f"[OK] BETTER_AUTH_SECRET loaded: {settings.better_auth_secret[:10]}...")
    print(f"[OK] DATABASE_URL loaded: {settings.database_url[:50]}...")

    assert settings.better_auth_secret, "BETTER_AUTH_SECRET is missing"
    assert settings.database_url, "DATABASE_URL is missing"
    print("[OK] All environment variables validated\n")
    return True

def test_database_connection():
    """Test 2: Validate Neon PostgreSQL database connection"""
    print("=== Test 2: Database Connection ===")
    try:
        conn = engine.connect()
        print("[OK] Database connection successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        return False

def test_password_hashing():
    """Test 3: Test password hashing and verification"""
    print("\n=== Test 3: Password Hashing ===")
    test_password = "TestPassword123!"

    hashed = hash_password(test_password)
    print(f"[OK] Password hashed successfully")

    is_valid = verify_password(test_password, hashed)
    print(f"[OK] Password verification: {'PASS' if is_valid else 'FAIL'}")

    is_wrong = verify_password("WrongPassword", hashed)
    print(f"[OK] Wrong password rejected: {'PASS' if not is_wrong else 'FAIL'}")

    assert is_valid, "Password verification failed"
    assert not is_wrong, "Wrong password should not be verified"
    return True

def test_jwt_creation_and_verification():
    """Test 4: Test JWT token creation and verification"""
    print("\n=== Test 4: JWT Token ===")
    settings = get_settings()

    user_id = "test-user-id-123"
    email = "test@example.com"

    # Create token
    token = create_access_token(user_id, email)
    print(f"[OK] JWT token created successfully")

    # Verify token
    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )
        print(f"[OK] Token verified successfully")

        assert payload["sub"] == user_id, "User ID mismatch"
        assert payload["email"] == email, "Email mismatch"
        print(f"[OK] Token payload correct: user_id={payload['sub']}, email={payload['email']}")

        # Check expiration
        exp = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        print(f"[OK] Token expires at: {exp}")
        assert exp > now, "Token is already expired"

        return True
    except jwt.JWTError as e:
        print(f"[FAIL] Token verification failed: {e}")
        return False

def test_signup_flow():
    """Test 5: Test user signup flow"""
    print("\n=== Test 5: Signup Flow ===")
    try:
        with Session(engine) as session:
            # Check if test user already exists and delete it
            statement = select(User).where(User.email == "test-auth@example.com")
            existing_user = session.exec(statement).first()
            if existing_user:
                session.delete(existing_user)
                session.commit()
                print("[OK] Cleaned up existing test user")

            # Create new user (simulating signup)
            user_id = "test-user-auth-validation"
            email = "test-auth@example.com"
            password = "TestPassword123!"

            new_user = User(
                id=user_id,
                email=email,
                password_hash=hash_password(password),
                created_at=datetime.utcnow()
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            print(f"[OK] User created: {email}")

            # Verify user in database
            statement = select(User).where(User.email == email)
            user = session.exec(statement).first()
            assert user is not None, "User not found in database"
            assert user.email == email, "Email mismatch"
            print(f"[OK] User verified in database")

            return True
    except Exception as e:
        print(f"[FAIL] Signup flow failed: {e}")
        return False

def test_login_flow():
    """Test 6: Test login flow and token generation"""
    print("\n=== Test 6: Login Flow ===")
    try:
        with Session(engine) as session:
            email = "test-auth@example.com"
            password = "TestPassword123!"

            # Find user
            statement = select(User).where(User.email == email)
            user = session.exec(statement).first()

            if not user:
                print(f"[FAIL] User not found for login test")
                return False

            # Verify password
            is_valid = verify_password(password, user.password_hash)
            if not is_valid:
                print(f"[FAIL] Password verification failed")
                return False
            print(f"[OK] Password verified successfully")

            # Create JWT token
            token = create_access_token(user.id, user.email)
            print(f"[OK] Login token generated")

            # Verify token
            settings = get_settings()
            payload = jwt.decode(
                token,
                settings.better_auth_secret,
                algorithms=["HS256"]
            )

            assert payload["sub"] == user.id, "User ID in token mismatch"
            assert payload["email"] == user.email, "Email in token mismatch"
            print(f"[OK] Login token verified")

            return True
    except Exception as e:
        print(f"[FAIL] Login flow failed: {e}")
        return False

def cleanup_test_user():
    """Clean up test user after all tests"""
    print("\n=== Cleanup ===")
    try:
        with Session(engine) as session:
            statement = select(User).where(User.email == "test-auth@example.com")
            user = session.exec(statement).first()
            if user:
                session.delete(user)
                session.commit()
                print("[OK] Test user cleaned up")
    except Exception as e:
        print(f"[WARN] Cleanup failed (non-critical): {e}")

def main():
    print("=" * 60)
    print("Better Auth Validation with New Secret")
    print("=" * 60)

    results = []

    # Run all tests
    results.append(("Environment Variables", test_environment_variables()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Password Hashing", test_password_hashing()))
    results.append(("JWT Token", test_jwt_creation_and_verification()))
    results.append(("Signup Flow", test_signup_flow()))
    results.append(("Login Flow", test_login_flow()))

    # Cleanup
    cleanup_test_user()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n[OK] ALL TESTS PASSED - Better Auth is fully functional!")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
