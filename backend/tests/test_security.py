import pytest
from datetime import timedelta
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)
from app.core.errors import AuthenticationError


def test_password_hashing_and_verification():
    plain = "SuperSecurePassword123!"
    hashed = get_password_hash(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_access_token_creation_and_decoding():
    sub = "user-12345"
    token = create_access_token(subject=sub, role="candidate")
    payload = decode_token(token)

    assert payload["sub"] == sub
    assert payload["role"] == "candidate"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_refresh_token_creation():
    sub = "user-67890"
    token = create_refresh_token(subject=sub)
    payload = decode_token(token)

    assert payload["sub"] == sub
    assert payload["type"] == "refresh"


def test_invalid_token_decoding():
    with pytest.raises(AuthenticationError):
        decode_token("completely.invalid.token")


def test_token_hash_deterministic():
    token = "some-long-random-jwt-string"
    h1 = hash_token(token)
    h2 = hash_token(token)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex length
