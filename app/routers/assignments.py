# app/routers/assignments.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Import our app modules
from .. import models, schemas, database, auth

router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)

# 1. CREATE ASSIGNMENT (This is the missing function!)
@router.post("/", response_model=schemas.Assignment)
def create_assignment(
    assignment: schemas.AssignmentCreate, 
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    # Only lecturers can create assignments
    if current_user.role != auth.UserRole.lecturer:
         raise HTTPException(status_code=403, detail="Not authorized")

    # The magic part: **assignment.dict() automatically unpacks title, description, AND DEADLINE
    new_assignment = models.Assignment(
        **assignment.dict(), 
        lecturer_id=current_user.id
    )
    
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment



@router.get("/", response_model=List[schemas.Assignment])
def read_assignments(
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    # Rule 1: If User is a Lecturer, only show THEIR assignments
    if current_user.role == auth.UserRole.lecturer:
        return db.query(models.Assignment).filter(
            models.Assignment.lecturer_id == current_user.id
        ).all()
    
    # Rule 2: If User is a Student, show EVERYTHING
    return db.query(models.Assignment).all()