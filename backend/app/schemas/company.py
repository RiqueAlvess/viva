from pydantic import BaseModel, field_validator
import uuid
from datetime import datetime
from typing import Optional


class CompanyBase(BaseModel):
    nome: str
    cnpj: str
    cnae: Optional[str] = None
    ativo: bool = True

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, v: str) -> str:
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) != 14:
            raise ValueError("CNPJ must have 14 digits")
        return digits


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    nome: Optional[str] = None
    cnpj: Optional[str] = None
    cnae: Optional[str] = None
    ativo: Optional[bool] = None

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) != 14:
            raise ValueError("CNPJ must have 14 digits")
        return digits


class CompanyResponse(CompanyBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
