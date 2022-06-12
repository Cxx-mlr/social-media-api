from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from . import models, utils
from .schemas import TokenData
from psycopg import sql
from .database import get_db
from typing import Optional
import time
from pydantic import EmailStr
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_payload(token: str):
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise e
    else:
        return payload

def get_user(p_key: str, value) -> models.User:
    query = sql.SQL("""SELECT * FROM users WHERE {p_key}=%s;""").format(p_key=sql.Identifier(p_key))
    conn = get_db()
    try:
        cur = conn.cursor()
        user_dict = cur.execute(
            query=query,
            params=[value]
        ).fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        conn.commit()

        if user_dict != None:
            return models.User(**user_dict)

def authenticate_user(email: EmailStr, password: str) -> models.User:
    user = get_user(p_key='email', value=email)
    if not user:
        return False
    if not utils.verify_password(plain_password=password, hashed_password=user.password):
        return False
    return user

def verify_access_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate':'Bearer'}
    )

    try:
        payload = get_payload(token=token)
        if not payload:
            raise credentials_exception
        token_data = TokenData(user_id=int(payload.get('user_id')))
    except JWTError as e:
        raise credentials_exception
    else:
        return token_data

def get_current_user(token_data: TokenData = Depends(verify_access_token)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate':'Bearer'}
    )

    user = get_user(p_key='user_id', value=token_data.user_id)
    if not user:
        raise credentials_exception
    
    return user