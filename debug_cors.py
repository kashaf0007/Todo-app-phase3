"""
Debug script to check CORS configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../../.env")  # Try loading from project root
load_dotenv(dotenv_path="../.env")    # Try loading from backend root
load_dotenv(dotenv_path=".env")       # Try loading from backend/src

# Check the ALLOWED_ORIGINS environment variable
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:8000")
print(f"ALLOWED_ORIGINS environment variable: '{allowed_origins_env}'")

# Split the origins
allowed_origins = allowed_origins_env.split(",")
print(f"Parsed allowed_origins: {allowed_origins}")

# Default origins
default_origins = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8000"]
print(f"Default origins: {default_origins}")

# Combined origins
all_origins = list(set(allowed_origins + default_origins))
print(f"All origins (deduplicated): {all_origins}")

# Check if http://localhost:3000 is in the list
if "http://localhost:3000" in all_origins:
    print("SUCCESS: http://localhost:3000 is in the allowed origins list")
else:
    print("FAILURE: http://localhost:3000 is NOT in the allowed origins list")

# Check if there are any extra spaces
cleaned_origins = [origin.strip() for origin in all_origins]
print(f"Cleaned origins (spaces removed): {cleaned_origins}")

if "http://localhost:3000" in cleaned_origins:
    print("SUCCESS: http://localhost:3000 is in the cleaned origins list")
else:
    print("FAILURE: http://localhost:3000 is NOT in the cleaned origins list after cleaning")