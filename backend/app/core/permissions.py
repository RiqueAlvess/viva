from enum import Enum
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.security import decode_access_token
from app.database import get_db

security = HTTPBearer()


class UserRole(str, Enum):
    ADM = "ADM"
    RH = "RH"
    LIDERANCA = "LIDERANCA"


async def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def get_current_user(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db),
):
    from app.models.user import User

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.ativo:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


async def get_current_active_user(
    current_user=Depends(get_current_user),
):
    if not current_user.ativo:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_roles(*roles: UserRole):
    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in [r.value for r in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker


def require_adm():
    return require_roles(UserRole.ADM)


def require_rh_or_adm():
    return require_roles(UserRole.ADM, UserRole.RH)


def require_any_role():
    return require_roles(UserRole.ADM, UserRole.RH, UserRole.LIDERANCA)
