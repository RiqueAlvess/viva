import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_fernet: Optional[Fernet] = None


def get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = settings.ENCRYPTION_KEY
        if isinstance(key, str):
            key = key.encode()
        _fernet = Fernet(key)
    return _fernet


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Returns (raw_token, token_hash)."""
    raw_token = secrets.token_urlsafe(64)
    return raw_token


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_magic_link_token() -> tuple[str, str]:
    """Returns (raw_uuid_token, token_hash)."""
    raw = str(uuid.uuid4())
    hashed = hash_token(raw)
    return raw, hashed


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def encrypt_email(email: str) -> str:
    f = get_fernet()
    return f.encrypt(email.encode()).decode()


def decrypt_email(encrypted: str) -> str:
    f = get_fernet()
    return f.decrypt(encrypted.encode()).decode()


def hash_email_with_salt(email: str, salt: str) -> str:
    """Hash email with campaign salt for collaborator identification."""
    combined = (email.lower().strip() + salt).encode()
    return hashlib.sha256(combined).hexdigest()


def generate_campaign_salt() -> str:
    return secrets.token_hex(32)
