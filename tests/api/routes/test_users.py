from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings
from tests.utils.auth import BearerAuth 
from tests.utils.utils import random_email, random_password

from app.models import UserRegister, UserPublic

def test_read_users(client: TestClient):
    read_users__response = client.get(f"{settings.API_V1_STR}/users")

    assert read_users__response.status_code == status.HTTP_200_OK

def test_read_users_me(client: TestClient, first_user_auth: BearerAuth):
    read_users_me__response = client.get(f"{settings.API_V1_STR}/users/me", auth=first_user_auth)

    assert read_users_me__response.status_code == status.HTTP_200_OK

def test_read_users_me_unauthorized(client: TestClient, first_user_auth: BearerAuth):
    first_user_auth.token = "invalid"
    read_users_me__response = client.get(f"{settings.API_V1_STR}/users/me", auth=first_user_auth)

    assert read_users_me__response.status_code == status.HTTP_401_UNAUTHORIZED

def test_register_new_user(client: TestClient):
    email = random_email()
    password = random_password()

    user_register = UserRegister(email=email, password=password)

    signup_response = client.post(
        f"{settings.API_V1_STR}/users/signup",
        json=user_register.model_dump()
    )

    assert signup_response.status_code == status.HTTP_201_CREATED

def test_register_existent_user(client: TestClient):
    user_register = UserRegister(email=settings.FIRST_USER_EMAIL, password=settings.FIRST_USER_PASSWORD)

    signup_response = client.post(
        f"{settings.API_V1_STR}/users/signup",
        json=user_register.model_dump()
    )

    assert signup_response.status_code == status.HTTP_400_BAD_REQUEST

def test_read_user_by_id(client: TestClient):
    read_users__response = client.get(f"{settings.API_V1_STR}/users")
    assert read_users__response.status_code == status.HTTP_200_OK

    users = [UserPublic.model_validate(user) for user in read_users__response.json()]

    assert users

    for user in users:
        read_user_by_id__response = client.get(f"{settings.API_V1_STR}/users/{user.id}")
        assert read_user_by_id__response.status_code == status.HTTP_200_OK

        user_by_id = UserPublic.model_validate(read_user_by_id__response.json())

        assert user.id == user_by_id.id