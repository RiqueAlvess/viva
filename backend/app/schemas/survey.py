from pydantic import BaseModel, model_validator
import uuid
from datetime import datetime
from typing import Optional, Dict
from enum import Enum


class FaixaEtaria(str, Enum):
    E18_24 = "18-24"
    E25_34 = "25-34"
    E35_44 = "35-44"
    E45_54 = "45-54"
    E55_64 = "55-64"
    E65_PLUS = "65+"


class Genero(str, Enum):
    M = "M"
    F = "F"
    O = "O"
    N = "N"


class TempoEmpresa(str, Enum):
    LESS_1 = "<1"
    ONE_3 = "1-3"
    THREE_5 = "3-5"
    FIVE_10 = "5-10"
    MORE_10 = ">10"


class ValidateTokenResponse(BaseModel):
    session_uuid: uuid.UUID
    campaign_id: uuid.UUID
    company_name: str
    data_inicio: datetime
    data_fim: datetime
    unit_id: uuid.UUID
    sector_id: uuid.UUID


class SurveySubmitRequest(BaseModel):
    session_uuid: uuid.UUID
    answers: Dict[str, int]  # {"q1": 1, "q2": 3, ...} scale 1-5
    faixa_etaria: Optional[FaixaEtaria] = None
    genero: Optional[Genero] = None
    tempo_empresa: Optional[TempoEmpresa] = None
    lgpd_consent: bool
    unit_id: uuid.UUID
    sector_id: uuid.UUID

    @model_validator(mode="after")
    def validate_lgpd(self):
        if not self.lgpd_consent:
            raise ValueError("LGPD consent is required")
        return self

    @model_validator(mode="after")
    def validate_answers(self):
        if not self.answers:
            raise ValueError("Answers cannot be empty")
        for key, value in self.answers.items():
            if not isinstance(value, int) or value < 1 or value > 5:
                raise ValueError(f"Answer {key} must be an integer between 1 and 5")
        return self


class SurveySubmitResponse(BaseModel):
    success: bool
    message: str


class InvitationListItem(BaseModel):
    id: uuid.UUID
    collaborator_id: uuid.UUID
    email_hash: str
    display_status: str
    unit_id: Optional[uuid.UUID] = None
    sector_id: Optional[uuid.UUID] = None
    unit_nome: Optional[str] = None
    sector_nome: Optional[str] = None
    sent_at: Optional[datetime] = None
    expires_at: datetime

    model_config = {"from_attributes": True}


class SendInvitationsRequest(BaseModel):
    collaborator_ids: Optional[list[uuid.UUID]] = None
    send_all: bool = False

    @model_validator(mode="after")
    def validate_send_target(self):
        if not self.send_all and not self.collaborator_ids:
            raise ValueError("Must specify collaborator_ids or send_all=true")
        return self
