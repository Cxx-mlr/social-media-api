from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from tests.utils.utils import random_email, random_password

from app.models import UserCreate, User
from app import crud

def test_create_user(session: Session):
    email = random_email()
    password = random_password()

    user_create = UserCreate(email=email, password=password)
    user = crud.create_user(session=session, user_create=user_create)

    assert hasattr(user, "hashed_password")

def test_authenticate_user(session: Session):
    email = random_email()
    password = random_password()

    user_create = UserCreate(email=email, password=password)
    user = crud.create_user(session=session, user_create=user_create)

    authenticated_user = crud.authenticate(session=session, email=email, password=password)

    assert authenticated_user
    assert user.email == authenticated_user.email

def test_not_authenticate_user(session: Session):
    email = random_email()
    password = random_password()

    user = crud.authenticate(session=session, email=email, password=password)
    assert user is None

def test_get_user(session: Session):
    email = random_email()
    password = random_password()

    user_create = UserCreate(email=email, password=password)
    user = crud.create_user(session=session, user_create=user_create)

    user_2 = session.get(User, user.id)

    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)