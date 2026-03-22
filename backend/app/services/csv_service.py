"""CSV upload service for collaborator bulk import."""
import io
import uuid
import logging
from typing import Optional

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.campaign import Campaign, Unit, Sector, Position
from app.models.survey import Collaborator
from app.core.security import hash_email_with_salt
from app.schemas.campaign import CSVUploadPreview

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"unidade", "setor", "cargo", "email"}


class CSVService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def parse_csv(
        self, content: bytes, encoding: str = "utf-8-sig"
    ) -> pd.DataFrame:
        """Parse CSV content, auto-detecting delimiter."""
        text = content.decode(encoding)
        # Try semicolon first, then comma
        for sep in [";", ","]:
            try:
                df = pd.read_csv(io.StringIO(text), sep=sep, dtype=str)
                df.columns = [c.strip().lower() for c in df.columns]
                if REQUIRED_COLUMNS.issubset(set(df.columns)):
                    return df
            except Exception:
                pass
        raise ValueError("Could not parse CSV. Ensure it has columns: unidade,setor,cargo,email")

    async def preview_csv(self, content: bytes) -> CSVUploadPreview:
        """Parse CSV and return preview stats without saving."""
        errors: list[str] = []
        try:
            df = await self.parse_csv(content)
        except ValueError as e:
            return CSVUploadPreview(
                total_rows=0, units=0, sectors=0, positions=0, collaborators=0,
                errors=[str(e)]
            )

        df = df.dropna(subset=list(REQUIRED_COLUMNS))
        total_rows = len(df)

        # Validate emails
        for idx, row in df.iterrows():
            email = str(row.get("email", "")).strip()
            if "@" not in email:
                errors.append(f"Row {idx + 2}: invalid email '{email}'")

        units = df["unidade"].nunique()
        sectors = df["setor"].nunique()
        positions = df["cargo"].nunique()
        collaborators = len(df)
        sample = df.head(5).to_dict(orient="records")

        return CSVUploadPreview(
            total_rows=total_rows,
            units=units,
            sectors=sectors,
            positions=positions,
            collaborators=collaborators,
            errors=errors[:20],  # cap error list
            sample_rows=sample,
        )

    async def import_csv(
        self, content: bytes, campaign_id: uuid.UUID
    ) -> CSVUploadPreview:
        """Parse and import CSV into the database."""
        df = await self.parse_csv(content)
        df = df.dropna(subset=list(REQUIRED_COLUMNS))

        # Load campaign salt
        campaign_result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        campaign = campaign_result.scalar_one_or_none()
        if not campaign:
            raise ValueError("Campaign not found")

        salt = campaign.salt
        unit_cache: dict[str, Unit] = {}
        sector_cache: dict[str, Sector] = {}
        position_cache: dict[str, Position] = {}
        collab_count = 0
        errors: list[str] = []

        for idx, row in df.iterrows():
            unidade = str(row["unidade"]).strip()
            setor = str(row["setor"]).strip()
            cargo = str(row["cargo"]).strip()
            email = str(row["email"]).strip().lower()

            if "@" not in email:
                errors.append(f"Row {idx + 2}: invalid email '{email}'")
                continue

            # Upsert Unit
            unit_key = f"{campaign_id}:{unidade}"
            if unit_key not in unit_cache:
                existing = await self.db.execute(
                    select(Unit).where(
                        Unit.campaign_id == campaign_id,
                        Unit.nome == unidade,
                    )
                )
                unit = existing.scalar_one_or_none()
                if not unit:
                    unit = Unit(campaign_id=campaign_id, nome=unidade)
                    self.db.add(unit)
                    await self.db.flush()
                unit_cache[unit_key] = unit
            unit = unit_cache[unit_key]

            # Upsert Sector
            sector_key = f"{campaign_id}:{unidade}:{setor}"
            if sector_key not in sector_cache:
                existing = await self.db.execute(
                    select(Sector).where(
                        Sector.campaign_id == campaign_id,
                        Sector.unit_id == unit.id,
                        Sector.nome == setor,
                    )
                )
                sector = existing.scalar_one_or_none()
                if not sector:
                    sector = Sector(
                        campaign_id=campaign_id,
                        unit_id=unit.id,
                        nome=setor,
                    )
                    self.db.add(sector)
                    await self.db.flush()
                sector_cache[sector_key] = sector
            sector = sector_cache[sector_key]

            # Upsert Position
            position_key = f"{campaign_id}:{setor}:{cargo}"
            if position_key not in position_cache:
                existing = await self.db.execute(
                    select(Position).where(
                        Position.campaign_id == campaign_id,
                        Position.sector_id == sector.id,
                        Position.nome == cargo,
                    )
                )
                position = existing.scalar_one_or_none()
                if not position:
                    position = Position(
                        campaign_id=campaign_id,
                        sector_id=sector.id,
                        nome=cargo,
                    )
                    self.db.add(position)
                    await self.db.flush()
                position_cache[position_key] = position
            position = position_cache[position_key]

            # Create Collaborator (hash email with salt)
            email_hash = hash_email_with_salt(email, salt)
            # Check if already exists (avoid duplicates)
            existing_collab = await self.db.execute(
                select(Collaborator).where(
                    Collaborator.campaign_id == campaign_id,
                    Collaborator.email_hash == email_hash,
                )
            )
            collab = existing_collab.scalar_one_or_none()
            if not collab:
                collab = Collaborator(
                    campaign_id=campaign_id,
                    position_id=position.id,
                    email_hash=email_hash,
                )
                self.db.add(collab)
                collab_count += 1

        await self.db.flush()

        return CSVUploadPreview(
            total_rows=len(df),
            units=len(unit_cache),
            sectors=len(sector_cache),
            positions=len(position_cache),
            collaborators=collab_count,
            errors=errors,
        )
