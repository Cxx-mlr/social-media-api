from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select, Session

from app.api.deps import SessionDep, CurrentUserDep
from app.models import Post, User, Vote, VoteDirection

import uuid

router = APIRouter()
    

@router.post(path="/{id}")
def vote_post(
    session: SessionDep,
    current_user: CurrentUserDep,
    id: uuid.UUID,
    direction: VoteDirection
):
    post = session.exec(
        select(Post)
            .where(Post.id == id)
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot upvote your own post"
        )
    
    for vote in current_user.votes:
        if vote.post_id == post.id:
            if vote.direction == direction:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"You have already {vote.direction}voted this post"
                )
            else:
                vote.direction = direction
            break
    else:
        vote = Vote(
            user_id=current_user.id,
            post_id=post.id,
            direction=direction
        )

    session.add(vote)
    session.commit()

    session.refresh(vote)

    return vote