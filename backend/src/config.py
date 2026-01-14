"""
Configuration Management
Loads environment variables and application settings.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables are read from:
    1. System environment
    2. .env file in backend/ directory
    3. .env file in root directory
    """

    # JWT Authentication
    better_auth_secret: str
    """
    Shared secret for JWT signing and verification.
    Must be identical in frontend and backend.
    Generate with: openssl rand -base64 32
    """

    # Database
    database_url: str
    """
    Neon PostgreSQL connection string.
    Format: postgresql://user:password@host/database?sslmode=require
    """

    # API Configuration
    api_title: str = "Phase II Todo Application API"
    api_version: str = "1.0.0"
    api_description: str = "REST API for multi-user todo application with JWT authentication"

    # CORS Configuration
    cors_origins: list[str] = ["http://localhost:3000", "https://hackathon2-phase1-five.vercel.app"]
    """Allowed origins for CORS (frontend URLs)"""

    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    class Config:
        """Pydantic settings configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Allow BETTER_AUTH_SECRET or better_auth_secret
        extra = "ignore"  # Ignore extra environment variables (e.g., NEXT_PUBLIC_API_URL)


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Settings: Application configuration

    Note:
        - Cached with lru_cache for performance (loaded once)
        - Raises ValidationError if required environment variables missing
    """
    return Settings()
