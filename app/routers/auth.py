from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import crud, auth
from ..database import get_db

router = APIRouter(tags=["Authentication"])

@router.post("/login/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    user = crud.get_user_by_email(db, email=form_data.username)
    
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(data={"sub": user.email,
                                                  "role": user.role.value if hasattr(user.role, 'value') else user.role})
    return {"access_token": access_token, "token_type": "bearer"}