import logging
import asyncio
import uuid
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.workers.tasks.report_tasks.generate_report_task",
    bind=True,
    max_retries=2,
    default_retry_delay=60,
)
def generate_report_task(self, campaign_id: str):
    """Generate PDF report for a campaign and upload to storage."""
    try:
        asyncio.run(_generate_report(campaign_id))
    except Exception as exc:
        logger.error(f"Report task failed for campaign {campaign_id}: {exc}")
        raise self.retry(exc=exc)


async def _generate_report(campaign_id: str):
    from app.database import AsyncSessionLocal
    from app.services.dashboard_service import DashboardService
    from app.services.report_service import ReportService
    from app.services.storage_service import StorageService

    cid = uuid.UUID(campaign_id)
    await StorageService.set_report_status(cid, "processing")

    try:
        async with AsyncSessionLocal() as db:
            service = DashboardService(db)
            dashboard = await service.get_dashboard(cid)

        # Convert dashboard to dict for report generation
        dashboard_dict = dashboard.model_dump()

        report_service = ReportService(dashboard_dict)
        pdf_bytes = report_service.generate_pdf()

        url = await StorageService.upload_report(cid, pdf_bytes)
        await StorageService.set_report_status(cid, "ready", url=url)
        logger.info(f"Report generated for campaign {campaign_id}: {url}")

    except Exception as e:
        logger.error(f"Failed to generate report for {campaign_id}: {e}")
        await StorageService.set_report_status(cid, "error", error=str(e))
        raise
