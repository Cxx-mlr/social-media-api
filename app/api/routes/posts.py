from fastapi import APIRouter, HTTPException, status, Body
from sqlmodel import select, col

from typing_extensions import Annotated

from app.api.deps import SessionDep, CurrentUserDep
from app.models import PostCreate, PostPublic, Post

import uuid

router = APIRouter()

@router.post("/", response_model=PostPublic)
def create_post(
    session: SessionDep,
    current_user: CurrentUserDep,
    post_in: Annotated[PostCreate, Body()],
):
    post = Post.model_validate(
        post_in,
        update={
            "owner_id": current_user.id
        }
    )

    session.add(post)
    session.commit()
    session.refresh(post)

    return post

@router.get("/")
def read_posts(
    session: SessionDep,
    skip: int=0,
    limit: int=10,
):
    posts = session.exec(
        select(Post)
            .order_by(col(Post.created_at).desc())
            .limit(limit)
            .offset(skip)
    ).all()
    
    return posts

@router.get("/me")
def read_posts_me(
    session: SessionDep,
    current_user: CurrentUserDep,
    skip: int=0,
    limit: int=10,
):
    posts = session.exec(
        select(Post)
            .where(Post.owner_id == current_user.id)
            .order_by(col(Post.created_at).desc())
            .limit(limit)
            .offset(skip)
    ).all()
    
    return posts

@router.get("/latest", response_model=PostPublic)
def read_latest_post(
    session: SessionDep
):
    latest_post = session.exec(
        select(Post)
            .order_by(col(Post.created_at).desc())
            .limit(1)
    ).first()

    if not latest_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found for the current user.")
    return latest_post

@router.get("/me/latest", response_model=PostPublic)
def read_latest_post_me(
    session: SessionDep,
    current_user: CurrentUserDep
):
    latest_post = session.exec(
        select(Post)
            .where(Post.owner_id == current_user.id)
            .order_by(col(Post.created_at).desc())
            .limit(1)
    ).first()

    if not latest_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found for the current user.")
    return latest_post

@router.get("/{post_id}", response_model=PostPublic)
def read_post_by_id(
    post_id: uuid.UUID,
    session: SessionDep
):
    posts = session.exec(
        select(Post)
            .where(Post.id == post_id)
    ).all()

    return posts

@router.put("/{post_id}", response_model=PostPublic)
def update_post_by_id(
    post_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
    post_in: PostCreate,
):
    post = session.exec(
        select(Post)
            .where(Post.id == post_id)
    ).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found.")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this post.")

    post.title = post_in.title
    post.content = post_in.content

    session.add(post)
    session.commit()
    session.refresh(post)

    return post

@router.delete("/{post_id}", response_model=PostPublic)
def delete_post_by_id(
    post_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUserDep
):
    for index, post in enumerate(current_user.posts):
        if post.id == post_id:
            deleted = post.model_copy()
            current_user.posts.pop(index)
            break
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found.")

    session.add(current_user)
    session.commit()

    return deleted

@router.delete("/", response_model=PostPublic)
def delete_posts_me(
    session: SessionDep,
    current_user: CurrentUserDep
):
    if not current_user.posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found for the current user.")
    
    deleted = [post.model_copy() for post in current_user.posts]
    current_user.posts = []

    session.add(current_user)
    session.commit()

    return deleted