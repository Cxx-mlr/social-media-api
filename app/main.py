from fastapi import FastAPI, Request
from .routers import post, user, auth, vote
import time

app = FastAPI()

app.include_router(router=auth.router)
app.include_router(router=post.router)
app.include_router(router=user.router)
app.include_router(router=vote.router)

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    proccess_time = time.time() - start_time

    response.headers['X-Process-Time'] = str(proccess_time)
    return response

@app.get('/')
def root():
    return {'message':'Successfully deployed from CI/CD pipeline'}