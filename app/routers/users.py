# app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schemas, models, auth
from ..database import get_db, SessionLocal

# Create a "router"
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    # 1. Check if email or reg number already exists
    db_user_email = crud.get_user_by_email(db, email=user.email)
    if db_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    validated_role = user.role 
    
    if validated_role == models.UserRole.student:
        if not user.reg_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration number is required for students."
            )
        
        db_user_reg = crud.get_user_by_reg_number(db, reg_number=user.reg_number)
        if db_user_reg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration number already registered"
            )
    
    if validated_role == models.UserRole.lecturer and user.reg_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lecturer cannot have a registration number."
        )
    if validated_role == models.UserRole.lecturer:
        user.reg_number = None

    # 3. If all checks pass, create the user
    return crud.create_user(db=db, user=user)

@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    """
    Get the current user's profile.
    This endpoint is PROTECTED.
    
    1. 'Depends(auth.get_current_user)' acts as the Security Guard.
    2. It checks the token.
    3. If valid, it gives us the 'current_user' object.
    4. If invalid, it kicks the user out (401 error).
    """
    return current_user