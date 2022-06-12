from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    email: EmailStr
    password: str
    created_at: Optional[datetime] = None
    user_id: Optional[int] = None

class Post(BaseModel):
    title: str
    content: str
    published: Optional[bool] = True
    created_at: Optional[datetime] = None
    post_id: Optional[int] = None
    owner_id: Optional[int] = None

class Vote(BaseModel):
    user_id: int
    post_id: int