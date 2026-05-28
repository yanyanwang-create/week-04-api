from fastapi import FastAPI
from database import engine, Base
import models
app = FastAPI()
Base.metadata.create_all(bind=engine)
@app.get("/books")
def get_books():
    return {"message": "Books endpoint connected to database"}