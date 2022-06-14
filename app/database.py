import psycopg
from psycopg.rows import dict_row
import time
from .config import settings

def get_db():
    if not hasattr(get_db, 'conn'):
        try:
            get_db.conn = psycopg.connect(
                host=settings.DB_HOST,
                dbname=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                port=settings.DB_PORT,
                row_factory=dict_row
            )
        except Exception as e:
            raise Exception('Connecting to database failed...\nerror: {}'.format(str(e)))
        else:
            print('Database connection was succesfull!!')
    return get_db.conn