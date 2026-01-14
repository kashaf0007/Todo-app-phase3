"""
Authentication Routes
Better Auth compatible endpoints for user registration and login
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from jose import JWTError, jwt
import bcrypt

from ...database import get_session
from ...models.user import User
from ...config import get_settings

# Router
router = APIRouter(prefix="/api/auth")

# Settings
settings = get_settings()


# Request/Response Models
class SignUpRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class SignInRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    emailVerified: bool = False
    createdAt: str
    updatedAt: str


class SessionResponse(BaseModel):
    user: UserResponse
    session: dict


# Helper functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Convert password to bytes and hash it
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Convert both to bytes for comparison
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(user_id: str, email: str) -> str:
    """Create a JWT access token"""
    expires = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode = {
        "sub": user_id,
        "email": email,
        "exp": expires
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.better_auth_secret,
        algorithm="HS256"
    )
    return encoded_jwt


# Routes
@router.post("/sign-up/email")
async def sign_up(
    request: SignUpRequest,
    session: Session = Depends(get_session)
):
    """
    Register a new user account

    Compatible with Better Auth sign-up flow
    """
    # Check if user already exists
    statement = select(User).where(User.email == request.email.lower())
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Create new user
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=request.email.lower(),
        password_hash=hash_password(request.password),
        created_at=datetime.now(timezone.utc)
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Create JWT token
    token = create_access_token(new_user.id, new_user.email)

    # Return Better Auth compatible response
    return {
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "name": request.name or new_user.email.split("@")[0],
            "emailVerified": False,
            "createdAt": new_user.created_at.isoformat(),
            "updatedAt": new_user.created_at.isoformat()
        },
        "session": {
            "token": token,
            "expiresAt": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        }
    }


@router.post("/sign-in/email")
async def sign_in(
    request: SignInRequest,
    session: Session = Depends(get_session)
):
    """
    Sign in with email and password

    Compatible with Better Auth sign-in flow
    """
    # Find user by email
    statement = select(User).where(User.email == request.email.lower())
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create JWT token
    token = create_access_token(user.id, user.email)

    # Return Better Auth compatible response
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.email.split("@")[0],
            "emailVerified": False,
            "createdAt": user.created_at.isoformat(),
            "updatedAt": user.created_at.isoformat()
        },
        "session": {
            "token": token,
            "expiresAt": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        }
    }


@router.get("/get-session")
async def get_session_endpoint():
    """
    Get current session

    Compatible with Better Auth session retrieval
    Note: This is a simplified version. In production, you'd verify the session cookie/token.
    """
    # For now, return null session (frontend will handle this)
    # In a full implementation, you'd verify the session token from cookies
    return {
        "data": None
    }


@router.post("/sign-out")
async def sign_out():
    """
    Sign out current user

    Compatible with Better Auth sign-out flow
    """
    # In a cookie-based session, you'd clear the session cookie here
    # For JWT, the frontend just removes the token
    return {"success": True}
