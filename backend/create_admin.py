#!/usr/bin/env python3
"""Cria um usuário admin no banco de dados."""
import psycopg2
import os
from dotenv import load_dotenv
import hashlib
import uuid

load_dotenv()

# Obter DATABASE_URL
db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("❌ DATABASE_URL não encontrada no .env")
    print("\nConfigure o arquivo .env com:")
    print("DATABASE_URL=postgresql://user:password@localhost:5432/viva_db")
    exit(1)

# Converter asyncpg URL para psycopg2
db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')

def hash_password(password: str) -> str:
    """Hash bcrypt-like para a senha."""
    # Usando hashlib para simplificar (em produção use bcrypt)
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        print("\n" + "="*50)
        print("CRIAR ADMIN")
        print("="*50)

        # Obter dados
        nome = input("Nome do admin: ").strip() or "Admin"
        email = input("Email do admin: ").strip() or "admin@example.com"
        password = input("Senha do admin: ").strip() or "admin123"

        # Gerar UUID
        admin_id = str(uuid.uuid4())
        company_id = str(uuid.uuid4())

        # Primeiro, criar uma empresa se não existir
        cursor.execute("SELECT id FROM core.companies LIMIT 1;")
        existing_company = cursor.fetchone()

        if existing_company:
            company_id = str(existing_company[0])
            print(f"✓ Usando empresa existente: {company_id}")
        else:
            # Criar nova empresa
            cursor.execute("""
                INSERT INTO core.companies (id, nome, email, ativo)
                VALUES (%s, %s, %s, true)
            """, (company_id, "Empresa Padrão", "empresa@example.com"))
            print(f"✓ Empresa criada: {company_id}")

        # Hash da senha
        hashed_password = hash_password(password)

        # Inserir usuário admin
        cursor.execute("""
            INSERT INTO core.users (id, company_id, nome, email, hashed_password, role, ativo)
            VALUES (%s, %s, %s, %s, %s, %s, true)
        """, (admin_id, company_id, nome, email, hashed_password, 'ADM'))

        conn.commit()
        cursor.close()
        conn.close()

        print("\n" + "="*50)
        print("✓ ADMIN CRIADO COM SUCESSO!")
        print("="*50)
        print(f"Email: {email}")
        print(f"Senha: {password}")
        print(f"Role: ADM")
        print("\nVocê pode fazer login agora!")
        print("="*50 + "\n")

    except psycopg2.IntegrityError as e:
        print(f"❌ Erro: Email já existe ou outro erro de integridade")
        print(f"Detalhes: {e}")
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        print("\nVerifique:")
        print("1. Se o PostgreSQL está rodando")
        print("2. Se o arquivo .env tem DATABASE_URL correto")
        print("3. Se as credenciais estão corretas")

if __name__ == "__main__":
    main()
