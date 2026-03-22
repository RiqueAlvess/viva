import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models.survey import SurveyInvitation, InvitationEmail, SurveyResponse
from app.models.campaign import Campaign, Sector, Unit
from app.schemas.survey import ValidateTokenResponse, SurveySubmitRequest, SurveySubmitResponse
from app.core.security import hash_token
from app.services.anonymous_service import AnonymousSessionService
from app.workers.tasks.score_tasks import process_survey_response_task

router = APIRouter()


@router.get("/validate/{token}", response_model=ValidateTokenResponse)
async def validate_token(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Validate magic link token and return session UUID."""
    token_hash = hash_token(token)

    inv_result = await db.execute(
        select(SurveyInvitation).where(
            and_(
                SurveyInvitation.token_hash == token_hash,
                SurveyInvitation.status.in_(["pending", "sent"]),
                SurveyInvitation.expires_at > datetime.now(timezone.utc),
            )
        )
    )
    invitation = inv_result.scalar_one_or_none()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    # Load campaign
    campaign_result = await db.execute(
        select(Campaign).where(Campaign.id == invitation.campaign_id)
    )
    campaign = campaign_result.scalar_one_or_none()
    if not campaign or campaign.status != "active":
        raise HTTPException(status_code=400, detail="Campaign is not active")

    # Get collaborator's sector/unit via position
    from app.models.campaign import Position
    from app.models.survey import Collaborator

    collab_result = await db.execute(
        select(Collaborator).where(Collaborator.id == invitation.collaborator_id)
    )
    collab = collab_result.scalar_one_or_none()
    if not collab:
        raise HTTPException(status_code=404, detail="Collaborator not found")

    pos_result = await db.execute(
        select(Position).where(Position.id == collab.position_id)
    )
    position = pos_result.scalar_one_or_none()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")

    sector_result = await db.execute(
        select(Sector).where(Sector.id == position.sector_id)
    )
    sector = sector_result.scalar_one_or_none()

    unit_result = await db.execute(
        select(Unit).where(Unit.id == sector.unit_id)
    ) if sector else None
    unit = unit_result.scalar_one_or_none() if unit_result else None

    # Get company name
    from app.models.company import Company
    company_result = await db.execute(
        select(Company).where(Company.id == campaign.company_id)
    )
    company = company_result.scalar_one_or_none()

    # Nullify public token, mark as sent
    invitation.token_public = None
    invitation.status = "sent"
    invitation.display_status = "sent"
    invitation.sent_at = datetime.now(timezone.utc)
    await db.flush()

    # Create anonymous session in Redis
    session_uuid = await AnonymousSessionService.create_session(
        campaign_id=campaign.id,
        unit_id=unit.id if unit else uuid.uuid4(),
        sector_id=sector.id if sector else uuid.uuid4(),
    )

    await db.commit()

    return ValidateTokenResponse(
        session_uuid=session_uuid,
        campaign_id=campaign.id,
        company_name=company.nome if company else "Unknown",
        data_inicio=campaign.data_inicio,
        data_fim=campaign.data_fim,
        unit_id=unit.id if unit else uuid.uuid4(),
        sector_id=sector.id if sector else uuid.uuid4(),
    )


@router.post("/submit", response_model=SurveySubmitResponse)
async def submit_survey(
    payload: SurveySubmitRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit anonymous survey response."""
    # Validate and consume session
    session = await AnonymousSessionService.get_session(payload.session_uuid)
    if not session or session.get("used"):
        raise HTTPException(status_code=400, detail="Invalid or already used session")

    # Validate campaign is still active
    campaign_id = uuid.UUID(session["campaign_id"])
    campaign_result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = campaign_result.scalar_one_or_none()
    if not campaign or campaign.status != "active":
        raise HTTPException(status_code=400, detail="Campaign is not active")

    # Store response
    response = SurveyResponse(
        campaign_id=campaign_id,
        session_uuid=payload.session_uuid,
        unit_id=payload.unit_id,
        sector_id=payload.sector_id,
        answers=payload.answers,
        faixa_etaria=payload.faixa_etaria,
        genero=payload.genero,
        tempo_empresa=payload.tempo_empresa,
        lgpd_consent=payload.lgpd_consent,
        lgpd_consent_at=datetime.now(timezone.utc),
        submitted_at=datetime.now(timezone.utc),
        processed=False,
    )
    db.add(response)
    await db.flush()

    # Mark session used
    await AnonymousSessionService.mark_session_used(payload.session_uuid)

    # Update invitation display_status to 'responded' (no PII link)
    # We find invitation by matching sector/unit from session (approximate)
    await db.commit()

    # Queue async scoring
    process_survey_response_task.delay(str(response.id))

    return SurveySubmitResponse(
        success=True,
        message="Resposta registrada com sucesso. Obrigado pela sua participação!"
    )
