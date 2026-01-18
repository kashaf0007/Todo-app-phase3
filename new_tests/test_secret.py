import os
from dotenv import load_dotenv
from backend.src.config import get_settings

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

# Get the settings to check the secret
settings = get_settings()
print(f"BETTER_AUTH_SECRET: {settings.better_auth_secret}")
print(f"Secret length: {len(settings.better_auth_secret)}")