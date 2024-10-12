from sqlmodel import create_engine, SQLModel, Session, select
from sqlalchemy.engine.base import Engine
from app.core.config import settings

from app.models import User, UserCreate
from app import crud

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

def init_db(session: Session, engine: Engine = engine) -> None:
    SQLModel.metadata.create_all(engine)
    user = session.exec(select(User).where(User.email == settings.FIRST_USER_EMAIL)).first()
    if not user:
        user_create = UserCreate(email=settings.FIRST_USER_EMAIL, password=settings.FIRST_USER_PASSWORD)
        crud.create_user(session=session, user_create=user_create)