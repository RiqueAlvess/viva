from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    ADM = "ADM"
    RH = "RH"
    LIDERANCA = "LIDERANCA"


class UserBase(BaseModel):
    nome: str
    email: EmailStr
    role: UserRole
    ativo: bool = True
    sector_id: Optional[uuid.UUID] = None


class UserCreate(UserBase):
    company_id: uuid.UUID
    password: str


class UserCreateByRH(BaseModel):
    """RH can only create LIDERANCA users for their own company."""
    nome: str
    email: EmailStr
    password: str
    sector_id: Optional[uuid.UUID] = None


class UserUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    ativo: Optional[bool] = None
    sector_id: Optional[uuid.UUID] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
