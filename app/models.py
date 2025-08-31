from sqlmodel import SQLModel, Field, Column, ForeignKey
from sqlalchemy import Text, DateTime, Integer, String, Float
from datetime import datetime
from typing import Optional


# === Users ===
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    tg_id: int = Field(index=True, unique=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


# === FAQ Entries ===
class FAQEntry(SQLModel, table=True):
    __tablename__ = "faq_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    question: str = Field(sa_column=Column(Text, nullable=False))
    answer: str = Field(sa_column=Column(Text, nullable=False))
    popularity: int = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


# === Unanswered Questions ===
class UnansweredQuestion(SQLModel, table=True):
    __tablename__ = "unanswered_questions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    question_text: str = Field(sa_column=Column(Text, nullable=False))
    similar_score: Optional[float] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


# === GPT Cache ===
class GPTCache(SQLModel, table=True):
    __tablename__ = "gpt_cache"

    id: Optional[int] = Field(default=None, primary_key=True)
    qhash: str = Field(sa_column=Column(String(64), unique=True, index=True, nullable=False))
    answer: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    hits: int = Field(default=0, nullable=False)


# === Usage Limits ===
class UsageLimit(SQLModel, table=True):
    __tablename__ = "usage_limits"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    window_start: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    count: int = Field(default=0, nullable=False)


# === Admins ===
class Admin(SQLModel, table=True):
    __tablename__ = "admins"

    # FK → users.id (админ всегда является пользователем)
    user_id: int = Field(foreign_key="users.id", primary_key=True, nullable=False)
