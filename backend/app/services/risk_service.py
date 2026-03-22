"""Risk aggregation service for campaigns."""
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional

from app.models.analytics import FactDimensionScore, FactCampaignMetrics, FactSectorScore
from app.models.survey import SurveyResponse, SurveyInvitation, Collaborator
from app.models.campaign import Campaign, Sector, Unit
from app.services.score_service import DIMENSIONS, calculate_igrp


class RiskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_campaign_metrics(self, campaign_id: uuid.UUID) -> Optional[FactCampaignMetrics]:
        result = await self.db.execute(
            select(FactCampaignMetrics).where(
                FactCampaignMetrics.campaign_id == campaign_id
            )
        )
        return result.scalar_one_or_none()

    async def compute_campaign_metrics(self, campaign_id: uuid.UUID) -> FactCampaignMetrics:
        """Recompute and upsert fact_campaign_metrics for a campaign."""
        # Count invited
        total_invited_result = await self.db.execute(
            select(func.count(SurveyInvitation.id)).where(
                SurveyInvitation.campaign_id == campaign_id
            )
        )
        total_invited = total_invited_result.scalar() or 0

        # Count responded
        total_responded_result = await self.db.execute(
            select(func.count(SurveyResponse.id)).where(
                SurveyResponse.campaign_id == campaign_id
            )
        )
        total_responded = total_responded_result.scalar() or 0

        adhesion_rate = (
            Decimal(str(total_responded)) / Decimal(str(total_invited)) * 100
            if total_invited > 0
            else Decimal("0")
        )

        # Get all dimension scores for IGRP
        scores_result = await self.db.execute(
            select(FactDimensionScore).where(
                FactDimensionScore.campaign_id == campaign_id
            )
        )
        all_scores = scores_result.scalars().all()

        # IGRP
        nr_values = [s.nr_value for s in all_scores]
        igrp = (
            sum(nr_values) / Decimal(str(len(nr_values)))
            if nr_values
            else Decimal("0")
        )

        # Risk distribution
        risk_dist: dict[str, int] = {
            "aceitavel": 0, "moderado": 0, "importante": 0, "critico": 0
        }
        for s in all_scores:
            if s.risk_level in risk_dist:
                risk_dist[s.risk_level] += 1

        # Upsert
        existing = await self.get_campaign_metrics(campaign_id)
        if existing:
            existing.total_invited = total_invited
            existing.total_responded = total_responded
            existing.adhesion_rate = adhesion_rate
            existing.igrp = igrp
            existing.risk_distribution = risk_dist
            existing.computed_at = datetime.now(timezone.utc)
            await self.db.flush()
            return existing
        else:
            metrics = FactCampaignMetrics(
                campaign_id=campaign_id,
                total_invited=total_invited,
                total_responded=total_responded,
                adhesion_rate=adhesion_rate,
                igrp=igrp,
                risk_distribution=risk_dist,
                computed_at=datetime.now(timezone.utc),
            )
            self.db.add(metrics)
            await self.db.flush()
            return metrics

    async def get_sector_scores(self, campaign_id: uuid.UUID) -> list[FactSectorScore]:
        result = await self.db.execute(
            select(FactSectorScore).where(
                FactSectorScore.campaign_id == campaign_id
            )
        )
        return list(result.scalars().all())

    async def get_dimension_scores_by_campaign(
        self, campaign_id: uuid.UUID
    ) -> list[FactDimensionScore]:
        result = await self.db.execute(
            select(FactDimensionScore).where(
                FactDimensionScore.campaign_id == campaign_id
            )
        )
        return list(result.scalars().all())
