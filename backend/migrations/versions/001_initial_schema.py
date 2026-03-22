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


def upgrade() -> None:
    # Create schemas
    op.execute("CREATE SCHEMA IF NOT EXISTS core")
    op.execute("CREATE SCHEMA IF NOT EXISTS survey")
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics")

    # Create enums
    op.execute("CREATE TYPE core.user_role AS ENUM ('ADM', 'RH', 'LIDERANCA')")
    op.execute("CREATE TYPE survey.campaign_status AS ENUM ('draft', 'active', 'closed')")
    op.execute("CREATE TYPE survey.invitation_status AS ENUM ('pending', 'sent', 'used', 'expired')")
    op.execute("CREATE TYPE survey.invitation_display_status AS ENUM ('pending', 'sent', 'responded', 'expired')")
    op.execute("CREATE TYPE survey.faixa_etaria_enum AS ENUM ('18-24', '25-34', '35-44', '45-54', '55-64', '65+')")
    op.execute("CREATE TYPE survey.genero_enum AS ENUM ('M', 'F', 'O', 'N')")
    op.execute("CREATE TYPE survey.tempo_empresa_enum AS ENUM ('<1', '1-3', '3-5', '5-10', '>10')")

    # core.companies
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("cnpj", sa.String(14), unique=True, nullable=False),
        sa.Column("cnae", sa.String(10), nullable=True),
        sa.Column("ativo", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        schema="core",
    )

    # core.users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.companies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("ADM", "RH", "LIDERANCA", name="user_role", schema="core"), nullable=False),
        sa.Column("ativo", sa.Boolean, server_default="true", nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        schema="core",
    )
    op.create_index("ix_core_users_email", "users", ["email"], schema="core")

    # core.refresh_tokens
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("core.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(255), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean, server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        schema="core",
    )

    # survey.campaigns
    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("data_inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_fim", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.Enum("draft", "active", "closed", name="campaign_status", schema="survey"), server_default="draft", nullable=False),
        sa.Column("salt", sa.String(64), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        schema="survey",
    )

    # survey.units
    op.create_table(
        "units",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey.campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        schema="survey",
    )

    # survey.sectors
    op.create_table(
        "sectors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("unit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey.units.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey.campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        schema="survey",
    )

    # survey.positions
    op.create_table(
        "positions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey.sectors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey.campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        schema="survey",
    )

    # survey.collaborators
    op.create_table(
        "collaborators",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey.campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey.positions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        schema="survey",
    )

    # survey.survey_invitations
    op.create_table(
        "survey_invitations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey.campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("collaborator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey.collaborators.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_public", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.Enum("pending", "sent", "used", "expired", name="invitation_status", schema="survey"), server_default="pending", nullable=False),
        sa.Column("display_status", sa.Enum("pending", "sent", "responded", "expired", name="invitation_display_status", schema="survey"), server_default="pending", nullable=False),
        sa.Column("status_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("display_status_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        schema="survey",
    )
    op.create_index("ix_survey_invitations_token_hash", "survey_invitations", ["token_hash"], schema="survey")

    # survey.invitation_emails
    op.create_table(
        "invitation_emails",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("invitation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey.survey_invitations.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("email_encrypted", sa.Text, nullable=False),
        sa.Column("used", sa.Boolean, server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        schema="survey",
    )

    # survey.survey_responses
    op.create_table(
        "survey_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey.campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("session_uuid", postgresql.UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column("unit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey.units.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey.sectors.id", ondelete="SET NULL"), nullable=True),
        sa.Column("answers", postgresql.JSONB, nullable=False),
        sa.Column("faixa_etaria", sa.Enum("18-24", "25-34", "35-44", "45-54", "55-64", "65+", name="faixa_etaria_enum", schema="survey"), nullable=True),
        sa.Column("genero", sa.Enum("M", "F", "O", "N", name="genero_enum", schema="survey"), nullable=True),
        sa.Column("tempo_empresa", sa.Enum("<1", "1-3", "3-5", "5-10", ">10", name="tempo_empresa_enum", schema="survey"), nullable=True),
        sa.Column("lgpd_consent", sa.Boolean, nullable=False),
        sa.Column("lgpd_consent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed", sa.Boolean, server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        schema="survey",
    )

    # analytics.fact_dimension_scores
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
        schema="analytics",
    )
    op.create_index("ix_fact_dimension_scores_campaign_id", "fact_dimension_scores", ["campaign_id"], schema="analytics")
    op.create_index("ix_fact_dimension_scores_response_id", "fact_dimension_scores", ["response_id"], schema="analytics")

    # analytics.fact_campaign_metrics
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
        schema="analytics",
    )

    # analytics.fact_sector_scores
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
        schema="analytics",
    )
    op.create_index("ix_fact_sector_scores_campaign_id", "fact_sector_scores", ["campaign_id"], schema="analytics")
    op.create_index("ix_fact_sector_scores_sector_id", "fact_sector_scores", ["sector_id"], schema="analytics")


def downgrade() -> None:
    op.drop_table("fact_sector_scores", schema="analytics")
    op.drop_table("fact_campaign_metrics", schema="analytics")
    op.drop_table("fact_dimension_scores", schema="analytics")
    op.drop_table("survey_responses", schema="survey")
    op.drop_table("invitation_emails", schema="survey")
    op.drop_table("survey_invitations", schema="survey")
    op.drop_table("collaborators", schema="survey")
    op.drop_table("positions", schema="survey")
    op.drop_table("sectors", schema="survey")
    op.drop_table("units", schema="survey")
    op.drop_table("campaigns", schema="survey")
    op.drop_table("refresh_tokens", schema="core")
    op.drop_table("users", schema="core")
    op.drop_table("companies", schema="core")
    op.execute("DROP SCHEMA IF EXISTS analytics CASCADE")
    op.execute("DROP SCHEMA IF EXISTS survey CASCADE")
    op.execute("DROP SCHEMA IF EXISTS core CASCADE")
