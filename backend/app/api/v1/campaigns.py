import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.permissions import require_rh_or_adm, get_current_user
from app.models.campaign import Campaign, Unit, Sector, Position
from app.models.survey import Collaborator
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse,
    CloseConfirmation, HierarchyResponse, UnitSchema, SectorSchema, PositionSchema,
    CSVUploadPreview,
)
from app.core.security import generate_campaign_salt
from app.services.csv_service import CSVService

router = APIRouter()


def _check_campaign_access(campaign: Campaign, current_user) -> None:
    if current_user.role == "ADM":
        return
    if campaign.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Access forbidden")


@router.get("/", response_model=list[CampaignResponse])
async def list_campaigns(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "ADM":
        result = await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
    else:
        result = await db.execute(
            select(Campaign)
            .where(Campaign.company_id == current_user.company_id)
            .order_by(Campaign.created_at.desc())
        )
    return list(result.scalars().all())


@router.post("/", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    payload: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_rh_or_adm()),
):
    company_id = payload.company_id if current_user.role == "ADM" and payload.company_id else current_user.company_id
    campaign = Campaign(
        company_id=company_id,
        nome=payload.nome,
        descricao=payload.descricao,
        data_inicio=payload.data_inicio,
        data_fim=payload.data_fim,
        status="draft",
        salt=generate_campaign_salt(),
        created_by=current_user.id,
    )
    db.add(campaign)
    await db.flush()
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    _check_campaign_access(campaign, current_user)
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: uuid.UUID,
    payload: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_rh_or_adm()),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    _check_campaign_access(campaign, current_user)
    if campaign.status == "closed":
        raise HTTPException(status_code=400, detail="Cannot update a closed campaign")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(campaign, field, value)
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/activate", response_model=CampaignResponse)
async def activate_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_rh_or_adm()),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    _check_campaign_access(campaign, current_user)
    if campaign.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft campaigns can be activated")
    campaign.status = "active"
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/close", response_model=CampaignResponse)
async def close_campaign(
    campaign_id: uuid.UUID,
    payload: CloseConfirmation,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_rh_or_adm()),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    _check_campaign_access(campaign, current_user)
    if campaign.status != "active":
        raise HTTPException(status_code=400, detail="Only active campaigns can be closed")
    campaign.status = "closed"
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}/hierarchy", response_model=HierarchyResponse)
async def get_hierarchy(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    _check_campaign_access(campaign, current_user)

    units_result = await db.execute(
        select(Unit).where(Unit.campaign_id == campaign_id).order_by(Unit.nome)
    )
    units = units_result.scalars().all()

    unit_schemas = []
    for unit in units:
        sectors_result = await db.execute(
            select(Sector).where(
                Sector.campaign_id == campaign_id,
                Sector.unit_id == unit.id,
            ).order_by(Sector.nome)
        )
        sectors = sectors_result.scalars().all()

        sector_schemas = []
        for sector in sectors:
            positions_result = await db.execute(
                select(Position, )
                .where(
                    Position.campaign_id == campaign_id,
                    Position.sector_id == sector.id,
                ).order_by(Position.nome)
            )
            positions_data = positions_result.scalars().all()

            position_schemas = []
            for pos in positions_data:
                count_result = await db.execute(
                    select(Collaborator).where(Collaborator.position_id == pos.id)
                )
                collab_count = len(count_result.scalars().all())
                position_schemas.append(PositionSchema(
                    id=pos.id,
                    nome=pos.nome,
                    collaborator_count=collab_count,
                ))
            sector_schemas.append(SectorSchema(
                id=sector.id,
                nome=sector.nome,
                positions=position_schemas,
            ))
        unit_schemas.append(UnitSchema(
            id=unit.id,
            nome=unit.nome,
            sectors=sector_schemas,
        ))

    return HierarchyResponse(campaign_id=campaign_id, units=unit_schemas)


@router.post("/{campaign_id}/upload-csv", response_model=CSVUploadPreview)
async def upload_csv(
    campaign_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_rh_or_adm()),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    _check_campaign_access(campaign, current_user)
    if campaign.status == "closed":
        raise HTTPException(status_code=400, detail="Cannot upload to a closed campaign")

    content = await file.read()
    service = CSVService(db)
    result_data = await service.import_csv(content, campaign_id)
    await db.commit()
    return result_data


@router.post("/{campaign_id}/preview-csv", response_model=CSVUploadPreview)
async def preview_csv(
    campaign_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_rh_or_adm()),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    _check_campaign_access(campaign, current_user)

    content = await file.read()
    service = CSVService(db)
    return await service.preview_csv(content)
