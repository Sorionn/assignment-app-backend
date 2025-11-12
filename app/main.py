
from fastapi import FastAPI

app = FastAPI(title="Assignment App API")


@app.get("/")
def read_root():
       return {"message": "Welcome to the Assignment App API!"}