# app/main.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from .database import engine, Base  
from . import models 
from .routers import users, auth, assignments, submissions
from fastapi.responses import JSONResponse
# This line tells SQLAlchemy to look at all the classes
# that inherited from Base (like our User model) and
# create the corresponding tables in the database.
models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Assignment App API",
    description="Backend for the assignment management system.",
    version="0.1.0",
)
# <--- ADD THIS DEBUG BLOCK --->
@app.middleware("http")
async def debug_logging(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print(f"🔥 SERVER CRASHED: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})
# <--- END DEBUG BLOCK --->

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(assignments.router)
app.include_router(submissions.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# --- A simple "Hello World" endpoint ---
@app.get("/")
def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to the Assignment App API!"}



# We will later add our routers here