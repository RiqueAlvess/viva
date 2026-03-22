"""Admin-only endpoints for system management."""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.core.permissions import require_adm
from app.models.company import Company
from app.models.user import User
from app.schemas.company import CompanyResponse
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/stats")
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_adm()),
):
    company_count = await db.scalar(select(func.count(Company.id)))
    user_count = await db.scalar(select(func.count(User.id)))
    return {
        "total_companies": company_count or 0,
        "total_users": user_count or 0,
    }


@router.get("/companies", response_model=list[CompanyResponse])
async def list_all_companies(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_adm()),
):
    result = await db.execute(select(Company).order_by(Company.nome))
    return list(result.scalars().all())


@router.get("/users", response_model=list[UserResponse])
async def list_all_users(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_adm()),
):
    result = await db.execute(select(User).order_by(User.email))
    return list(result.scalars().all())
