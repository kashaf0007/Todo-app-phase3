"""
API Dependencies
JWT verification and authentication dependencies for FastAPI.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlmodel import Session, select

from ..config import get_settings
from ..database import get_session
from ..models import User


# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> User:
    """
    JWT verification dependency to extract authenticated user.

    Verifies JWT token signature, expiration, and extracts user identity.

    Args:
        credentials: HTTP Bearer token from Authorization header
        session: Database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException: 401 Unauthorized if token is missing, invalid, or expired

    Usage:
        @router.get("/endpoint")
        async def endpoint(current_user: User = Depends(get_current_user)):
            # Use current_user.id for database queries
            pass

    Security Notes:
        - ALWAYS derive user_id from JWT payload (current_user.id)
        - NEVER trust user_id from request body or path parameters
        - Token signature verified using BETTER_AUTH_SECRET
        - Token expiration checked automatically
    """
    try:
        settings = get_settings()

        # Extract token from Authorization header
        token = credentials.credentials

        # Define credentials exception
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Verify JWT signature and decode payload
            payload = jwt.decode(
                token,
                settings.better_auth_secret,
                algorithms=["HS256"]  # Standard JWT algorithm
            )

            # Extract user_id from payload
            user_id: str = payload.get("sub")  # "sub" is standard JWT claim for user ID

            if user_id is None:
                raise credentials_exception

        except JWTError as e:
            # Token invalid, expired, or signature verification failed
            print(f"JWT verification failed: {str(e)}")
            raise credentials_exception

        # Fetch user from database
        user = session.exec(select(User).where(User.id == user_id)).first()

        if user is None:
            # User not found (token references non-existent user)
            raise credentials_exception

        return user
    except HTTPException:
        # Re-raise HTTP exceptions (like 401)
        raise
    except Exception as e:
        # Catch any other unexpected errors and return 401 instead of 500
        print(f"Unexpected error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_user_access(
    current_user: User = Depends(get_current_user),
    path_user_id: str = None,
) -> User:
    """
    Verify that authenticated user matches path user_id (if provided).

    Args:
        current_user: Authenticated user from JWT
        path_user_id: User ID from URL path parameter (optional)

    Returns:
        User: Authenticated user if access granted

    Raises:
        HTTPException: 403 Forbidden if user_id mismatch

    Usage:
        @router.get("/api/{user_id}/tasks")
        async def list_tasks(
            user_id: str,  # From path
            current_user: User = Depends(get_current_user)
        ):
            # Verify access (optional but recommended)
            if user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")

            # Always use current_user.id for queries
            tasks = session.query(Task).filter(Task.user_id == current_user.id).all()
    """
    if path_user_id and path_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user ID mismatch"
        )

    return current_user
