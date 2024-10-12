from fastapi import APIRouter, Body, HTTPException, status
from sqlmodel import select

from app.models import User, UserCreate, UserPublic, UserRegister
from app import crud

from app.api.deps import SessionDep, CurrentUserDep

from typing_extensions import Annotated

import uuid

router = APIRouter()

@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(
    session: SessionDep,
    user_in: Annotated[UserRegister, Body()]
):
    user = session.exec(select(User).where(User.email == user_in.email)).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system."
        )

    user = crud.create_user(session=session, user_create=UserCreate.model_validate(user_in))
    return user

@router.get("/")
async def read_users(session: SessionDep):
    users = session.exec(select(User))
    return users.all()

@router.get("/me", response_model=UserPublic)
async def read_users_me(current_user: CurrentUserDep):
    return current_user

@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    session: SessionDep,
    user_id: uuid.UUID
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return user