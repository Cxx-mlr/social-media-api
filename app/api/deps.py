from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlmodel import Session

from app.core.db import engine
from app.core.security import ALGORITHM
from app.core.config import settings
from app.models import TokenPayload
from app.models import User

import jwt

from jwt import InvalidTokenError
from pydantic import ValidationError

from typing_extensions import Generator, Annotated

import uuid

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]

def get_current_user(session: SessionDep, token: TokenDep):
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_payload = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = session.get(User, uuid.UUID(token_payload.sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]