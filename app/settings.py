# app/settings.py

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# This line loads the variables from your .env file
# into the environment
load_dotenv()

class Settings(BaseSettings):
    """
    This class reads and validates our settings
    from the environment variables.
    """

    # This tells Pydantic to find a variable named "DATABASE_URL"
    # and store it here. It will fail with an error if it
    # can't find it, which is good for debugging.
    DATABASE_URL: str

    # JWT secret key 
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

class Config:
        env_file = ".env"
        
settings = Settings()