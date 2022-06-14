from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from .. import models, schemas, utils, oauth2
from ..database import get_db

from pydantic import BaseModel, EmailStr
from datetime import timedelta

router = APIRouter(tags=['Authentication'])

@router.post(path='/login', response_model=schemas.Token, status_code=status.HTTP_200_OK)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = oauth2.authenticate_user(email=user_credentials.username, password=user_credentials.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    access_token = oauth2.create_access_token(data={'user_id': user.user_id}, expires_delta=timedelta(seconds=6000))
    return {'access_token': access_token, 'token_type':'bearer'}