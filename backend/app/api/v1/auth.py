from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import AuthService
from app.core.permissions import get_current_user

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    user = await service.authenticate_user(payload.email, payload.password)
    access_token = await service.create_access_token_for_user(user)
    return LoginResponse(
        access_token=access_token,
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


@router.post("/logout")
async def logout():
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
