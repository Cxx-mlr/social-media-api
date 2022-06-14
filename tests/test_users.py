#pytest -x -s -v tests/test_users.py
from app.schemas import UserOut, Token
import pytest
from app.oauth2 import get_payload
from fastapi import status

def test_root(client):
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'Hello World'}

@pytest.mark.parametrize(
    argnames='email, password, status_code',
    argvalues=[
        ('Usuario1@gmail.com', "secret1", status.HTTP_201_CREATED),
        ('Usuario2@gmail.com', "secret2", status.HTTP_201_CREATED),
    ]
)
def test_add_user(client, email: str, password: str, status_code: int):
    response = client.post('/users/', json={"email": email, "password": password})
    
    new_user = UserOut(**response.json())

    assert new_user.email == email
    assert response.status_code == status_code

@pytest.mark.parametrize(
    argnames="email, password, status_code",
    argvalues=[
        ("Usuario1@gmail.com", "secret1", status.HTTP_200_OK)
    ]
)
def test_login_user(test_user, client, email: str, password: str, status_code: int):
    response = client.post('/login', data={"username": test_user["email"], "password": test_user["password"]})
    assert response.status_code == status_code

    token = Token(**response.json())
    payload = get_payload(token=token.access_token)
    assert payload["user_id"] == test_user["user_id"]
    assert token.token_type == "bearer"

@pytest.mark.parametrize(
    argnames="email, password, status_code",
    argvalues=[
        ("XY@gmail.com", "wrongPassword", status.HTTP_401_UNAUTHORIZED),
        (None, "wrongPassword", status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("wrongEmail@gmail.com", None, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("wrongEmail", None, status.HTTP_422_UNPROCESSABLE_ENTITY)
    ]
)
def test_incorrect_login(test_user, client, email, password, status_code):
    response = client.post("/login", data={"username": email, "password": password})
    assert response.status_code == status_code