import os
import json
import hmac
import hashlib
import base64
import time
import secrets
from typing import Optional, Dict, Any

# Secret key for token signing (override via environment in production)
SECRET_KEY = os.getenv("SECRET_KEY", "hortisentry-super-secret-production-grade-key-2026")
TOKEN_EXPIRE_SECONDS = 86400 * 7 # 7 days validity

def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with a unique random 16-byte salt.
    Format: salt$hash
    """
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a stored PBKDF2-HMAC-SHA256 hash.
    """
    if not hashed_password or "$" not in hashed_password:
        return False
    try:
        salt, key_hex = hashed_password.split("$", 1)
        computed_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return hmac.compare_digest(computed_key.hex(), key_hex)
    except Exception:
        return False

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64url_decode(s: str) -> bytes:
    padding = 4 - (len(s) % 4)
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
    """
    Generates an RFC 7519 compliant HMAC-SHA256 JWT access token.
    """
    payload = data.copy()
    now = int(time.time())
    payload["iat"] = now
    payload["exp"] = now + (expires_delta if expires_delta is not None else TOKEN_EXPIRE_SECONDS)

    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validates and decodes an HMAC-SHA256 JWT access token. Returns payload or None if invalid/expired.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _b64url_decode(signature_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload_bytes = _b64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Verify expiration
        if "exp" in payload and payload["exp"] < int(time.time()):
            return None

        return payload
    except Exception:
        return None
