#pytest -s tests/test_votes.py
from fastapi import status
import pytest
from app.models import Vote

@pytest.fixture
def test_vote(test_posts, test_user, session):
    result = session.execute(
        query="""INSERT INTO votes (post_id, user_id) VALUES (%s, %s) RETURNING *;""",
        params=[test_posts[0]["post_id"], test_user["user_id"]]
    ).fetchone()
    session.commit()

    return Vote(**result)


@pytest.fixture
def test_vote2(authorized_client, test_posts):
    response = authorized_client.post("/vote/", json={"post_id": test_posts[0]["post_id"], "dir":1})
    return Vote(**response.json())

def test_vote_on_post(authorized_client, test_posts):
    response = authorized_client.post("/vote/", json={"post_id": test_posts[0]["post_id"], "dir":1})
    assert response.status_code == status.HTTP_201_CREATED
    response = authorized_client.post("/vote/", json={"post_id": test_posts[1]["post_id"], "dir":1})
    assert response.status_code == status.HTTP_201_CREATED
    response = authorized_client.post("/vote/", json={"post_id": test_posts[2]["post_id"], "dir":1})
    assert response.status_code == status.HTTP_201_CREATED

def test_vote_twice_post(authorized_client, test_vote2):
    response = authorized_client.post("/vote/", json={"post_id": test_vote2.post_id, "dir":1})
    assert response.status_code == status.HTTP_409_CONFLICT

def test_delete_vote(authorized_client, test_posts, test_vote2):
    response = authorized_client.post("/vote/", json={"post_id": test_vote2.post_id, "dir":0})
    assert response.status_code == status.HTTP_201_CREATED

def test_delete_post_non_exist(authorized_client, test_posts):
    response = authorized_client.post("/vote/", json={"post_id": -1, "dir":0})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_vote_post_non_exist(authorized_client, test_posts):
    response = authorized_client.post("/vote/", json={"post_id": -1, "dir":1})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_vote_unauthorized_user(client, token, test_vote):
    client.headers.update({"Authorization": f"Bearer {token}"})
    response = client.post("/vote/", json={"post_id": test_vote.post_id, "dir": 0})
    assert response.status_code == status.HTTP_201_CREATED