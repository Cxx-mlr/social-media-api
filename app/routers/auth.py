from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from .. import models, schemas, utils, oauth2

from pydantic import BaseModel, EmailStr
from datetime import timedelta

router = APIRouter(tags=['Authentication'])

@router.post(path='/token', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    user = oauth2.authenticate_user(email=user_credentials.username, password=user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    access_token = oauth2.create_access_token(data={'user_id': user.user_id}, expires_delta=timedelta(seconds=6000))
    return {'access_token': access_token, 'token_type':'bearer'}