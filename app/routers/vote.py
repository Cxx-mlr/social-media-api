from fastapi import APIRouter, HTTPException, status, Depends, Response
from .. import schemas, models, oauth2
from ..database import get_db


router = APIRouter(prefix='/vote', tags=['Vote'])

@router.post(path='/', status_code=status.HTTP_201_CREATED)
def vote_post(vote: schemas.Vote, current_user: models.User = Depends(oauth2.get_current_user), conn=Depends(get_db)):
    try:
        post_dict = conn.execute(
            query="""SELECT true AS existent FROM posts WHERE post_id=%s;""",
            params=[vote.post_id]
        ).fetchone()
    except Exception as e:
        conn.rollback()
        return {'message': str(e)}
    else:
        conn.commit()
        if not post_dict or bool(post_dict['existent']) == False:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Post with id: {vote.post_id} does not exists'
            )

    try:
        post_dict = conn.execute(
            query="""SELECT post_id, user_id FROM votes WHERE post_id=%s AND user_id=%s;""",
            params=[vote.post_id, current_user.user_id]
        ).fetchone()
    except Exception as e:
        conn.rollback()
        return {'message': str(e)}
    else:
        conn.commit()

        if vote.dir == 1:
            if post_dict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'User {current_user.user_id} has already voted on posts {vote.post_id}'
                )
            else:
                try:
                    conn.execute(
                        query="""INSERT INTO votes (post_id, user_id) VALUES (%s, %s);""",
                        params=[vote.post_id, current_user.user_id]
                    )
                except Exception as e:
                    conn.rollback()
                    return {'message': str(e)}
                else:
                    conn.commit()
                    return {"post_id": vote.post_id, "user_id": current_user.user_id}

        elif vote.dir == 0:
            if not post_dict:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Yo can not unvote this post'
                )
            else:
                try:
                    conn.execute(
                        query="""DELETE FROM votes WHERE post_id=%s AND user_id=%s;""",
                        params=[vote.post_id, current_user.user_id]
                    )
                except Exception as e:
                    conn.rollback()
                    return {'message': str(e)}
                else:
                    conn.commit()
                    return {"post_id": vote.post_id, "user_id": current_user.user_id}