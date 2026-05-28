from pydantic import BaseModel

class BookBase(BaseModel):
    title: str

class Book(BookBase):
    id: int

    class Config:
        from_attributes = True