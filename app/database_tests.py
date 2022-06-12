import psycopg
from psycopg.rows import dict_row
import json
from pydantic import EmailStr

class Posts:
    def __init__(self, conn):
        self.conn = conn

    def delete(self):
        try:
            self.conn.execute(
                query='DROP TABLE IF EXISTS posts;'
            )
        except Exception as e:
            self.conn.rollback()
            print('--Failed deleting posts table')
            print('error:', str(e))
        else:
            self.conn.commit()
            print('--Succesfully deleted posts table (if exists)')

    def create(self):
        try:
            self.conn.execute(
                query='CREATE SEQUENCE posts_post_id_seq;'
            )
            self.conn.execute(
                query="""CREATE TABLE IF NOT EXISTS posts (
                    post_id INT NOT NULL PRIMARY KEY DEFAULT nextval('posts_post_id_seq'),
                    title VARCHAR NOT NULL,
                    content VARCHAR NOT NULL,
                    published BOOLEAN NOT NULL DEFAULT(true),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT(now()),
                    owner_id INT NOT NULL CONSTRAINT posts_users_fkey REFERENCES users(user_id) ON DELETE CASCADE
                );"""
            )
            self.conn.execute(
                query='ALTER SEQUENCE posts_post_id_seq OWNED BY posts.post_id;'
            )
        except Exception as e:
            self.conn.rollback()
            print('--Failed creating posts table')
            print('error:', e)
        else:
            self.conn.commit()
            print('--Succesfully created new posts table')
    
    def update(self):
        print('         -- Updating Database: posts --')
        self.delete()
        self.create()

class Users:
    def __init__(self, conn):
        self.conn = conn

    def delete(self):
        try:
            self.conn.execute(
                query='DROP TABLE IF EXISTS users CASCADE;'
            )
        except Exception as e:
            self.conn.rollback()
            print('--Failed deleting users table')
            print('error:', str(e))
        else:
            self.conn.commit()
            print('--Succesfully deleted users table (if exists)')

    def create(self):
        try:
            self.conn.execute(
                query='CREATE SEQUENCE users_user_id_seq'
            )
            self.conn.execute(
                query="""CREATE TABLE IF NOT EXISTS users (
                    user_id INT NOT NULL DEFAULT nextval('users_user_id_seq'),
                    email VARCHAR NOT NULL UNIQUE,
                    password VARCHAR NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT(now()),
                    PRIMARY KEY (user_id)
                );"""
            )
            self.conn.execute(
                query='ALTER SEQUENCE users_user_id_seq OWNED BY users.user_id;'
            )
        except Exception as e:
            self.conn.rollback()
            print('--Failed creating users table')
            print('error:', e)
        else:
            self.conn.commit()
            print('--Succesfully created new users table')
    
    def update(self):
        print('         -- Updating Database: users --')
        self.delete()
        self.create()

class Votes:
    def __init__(self, conn):
        self.conn = conn

    def delete(self):
        try:
            self.conn.execute(
                query="""DROP TABLE IF EXISTS votes;"""
            )
        except Exception as e:
            conn.rollback()
            print('--Failed deleting votes table')
            print('error:', str(e))
        else:
            conn.commit()
            print('--Successfully deleted votes table (if exists)')
    
    def create(self):
        try:
            self.conn.execute(
                query="""CREATE TABLE IF NOT EXISTS votes (
                    user_id INT NOT NULL,
                    post_id INT NOT NULL,
                    CONSTRAINT votes_users_fkey FOREIGN KEY(user_id)
                        REFERENCES users(user_id)
                        ON DELETE CASCADE,
                    CONSTRAINT votes_posts_fkey FOREIGN KEY(post_id)
                        REFERENCES posts(post_id)
                        ON DELETE CASCADE,
                    PRIMARY KEY(user_id, post_id)
                );"""
            )
        except Exception as e:
            conn.rollback()
            print('--Failed creating votes table')
            print('error:', str(e))
        else:
            conn.commit()
            print('--Successfully created new votes table')
    
    def update(self):
        print('         -- Updating Database: votes --')
        self.delete()
        self.create()


with psycopg.connect(host='localhost',
                     dbname='fastapi_database',
                     user='postgres',
                     password='PasswordUser357',
                     row_factory=dict_row) as conn:
    
    Votes(conn).update()

    exit()
    Users(conn).update()
    print()
    Posts(conn).update()

exit()