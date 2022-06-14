#pytest -s tests/test_posts.py
from fastapi import status
from app.schemas import PostOut
import pytest
from pydantic import ValidationError

def test_get_posts(authorized_client, test_posts):
    response = authorized_client.get("/posts/")
    assert response.status_code == status.HTTP_200_OK
    assert len(test_posts) == len(response.json())

def test_unauthorized_user_get_posts(client, test_posts):
    response = client.get("/posts/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_unauthorized_user_get_one_post(client, test_posts):
    response = client.get(f"""/posts/{test_posts[0]["post_id"]}""")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_authorized_user_get_one_post(authorized_client, test_posts):
    response = authorized_client.get(f"""/posts/{test_posts[0]["post_id"]}""")
    assert response.status_code == status.HTTP_200_OK
    post = PostOut(**response.json())
    assert post.post_id == test_posts[0]["post_id"]

def test_get_post_not_exist(authorized_client, test_posts):
    response = authorized_client.get(f"""/posts/{-1}""")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.parametrize(
    argnames="title, content, status_code",
    argvalues=[
        ("sky", "i like blue", status.HTTP_201_CREATED),
        (None, "i like blue", 0),
        ("sky", None, 0),
    ]
)
def test_create_new_post(authorized_client, test_user, test_posts, title: str, content: str, status_code: int):
    def impl():
        response = authorized_client.post("/posts/", json={
            "title": title,
            "content": content,
            "owner_id": test_user["user_id"]
        })

        assert response.status_code == status_code
    
    if None in [title, content]:
        with pytest.raises(expected_exception=ValidationError):
            impl()
    else:
        impl()

def test_delete_post(authorized_client, test_posts):
    response = authorized_client.delete(f"""/posts/{test_posts[0]["post_id"]}""")
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_create_post_unauthorized_client(client, test_posts, token, test_user):
    client.headers.update({"Authorization": f"Bearer {token}"})
    response = client.post("/posts/", json={"title": "new title", "content": "new content", "owner_id": test_user["user_id"]})
    assert response.status_code == status.HTTP_201_CREATED

def test_delete_post_non_exist(authorized_client, test_posts):
    response = authorized_client.delete(f"""/posts/{-1}""")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_other_user_post(authorized_client, test_user, test_posts, test_user2):
    response = authorized_client.delete(f"""/posts/{test_posts[3]["post_id"]}""")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_post(authorized_client, test_posts):
    response = authorized_client.put(f"""/posts/{test_posts[0]["post_id"]}""", json={"title": "content updated", "content": "content updated"})
    assert response.status_code == status.HTTP_200_OK
    