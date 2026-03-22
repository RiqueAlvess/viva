import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.permissions import require_adm, require_rh_or_adm, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserCreateByRH, UserUpdate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "ADM":
        result = await db.execute(select(User).order_by(User.email))
    else:
        result = await db.execute(
            select(User)
            .where(User.company_id == current_user.company_id)
            .order_by(User.email)
        )
    return list(result.scalars().all())


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_adm()),
):
    existing = await db.execute(select(User).where(User.email == payload.email.lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    service = AuthService(db)
    user = await service.create_user(
        company_id=payload.company_id,
        nome=payload.nome,
        email=payload.email,
        password=payload.password,
        role=payload.role,
        sector_id=payload.sector_id,
    )
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/rh-create", response_model=UserResponse, status_code=201)
async def rh_create_user(
    payload: UserCreateByRH,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_rh_or_adm()),
):
    """RH creates a LIDERANCA user in their own company."""
    existing = await db.execute(select(User).where(User.email == payload.email.lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    service = AuthService(db)
    user = await service.create_user(
        company_id=current_user.company_id,
        nome=payload.nome,
        email=payload.email,
        password=payload.password,
        role="LIDERANCA",
        sector_id=payload.sector_id,
    )
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.role != "ADM" and user.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_rh_or_adm()),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.role != "ADM" and user.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    update_data = payload.model_dump(exclude_none=True)
    if "password" in update_data:
        from app.core.security import hash_password
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_adm()),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
