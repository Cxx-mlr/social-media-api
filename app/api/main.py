from fastapi import APIRouter

from app.api.routes import login, users, posts, votes

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(votes.router, prefix="/votes", tags=["votes"])