from fastapi import Response, Request
from .security import encrypt_data, decrypt_data
from settings import settings

async def set_session_cookie(
    response: Response,
    session_token: str,
    expires_at: str
) -> None:
    """
    Sets the encrypted session cookie.

    Args:
        response: The FastAPI Response object.
        session_token: The session token to encrypt and store.
        expires_at: The expiration date of the cookie.
    """
    encrypted_session_token = encrypt_data(session_token, settings.fernet_key)
    response.set_cookie(
        key="sessionId",
        value=encrypted_session_token,
        httponly=True,
        secure=settings.environment == 'production',  # Only secure in production
        samesite='lax',  # Recommended for CSRF protection
        max_age=24 * 60 * 60,  # 24 hours in seconds
        expires=expires_at,  # Explicitly set expiration time
        path="/",  # Ensure cookie is available for all paths
        domain=None  # Let browser set domain automatically
    )

async def get_session_from_cookie(request: Request) -> str | None:
    """
    Gets and decrypts the session cookie from the request.

    Args:
        request: The FastAPI Request object.

    Returns:
        The decrypted session token, or None if the cookie doesn't exist or decryption fails.
    """
    encrypted_session_id = request.cookies.get("sessionId")
    if not encrypted_session_id:
        return None
    
    try:
        return decrypt_data(encrypted_session_id, settings.fernet_key)
    except Exception:
        return None