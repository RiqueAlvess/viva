#!/bin/bash
# Script para criar usuário ADM

cd "$(dirname "$0")"

# Ativa o venv se existir (tenta locais comuns)
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "../venv/bin/activate" ]; then
    source ../venv/bin/activate
fi

python3 << 'EOF'
import asyncio
import uuid
import sys
import os

# Garante que app está no path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

async def create_admin():
    from app.core.config import settings
    from app.models.company import Company
    from app.models.user import User
    from app.core.security import hash_password

    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        # Criar ou obter empresa padrão
        result = await session.execute(select(Company).limit(1))
        company = result.scalar_one_or_none()

        if not company:
            company = Company(
                nome="Empresa Test",
                cnpj="00000000000000",
                ativo=True
            )
            session.add(company)
            await session.flush()
            print(f"✓ Empresa criada: {company.nome}")
        else:
            print(f"✓ Usando empresa existente: {company.nome}")

        # Verificar se usuário já existe
        result = await session.execute(select(User).where(User.email == "admin@admin.com"))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"✓ Usuário admin@admin.com já existe (ID: {existing.id})")
            await session.close()
            await engine.dispose()
            return

        # Criar usuário ADM
        user = User(
            company_id=company.id,
            nome="Admin",
            email="admin@admin.com",
            hashed_password=hash_password("admin"),
            role="ADM",
            ativo=True
        )
        session.add(user)
        await session.commit()
        print(f"✓ Usuário ADM criado: admin@admin.com (ID: {user.id})")
        print(f"✓ Senha: admin")

asyncio.run(create_admin())
EOF
