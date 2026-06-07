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


@app.put("/books/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book: schemas.BookBase, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    db_book.title = book.title
    db.commit()
    db.refresh(db_book)
    return db_book


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted successfully"}