import uuid
from datetime import datetime
from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey, Text, func,
    Enum as SAEnum, Integer, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class Collaborator(Base):
    __tablename__ = "collaborators"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    position_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("positions.id", ondelete="CASCADE"),
        nullable=False,
    )
    email_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign", back_populates="collaborators"
    )
    position: Mapped["Position"] = relationship(
        "Position", back_populates="collaborators"
    )
    invitations: Mapped[list["SurveyInvitation"]] = relationship(
        "SurveyInvitation", back_populates="collaborator"
    )


class SurveyInvitation(Base):
    __tablename__ = "survey_invitations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    collaborator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("collaborators.id", ondelete="CASCADE"),
        nullable=False,
    )
    # token_public is set to NULL after use
    token_public: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        SAEnum(
            "pending", "sent", "used", "expired",
            name="invitation_status",
        ),
        default="pending",
        nullable=False,
    )
    display_status: Mapped[str] = mapped_column(
        SAEnum(
            "pending", "sent", "responded", "expired",
            name="invitation_display_status",
        ),
        default="pending",
        nullable=False,
    )
    status_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    display_status_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign", back_populates="invitations"
    )
    collaborator: Mapped["Collaborator"] = relationship(
        "Collaborator", back_populates="invitations"
    )
    email_record: Mapped["InvitationEmail"] = relationship(
        "InvitationEmail", back_populates="invitation", uselist=False
    )


class InvitationEmail(Base):
    """Separate encrypted email storage — never exposed via API."""
    __tablename__ = "invitation_emails"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    invitation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("survey_invitations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    email_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    invitation: Mapped["SurveyInvitation"] = relationship(
        "SurveyInvitation", back_populates="email_record"
    )


class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )
    unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("units.id", ondelete="SET NULL"),
        nullable=True,
    )
    sector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sectors.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Intentionally NO position_id / NO collaborator_id / NO invitation_id
    answers: Mapped[dict] = mapped_column(JSONB, nullable=False)
    faixa_etaria: Mapped[str | None] = mapped_column(
        SAEnum(
            "18-24", "25-34", "35-44", "45-54", "55-64", "65+",
            name="faixa_etaria_enum",
        ),
        nullable=True,
    )
    genero: Mapped[str | None] = mapped_column(
        SAEnum("M", "F", "O", "N", name="genero_enum"),
        nullable=True,
    )
    tempo_empresa: Mapped[str | None] = mapped_column(
        SAEnum(
            "<1", "1-3", "3-5", "5-10", ">10",
            name="tempo_empresa_enum",
        ),
        nullable=True,
    )
    lgpd_consent: Mapped[bool] = mapped_column(Boolean, nullable=False)
    lgpd_consent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign", back_populates="responses"
    )
    unit: Mapped["Unit"] = relationship("Unit", back_populates="responses")
    sector: Mapped["Sector"] = relationship("Sector", back_populates="responses")


# Session tracking for anonymous tokens (in-memory via Redis)
# session_uuid -> {campaign_id, unit_id, sector_id, used: bool}
# Stored in Redis with 48h TTL, NOT in PostgreSQL
