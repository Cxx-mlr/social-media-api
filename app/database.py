import psycopg
from psycopg.rows import dict_row
import time
from .config import settings

while True:
    try:
        conn = psycopg.connect(
            host=settings.DB_HOST,
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            port=settings.DB_PORT,
            row_factory=dict_row
        )
    except Exception as e:
        print('Connecting to database failed')
        print('error:', e)
        time.sleep(3)
    else:
        print('Database connection was succesfull!!')
        break

def get_db():
    return conn