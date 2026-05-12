"""
JWT Authentication and Security utilities for ZenSeva Communication Service.
Provides token verification, role-based access control, and rate limiting.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
import time
from collections import defaultdict

from app.core.config import settings


# Security scheme
security_scheme = HTTPBearer()


class TokenPayload(BaseModel):
    """JWT Token payload schema."""
    sub: str
    role: str
    exp: Optional[int] = None


class CurrentUser(BaseModel):
    """Authenticated user model."""
    user_id: str
    role: str


# Rate limiting storage (in-memory, use Redis in production cluster)
rate_limit_store: dict = defaultdict(list)


def create_access_token(user_id: str, role: str) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> CurrentUser:
    """Verify JWT token and return current user."""
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return CurrentUser(user_id=user_id, role=role)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(*allowed_roles: str):
    """Dependency to enforce role-based access control."""
    def role_checker(current_user: CurrentUser = Depends(verify_token)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' does not have access to this resource",
            )
        return current_user
    return role_checker


def rate_limiter(request: Request):
    """Simple rate limiter middleware dependency."""
    client_ip = request.client.host
    current_time = time.time()
    window_start = current_time - 60

    # Clean old entries
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip] if t > window_start
    ]

    if len(rate_limit_store[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )

    rate_limit_store[client_ip].append(current_time)
