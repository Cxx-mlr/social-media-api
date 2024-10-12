import pytest

from fastapi import status
from fastapi.testclient import TestClient

from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.api.deps import get_db
from app.core.config import settings
from app.models import PostCreate, PostPublic, UserPublic

from typing_extensions import Generator

from app.core.db import init_db

from tests.utils.auth import BearerAuth
from tests.utils.utils import random_title, random_content

@pytest.fixture(name="session", scope="session", autouse=True)
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    from app.models import User, Post, Vote

    with Session(engine) as session:
        init_db(session, engine=engine)
        yield session

@pytest.fixture(name="client", scope="module")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = lambda: session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(scope="module")
def first_user_auth(client: TestClient):
    response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": settings.FIRST_USER_EMAIL,
            "password": settings.FIRST_USER_PASSWORD
        }
    )

    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    access_token = response_json["access_token"]

    return BearerAuth(token=access_token)

@pytest.fixture(scope="function")
def ensure_first_user_posts_exists(client: TestClient, first_user_auth: BearerAuth):
    read_posts_me__response = client.get(f"{settings.API_V1_STR}/posts/me", auth=first_user_auth)
    assert read_posts_me__response.status_code == status.HTTP_200_OK

    posts = [PostPublic.model_validate(post) for post in read_posts_me__response.json()]

    if posts:
        return

    for _ in range(3):
        post_create = PostCreate(title=random_title(), content=random_content())

        create_post__response = client.post(
            f"{settings.API_V1_STR}/posts", json=post_create.model_dump(), auth=first_user_auth
        )

        assert create_post__response.status_code == status.HTTP_201_CREATED

@pytest.fixture(scope="function")
def ensure_first_user_posts_does_not_exists(client: TestClient, first_user_auth: BearerAuth):
    read_posts__response = client.get(f"{settings.API_V1_STR}/posts")
    assert read_posts__response.status_code == status.HTTP_200_OK

    posts = [PostPublic.model_validate(post) for post in read_posts__response.json()]

    if not posts:
        return

    read_posts_me__response = client.get(f"{settings.API_V1_STR}/posts/me", auth=first_user_auth)
    assert read_posts_me__response.status_code == status.HTTP_200_OK

    posts = [PostPublic.model_validate(post) for post in read_posts_me__response.json()]

    for post in posts:
        delete_post_by_id__response = client.delete(f"{settings.API_V1_STR}/posts/{post.id}", auth=first_user_auth)
        assert delete_post_by_id__response.status_code == status.HTTP_200_OK