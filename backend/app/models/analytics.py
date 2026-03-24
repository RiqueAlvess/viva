import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    String, DateTime, ForeignKey, func, Integer, Numeric
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class FactDimensionScore(Base):
    __tablename__ = "fact_dimension_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    unit_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    sector_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    response_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    dimension: Mapped[str] = mapped_column(String(50), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    nr_value: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class FactCampaignMetrics(Base):
    __tablename__ = "fact_campaign_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True, index=True
    )
    total_invited: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_responded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    adhesion_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=0
    )
    igrp: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    risk_distribution: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class FactSectorScore(Base):
    __tablename__ = "fact_sector_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    sector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    dimension_scores: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    avg_nr: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False, default=0)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="aceitavel")
    response_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
