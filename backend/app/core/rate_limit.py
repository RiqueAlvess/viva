from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)


def get_login_key(request: Request) -> str:
    """Key combines IP + email for login rate limiting."""
    ip = get_remote_address(request)
    body = None
    # Try to get email from body (will be populated in middleware)
    email = getattr(request.state, "login_email", "")
    return f"{ip}:{email}"
