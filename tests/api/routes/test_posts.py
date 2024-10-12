from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings
from tests.utils.auth import BearerAuth

from app.models import PostCreate, PostPublic, PostUpdate

from tests.utils.auth import BearerAuth
from tests.utils.utils import random_title, random_content

def test_create_post(client: TestClient, first_user_auth: BearerAuth):
    post_create = PostCreate(title=random_title(), content=random_content())
    create_post__response = client.post(f"{settings.API_V1_STR}/posts", auth=first_user_auth, json=post_create.model_dump())

    assert create_post__response.status_code == status.HTTP_201_CREATED
    post = PostPublic.model_validate(create_post__response.json())

    assert post.title == post_create.title
    assert post.content == post_create.content

def test_create_post_unauthorized(client: TestClient, first_user_auth: BearerAuth, monkeypatch):
    monkeypatch.setattr(first_user_auth, "token", "invalid")

    post_create = PostCreate(title=random_title(), content=random_content())
    create_post__response = client.post(f"{settings.API_V1_STR}/posts", auth=first_user_auth, json=post_create.model_dump())

    assert create_post__response.status_code == status.HTTP_401_UNAUTHORIZED

def test_read_posts(client: TestClient):
    read_posts__response = client.get(f"{settings.API_V1_STR}/posts")
    assert read_posts__response.status_code == status.HTTP_200_OK

    posts = [PostPublic.model_validate(post) for post in read_posts__response.json()]

    assert posts

def test_read_posts_me(client: TestClient, first_user_auth: BearerAuth):
    read_posts_me__response = client.get(f"{settings.API_V1_STR}/posts/me", auth=first_user_auth)
    assert read_posts_me__response.status_code == status.HTTP_200_OK

def test_read_posts_me_unauthorized(client: TestClient, first_user_auth: BearerAuth, monkeypatch):
    monkeypatch.setattr(first_user_auth, "token", "invalid")

    read_posts_me__response = client.get(f"{settings.API_V1_STR}/posts/me", auth=first_user_auth)
    assert read_posts_me__response.status_code == status.HTTP_401_UNAUTHORIZED

def test_read_latest_post(client: TestClient):
    read_latest_posts__response = client.get(f"{settings.API_V1_STR}/posts/latest")
    assert read_latest_posts__response.status_code == status.HTTP_200_OK

    latest_post = PostPublic.model_validate(read_latest_posts__response.json())
    assert latest_post.id

def test_read_latest_post_me(client: TestClient, first_user_auth: BearerAuth):
    read_latest_posts__response = client.get(f"{settings.API_V1_STR}/posts/latest", auth=first_user_auth)
    assert read_latest_posts__response.status_code == status.HTTP_200_OK

    latest_post = PostPublic.model_validate(read_latest_posts__response.json())
    assert latest_post.id

def test_read_latest_post_me_unauthorized(client: TestClient, first_user_auth: BearerAuth, monkeypatch):
    monkeypatch.setattr(first_user_auth, "token", "invalid")

    read_latest_posts__response = client.get(f"{settings.API_V1_STR}/posts/me/latest", auth=first_user_auth)
    assert read_latest_posts__response.status_code == status.HTTP_401_UNAUTHORIZED

def test_read_post_by_id(client: TestClient):
    read_latest_posts__response = client.get(f"{settings.API_V1_STR}/posts/latest")
    post = PostPublic.model_validate(read_latest_posts__response.json())

    read_post_by_id__response = client.get(f"{settings.API_V1_STR}/posts/{post.id}")
    assert read_post_by_id__response.status_code == status.HTTP_200_OK

    post_by_id = PostPublic.model_validate(read_post_by_id__response.json())

    assert post.id == post_by_id.id
    assert post.title == post_by_id.title
    assert post.content == post_by_id.content

def test_update_post_by_id(client: TestClient, first_user_auth: BearerAuth):
    read_latest_posts__response = client.get(f"{settings.API_V1_STR}/posts/latest")
    post = PostPublic.model_validate(read_latest_posts__response.json())

    new_title = random_title()
    new_content = random_content()

    post_update = PostUpdate(title=new_title, content=new_content)

    update_post_by_id__response = client.put(
        f"{settings.API_V1_STR}/posts/{post.id}",
        auth=first_user_auth,
        json=post_update.model_dump()
    )
    assert update_post_by_id__response.status_code == status.HTTP_200_OK

    post_by_id = PostPublic.model_validate(update_post_by_id__response.json())

    assert post.id == post_by_id.id
    assert post.title != post_by_id.title
    assert post.content != post_by_id.content

def test_update_post_by_id_unauthorized(client: TestClient, first_user_auth: BearerAuth, monkeypatch):
    monkeypatch.setattr(first_user_auth, "token", "invalid")

    read_latest_posts__response = client.get(f"{settings.API_V1_STR}/posts/latest")
    post = PostPublic.model_validate(read_latest_posts__response.json())

    new_title = random_title()
    new_content = random_content()

    post_update = PostUpdate(title=new_title, content=new_content)

    update_post_by_id__response = client.put(
        f"{settings.API_V1_STR}/posts/{post.id}",
        auth=first_user_auth,
        json=post_update.model_dump()
    )
    assert update_post_by_id__response.status_code == status.HTTP_401_UNAUTHORIZED

def test_delete_post_by_id(client: TestClient, first_user_auth: BearerAuth, monkeypatch):
    read_latest_posts__response = client.get(f"{settings.API_V1_STR}/posts/latest")
    post = PostPublic.model_validate(read_latest_posts__response.json())

    delete_post_by_id__response = client.delete(f"{settings.API_V1_STR}/posts/{post.id}", auth=first_user_auth)
    assert delete_post_by_id__response.status_code == status.HTTP_200_OK

    deleted_post_by_id = PostPublic.model_validate(delete_post_by_id__response.json())

    assert post.id == deleted_post_by_id.id
    assert post.title == deleted_post_by_id.title
    assert post.content == deleted_post_by_id.content

def test_delete_post_by_id_unauthorized(client: TestClient, first_user_auth: BearerAuth, monkeypatch):
    monkeypatch.setattr(first_user_auth, "token", "invalid")

    read_latest_posts__response = client.get(f"{settings.API_V1_STR}/posts/latest")
    post = PostPublic.model_validate(read_latest_posts__response.json())

    delete_post_by_id__response = client.delete(f"{settings.API_V1_STR}/posts/{post.id}", auth=first_user_auth)
    assert delete_post_by_id__response.status_code == status.HTTP_401_UNAUTHORIZED

def test_delete_posts_me(client: TestClient, first_user_auth: BearerAuth, ensure_first_user_posts_exists):
    delete_posts_me__response = client.delete(f"{settings.API_V1_STR}/posts", auth=first_user_auth)
    assert delete_posts_me__response.status_code == status.HTTP_200_OK

def test_delete_posts_me_unauthorized(client: TestClient, first_user_auth: BearerAuth, monkeypatch, ensure_first_user_posts_exists):
    monkeypatch.setattr(first_user_auth, "token", "invalid")

    read_latest_posts__response = client.get(f"{settings.API_V1_STR}/posts/latest")
    post = PostPublic.model_validate(read_latest_posts__response.json())

    delete_posts_me__response = client.delete(f"{settings.API_V1_STR}/posts/", auth=first_user_auth)
    assert delete_posts_me__response.status_code == status.HTTP_401_UNAUTHORIZED