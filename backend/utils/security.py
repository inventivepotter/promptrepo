from cryptography.fernet import Fernet
import base64
import os

def _ensure_fernet_key(key: str) -> bytes:
    """Ensure the key is a valid 32-byte URL-safe base64-encoded string."""
    try:
        # Try to decode the key as base64
        decoded_key = base64.urlsafe_b64decode(key)
        if len(decoded_key) != 32:
            # If it's not 32 bytes, hash it or raise an error
            # For simplicity, we'll hash it to make it 32 bytes
            import hashlib
            hashed_key = hashlib.sha256(key.encode()).digest()
            return base64.urlsafe_b64encode(hashed_key)
        return key.encode()
    except Exception:
        # If decoding fails, hash the key to make it valid
        import hashlib
        hashed_key = hashlib.sha256(key.encode()).digest()
        return base64.urlsafe_b64encode(hashed_key)

def encrypt_data(data: str, secret_key: str) -> str:
    """
    Encrypts the given data using Fernet symmetric encryption.

    Args:
        data: The string data to encrypt.
        secret_key: The secret key for encryption.

    Returns:
        The encrypted string, URL-safe base64-encoded.
    """
    fernet_key = _ensure_fernet_key(secret_key)
    f = Fernet(fernet_key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt_data(encrypted_data: str, secret_key: str) -> str | None:
    """
    Decrypts the given encrypted data using Fernet symmetric encryption.

    Args:
        encrypted_data: The encrypted string to decrypt.
        secret_key: The secret key for decryption.

    Returns:
        The original decrypted string, or None if decryption fails.
    """
    try:
        fernet_key = _ensure_fernet_key(secret_key)
        f = Fernet(fernet_key)
        decrypted_data = f.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except Exception:
        # Handle decryption errors gracefully (e.g., invalid token, wrong key)
        return None