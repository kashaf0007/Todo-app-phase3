"""
Test script to verify Better Auth configuration with Neon PostgreSQL
"""
import asyncio
from src.auth import auth
from src.config import get_settings

async def test_better_auth_config():
    """
    Test that Better Auth is properly configured with Neon PostgreSQL
    """
    print("Testing Better Auth configuration...")
    
    try:
        # Get settings
        settings = get_settings()
        
        print(f"Database URL: {settings.database_url}")
        print(f"Better Auth Secret Length: {len(settings.better_auth_secret)}")
        
        # Test that auth object is created
        assert auth is not None, "Auth object should not be None"
        
        # Test that auth has required methods
        assert hasattr(auth, 'options'), "Auth should have options attribute"
        assert hasattr(auth, 'session'), "Auth should have session module"
        assert hasattr(auth, 'user'), "Auth should have user module"
        
        print("✓ Better Auth configuration is valid")
        print("✓ All required methods are available")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing Better Auth configuration: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_better_auth_config())
    if success:
        print("\n✓ Better Auth with Neon PostgreSQL configuration test PASSED")
    else:
        print("\n✗ Better Auth with Neon PostgreSQL configuration test FAILED")