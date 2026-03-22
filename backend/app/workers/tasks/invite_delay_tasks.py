import logging
import asyncio
from datetime import datetime, timezone
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.workers.tasks.invite_delay_tasks.expire_invitations_task",
)
def expire_invitations_task():
    """Mark expired invitations. Run periodically via Celery Beat."""
    asyncio.run(_expire_invitations())


async def _expire_invitations():
    from sqlalchemy import select, and_
    from app.database import AsyncSessionLocal
    from app.models.survey import SurveyInvitation

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(SurveyInvitation).where(
                and_(
                    SurveyInvitation.expires_at <= datetime.now(timezone.utc),
                    SurveyInvitation.status.in_(["pending", "sent"]),
                )
            )
        )
        expired = result.scalars().all()
        count = 0
        for inv in expired:
            inv.status = "expired"
            inv.display_status = "expired"
            count += 1

        if count > 0:
            await db.commit()
            logger.info(f"Marked {count} invitations as expired")
