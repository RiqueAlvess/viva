from pydantic import BaseModel, model_validator
import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class CampaignBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    data_inicio: datetime
    data_fim: datetime

    @model_validator(mode="after")
    def validate_dates(self):
        if self.data_fim <= self.data_inicio:
            raise ValueError("data_fim must be after data_inicio")
        return self


class CampaignCreate(CampaignBase):
    company_id: Optional[uuid.UUID] = None  # ADM can specify, RH uses own company


class CampaignUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None


class CampaignResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    nome: str
    descricao: Optional[str] = None
    data_inicio: datetime
    data_fim: datetime
    status: str
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CloseConfirmation(BaseModel):
    confirm: bool

    @model_validator(mode="after")
    def must_confirm(self):
        if not self.confirm:
            raise ValueError("Must set confirm=true to close a campaign irreversibly")
        return self


class PositionSchema(BaseModel):
    id: uuid.UUID
    nome: str
    collaborator_count: int = 0

    model_config = {"from_attributes": True}


class SectorSchema(BaseModel):
    id: uuid.UUID
    nome: str
    positions: List[PositionSchema] = []

    model_config = {"from_attributes": True}


class UnitSchema(BaseModel):
    id: uuid.UUID
    nome: str
    sectors: List[SectorSchema] = []

    model_config = {"from_attributes": True}


class HierarchyResponse(BaseModel):
    campaign_id: uuid.UUID
    units: List[UnitSchema]


class CSVUploadPreview(BaseModel):
    total_rows: int
    units: int
    sectors: int
    positions: int
    collaborators: int
    errors: List[str] = []
    sample_rows: List[dict] = []


class InvitationStatsResponse(BaseModel):
    total: int
    sent: int
    responded: int
    pending: int
    expired: int
