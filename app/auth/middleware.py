"""
Auth middleware for FastAPI

Extracts user from Authorization header and attaches to request.state
"""

import os
from functools import wraps
from fastapi import Request, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from .models import User
from .service import get_auth_service


security = HTTPBearer(auto_error=False)

# Admin API key from environment (for background worker endpoints)
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", None)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Extract current user from Authorization header.

    Returns None if no auth provided (for optional auth endpoints).
    Raises 401 if invalid token provided.
    """
    if not credentials:
        return None

    token = credentials.credentials
    auth_service = get_auth_service()

    user = await auth_service.get_user_from_token(token)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session token"
        )

    return user


async def require_auth(user: Optional[User] = Depends(get_current_user)) -> User:
    """
    Require authentication - raises 401 if not authenticated.

    Use this as a dependency for protected endpoints.
    """
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    return user


async def require_admin_key(x_admin_key: Optional[str] = Header(None)):
    """
    Require admin API key for admin-only endpoints.

    Use this for background worker endpoints that need to be protected
    but don't have user authentication.

    Usage:
        @router.post("/admin/purge")
        async def admin_endpoint(auth: None = Depends(require_admin_key)):
            ...
    """
    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Admin API key not configured (set ADMIN_API_KEY environment variable)"
        )

    if not x_admin_key or x_admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing admin API key"
        )

    return None
