from typing_extensions import Optional

from app.models import User, UserCreate
from sqlmodel import Session, select

from app.core.security import verify_password, hash_password

def authenticate(*, session: Session, email: str, password: str) -> Optional[User]:
    user = session.exec(select(User).where(User.email == email)).first()

    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

def create_user(*, session: Session, user_create: UserCreate) -> User:
    user = User.model_validate(
        user_create, update={"hashed_password": hash_password(user_create.password)}
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return user