import logging
import asyncio
import uuid
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.workers.tasks.score_tasks.process_survey_response_task",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def process_survey_response_task(self, response_id: str):
    """Process and score a survey response, store in analytics."""
    try:
        asyncio.run(_process_response(response_id))
    except Exception as exc:
        logger.error(f"Score task failed for response {response_id}: {exc}")
        raise self.retry(exc=exc)


async def _process_response(response_id: str):
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models.survey import SurveyResponse
    from app.models.analytics import FactDimensionScore
    from app.services.score_service import score_response
    from app.services.risk_service import RiskService
    from datetime import datetime, timezone

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(SurveyResponse).where(
                SurveyResponse.id == uuid.UUID(response_id)
            )
        )
        response = result.scalar_one_or_none()
        if not response:
            logger.error(f"Response {response_id} not found")
            return

        if response.processed:
            logger.info(f"Response {response_id} already processed")
            return

        # Score the response
        scored = score_response(response.answers)

        # Store dimension scores
        for dimension, data in scored.items():
            fact = FactDimensionScore(
                campaign_id=response.campaign_id,
                unit_id=response.unit_id,
                sector_id=response.sector_id,
                response_id=response.id,
                dimension=dimension,
                score=data["score"],
                risk_level=data["risk_level"],
                nr_value=data["nr_value"],
            )
            db.add(fact)

        response.processed = True
        await db.flush()

        # Recompute campaign metrics
        risk_service = RiskService(db)
        await risk_service.compute_campaign_metrics(response.campaign_id)
        await _compute_sector_scores(db, response.campaign_id, risk_service)

        await db.commit()
        logger.info(f"Response {response_id} scored and processed successfully")


async def _compute_sector_scores(db, campaign_id: uuid.UUID, risk_service):
    """Recompute sector-level aggregate scores."""
    from sqlalchemy import select, func
    from app.models.analytics import FactDimensionScore, FactSectorScore
    from app.models.campaign import Sector
    from datetime import datetime, timezone
    from decimal import Decimal

    # Get all sectors for this campaign
    sectors_result = await db.execute(
        select(Sector).where(Sector.campaign_id == campaign_id)
    )
    sectors = sectors_result.scalars().all()

    for sector in sectors:
        scores_result = await db.execute(
            select(FactDimensionScore).where(
                FactDimensionScore.campaign_id == campaign_id,
                FactDimensionScore.sector_id == sector.id,
            )
        )
        scores = scores_result.scalars().all()
        if not scores:
            continue

        dimension_scores: dict[str, float] = {}
        for score in scores:
            if score.dimension not in dimension_scores:
                dimension_scores[score.dimension] = []
            dimension_scores[score.dimension].append(float(score.score))

        avg_dims = {dim: sum(vals) / len(vals) for dim, vals in dimension_scores.items()}

        all_nr = [float(s.nr_value) for s in scores]
        avg_nr = sum(all_nr) / len(all_nr) if all_nr else 0.0

        risk_counts = {}
        for s in scores:
            risk_counts[s.risk_level] = risk_counts.get(s.risk_level, 0) + 1
        dominant_risk = max(risk_counts, key=risk_counts.get) if risk_counts else "aceitavel"

        response_count = len(set(s.response_id for s in scores))

        # Upsert
        existing = await db.execute(
            select(FactSectorScore).where(
                FactSectorScore.campaign_id == campaign_id,
                FactSectorScore.sector_id == sector.id,
            )
        )
        existing_record = existing.scalar_one_or_none()
        if existing_record:
            existing_record.dimension_scores = avg_dims
            existing_record.avg_nr = Decimal(str(avg_nr))
            existing_record.risk_level = dominant_risk
            existing_record.response_count = response_count
            existing_record.computed_at = datetime.now(timezone.utc)
        else:
            sector_score = FactSectorScore(
                campaign_id=campaign_id,
                sector_id=sector.id,
                dimension_scores=avg_dims,
                avg_nr=Decimal(str(avg_nr)),
                risk_level=dominant_risk,
                response_count=response_count,
                computed_at=datetime.now(timezone.utc),
            )
            db.add(sector_score)
    await db.flush()
