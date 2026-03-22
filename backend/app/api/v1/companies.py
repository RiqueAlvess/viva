import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.permissions import require_adm, get_current_user
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse

router = APIRouter()


@router.get("/", response_model=list[CompanyResponse])
async def list_companies(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "ADM":
        result = await db.execute(select(Company).order_by(Company.nome))
        return list(result.scalars().all())
    # RH/LIDERANCA only see their own company
    result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = result.scalar_one_or_none()
    return [company] if company else []


@router.post("/", response_model=CompanyResponse, status_code=201)
async def create_company(
    payload: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_adm()),
):
    # Check for duplicate CNPJ
    existing = await db.execute(select(Company).where(Company.cnpj == payload.cnpj))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="CNPJ already registered")
    company = Company(**payload.model_dump())
    db.add(company)
    await db.flush()
    await db.commit()
    await db.refresh(company)
    return company


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    # Non-ADM can only see their own company
    if current_user.role != "ADM" and company.id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    return company


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: uuid.UUID,
    payload: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_adm()),
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(company, field, value)
    await db.commit()
    await db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=204)
async def delete_company(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_adm()),
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    await db.delete(company)
    await db.commit()
