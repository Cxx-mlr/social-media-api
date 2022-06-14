from .. import models, schemas, oauth2
from fastapi import status, HTTPException, APIRouter, Depends, Response
from ..database import get_db
from typing import List, Optional
import random
from pydantic import BaseModel

router = APIRouter(prefix='/posts', tags=['Posts'])

class schema_test(schemas.PostOut):
    count: int

#query="""SELECT * FROM posts WHERE title LIKE (%s) ORDER BY owner_id ASC LIMIT %s OFFSET %s;""",
#@router.get(path='/', response_model=List[schemas.PostOut])
@router.get(path='/', response_model=List[schema_test], status_code=status.HTTP_200_OK)
#@router.get(path='/')
def get_posts(
    limit: int=10, skip: int=0, search: Optional[str] = '',
    conn=Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)
    ):
    try:
        cur = conn.cursor()
        posts = cur.execute(
            query="""SELECT posts.*, COUNT(votes.post_id) FROM posts LEFT JOIN votes ON posts.post_id=votes.post_id WHERE title LIKE (%s) GROUP BY posts.post_id ORDER BY owner_id ASC LIMIT %s OFFSET %s;""",
            params=['%' + search + '%', limit, skip]
        ).fetchall()
    except Exception as e:
        conn.rollback()
        return {'message': str(e)}
    else:
        conn.commit()
        for post in posts:
            post.update({'owner': schemas.UserOut(**oauth2.get_user(p_key='user_id', value=post['owner_id'], db=conn).dict())})
        return posts

@router.post(path='/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostOut)
def create_post(post: schemas.PostCreate, conn=Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        cur = conn.cursor()
        created_post = cur.execute(
            query='INSERT INTO posts (title, content, owner_id) VALUES (%s, %s, %s) RETURNING *;',
            params=[post.title, post.content, current_user.user_id]
        ).fetchone()
    except Exception as e:
        conn.rollback()
        return {'message': str(e)}
    else:
        conn.commit()
        created_post.update({'owner': schemas.UserOut(**oauth2.get_user(p_key='user_id', value=created_post['owner_id'], db=conn).dict())})
        return created_post

@router.get(path='/latest', response_model=schemas.PostOut)
def get_latest_post(conn=Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        cur = conn.cursor()
        latest = cur.execute(
            query='SELECT * FROM posts WHERE owner_id=%s ORDER BY created_at DESC LIMIT 1;',
            params=[current_user.user_id]
        ).fetchone()
    except Exception as e:
        conn.rollback()
        return {'message': str(e)}
    else:
        conn.commit()
        if latest != None:
            latest.update({'owner': schemas.UserOut(**oauth2.get_user(p_key='user_id', value=latest['owner_id'], db=conn).dict())})
            return latest
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Posts Published')

@router.get(path='/random', response_model=schemas.PostOut)
def get_random_post(conn=Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        cur = conn.cursor()
        posts = cur.execute(
            query='SELECT * FROM posts LIMIT 100;',
            params=[current_user.user_id]
        ).fetchall()
    except Exception as e:
        conn.rollback()
        return {'message': str(e)}
    else:
        conn.commit()
        if posts:
            random_post = random.choice(posts)
            random_post.update({'owner': schemas.UserOut(**oauth2.get_user(p_key='user_id', value=random_post['owner_id'], db=conn).dict())})
            return random_post
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Posts Published')

@router.get(path='/{id}', response_model=schemas.PostOut, status_code=status.HTTP_200_OK)
def get_post(id: int, conn=Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        cur = conn.cursor()
        post = cur.execute(
            query='SELECT * FROM posts WHERE post_id=%s LIMIT 100;',
            params=[id]
        ).fetchone()
    except Exception as e:
        conn.rollback()
        return {'message': str(e)}
    else:
        conn.commit()
        if post != None:
            post.update({'owner': schemas.UserOut(**oauth2.get_user(p_key='user_id', value=post['owner_id'], db=conn).dict())})
            return post
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'post with id: {id} was not found.')

@router.delete(path='/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, conn=Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    raw_post = conn.execute(
            query='SELECT * FROM posts WHERE post_id=%s;',
            params=[id]
    ).fetchone()

    try:
        cur = conn.cursor()
        post = cur.execute(
            query='DELETE FROM posts WHERE post_id=%s AND owner_id=%s RETURNING *;',
            params=[id, current_user.user_id]
        ).fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        conn.commit()
        if raw_post and not post:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        if post == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found.')
        else:
            return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete(path='/', status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(conn=Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        conn.execute(
            query='DELETE FROM posts WHERE owner_id=%s;',
            params=[current_user.user_id]
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        conn.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

from typing import Dict

@router.put(path='/{id}', response_model=Dict[str, schemas.PostOut])
def update_post(id: int, new_post: schemas.PostCreate, conn=Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        cur = conn.cursor()
        before_post = cur.execute(
            query='SELECT * FROM posts WHERE post_id=%s AND owner_id=%s;',
            params=[id, current_user.user_id]
        ).fetchone()

        after_post = cur.execute(
            query='UPDATE posts SET title=%s, content=%s WHERE post_id=%s RETURNING *;',
            params=[new_post.title, new_post.content, id]
        ).fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        if (before_post != None) and (after_post != None):
            before_post.update({'owner': schemas.UserOut(**oauth2.get_user(p_key='user_id', value=before_post['owner_id'], db=conn).dict())})
            after_post.update({'owner': schemas.UserOut(**oauth2.get_user(p_key='user_id', value=after_post['owner_id'], db=conn).dict())})
            conn.commit()
            return {'before': before_post, 'after': after_post}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found.')