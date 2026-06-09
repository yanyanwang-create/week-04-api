from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas

import os
import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel
from database import engine, SessionLocal, Base

app = FastAPI()

load_dotenv()

ai_client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

Base.metadata.create_all(bind=engine)


def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ChatRequest(BaseModel):
    message: str
    conversation_history: list[dict] = []



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

@app.post("/ai/chat")
def chat_with_assistant(request: ChatRequest):
    messages = request.conversation_history + [
        {"role": "user", "content": request.message}
    ]

    response = ai_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="""You are a helpful book assistant for a personal book tracking app.
Help users discover books, discuss what they've read, and get personalized recommendations.
Be conversational, enthusiastic about books, and concise in your responses.""",
        messages=messages
    )

    reply = response.content[0].text

    return {
        "reply": reply,
        "updated_history": messages + [{"role": "assistant", "content": reply}]
    }

@app.post("/ai/recommend")
def get_recommendations(request: ChatRequest, db: Session = Depends(get_db)):
    books = db.query(models.Book).all()

    book_context = "Here is the user's book library:\n"

    if books:
        book_context += "\nBooks in the library:\n"
        for b in books:
            book_context += f"- {b.title}\n"
    else:
        book_context += "No books tracked yet.\n"

    system_prompt = f"""You are a personalized book recommendation assistant.

{book_context}

Based on this book library, provide thoughtful, personalized recommendations.
Be specific about why each recommendation matches the user's taste.
Keep responses concise — 2-3 recommendations at most unless asked for more."""

    messages = request.conversation_history + [
        {"role": "user", "content": request.message}
    ]

    response = ai_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=messages
    )

    reply = response.content[0].text

    return {
        "reply": reply,
        "updated_history": messages + [{"role": "assistant", "content": reply}]
    }