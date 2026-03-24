#!/usr/bin/env python3
"""Script para criar usuário ADM de teste"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.models import Company, User
from app.core.security import hash_password

async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        # Criar ou obter empresa padrão
        from sqlalchemy import select
        result = await session.execute(select(Company).limit(1))
        company = result.scalar_one_or_none()

        if not company:
            company = Company(
                id=uuid.uuid4(),
                nome="Empresa Test",
                cnpj="00000000000000",
                ativo=True
            )
            session.add(company)
            await session.flush()
            print(f"✓ Empresa criada: {company.nome}")
        else:
            print(f"✓ Usando empresa existente: {company.nome}")

        # Criar usuário ADM
        user = User(
            id=uuid.uuid4(),
            company_id=company.id,
            nome="Admin",
            email="admin@admin.com",
            hashed_password=hash_password("admin"),
            role="ADM",
            ativo=True
        )
        session.add(user)
        await session.commit()
        print(f"✓ Usuário ADM criado: {user.email}")

if __name__ == "__main__":
    asyncio.run(seed())
