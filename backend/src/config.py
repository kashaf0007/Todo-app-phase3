"""
Configuration Management
Loads environment variables and application settings.
"""

import os
import json
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


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
    cohere_api_key: str

    # API Configuration
    api_title: str = "Phase II Todo Application API"
    api_version: str = "1.0.0"
    api_description: str = "REST API for multi-user todo application with JWT authentication"

    # CORS Configuration - Reading from environment variables with defaults
    cors_origins: str = "http://localhost:3000,http://localhost:3000/,http://127.0.0.1:3000,https://localhost:3000,https://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,https://hackathon2-phase1-five.vercel.app"
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]  # Allows all methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    cors_allow_headers: list[str] = ["*"]  # Allows all headers

    class Config:
        """Pydantic settings configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Allow BETTER_AUTH_SECRET or better_auth_secret
        extra = "ignore"  # Ignore extra environment variables (e.g., NEXT_PUBLIC_API_URL)

    @property
    def cors_origins_list(self):
        """Convert the comma-separated string of origins to a list."""
        if isinstance(self.cors_origins, list):
            return self.cors_origins
        elif isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        else:
            return []

    @property
    def cors_methods_list(self):
        """Convert the comma-separated string of methods to a list, or return ['*'] if wildcard."""
        return self.cors_allow_methods

    @property
    def cors_headers_list(self):
        """Convert the comma-separated string of headers to a list, or return ['*'] if wildcard."""
        return self.cors_allow_headers


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
