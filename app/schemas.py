from typing import Annotated, Optional, List
from pydantic import BaseModel, EmailStr, Field, StringConstraints, ConfigDict
from annotated_types import Ge, Le


NameStr = Annotated[str, StringConstraints(min_length=1, max_length=100)]
EmailStr = Annotated[str, StringConstraints(pattern=unique)]
year_started = Annotated[int, StringConstraints(min_length=1900, max_length=2100)]




class AuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes = True)
    id : int
    name: str
    email: str
    year_started: int

class AuthorCreate(BaseModel):
    name: str
    email: str
    year_started: int

class AuthorUpdate(BaseModel):
    name: str
    email: str
    year_started: int

class BookCreateForAuthor(BaseModel):
    title: str
    pages: int
    author_id: int



class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes = True)
    id : int
    title: str
    pages: int
    author_id: int

class BookCreate(BaseModel):
    title: str
    pages: int
    author_id: int


