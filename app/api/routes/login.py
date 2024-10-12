from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core import security
from app.models import Token, UserPublic

from app.api.deps import SessionDep
from app import crud

from typing_extensions import Annotated
from datetime import timedelta

from app.api.deps import CurrentUserDep

router = APIRouter()

@router.post(path="/login/access-token")
async def login_for_access_token(
    session: SessionDep,
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = crud.authenticate(session=session, email=credentials.username, password=credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password",
        )

    return Token(
        access_token=security.create_access_token(
            user.id,
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    )

from fastapi import Request

@router.post("/login/test-token", response_model=UserPublic)
async def test_access_token(current_user: CurrentUserDep):
    return current_user