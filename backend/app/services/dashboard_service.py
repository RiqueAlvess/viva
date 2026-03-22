"""Dashboard data aggregation service."""
import uuid
from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.campaign import Campaign, Unit, Sector
from app.models.survey import SurveyResponse
from app.models.analytics import (
    FactDimensionScore, FactCampaignMetrics, FactSectorScore
)
from app.services.score_service import DIMENSIONS
from app.schemas.dashboard import (
    DashboardResponse, DimensionScore, SectorDashboard,
    DemographicBreakdown
)

MIN_RESPONSES_FOR_DEMOGRAPHIC = 5


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(
        self,
        campaign_id: uuid.UUID,
        sector_id_filter: Optional[uuid.UUID] = None,
    ) -> DashboardResponse:
        # Load campaign
        campaign_result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        campaign = campaign_result.scalar_one_or_none()
        if not campaign:
            raise ValueError("Campaign not found")

        # Load metrics
        metrics_result = await self.db.execute(
            select(FactCampaignMetrics).where(
                FactCampaignMetrics.campaign_id == campaign_id
            )
        )
        metrics = metrics_result.scalar_one_or_none()

        # Aggregate dimension scores
        dim_query = select(
            FactDimensionScore.dimension,
            func.avg(FactDimensionScore.score).label("avg_score"),
            func.avg(FactDimensionScore.nr_value).label("avg_nr"),
        ).where(FactDimensionScore.campaign_id == campaign_id)
        if sector_id_filter:
            dim_query = dim_query.where(
                FactDimensionScore.sector_id == sector_id_filter
            )
        dim_query = dim_query.group_by(FactDimensionScore.dimension)
        dim_result = await self.db.execute(dim_query)
        dim_rows = dim_result.all()

        dimension_scores = []
        for row in dim_rows:
            avg_score = Decimal(str(row.avg_score or 0))
            direction = DIMENSIONS.get(row.dimension, ([], "positive"))[1]
            risk_level = _get_risk_level_from_score(avg_score, direction)
            dimension_scores.append(DimensionScore(
                dimension=row.dimension,
                score=float(avg_score),
                risk_level=risk_level,
                nr_value=float(row.avg_nr or 0),
            ))

        # Sector scores
        sector_query = select(FactSectorScore).where(
            FactSectorScore.campaign_id == campaign_id
        )
        if sector_id_filter:
            sector_query = sector_query.where(
                FactSectorScore.sector_id == sector_id_filter
            )
        sector_result = await self.db.execute(sector_query)
        sector_scores = sector_result.scalars().all()

        # Enrich sector scores with names
        sector_dashboard_list = []
        for ss in sector_scores:
            sector_name_result = await self.db.execute(
                select(Sector.nome, Unit.nome.label("unit_nome"))
                .join(Unit, Sector.unit_id == Unit.id)
                .where(Sector.id == ss.sector_id)
            )
            name_row = sector_name_result.first()
            sector_nome = name_row.nome if name_row else "Unknown"
            unit_nome = name_row.unit_nome if name_row else "Unknown"

            sector_dashboard_list.append(SectorDashboard(
                sector_id=ss.sector_id,
                sector_nome=sector_nome,
                unit_nome=unit_nome,
                avg_nr=float(ss.avg_nr),
                risk_level=ss.risk_level,
                response_count=ss.response_count,
                dimension_scores=ss.dimension_scores or {},
            ))

        # Top 5 sectors by risk (highest avg_nr)
        top5 = sorted(sector_dashboard_list, key=lambda x: x.avg_nr, reverse=True)[:5]

        # Demographic breakdown (only if enough responses)
        demographic = await self._get_demographic(campaign_id, sector_id_filter)

        total_invited = metrics.total_invited if metrics else 0
        total_responded = metrics.total_responded if metrics else 0
        adhesion_rate = float(metrics.adhesion_rate) if metrics else 0.0
        igrp = float(metrics.igrp) if metrics else 0.0
        risk_distribution = metrics.risk_distribution if metrics else {}
        computed_at = metrics.computed_at if metrics else None

        # Company name from core schema (cross-schema join not available easily)
        # We embed company_id and fetch separately
        company_nome = await self._get_company_name(campaign.company_id)

        return DashboardResponse(
            campaign_id=campaign_id,
            campaign_nome=campaign.nome,
            company_nome=company_nome,
            data_inicio=campaign.data_inicio,
            data_fim=campaign.data_fim,
            total_invited=total_invited,
            total_responded=total_responded,
            adhesion_rate=adhesion_rate,
            igrp=igrp,
            risk_distribution=risk_distribution,
            dimension_scores=dimension_scores,
            top5_sectors=top5,
            demographic=demographic,
            heatmap=sector_dashboard_list,
            computed_at=computed_at,
        )

    async def _get_company_name(self, company_id: uuid.UUID) -> str:
        from app.models.company import Company
        result = await self.db.execute(
            select(Company.nome).where(Company.id == company_id)
        )
        row = result.first()
        return row[0] if row else "Unknown"

    async def _get_demographic(
        self,
        campaign_id: uuid.UUID,
        sector_id_filter: Optional[uuid.UUID],
    ) -> DemographicBreakdown:
        query = select(
            SurveyResponse.faixa_etaria,
            SurveyResponse.genero,
            SurveyResponse.tempo_empresa,
        ).where(SurveyResponse.campaign_id == campaign_id)

        if sector_id_filter:
            query = query.where(SurveyResponse.sector_id == sector_id_filter)

        result = await self.db.execute(query)
        rows = result.all()

        if len(rows) < MIN_RESPONSES_FOR_DEMOGRAPHIC:
            return DemographicBreakdown()

        faixa: dict[str, int] = {}
        genero: dict[str, int] = {}
        tempo: dict[str, int] = {}

        for row in rows:
            if row.faixa_etaria:
                faixa[row.faixa_etaria] = faixa.get(row.faixa_etaria, 0) + 1
            if row.genero:
                genero[row.genero] = genero.get(row.genero, 0) + 1
            if row.tempo_empresa:
                tempo[row.tempo_empresa] = tempo.get(row.tempo_empresa, 0) + 1

        return DemographicBreakdown(
            faixa_etaria=faixa if faixa else None,
            genero=genero if genero else None,
            tempo_empresa=tempo if tempo else None,
        )


def _get_risk_level_from_score(score: Decimal, direction: str) -> str:
    from app.services.score_service import get_risk_level
    return get_risk_level(score, direction)
