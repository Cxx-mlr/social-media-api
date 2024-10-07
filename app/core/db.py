from sqlmodel import create_engine
from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

def init_db() -> None:
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)