import logging
import asyncio
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.workers.tasks.email_tasks.send_invitation_email_task",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_invitation_email_task(self, invitation_id: str, token_raw: str):
    """Send magic link email for a survey invitation."""
    try:
        asyncio.run(_send_invitation_email(invitation_id, token_raw))
    except Exception as exc:
        logger.error(f"Email task failed for invitation {invitation_id}: {exc}")
        raise self.retry(exc=exc)


async def _send_invitation_email(invitation_id: str, token_raw: str):
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models.survey import SurveyInvitation, InvitationEmail
    from app.models.campaign import Campaign
    from app.models.company import Company
    from app.services.email_service import EmailService
    from app.core.security import decrypt_email
    from datetime import datetime, timezone
    import uuid

    async with AsyncSessionLocal() as db:
        # Load invitation
        result = await db.execute(
            select(SurveyInvitation).where(
                SurveyInvitation.id == uuid.UUID(invitation_id)
            )
        )
        invitation = result.scalar_one_or_none()
        if not invitation:
            logger.error(f"Invitation {invitation_id} not found")
            return

        # Load email record
        email_result = await db.execute(
            select(InvitationEmail).where(
                InvitationEmail.invitation_id == invitation.id
            )
        )
        email_record = email_result.scalar_one_or_none()
        if not email_record:
            logger.warning(f"No email record for invitation {invitation_id}, skipping")
            return

        email = decrypt_email(email_record.email_encrypted)

        # Load company name
        campaign_result = await db.execute(
            select(Campaign).where(Campaign.id == invitation.campaign_id)
        )
        campaign = campaign_result.scalar_one_or_none()
        company_nome = "Unknown"
        if campaign:
            company_result = await db.execute(
                select(Company).where(Company.id == campaign.company_id)
            )
            company = company_result.scalar_one_or_none()
            if company:
                company_nome = company.nome

        success = await EmailService.send_magic_link(email, company_nome, token_raw)

        if success:
            invitation.status = "sent"
            invitation.display_status = "sent"
            invitation.sent_at = datetime.now(timezone.utc)
            await db.commit()
            logger.info(f"Invitation {invitation_id} email sent successfully")
        else:
            logger.error(f"Failed to send email for invitation {invitation_id}")
