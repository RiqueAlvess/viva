import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, RefreshToken
from app.core.security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, hash_token
)
from app.core.config import settings
from app.core.exceptions import UnauthorizedError


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(self, email: str, password: str) -> User:
        result = await self.db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not user.ativo:
            raise UnauthorizedError("User account is deactivated")
        return user

    async def create_tokens(self, user: User) -> tuple[str, str]:
        """Returns (access_token, raw_refresh_token)."""
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role, "company_id": str(user.company_id)}
        )
        raw_refresh = create_refresh_token(data={"sub": str(user.id)})
        token_hash = hash_token(raw_refresh)

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked=False,
        )
        self.db.add(refresh_record)
        await self.db.flush()
        return access_token, raw_refresh

    async def refresh_tokens(self, raw_refresh_token: str) -> tuple[str, str]:
        token_hash = hash_token(raw_refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise UnauthorizedError("Invalid or expired refresh token")

        # Revoke old token
        record.revoked = True
        await self.db.flush()

        # Load user
        user_result = await self.db.execute(
            select(User).where(User.id == record.user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user or not user.ativo:
            raise UnauthorizedError("User not found or inactive")

        return await self.create_tokens(user)

    async def revoke_refresh_token(self, raw_refresh_token: str) -> None:
        token_hash = hash_token(raw_refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        record = result.scalar_one_or_none()
        if record:
            record.revoked = True
            await self.db.flush()

    async def create_user(
        self,
        company_id: uuid.UUID,
        nome: str,
        email: str,
        password: str,
        role: str,
        sector_id: uuid.UUID | None = None,
    ) -> User:
        hashed = hash_password(password)
        user = User(
            company_id=company_id,
            nome=nome,
            email=email.lower().strip(),
            hashed_password=hashed,
            role=role,
            sector_id=sector_id,
        )
        self.db.add(user)
        await self.db.flush()
        return user
