from datetime import datetime
from typing import Generator, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base, Language, MentorProfile, ProgressLog, Session as StudySession, User

app = FastAPI(
    title="Nyelvcsere Backend API",
    description="FastAPI server for the language exchange platform.",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str


class LanguageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class MentorProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    offered_language_id: Optional[int]
    requested_language_id: Optional[int]
    session_length_minutes: int


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    mentor_profile_id: int
    scheduled_time: datetime
    status: str


class ProgressLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    student_id: int
    notes: Optional[str]
    rating: Optional[int]


@app.get("/")
def root() -> dict:
    return {"message": "Nyelvcsere FastAPI backend is running"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/users", response_model=List[UserOut])
def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/languages", response_model=List[LanguageOut])
def list_languages(db: Session = Depends(get_db)) -> List[Language]:
    return db.query(Language).order_by(Language.name.asc()).all()


@app.get("/mentor-profiles", response_model=List[MentorProfileOut])
def list_mentor_profiles(db: Session = Depends(get_db)) -> List[MentorProfile]:
    return db.query(MentorProfile).all()


@app.get("/sessions", response_model=List[SessionOut])
def list_sessions(db: Session = Depends(get_db)) -> List[StudySession]:
    return db.query(StudySession).all()


@app.get("/progress-logs", response_model=List[ProgressLogOut])
def list_progress_logs(db: Session = Depends(get_db)) -> List[ProgressLog]:
    return db.query(ProgressLog).all()
