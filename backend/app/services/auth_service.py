import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
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

    async def create_access_token_for_user(self, user: User) -> str:
        return create_access_token(
            data={"sub": str(user.id), "role": user.role, "company_id": str(user.company_id)}
        )

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
