from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from pydantic import BaseModel, EmailStr
from fastapi import Request

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import jose
import time

SECRET_KEY = '22bRjINpjVuoU5HiMJ7YykqIOo4+fIi5+W1+eq72dqg='
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 1

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(secret=plain_password, hash=hashed_password)

def get_hashed_password(password: str):
    return pwd_context.hash(secret=password)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

app = FastAPI()

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f'-----Response:\n{response}\n')
    print(f'Response.Headers Before:\n{response.headers}\n')
    response.headers['X-Process-Time'] = str(process_time)
    print(f'Response.Headers After:\n{response.headers}\n')
    return response

users_database = {
    'Primero': {
        'username': 'Primero',
        'fullname': '1 uno Primero',
        'email': 'Primero@gmail.com',
        'hashed_password': '$2b$12$E8fNHleX9xOPwLvSqGvtB.geG7LFuPGlgm7Dp9cGdwiRAArIfsP9q',
        'disabled': False
    },
    'Segundo': {
        'username': 'Segundo',
        'fullname': '2 dos Segundo',
        'email': 'Segundo@gmail.com',
        'hashed_password': '$2b$12$5olAUJ9eBMClTxiim.zIie1dR3MsdRFCxOk5R0XGucegnFNIp4uiK',
        'disabled': False
    },
    'Tercero': {
        'username': 'Tercero',
        'fullname': '3 tres Tercero',
        'email': 'Tercero@gmail.com',
        'hashed_password': '$2b$12$OUBvkWyhsJZZP8yMBjizL.AXr6XibPO6sMUIN2a2/1RafqjGgFD0C',
        'disabled': True
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

class User(BaseModel):
    username: str
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class UserResponseModel(BaseModel):
    email: Optional[EmailStr] = None
    username: str

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=60)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
            
    user = get_user(users_database, token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post('/token', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db=users_database, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')
    access_token = create_access_token(data={'sub': user.username}, expires_delta=timedelta(seconds=500))
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.get('/users/me', response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user