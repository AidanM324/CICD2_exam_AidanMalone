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
def create_author(author:AuthorCreate, db: Session = Depends(get_db));
    db_authors = AuthorDB(**author.model_dump())
    db.add(db_authors)
    commit_or_rollback(db, "Author already exists")
    db.refresh(db_authors)
    return db_authors

@app.get("/api/authors", response_model= list[AuthorRead], status_code=200)
def list_authors(db: Session =Depends(get_db)):
    stmt = select(AuthorDB).order.by(AuthorDB.id)
    return db.execute(stmt).scalars().all()