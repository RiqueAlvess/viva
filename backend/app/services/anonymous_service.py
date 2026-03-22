"""
Anonymous session management via Redis.
session_uuid -> {campaign_id, unit_id, sector_id, used: bool}
TTL: 48 hours
"""
import json
import uuid
import logging
from typing import Optional
import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

SESSION_PREFIX = "session:"
SESSION_TTL = 48 * 3600  # 48 hours in seconds


def _get_redis_client() -> aioredis.Redis:
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


class AnonymousSessionService:
    @staticmethod
    async def create_session(
        campaign_id: uuid.UUID,
        unit_id: uuid.UUID,
        sector_id: uuid.UUID,
    ) -> uuid.UUID:
        session_uuid = uuid.uuid4()
        session_data = {
            "campaign_id": str(campaign_id),
            "unit_id": str(unit_id),
            "sector_id": str(sector_id),
            "used": False,
        }
        key = f"{SESSION_PREFIX}{session_uuid}"
        async with _get_redis_client() as redis:
            await redis.setex(key, SESSION_TTL, json.dumps(session_data))
        logger.info(f"Created anonymous session {session_uuid}")
        return session_uuid

    @staticmethod
    async def get_session(session_uuid: uuid.UUID) -> Optional[dict]:
        key = f"{SESSION_PREFIX}{session_uuid}"
        async with _get_redis_client() as redis:
            data = await redis.get(key)
        if not data:
            return None
        return json.loads(data)

    @staticmethod
    async def mark_session_used(session_uuid: uuid.UUID) -> bool:
        key = f"{SESSION_PREFIX}{session_uuid}"
        async with _get_redis_client() as redis:
            data = await redis.get(key)
            if not data:
                return False
            session = json.loads(data)
            if session.get("used"):
                return False
            session["used"] = True
            await redis.setex(key, SESSION_TTL, json.dumps(session))
        return True

    @staticmethod
    async def is_session_valid(session_uuid: uuid.UUID) -> bool:
        session = await AnonymousSessionService.get_session(session_uuid)
        if not session:
            return False
        return not session.get("used", True)
