import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.core.permissions import require_rh_or_adm, get_current_user
from app.core.security import generate_magic_link_token, encrypt_email, decrypt_email
from app.models.campaign import Campaign, Sector, Unit
from app.models.survey import (
    SurveyInvitation, Collaborator, InvitationEmail
)
from app.schemas.survey import (
    InvitationListItem, SendInvitationsRequest,
)
from app.schemas.campaign import InvitationStatsResponse
from app.workers.tasks.email_tasks import send_invitation_email_task

router = APIRouter()

INVITATION_TTL_HOURS = 24


@router.get("/{campaign_id}/list", response_model=list[InvitationListItem])
async def list_invitations(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if current_user.role != "ADM" and campaign.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    inv_result = await db.execute(
        select(SurveyInvitation)
        .where(SurveyInvitation.campaign_id == campaign_id)
        .order_by(SurveyInvitation.created_at.desc())
    )
    invitations = inv_result.scalars().all()

    items = []
    for inv in invitations:
        collab_result = await db.execute(
            select(Collaborator).where(Collaborator.id == inv.collaborator_id)
        )
        collab = collab_result.scalar_one_or_none()
        unit_nome = None
        sector_nome = None
        unit_id = None
        sector_id = None

        if collab:
            pos_result = await db.execute(
                select(
                    Sector.id.label("sector_id"),
                    Sector.nome.label("sector_nome"),
                    Unit.id.label("unit_id"),
                    Unit.nome.label("unit_nome"),
                )
                .join(Unit, Sector.unit_id == Unit.id)
                .where(Sector.id == collab.position.sector_id if hasattr(collab, 'position') else None)
            )

        items.append(InvitationListItem(
            id=inv.id,
            collaborator_id=inv.collaborator_id,
            email_hash=collab.email_hash if collab else "",
            display_status=inv.display_status,
            unit_id=unit_id,
            sector_id=sector_id,
            unit_nome=unit_nome,
            sector_nome=sector_nome,
            sent_at=inv.sent_at,
            expires_at=inv.expires_at,
        ))
    return items


@router.get("/{campaign_id}/stats")
async def get_invitation_stats(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if current_user.role != "ADM" and campaign.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    inv_result = await db.execute(
        select(SurveyInvitation).where(SurveyInvitation.campaign_id == campaign_id)
    )
    invitations = inv_result.scalars().all()

    stats = {"total": len(invitations), "sent": 0, "responded": 0, "pending": 0, "expired": 0}
    for inv in invitations:
        if inv.display_status == "responded":
            stats["responded"] += 1
        elif inv.display_status == "sent":
            stats["sent"] += 1
        elif inv.display_status == "expired":
            stats["expired"] += 1
        else:
            stats["pending"] += 1
    return stats


@router.post("/{campaign_id}/send")
async def send_invitations(
    campaign_id: uuid.UUID,
    payload: SendInvitationsRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_rh_or_adm()),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if current_user.role != "ADM" and campaign.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    if campaign.status != "active":
        raise HTTPException(status_code=400, detail="Campaign must be active to send invitations")

    # Get collaborators
    if payload.send_all:
        collab_result = await db.execute(
            select(Collaborator).where(Collaborator.campaign_id == campaign_id)
        )
        collaborators = collab_result.scalars().all()
    else:
        collab_result = await db.execute(
            select(Collaborator).where(
                Collaborator.id.in_(payload.collaborator_ids or [])
            )
        )
        collaborators = collab_result.scalars().all()

    sent_count = 0
    for collab in collaborators:
        # Check if invitation already exists and pending/sent
        existing = await db.execute(
            select(SurveyInvitation).where(
                and_(
                    SurveyInvitation.collaborator_id == collab.id,
                    SurveyInvitation.display_status.in_(["pending", "sent"]),
                )
            )
        )
        if existing.scalar_one_or_none():
            continue  # Already has pending invitation

        # Get email from invitation_emails
        email_record_result = await db.execute(
            select(InvitationEmail)
            .join(SurveyInvitation, InvitationEmail.invitation_id == SurveyInvitation.id)
            .where(SurveyInvitation.collaborator_id == collab.id)
            .order_by(SurveyInvitation.created_at.desc())
        )

        token_raw, token_hash = generate_magic_link_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=INVITATION_TTL_HOURS)

        invitation = SurveyInvitation(
            campaign_id=campaign_id,
            collaborator_id=collab.id,
            token_public=uuid.uuid4(),
            token_hash=token_hash,
            status="pending",
            display_status="pending",
            expires_at=expires_at,
        )
        db.add(invitation)
        await db.flush()

        # Queue email sending via Celery
        send_invitation_email_task.delay(
            str(invitation.id),
            token_raw,
        )
        sent_count += 1

    await db.commit()
    return {"message": f"Queued {sent_count} invitations", "queued": sent_count}
