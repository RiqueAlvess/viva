import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.permissions import require_rh_or_adm, get_current_user
from app.models.campaign import Campaign
from app.schemas.report import ReportGenerateRequest, ReportResponse
from app.schemas.dashboard import ReportStatusResponse
from app.workers.tasks.report_tasks import generate_report_task

router = APIRouter()


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    payload: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_rh_or_adm()),
):
    result = await db.execute(select(Campaign).where(Campaign.id == payload.campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if current_user.role != "ADM" and campaign.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    if campaign.status not in ("active", "closed"):
        raise HTTPException(status_code=400, detail="Campaign must be active or closed to generate report")

    task = generate_report_task.delay(str(payload.campaign_id))
    return ReportResponse(
        task_id=task.id,
        campaign_id=payload.campaign_id,
        message="Report generation queued",
        status="queued",
    )


@router.get("/{campaign_id}/status", response_model=ReportStatusResponse)
async def get_report_status(
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

    from app.services.storage_service import StorageService
    report_info = await StorageService.get_report_url(campaign_id)
    return ReportStatusResponse(
        campaign_id=campaign_id,
        status=report_info.get("status", "pending"),
        report_url=report_info.get("url"),
        generated_at=report_info.get("generated_at"),
        error_message=report_info.get("error"),
    )
