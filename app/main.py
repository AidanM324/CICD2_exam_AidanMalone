# app/main.py
from typing import Optional

from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Response
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import selectinload


from app.database import engine, SessionLocal
from app.models import Base, AuthorDB, BookDB
#from app.schemas import 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (dev/exam). Prefer Alembic in production.
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

def commit_or_rollback(db: Session, error_msg:str):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail= error_msg)
    
# ---- Health ----
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/authors", response_model=AuthorRead, status_code=201, summary="Creates new author")
def create_author(author:AuthorCreate, db: Session = Depends(get_db)):
    db_authors = AuthorDB(**author.model_dump())
    db.add(db_authors)
    commit_or_rollback(db, "Author already exists")
    db.refresh(db_authors)
    return db_authors

@app.get("/api/authors", response_model= list[AuthorRead], status_code=200)
def list_authors(db: Session =Depends(get_db)):
    stmt = select(AuthorDB).order.by(AuthorDB.id)
    return db.execute(stmt).scalars().all()

@app.get("/api/authors/{id}", response_model= AuthorRead, status_code=200)
def get_author(id:int, db: Session =Depends(get_db)):
    stmt = select(AuthorDB).where(AuthorDB.id == id).options(selectinload(AuthorDB.owner))
    auth = db.execute(stmt).scalar_one_or_none()
    if not auth:
        raise HTTPException(status_code=404, detail="Author not found")
    return auth

@app.put("/api/authors/{id}", response_model= AuthorRead, status_code=200)
def update_author(id:int, payload: AuthorCreate, db: Session =Depends(get_db)):
    author = db.get(AuthorDB, id)

    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    data = payload.model_dump()
    author.name = data["name"]
    author.email = data["email"]
    author.year_started = data["year_started"]
    commit_or_rollback(db, "User update failed")
    db.refresh(author)
    return author

@app.patch("/api/authors/{id}", response_model= AuthorRead, status_code=200)
def update_author_patch(id:int, payload: AuthorUpdate, db: Session =Depends(get_db)):
    author = db.get(AuthorDB, id)

    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    update_data = payload.model_dump(exclude_unset = True)
    for field, value in update_data.items():
        setattr(author, field, value)

    commit_or_rollback(db, "Author update failed")
    db.refresh(author)
    return author
