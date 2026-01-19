from src.config import get_settings
import os

print("Checking environment variables...")
print(f"BETTER_AUTH_SECRET: {'SET' if os.getenv('BETTER_AUTH_SECRET') else 'NOT SET'}")
print(f"DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT SET'}")
print(f"COHERE_API_KEY: {'SET' if os.getenv('COHERE_API_KEY') else 'NOT SET'}")

try:
    settings = get_settings()
    print("\nSettings loaded:")
    print(f"  better_auth_secret: {'SET' if settings.better_auth_secret else 'NOT SET'}")
    print(f"  database_url: {'SET' if settings.database_url else 'NOT SET'}")
    print(f"  cohere_api_key: {'SET' if settings.cohere_api_key else 'NOT SET'}")
except Exception as e:
    print(f"\nError loading settings: {e}")