from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

PASSWORD_ALGORITHM = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 600_000
PASSWORD_SALT_BYTES = 16
SESSION_TOKEN_BYTES = 32
PASSWORD_MIN_LENGTH = 3
PASSWORD_MAX_LENGTH = 256

def hash_password(password: str) -> str:
    validate_password(password)
    salt = secrets.token_bytes(PASSWORD_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )
    return "$".join(
        (
            PASSWORD_ALGORITHM,
            str(PASSWORD_ITERATIONS),
            _encode(salt),
            _encode(digest),
        )
    )

def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, expected_text = encoded_hash.split("$", 3)
        if algorithm != PASSWORD_ALGORITHM:
            return False
        iterations = int(iterations_text)
        if iterations <= 0:
            return False
        salt = _decode(salt_text)
        expected = _decode(expected_text)
    except (ValueError, TypeError):
        return False

    actual = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(actual, expected)

def create_session_token() -> str:
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)

def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def validate_password(password: str) -> None:
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"Mật khẩu phải có ít nhất {PASSWORD_MIN_LENGTH} ký tự.")
    if len(password) > PASSWORD_MAX_LENGTH:
        raise ValueError(f"Mật khẩu không được vượt quá {PASSWORD_MAX_LENGTH} ký tự.")

def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")

def _decode(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"), altchars=b"-_", validate=True)