"""Supabase Storage service for report files."""
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# In-memory report status store (production would use Redis or DB)
_report_status: dict[str, dict] = {}


class StorageService:
    @staticmethod
    async def upload_report(campaign_id: uuid.UUID, pdf_bytes: bytes) -> str:
        """Upload PDF report to Supabase Storage and return public URL."""
        from app.core.config import settings
        try:
            from supabase import create_client
            supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
            filename = f"reports/{campaign_id}/report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.pdf"
            response = supabase.storage.from_("viva-reports").upload(
                path=filename,
                file=pdf_bytes,
                file_options={"content-type": "application/pdf"},
            )
            # Get public URL
            url_response = supabase.storage.from_("viva-reports").get_public_url(filename)
            url = url_response if isinstance(url_response, str) else url_response.get("publicURL", "")
            logger.info(f"Report uploaded for campaign {campaign_id}: {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to upload report: {e}")
            raise

    @staticmethod
    async def set_report_status(
        campaign_id: uuid.UUID,
        status: str,
        url: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        _report_status[str(campaign_id)] = {
            "status": status,
            "url": url,
            "generated_at": datetime.now(timezone.utc).isoformat() if url else None,
            "error": error,
        }

    @staticmethod
    async def get_report_url(campaign_id: uuid.UUID) -> dict:
        return _report_status.get(str(campaign_id), {"status": "pending"})
