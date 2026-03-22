from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional


class ReportGenerateRequest(BaseModel):
    campaign_id: uuid.UUID


class ReportResponse(BaseModel):
    task_id: str
    campaign_id: uuid.UUID
    message: str
    status: str = "queued"
