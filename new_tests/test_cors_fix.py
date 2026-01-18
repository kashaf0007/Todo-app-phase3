"""
Test script to verify CORS configuration is working properly
"""
import sys
import os

# Add the backend src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from config import get_settings

def test_cors_configuration():
    print("Testing CORS configuration...")

    # Load settings
    settings = get_settings()

    print(f"CORS Origins (raw): {settings.cors_origins}")
    print(f"CORS Origins (parsed): {settings.cors_origins_list}")
    print(f"CORS Allow Credentials: {settings.cors_allow_credentials}")
    print(f"CORS Allow Methods (raw): {settings.cors_allow_methods}")
    print(f"CORS Allow Methods (parsed): {settings.cors_methods_list}")
    print(f"CORS Allow Headers (raw): {settings.cors_allow_headers}")
    print(f"CORS Allow Headers (parsed): {settings.cors_headers_list}")

    # Check if localhost:3000 is in the allowed origins
    if "http://localhost:3000" in settings.cors_origins_list:
        print("\n[SUCCESS] http://localhost:3000 is in the allowed origins list")
    else:
        print("\n[FAILURE] http://localhost:3000 is NOT in the allowed origins list")

    # Check if other common origins are present
    expected_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "https://hackathon2-phase1-five.vercel.app"
    ]

    missing_origins = [origin for origin in expected_origins if origin not in settings.cors_origins_list]

    if not missing_origins:
        print("[SUCCESS] All expected origins are present in the CORS configuration")
    else:
        print(f"[WARNING] Missing origins: {missing_origins}")

    print("\nCORS configuration test completed!")

if __name__ == "__main__":
    test_cors_configuration()