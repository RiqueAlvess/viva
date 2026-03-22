"""PDF report generation service using ReportLab."""
import uuid
import logging
from datetime import datetime, timezone
from io import BytesIO
from typing import Optional

logger = logging.getLogger(__name__)

RISK_COLORS = {
    "aceitavel": (0.18, 0.8, 0.44),
    "moderado": (1.0, 0.76, 0.03),
    "importante": (1.0, 0.49, 0.0),
    "critico": (0.94, 0.27, 0.27),
}

DIMENSION_LABELS = {
    "demandas": "Demandas",
    "controle": "Controle",
    "apoio_chefia": "Apoio da Chefia",
    "apoio_colegas": "Apoio dos Colegas",
    "relacionamentos": "Relacionamentos",
    "cargo": "Cargo",
    "comunicacao_mudancas": "Comunicação e Mudanças",
}


class ReportService:
    def __init__(self, dashboard_data: dict):
        self.data = dashboard_data

    def generate_pdf(self) -> bytes:
        """Generate a PDF report from dashboard data."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                HRFlowable, PageBreak,
            )

            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2 * cm,
                leftMargin=2 * cm,
                topMargin=2 * cm,
                bottomMargin=2 * cm,
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "Title",
                parent=styles["Title"],
                fontSize=20,
                textColor=colors.HexColor("#1E40AF"),
                spaceAfter=12,
            )
            heading_style = ParagraphStyle(
                "Heading",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#1E3A5F"),
                spaceBefore=12,
                spaceAfter=6,
            )
            body_style = styles["Normal"]

            story = []

            # Header
            story.append(Paragraph("VIVA Psicossocial", title_style))
            story.append(Paragraph("Relatório de Análise de Risco Psicossocial (NR-1)", heading_style))
            story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1E40AF")))
            story.append(Spacer(1, 0.5 * cm))

            # Campaign info
            story.append(Paragraph(f"Campanha: {self.data.get('campaign_nome', 'N/A')}", body_style))
            story.append(Paragraph(f"Empresa: {self.data.get('company_nome', 'N/A')}", body_style))
            story.append(Paragraph(
                f"Período: {self._fmt_date(self.data.get('data_inicio'))} a {self._fmt_date(self.data.get('data_fim'))}",
                body_style,
            ))
            story.append(Paragraph(
                f"Gerado em: {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')}",
                body_style,
            ))
            story.append(Spacer(1, 0.5 * cm))

            # Participation metrics
            story.append(Paragraph("1. Métricas de Participação", heading_style))
            metrics_data = [
                ["Indicador", "Valor"],
                ["Total Convidados", str(self.data.get("total_invited", 0))],
                ["Total Respondentes", str(self.data.get("total_responded", 0))],
                ["Taxa de Adesão", f"{self.data.get('adhesion_rate', 0):.1f}%"],
                ["IGRP (Índice Geral de Risco Psicossocial)", f"{self.data.get('igrp', 0):.2f}"],
            ]
            metrics_table = Table(metrics_data, colWidths=[10 * cm, 6 * cm])
            metrics_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E40AF")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(metrics_table)
            story.append(Spacer(1, 0.5 * cm))

            # Dimension scores
            story.append(Paragraph("2. Pontuação por Dimensão", heading_style))
            dim_data = [["Dimensão", "Score Médio", "Nível de Risco", "NR Value"]]
            for dim in self.data.get("dimension_scores", []):
                dim_label = DIMENSION_LABELS.get(dim.get("dimension", ""), dim.get("dimension", ""))
                risk = dim.get("risk_level", "aceitavel")
                dim_data.append([
                    dim_label,
                    f"{dim.get('score', 0):.2f}",
                    risk.upper(),
                    f"{dim.get('nr_value', 0):.2f}",
                ])
            dim_table = Table(dim_data, colWidths=[6 * cm, 3 * cm, 4 * cm, 3 * cm])
            dim_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E40AF")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]))
            story.append(dim_table)
            story.append(Spacer(1, 0.5 * cm))

            # Top risk sectors
            top5 = self.data.get("top5_sectors", [])
            if top5:
                story.append(Paragraph("3. Top 5 Setores com Maior Risco", heading_style))
                top5_data = [["Unidade", "Setor", "Respostas", "Score NR", "Risco"]]
                for s in top5:
                    top5_data.append([
                        s.get("unit_nome", ""),
                        s.get("sector_nome", ""),
                        str(s.get("response_count", 0)),
                        f"{s.get('avg_nr', 0):.2f}",
                        s.get("risk_level", "").upper(),
                    ])
                top5_table = Table(top5_data, colWidths=[4 * cm, 4 * cm, 2.5 * cm, 2.5 * cm, 3 * cm])
                top5_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E40AF")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ALIGN", (2, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ]))
                story.append(top5_table)
                story.append(Spacer(1, 0.5 * cm))

            # LGPD notice
            story.append(PageBreak())
            story.append(Paragraph("Aviso Legal e LGPD", heading_style))
            story.append(Paragraph(
                "Este relatório foi gerado em conformidade com a NR-1 (Norma Regulamentadora nº 1) "
                "do Ministério do Trabalho e Emprego do Brasil. Todos os dados foram coletados "
                "de forma completamente anônima, em conformidade com a Lei Geral de Proteção de Dados "
                "(LGPD - Lei nº 13.709/2018). Nenhuma informação que permita a identificação individual "
                "dos respondentes está contida neste relatório.",
                body_style,
            ))

            doc.build(story)
            return buffer.getvalue()

        except ImportError:
            logger.error("ReportLab not installed. Install with: pip install reportlab")
            raise
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise

    def _fmt_date(self, dt) -> str:
        if not dt:
            return "N/A"
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt)
            except Exception:
                return dt
        return dt.strftime("%d/%m/%Y")
