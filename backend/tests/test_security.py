from app.core.security import hash_password, verify_password, create_access_token, decode_access_token


def test_password_hash_and_verify():
    hashed = hash_password("MySecurePass123")
    assert hashed != "MySecurePass123"
    assert verify_password("MySecurePass123", hashed)
    assert not verify_password("WrongPassword", hashed)


def test_jwt_roundtrip():
    token = create_access_token(subject="user-123")
    subject = decode_access_token(token)
    assert subject == "user-123"


def test_jwt_invalid_token_returns_none():
    assert decode_access_token("not-a-real-token") is None
