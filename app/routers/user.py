from .. import models, schemas, utils
from fastapi import status, HTTPException, APIRouter, Depends
from ..database import get_db
from ..oauth2 import get_current_user

router = APIRouter(prefix='/users', tags=['Users'])

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def add_user(user: schemas.UserCreate, conn=Depends(get_db)):
    user.password = utils.get_hashed_password(password=user.password)
    try:
        cur = conn.cursor()
        new_user = cur.execute(
            query="""INSERT INTO users (email, password) VALUES (%s, %s) RETURNING *;
            """,
            params=[user.email, user.password]
        ).fetchone()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        conn.commit()
        if new_user != None:
            return new_user

@router.get(path='/me', response_model=schemas.UserOut)
def read_users_me(current_user: schemas.UserOut = Depends(get_current_user)):
    return current_user