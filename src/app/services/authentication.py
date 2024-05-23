# Dependency to get the current user
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from models.token import TokenData
from models.user_in_db import UserInDB

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory user store for simplicity
fake_users_db = {
    "Jane": {
        "username": "Jane",
        "full_name": "Jane Doe",
        "email": "user@example.com",
        "hashed_password": "fakehashedpassword",
        "disabled": False,
    }
}

def fake_hash_password(password: str):
    return "fakehashed" + password


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=HTTPException.status_code,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = TokenData(username="user")  # Simplified token validation for demo
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)