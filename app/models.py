# app/models.py

from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from .database import Base  # Import the 'Base' we created in database.py
from sqlalchemy.orm import relationship
import enum
from sqlalchemy import DateTime 
from datetime import datetime

class UserRole(str, enum.Enum):
    student = "student"
    lecturer = "lecturer"

class User(Base):
    """
    This is our User model. It tells SQLAlchemy to create
    a 'users' table with these columns.
    """

    __tablename__ = "users"  # The name of the table in the database

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    reg_number = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)

    full_name = Column(String, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)

    is_active = Column(Boolean, default=True)

# This lets us access a lecturer's assignments easily (e.g., user.assignments)
    assignments = relationship("Assignment", back_populates="lecturer")

class Assignment(Base):
    """
    This represents the 'assignments' table in our database.
    It stores the homework details and links back to the lecturer who created it.
    """
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=True)
    
    # ForeignKey links this column to the 'id' column of the 'users' table.
    # This is how we know WHICH lecturer created this assignment.
    lecturer_id = Column(Integer, ForeignKey("users.id"))

    # This creates a virtual link back to the User object
    lecturer = relationship("User", back_populates="assignments")
    
class Submission(Base):
    """
    Table to store assignment submissions.
    It links a Student, an Assignment, and a File Path together.
    """
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False) # Where the file is on your PC
    submitted_at = Column(DateTime, default=datetime.utcnow) # Automatic timestamp

    grade = Column(Integer, nullable=True)     # Teacher fills this later
    feedback = Column(String, nullable=True)   # Teacher fills this later

    # Links to other tables
    student_id = Column(Integer, ForeignKey("users.id"))
    assignment_id = Column(Integer, ForeignKey("assignments.id"))

    # Relationships
    student = relationship("User")
    assignment = relationship("Assignment")