from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional, Dict, List
from decimal import Decimal


class DimensionScore(BaseModel):
    dimension: str
    score: float
    risk_level: str
    nr_value: float


class SectorDashboard(BaseModel):
    sector_id: uuid.UUID
    sector_nome: str
    unit_nome: str
    avg_nr: float
    risk_level: str
    response_count: int
    dimension_scores: Dict[str, float]


class DemographicBreakdown(BaseModel):
    faixa_etaria: Optional[Dict[str, int]] = None
    genero: Optional[Dict[str, int]] = None
    tempo_empresa: Optional[Dict[str, int]] = None


class DashboardResponse(BaseModel):
    campaign_id: uuid.UUID
    campaign_nome: str
    company_nome: str
    data_inicio: datetime
    data_fim: datetime
    total_invited: int
    total_responded: int
    adhesion_rate: float
    igrp: float
    risk_distribution: Dict[str, int]
    dimension_scores: List[DimensionScore]
    top5_sectors: List[SectorDashboard]
    demographic: DemographicBreakdown
    heatmap: List[SectorDashboard]
    computed_at: Optional[datetime] = None


class ReportStatusResponse(BaseModel):
    campaign_id: uuid.UUID
    status: str  # "pending", "processing", "ready", "error"
    report_url: Optional[str] = None
    generated_at: Optional[datetime] = None
    error_message: Optional[str] = None
