# app/auth.py

import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from enum import Enum

from . import database
from .settings import settings

class UserRole(str, Enum):
    student = "student"
    lecturer = "lecturer"

# <--- 1. NEW HASHING LOGIC (Using bcrypt directly, NO passlib) ---
def get_password_hash(password: str):
    # Convert the password to bytes
    pwd_bytes = password.encode('utf-8')
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    # Return as a string for storage in the database
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    # Convert both to bytes for comparison
    password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    # Check if they match
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

# <--- 2. TOKEN LOGIC (Standard JWT creation) ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# <--- 3. SECURITY GUARD (Validates the token) ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    except Exception:
        raise credentials_exception
    
    # Import crud here to avoid circular imports
    from . import crud 
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user