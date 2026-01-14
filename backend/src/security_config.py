"""
Security configuration for the RAG Todo Chatbot API
Implements various security measures to protect the application
"""

import os
import re
from datetime import timedelta
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.security import HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, validator
from typing import Optional


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security middleware to implement various security measures
    """

    async def dispatch(self, request: Request, call_next):
        # Perform security checks before processing the request
        await self.security_checks(request)

        # Add security headers
        response = await call_next(request)

        # Set security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # Set Content Security Policy - allow necessary sources for Swagger UI
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net",
            "font-src 'self' https://cdn.jsdelivr.net",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        return response

    async def security_checks(self, request: Request):
        """
        Perform various security checks on the incoming request
        """
        # Check for suspicious headers
        suspicious_headers = [
            'x-forwarded-for',
            'x-real-ip',
            'x-client-ip',
            'x-remote-ip'
        ]

        for header in suspicious_headers:
            if header in request.headers:
                # Log potential IP spoofing attempts
                pass  # In production, log this event

        # Check for potential malicious payloads in request body
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body_str = body_bytes.decode('utf-8')
                    if not validate_user_input(body_str):
                        raise HTTPException(
                            status_code=400,
                            detail="Malicious input detected in request body"
                        )
            except Exception:
                # If we can't read the body, continue (some requests may not have bodies)
                pass


def setup_security(app: FastAPI):
    """
    Setup security measures for the FastAPI application
    """
    # Add security middleware
    app.add_middleware(SecurityMiddleware)

    # Setup rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Additional security configurations
    setup_input_validation()

    # Add trusted host middleware to prevent HTTP Host Header attacks
    from fastapi.middleware.trustedhost import TrustedHostMiddleware

    # Prepare allowed hosts list, ensuring no compiled regex objects are included
    allowed_hosts_list = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        ".vercel.app",  # Vercel deployments
        ".hackathon2-phase1-five.vercel.app",  # Specific deployment
        ".hf.space",  # Hugging Face Spaces
        os.getenv("CUSTOM_HOST", "")  # Allow custom host from environment if set
    ]

    # Filter out empty strings
    allowed_hosts_list = [host for host in allowed_hosts_list if host]

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts_list
    )


def setup_input_validation():
    """
    Setup input validation and sanitization
    """
    # This would include various input validation measures
    pass


def validate_user_input(input_text: str) -> bool:
    """
    Validate user input to prevent injection attacks
    """
    if not input_text or not isinstance(input_text, str):
        return False

    # Check for potential SQL injection patterns
    sql_injection_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|WAITFOR|DELAY|TRUNCATE|MERGE|EXECUTE|XP_|SP_)\b)",
        r"(\'\s*(OR|AND)\s*\'\s*=\s*\')",
        r"(;\s*(DROP|EXEC|CALL|DECLARE|CREATE|ALTER|GRANT|REVOKE|INSERT|UPDATE|DELETE|TRUNCATE|MERGE))",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",  # Common SQLi patterns like "OR 1=1"
        r"(\'\s*(OR|AND)\s*\d+\s*=\s*\d+)",  # Common SQLi patterns like "' OR 1=1"
        r"(\/\*.*?\*\/)",  # SQL comments
        r"(\-\-.*$)",  # SQL line comments
        r"(xp_|sp_|fn_|spt_)",  # Stored procedure/function patterns
    ]

    for pattern in sql_injection_patterns:
        if re.search(pattern, input_text, re.IGNORECASE):
            return False

    # Check for potential XSS patterns
    xss_patterns = [
        r"<script[^>]*>",
        r"javascript:",
        r"vbscript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<meta[^>]*>",
        r"eval\(",
        r"expression\(",
        r"document\.cookie",
        r"window\.location",
        r"document\.write",
        r"innerHTML",
        r"outerHTML",
        r"location\.href",
        r"location\.replace",
        r"location\.assign",
    ]

    for pattern in xss_patterns:
        if re.search(pattern, input_text, re.IGNORECASE):
            return False

    # Check for potential command injection patterns
    cmd_injection_patterns = [
        r"[;&|]",
        r"\$\(",
        r"`.*`",
        r"\\",
        r"\|\s*\w+\s*$",  # Pipe to another command
        r"&&\s*\w+\s*$",  # AND command chaining
        r"\|\|",  # OR command chaining
    ]

    for pattern in cmd_injection_patterns:
        if re.search(pattern, input_text):
            return False

    # Check for potential path traversal
    path_traversal_patterns = [
        r"\.\.\/",
        r"\.\.\\",
        r"%2e%2e%2f",  # URL encoded ../
        r"%2e%2e%5c",  # URL encoded ..\
        r"\.\.\%2f",   # Mixed encoding
        r"\.\.%2f",    # Partial encoding
    ]

    for pattern in path_traversal_patterns:
        if re.search(pattern, input_text, re.IGNORECASE):
            return False

    # Check for potential LDAP injection
    ldap_patterns = [
        r"\*",
        r"\(",
        r"\)",
        r"\\",
        r"\\7c",  # URL encoded |
        r"\\28",  # URL encoded (
        r"\\29",  # URL encoded )
    ]

    for pattern in ldap_patterns:
        if input_text.count(pattern) > 3:  # If too many occurances of these chars
            return False

    # Additional checks can be added here
    return True


def sanitize_user_input(input_text: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    """
    if not input_text or not isinstance(input_text, str):
        return ""

    # Remove potentially dangerous characters/sequences
    sanitized = input_text.replace("<script", "&lt;script")
    sanitized = sanitized.replace("javascript:", "javascript&#58;")
    sanitized = sanitized.replace("vbscript:", "vbscript&#58;")
    sanitized = sanitized.replace("<iframe", "&lt;iframe")
    sanitized = sanitized.replace("<object", "&lt;object")
    sanitized = sanitized.replace("<embed", "&lt;embed")
    sanitized = sanitized.replace("<meta", "&lt;meta")
    sanitized = sanitized.replace("..\\", "")
    sanitized = sanitized.replace("../", "")
    sanitized = sanitized.replace(";", "&#59;")
    sanitized = sanitized.replace("--", "&#45;&#45;")

    # Escape HTML characters
    sanitized = sanitized.replace("&", "&amp;")
    sanitized = sanitized.replace("<", "&lt;")
    sanitized = sanitized.replace(">", "&gt;")
    sanitized = sanitized.replace('"', "&quot;")
    sanitized = sanitized.replace("'", "&#x27;")
    sanitized = sanitized.replace("/", "&#47;")
    sanitized = sanitized.replace("\\", "&#92;")

    return sanitized


# Pydantic models with security validations
class SecureTaskCreate(BaseModel):
    """Secure model for creating new task with input validation"""
    title: str
    description: Optional[str] = None

    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        if len(v) > 255:
            raise ValueError('Title too long')
        if not validate_user_input(v):
            raise ValueError('Title contains invalid characters')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            if len(v) > 2000:
                raise ValueError('Description too long')
            if not validate_user_input(v):
                raise ValueError('Description contains invalid characters')
        return v


class SecureTaskUpdate(BaseModel):
    """Secure model for updating task with input validation"""
    title: str
    description: Optional[str] = None

    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        if len(v) > 255:
            raise ValueError('Title too long')
        if not validate_user_input(v):
            raise ValueError('Title contains invalid characters')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            if len(v) > 2000:
                raise ValueError('Description too long')
            if not validate_user_input(v):
                raise ValueError('Description contains invalid characters')
        return v


# JWT Configuration
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET", "fallback_secret_for_development")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def get_password_hash(password: str) -> str:
    """
    Create a password hash using bcrypt
    """
    import bcrypt
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)  # Increased rounds for stronger hashing
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    import bcrypt
    pwd_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)


# Rate limiting configuration
RATE_LIMIT_DEFAULT = "100/minute"  # Default rate limit for general endpoints
RATE_LIMIT_AUTH = "5/minute"      # Rate limit for authentication endpoints
RATE_LIMIT_CHAT = "30/minute"     # Rate limit for chat endpoints