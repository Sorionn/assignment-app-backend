# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings import settings  # Import our settings object

# 1. The Engine
# This is the main connection point to our database.
# It uses the DATABASE_URL from our settings.py file.
engine = create_engine(
    settings.DATABASE_URL
)

# 2. The Session
# This creates a "session factory". Think of it as a
# template for creating new database sessions (conversations)
# Each API request will get its own session.
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# 3. The Base
# This is a "base class" for our database models.
# When we create our User, Assignment, etc. models,
# they will inherit from this Base. This is how
# SQLAlchemy knows what tables to create in our database.
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()