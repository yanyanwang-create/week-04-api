from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, SessionLocal, Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/books", response_model=list[schemas.Book])
def get_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()


@app.post("/books", response_model=schemas.Book)
def create_book(book: schemas.BookBase, db: Session = Depends(get_db)):
    db_book = models.Book(title=book.title)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book