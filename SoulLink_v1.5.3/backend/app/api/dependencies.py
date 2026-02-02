# /backend/app/api/dependencies.py
# /version.py
# /_dev/

"""
Authentication & User Management Dependencies
Provides flexible user handling for both dev (USR-001) and production users.
"""

from fastapi import Header, HTTPException, Depends
from sqlmodel import Session, select
from backend.app.database.session import get_session
from backend.app.models.user import User
from typing import Optional

async def get_current_user_id(
    x_user_id: Optional[str] = Header(default=None, description="User ID for authentication")
) -> str:
    """
    Extract user_id from request headers.
    
    Frontend should send: X-User-Id: <user_id>
    
    For MVP: This is a simple header-based auth.
    For Production: Replace with JWT token validation.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401, 
            detail="Authentication required. Please provide X-User-Id header."
        )
    
    return x_user_id


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> User:
    """
    Fetch the full User object from the database.
    Validates that the user exists.
    """
    user = session.get(User, user_id)
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User {user_id} not found. Please register or check your user ID."
        )
    
    return user


# For endpoints that only need user_id (most common)
CurrentUserId = Depends(get_current_user_id)

# For endpoints that need full User object
CurrentUser = Depends(get_current_user)
