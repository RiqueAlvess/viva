from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest, TokenResponse, LogoutRequest
from app.services.auth_service import AuthService
from app.core.permissions import get_current_user
from app.core.rate_limit import limiter

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
@limiter.limit("3/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    user = await service.authenticate_user(payload.email, payload.password)
    access_token, refresh_token = await service.create_tokens(user)
    await db.commit()
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "nome": user.nome,
            "email": user.email,
            "role": user.role,
            "company_id": user.company_id,
            "ativo": user.ativo,
            "sector_id": user.sector_id,
        },
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    access_token, refresh_token = await service.refresh_tokens(payload.refresh_token)
    await db.commit()
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout")
async def logout(
    payload: LogoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AuthService(db)
    await service.revoke_refresh_token(payload.refresh_token)
    await db.commit()
    return {"message": "Logged out successfully"}


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "nome": current_user.nome,
        "email": current_user.email,
        "role": current_user.role,
        "company_id": current_user.company_id,
        "ativo": current_user.ativo,
        "sector_id": current_user.sector_id,
    }
