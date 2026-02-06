# /backend/app/api/dependencies.py
# /version.py
# /_dev/

"""
Authentication & User Management Dependencies
Integrates Supabase Auth for secure JWT validation and Architect Role checks.
"""

from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.session import get_async_session
from backend.app.models.user import User
from backend.app.core.config import settings
from typing import Optional
from supabase import create_client, Client

# Initialize Supabase Client (For server-side validation)
try:
    supabase: Client = create_client(settings.supabase_url, settings.supabase_anon_key)
    print(f"Supabase Client Init: URL={settings.supabase_url[:20]}...")
except Exception as e:
    print(f"Supabase Init Failed: {e}")
    supabase = None

security = HTTPBearer()

async def get_current_user_uuid(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Validates Supabase JWT and returns the user UUID.
    """
    token = credentials.credentials
    
    if not supabase:
        raise HTTPException(500, detail="Auth Server Unavailable")

    try:
        # Verify the token with Supabase
        print(f"DEBUG: Validating token: {token[:10]}...") 
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
             print("DEBUG: Supabase returned no user.")
             raise HTTPException(401, detail="Invalid Authentication Token")
        
        print(f"DEBUG: Auth success for {user_response.user.id}")
        return user_response.user.id
        
    except Exception as e:
        print(f"DEBUG: Auth Error Details: {e}")
        raise HTTPException(401, detail="Invalid or Expired Token")

async def get_current_user(
    user_uuid: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(get_async_session)
) -> User:
    """
    Fetches the local User record asynchronously.
    If the user exists in Supabase but not locally, JIT creates them (Async).
    """
    user = await session.get(User, user_uuid)
    
    if not user:
        # JIT Provisioning (Async)
        new_user = User(
            user_id=user_uuid,
            username=f"Guest-{user_uuid[:8]}", # Temporary placeholder
            account_tier="free"
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
    return user

async def require_architect_role(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Checks if the user has the 'architect' role asynchronously.
    """
    token = credentials.credentials
    
    if not supabase:
        raise HTTPException(500, detail="Auth Server Unavailable")
        
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
             raise HTTPException(401, detail="Invalid Token")
        
        roles = user_response.user.app_metadata.get("role", "")
        if "architect" not in roles and roles != "architect":
             raise HTTPException(403, detail="⛔ ARCHITECT ACCESS ONLY")
             
        return user_response.user.id
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Role Check Error: {e}")
        raise HTTPException(401, detail="Auth Failed")

CurrentUserId = Depends(get_current_user_uuid)
CurrentUser = Depends(get_current_user)
ArchitectOnly = Depends(require_architect_role)
