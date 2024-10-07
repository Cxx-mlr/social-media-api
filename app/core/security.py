from typing_extensions import Any, Union
from datetime import datetime, timedelta, timezone

from app.core.config import settings

import bcrypt
import jwt

ALGORITHM = "HS256"

def create_access_token(subject: Union[str, Any], expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": f"{subject}", "exp": expire}
    encoded_jwt = jwt.encode(to_encode, key=settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(password: str, hashed_password: str):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()