from fastapi import APIRouter, Body, HTTPException, status
from sqlmodel import select

from app.models import User, UserCreate, UserPublic
from app import crud

from app.api.deps import SessionDep, CurrentUserDep

from typing_extensions import Annotated

router = APIRouter()

@router.get("/")
async def read_all_users(session: SessionDep):
    users = session.exec(select(User))
    return users.all()

@router.get("/me", response_model=UserPublic)
async def read_users_me(current_user: CurrentUserDep):
    return current_user

@router.post("/", response_model=UserPublic)
async def create_user(
    session: SessionDep,
    user_in: Annotated[UserCreate, Body()]
):
    user_in_db = session.exec(select(User).where(User.email == user_in.email)).first()
    if user_in_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system."
        )

    user = crud.create_user(session=session, user_create=user_in)
    return user