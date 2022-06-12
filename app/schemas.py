from pydantic import BaseModel, EmailStr
from pydantic.typing import Literal
from typing import Optional
from datetime import datetime

class Vote(BaseModel):
    post_id: int
    dir: Literal[0, 1]

class TokenData(BaseModel):
    user_id: int

class UserOut(BaseModel):
    user_id: int
    email: EmailStr
    created_at: datetime

class PostOut(BaseModel):
    title: str
    content: str
    created_at: datetime
    owner_id: int
    owner: UserOut
    post_id: int

class PostCreate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str