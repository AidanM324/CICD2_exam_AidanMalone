from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint

class Base(DeclarativeBase):
    pass

class AuthorDB(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key= True)
    name: Mapped[str] = mapped_column(String(100), nullable = False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    year_started: Mapped[int] = mapped_column(min(1900), max(2100), nullable = False)
    #books: Mapped[list["BookDB"]] = mapped_column(relationship(back_populates = "author", cascade="all, delete_orphan")

class BookDB(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key= True)
    title: Mapped[str] = mapped_column(String(255), nullable = False)
    pages: Mapped[int] = mapped_column(min(1), max(10000), nullable = False)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"), nullable = False)
    #author: Mapped["AuthorDB"] = mapped_column(back_populates = "books")

