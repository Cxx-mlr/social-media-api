from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings

from tests.utils.auth import BearerAuth

def test_get_access_token(client: TestClient):
    login__response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": settings.FIRST_USER_EMAIL,
            "password": settings.FIRST_USER_PASSWORD
        }
    )

    assert login__response.status_code == status.HTTP_200_OK
    token_json = login__response.json()
    assert token_json.get("access_token") is not None

def test_get_access_token_incorrect_password(client: TestClient):
    login__response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": settings.FIRST_USER_EMAIL,
            "password": "incorrect"
        }
    )

    assert login__response.status_code == status.HTTP_400_BAD_REQUEST

def test_use_access_token(client: TestClient, first_user_auth: BearerAuth):
    test_token__response = client.post(f"{settings.API_V1_STR}/login/test-token", auth=first_user_auth)

    assert test_token__response.status_code == status.HTTP_200_OK

def test_use_access_token_invalid_token(client: TestClient, first_user_auth: BearerAuth, monkeypatch):
    monkeypatch.setattr(first_user_auth, "token", "invalid")
    test_access_token__response = client.post(f"{settings.API_V1_STR}/login/test-token", auth=first_user_auth)

    assert test_access_token__response.status_code == status.HTTP_401_UNAUTHORIZED