# app/crud.py

from sqlalchemy.orm import Session
from . import models, schemas, auth # Import our new auth file
from .models import UserRole

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_reg_number(db: Session, reg_number: str):
    return db.query(models.User).filter(models.User.reg_number == reg_number).first()

def create_user(db: Session, user: schemas.UserCreate):
    
    # Get the hashed password
    hashed_password = auth.get_password_hash(user.password)
    
    # Get the validated role from the schema
    # (The validator already converted it to lowercase and an Enum)
    validated_role = user.role 
    
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        reg_number=user.reg_number,
        hashed_password=hashed_password,
        role=validated_role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_assignment(db: Session, assignment: schemas.AssignmentCreate, user_id: int):
    """
    Creates a new assignment linked to a specific lecturer (user_id).
    """
    db_assignment = models.Assignment(
        title=assignment.title,
        description=assignment.description,
        lecturer_id=user_id  # Link it to the lecturer who is logged in
    )
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def get_assignments(db: Session):
    return db.query(models.Assignment).all()

# app/crud.py

def create_submission(db: Session, submission: schemas.SubmissionCreate, user_id: int, assignment_id: int):
    # 1. Check if submission already exists
    existing_submission = db.query(models.Submission).filter(
        models.Submission.student_id == user_id,
        models.Submission.assignment_id == assignment_id
    ).first()

    if existing_submission:
        # 2. UPDATE existing
        existing_submission.file_path = submission.file_path
        # Reset grade/feedback since it's a new file
        existing_submission.grade = None 
        existing_submission.feedback = None
        db.commit()
        db.refresh(existing_submission)
        return existing_submission
    else:
        # 3. CREATE new
        db_submission = models.Submission(
            **submission.dict(), 
            student_id=user_id, 
            assignment_id=assignment_id
        )
        db.add(db_submission)
        db.commit()
        db.refresh(db_submission)
        return db_submission

def grade_submission(db: Session, submission_id: int, grade_data: schemas.SubmissionGrade):
    """
    Updates a submission with a grade and feedback.
    """
    # 1. Find the submission
    db_submission = db.query(models.Submission).filter(models.Submission.id == submission_id).first()
    
    # 2. Update the fields
    if db_submission:
        db_submission.grade = grade_data.grade
        db_submission.feedback = grade_data.feedback
        db.commit()
        db.refresh(db_submission)
        
    return db_submission

# To list submissions for a Lecturer
def get_submissions_by_assignment(db: Session, assignment_id: int):
    return db.query(models.Submission).filter(models.Submission.assignment_id == assignment_id).all()

def get_student_submission(db: Session, student_id: int, assignment_id: int):
    return db.query(models.Submission).filter(
        models.Submission.student_id == student_id,
        models.Submission.assignment_id == assignment_id
    ).first()