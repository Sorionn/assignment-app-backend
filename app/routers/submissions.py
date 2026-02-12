# app/routers/submissions.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
import time # To generate unique filenames

# Import everything we need
from .. import models, schemas, database, crud, auth 

router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"]
)

@router.post("/{assignment_id}", response_model=schemas.Submission)
async def submit_assignment(
    assignment_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    # 1. Validate Assignment exists
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    # <---  CHECK DEADLINE
    if assignment.deadline and datetime.now() > assignment.deadline:
         raise HTTPException(status_code=400, detail="Deadline has passed! Submission rejected.")
    

    # 2. Save the File
    # Create the directory if it doesn't exist
    upload_dir = "uploads/submissions"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate a unique filename (student_id_assignment_id_timestamp.pdf) to avoid overwrites on disk
    timestamp = int(time.time())
    file_extension = file.filename.split(".")[-1]
    saved_filename = f"{current_user.id}_{assignment_id}_{timestamp}.{file_extension}"
    file_location = f"{upload_dir}/{saved_filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Create the Schema Object (The missing link!)
    submission_data = schemas.SubmissionCreate(file_path=file_location)

    # 4. Call CRUD (Upsert logic)
    return crud.create_submission(
        db=db, 
        submission=submission_data, 
        user_id=current_user.id, 
        assignment_id=assignment_id
    )

@router.get("/assignment/{assignment_id}", response_model=List[schemas.Submission])
def read_submissions_for_assignment(
    assignment_id: int, 
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    # Only the lecturer who created the assignment should see submissions
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if not assignment:
         raise HTTPException(status_code=404, detail="Assignment not found")
         
    if assignment.lecturer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view these submissions")
        
    submissions = db.query(models.Submission).filter(models.Submission.assignment_id == assignment_id).all()
    return submissions


@router.put("/{submission_id}/grade", response_model=schemas.Submission)
def grade_submission(
    submission_id: int, 
    grade_data: schemas.SubmissionGrade,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    # 1. Find the submission
    submission = db.query(models.Submission).filter(models.Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # 2. Find the assignment related to this submission
    assignment = db.query(models.Assignment).filter(models.Assignment.id == submission.assignment_id).first()
    
    # 3. SECURITY CHECK: Is the current user the owner of this assignment?
    if assignment.lecturer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to grade this assignment.")
        
    # 4. Save Grade
    submission.grade = grade_data.grade
    submission.feedback = grade_data.feedback
    db.commit()
    db.refresh(submission)
    return submission

@router.get("/me/{assignment_id}", response_model=schemas.Submission)
def read_my_submission(
    assignment_id: int, 
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    submission = crud.get_student_submission(db, student_id=current_user.id, assignment_id=assignment_id)
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    return submission