import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.permissions import get_current_user
from app.models.campaign import Campaign
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/{campaign_id}", response_model=DashboardResponse)
async def get_dashboard(
    campaign_id: uuid.UUID,
    sector_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if current_user.role != "ADM" and campaign.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    service = DashboardService(db)
    try:
        return await service.get_dashboard(campaign_id, sector_id_filter=sector_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
