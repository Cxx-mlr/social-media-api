#pytest -x -s -v tests/test_users.py
#pytest -x -s tests/test_users.py
#pytest -s tests/test_users.py
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
import pytest

import psycopg
from psycopg.rows import dict_row
import time
from app.oauth2 import create_access_token
from app.schemas import Token
from app.config import settings

def get_test_db():
    try:
        testconn = psycopg.connect(
            host=settings.DB_HOST,
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            port=settings.DB_PORT,
            row_factory=dict_row
        )
    except Exception as e:
        raise Exception('Connecting to database failed...\nerror: {}'.format(str(e)))
    else:
        print('TEST Database connection was succesfull!!')
        return testconn

@pytest.fixture
def session():
    testconn = get_test_db()
    testconn.execute(query='DELETE FROM users;')
    testconn.commit()
    try:
        yield testconn
    finally:
        testconn.close()

@pytest.fixture
def client(session):
    app.dependency_overrides[get_db] = lambda: session
    yield TestClient(app)

@pytest.fixture
def test_user(client):
    user_data = {"email": "Usuario1@gmail.com", "password": "secret1"}
    response = client.post('/users/', json=user_data)
    response_json = response.json()
    response_json.update({"password": user_data["password"]})
    return response_json

@pytest.fixture
def test_user2(client):
    user_data = {"email": "Usuario123@gmail.com", "password": "secret1"}
    response = client.post('/users/', json=user_data)
    response_json = response.json()
    response_json.update({"password": user_data["password"]})
    return response_json

@pytest.fixture
def token(test_user):
    access_token = create_access_token(data={"user_id": test_user["user_id"]})
    return access_token

@pytest.fixture
def authorized_client(client, token):
    client.headers["Authorization"] = f"Bearer {token}"
    return client

@pytest.fixture
def test_posts(test_user, test_user2, session):
    posts_data = [
        {"title": "ants", "content": "small and curious", "owner_id": test_user["user_id"]},
        {"title": "flowers", "content": "beautiful nature", "owner_id": test_user["user_id"]},
        {"title": "chocolate ice cream", "content": "is my favorite", "owner_id": test_user["user_id"]},
        {"title": "a new post", "content": "the content is ...", "owner_id": test_user2["user_id"]},
    ]

    posts_result = []

    for p in posts_data:
        created_post = session.execute(
            query="""INSERT INTO posts (title, content, owner_id) VALUES (%s, %s, %s) RETURNING *;""",
            params=[p.get("title"), p.get("content"), p.get("owner_id")]
        ).fetchone()

        posts_result.append(created_post)
    session.commit()
    return posts_result