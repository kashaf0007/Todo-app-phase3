"""
Health Check Endpoint
Simple endpoint to verify API is running.
"""

from fastapi import APIRouter

router = APIRouter()

# This router is intentionally left empty since health check is already defined in main.py
# This file exists to maintain the directory structure and for potential future health-related endpoints
