from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

@app.post('/token')
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return {'access_token': form_data.username, 'token_type': 'bearer'}

@app.get('/username')
def read_token(token: str = Depends(oauth2_scheme)):
    return {'username': token}