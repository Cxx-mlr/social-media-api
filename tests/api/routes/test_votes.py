from fastapi import status
from fastapi.testclient import TestClient

from sqlmodel import Session

from app.core.config import settings
from tests.utils.auth import BearerAuth

def test_upvote_post(client: TestClient, first_user_auth: BearerAuth):
    pass

def test_upvote_post_unauthorized(client: TestClient, first_user_auth: BearerAuth):
    pass

def test_upvote_post_me(client: TestClient, first_user_auth: BearerAuth):
    pass

def test_upvote_post_me_unauthorized(client: TestClient, first_user_auth: BearerAuth):
    pass

def test_downvote_post(client: TestClient, first_user_auth: BearerAuth):
    pass

def test_downvote_post_unauthorized(client: TestClient, first_user_auth: BearerAuth):
    pass

def test_downvote_post_me(client: TestClient, first_user_auth: BearerAuth):
    pass

def test_downvote_post_me_unauthorized(client: TestClient, first_user_auth: BearerAuth):
    pass