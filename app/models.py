from sqlmodel import SQLModel, Field, Relationship

from datetime import datetime, timezone
from pydantic import EmailStr

import uuid

from typing_extensions import Optional, List
from enum import Enum

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)

class UserPublic(UserBase):
    id: uuid.UUID

class VoteDirection(str, Enum):
    up = "up"
    down = "down"

class Vote(SQLModel, table=True):
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id", primary_key=True, ondelete="CASCADE")
    post_id: Optional[uuid.UUID] = Field(default=None, foreign_key="post.id", primary_key=True, ondelete="CASCADE")
    direction: VoteDirection

    user: "User" = Relationship(back_populates="votes")
    post: "Post" = Relationship(back_populates="votes")

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

    posts: List["Post"] = Relationship(back_populates="owner")
    votes: List["Vote"] = Relationship(back_populates="user")

class PostBase(SQLModel):
    title: str = Field(index=True)
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    published: Optional[bool] = Field(default=True, nullable=False)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    owner_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id", ondelete="CASCADE")
    owner: User = Relationship(back_populates="posts")

    votes: List[Vote] = Relationship(back_populates="post")

PostPublic = Post

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(SQLModel):
    sub: Optional[str] = None