"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define ENUM types once — postgresql.ENUM with create_type=False
# prevents SQLAlchemy from auto-creating them during op.create_table.
# We create them explicitly via DO blocks (idempotent).
enum_user_role = postgresql.ENUM(
    "ADM", "RH", "LIDERANCA",
    name="user_role", create_type=False,
)
enum_campaign_status = postgresql.ENUM(
    "draft", "active", "closed",
    name="campaign_status", create_type=False,
)
enum_invitation_status = postgresql.ENUM(
    "pending", "sent", "used", "expired",
    name="invitation_status", create_type=False,
)
enum_invitation_display_status = postgresql.ENUM(
    "pending", "sent", "responded", "expired",
    name="invitation_display_status", create_type=False,
)
enum_faixa_etaria = postgresql.ENUM(
    "18-24", "25-34", "35-44", "45-54", "55-64", "65+",
    name="faixa_etaria_enum", create_type=False,
)
enum_genero = postgresql.ENUM(
    "M", "F", "O", "N",
    name="genero_enum", create_type=False,
)
enum_tempo_empresa = postgresql.ENUM(
    "<1", "1-3", "3-5", "5-10", ">10",
    name="tempo_empresa_enum", create_type=False,
)


def _create_enum_idempotent(sql: str) -> None:
    """Wrap CREATE TYPE in a DO block so it doesn't fail if the type exists."""
    op.execute(
        f"DO $$ BEGIN {sql}; EXCEPTION WHEN duplicate_object THEN NULL; END $$"
    )


def upgrade() -> None:
    # --- Enum types (idempotent) ---
    _create_enum_idempotent(
        "CREATE TYPE user_role AS ENUM ('ADM', 'RH', 'LIDERANCA')"
    )
    _create_enum_idempotent(
        "CREATE TYPE campaign_status AS ENUM ('draft', 'active', 'closed')"
    )
    _create_enum_idempotent(
        "CREATE TYPE invitation_status AS ENUM ('pending', 'sent', 'used', 'expired')"
    )
    _create_enum_idempotent(
        "CREATE TYPE invitation_display_status AS ENUM ('pending', 'sent', 'responded', 'expired')"
    )
    _create_enum_idempotent(
        "CREATE TYPE faixa_etaria_enum AS ENUM ('18-24', '25-34', '35-44', '45-54', '55-64', '65+')"
    )
    _create_enum_idempotent(
        "CREATE TYPE genero_enum AS ENUM ('M', 'F', 'O', 'N')"
    )
    _create_enum_idempotent(
        "CREATE TYPE tempo_empresa_enum AS ENUM ('<1', '1-3', '3-5', '5-10', '>10')"
    )

    # --- companies ---
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("cnpj", sa.String(14), unique=True, nullable=False),
        sa.Column("cnae", sa.String(10), nullable=True),
        sa.Column("ativo", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", enum_user_role, nullable=False),
        sa.Column("ativo", sa.Boolean, server_default="true", nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # --- refresh_tokens ---
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(255), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean, server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # --- campaigns ---
    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("data_inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_fim", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", enum_campaign_status, server_default="draft", nullable=False),
        sa.Column("salt", sa.String(64), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_campaigns_company_id", "campaigns", ["company_id"])

    # --- units ---
    op.create_table(
        "units",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # --- sectors ---
    op.create_table(
        "sectors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("unit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("units.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # --- positions ---
    op.create_table(
        "positions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sectors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # --- collaborators ---
    op.create_table(
        "collaborators",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("positions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # --- survey_invitations ---
    op.create_table(
        "survey_invitations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("collaborator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("collaborators.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_public", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("status", enum_invitation_status, server_default="pending", nullable=False),
        sa.Column("display_status", enum_invitation_display_status, server_default="pending", nullable=False),
        sa.Column("status_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("display_status_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_survey_invitations_token_hash", "survey_invitations", ["token_hash"])

    # --- invitation_emails ---
    op.create_table(
        "invitation_emails",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("invitation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey_invitations.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("email_encrypted", sa.Text, nullable=False),
        sa.Column("used", sa.Boolean, server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # --- survey_responses ---
    op.create_table(
        "survey_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("session_uuid", postgresql.UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column("unit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("units.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sectors.id", ondelete="SET NULL"), nullable=True),
        sa.Column("answers", postgresql.JSONB, nullable=False),
        sa.Column("faixa_etaria", enum_faixa_etaria, nullable=True),
        sa.Column("genero", enum_genero, nullable=True),
        sa.Column("tempo_empresa", enum_tempo_empresa, nullable=True),
        sa.Column("lgpd_consent", sa.Boolean, nullable=False),
        sa.Column("lgpd_consent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed", sa.Boolean, server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # --- fact_dimension_scores ---
    op.create_table(
        "fact_dimension_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("unit_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("response_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dimension", sa.String(50), nullable=False),
        sa.Column("score", sa.Numeric(4, 2), nullable=False),
        sa.Column("risk_level", sa.String(20), nullable=False),
        sa.Column("nr_value", sa.Numeric(4, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_fact_dimension_scores_campaign_id", "fact_dimension_scores", ["campaign_id"])
    op.create_index("ix_fact_dimension_scores_response_id", "fact_dimension_scores", ["response_id"])

    # --- fact_campaign_metrics ---
    op.create_table(
        "fact_campaign_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column("total_invited", sa.Integer, server_default="0", nullable=False),
        sa.Column("total_responded", sa.Integer, server_default="0", nullable=False),
        sa.Column("adhesion_rate", sa.Numeric(5, 2), server_default="0", nullable=False),
        sa.Column("igrp", sa.Numeric(5, 2), server_default="0", nullable=False),
        sa.Column("risk_distribution", postgresql.JSONB, server_default="{}", nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- fact_sector_scores ---
    op.create_table(
        "fact_sector_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dimension_scores", postgresql.JSONB, server_default="{}", nullable=False),
        sa.Column("avg_nr", sa.Numeric(4, 2), server_default="0", nullable=False),
        sa.Column("risk_level", sa.String(20), server_default="aceitavel", nullable=False),
        sa.Column("response_count", sa.Integer, server_default="0", nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_fact_sector_scores_campaign_id", "fact_sector_scores", ["campaign_id"])
    op.create_index("ix_fact_sector_scores_sector_id", "fact_sector_scores", ["sector_id"])


def downgrade() -> None:
    op.drop_table("fact_sector_scores")
    op.drop_table("fact_campaign_metrics")
    op.drop_table("fact_dimension_scores")
    op.drop_table("survey_responses")
    op.drop_table("invitation_emails")
    op.drop_table("survey_invitations")
    op.drop_table("collaborators")
    op.drop_table("positions")
    op.drop_table("sectors")
    op.drop_table("units")
    op.drop_table("campaigns")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
    op.drop_table("companies")
    op.execute("DROP TYPE IF EXISTS tempo_empresa_enum")
    op.execute("DROP TYPE IF EXISTS genero_enum")
    op.execute("DROP TYPE IF EXISTS faixa_etaria_enum")
    op.execute("DROP TYPE IF EXISTS invitation_display_status")
    op.execute("DROP TYPE IF EXISTS invitation_status")
    op.execute("DROP TYPE IF EXISTS campaign_status")
    op.execute("DROP TYPE IF EXISTS user_role")
