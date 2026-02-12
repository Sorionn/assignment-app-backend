# app/schemas.py

# Import field_validator from pydantic
from pydantic import BaseModel, EmailStr,Field ,field_validator 
from .models import UserRole  
from datetime import datetime
from typing import Optional

# --- User Schemas ---

class UserBase(BaseModel):
    """
    Base schema for a user. Contains fields
    that are common to creating and reading.
    """
    email: EmailStr
    full_name: str | None = None
    reg_number: str | None = None

# app/schemas.py

from pydantic import BaseModel, field_validator
from .models import UserRole

# ... (UserBase class remains unchanged) ...

class UserCreate(UserBase):
    """
    Schema for creating a new user.
    Handles password, optional registration number, and role validation.
    """
    password: str = Field(..., min_length=6)
    role: str = "student"
    
    # This field is optional and defaults to None.
    # This prevents unique constraint violations for users without a reg_number.
    reg_number: str | None = None 

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> UserRole:
        """
        Validates the role against the UserRole Enum, allowing case-insensitive input.
        """
        v_lower = v.lower()
        
        # Check against valid enum values
        valid_roles = [e.value for e in UserRole]
        if v_lower not in valid_roles:
            raise ValueError(f"'{v}' is not a valid role. Must be one of: {valid_roles}")
        
        return UserRole(v_lower)
    
    
class User(UserBase):
    
   # Schema for reading a user (e.g., sending from API to Flutter).
    
    id: int
    is_active: bool
    role: UserRole  # <-- This is fine, it's for *output*

    class Config:
        from_attributes = True
        
class AssignmentBase(BaseModel):
    """
    Shared properties for both creating and reading.
    """
    title: str
    description: str
    deadline: Optional[datetime] = None

class AssignmentCreate(AssignmentBase):
    """
    INPUT: What the teacher sends to us.
    We DON'T ask for teacher_id here, because we will grab it 
    securely from their Login Token instead.
    """
    pass 

class Assignment(AssignmentBase):
    """
    OUTPUT: What we send back to the app.
    We include the ID and the Teacher's ID.
    """
    id: int
    lecturer_id: int 

    class Config:
        # This tells Pydantic to treat the SQLAlchemy model like a dict
        from_attributes = True

class Submission(BaseModel):
    id: int
    file_path: str
    submitted_at: datetime
    student_id: int
    assignment_id: int
    grade: int | None = None
    feedback: str | None = None

    class Config:
        from_attributes = True   
        
class SubmissionGrade(BaseModel):
    """
    INPUT: What the lecturer sends to grade a student.
    """
    grade: int
    feedback: str             

class SubmissionBase(BaseModel):
    file_path: str

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionGrade(BaseModel):
    grade: int
    feedback: str

class Submission(SubmissionBase):
    id: int
    student_id: int
    assignment_id: int
    grade: int | None = None
    feedback: str | None = None

    class Config:
        orm_mode = True    