from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from jose import JWTError, jwt
from passlib.context import CryptContext
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "change-this-secret-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
MAX_BCRYPT_PASSWORD_BYTES = 72


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str


class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: str = "student"


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


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


def truncate_password_for_bcrypt(password: str) -> str:
    raw = password.encode("utf-8")
    if len(raw) <= MAX_BCRYPT_PASSWORD_BYTES:
        return password
    # Truncate to bcrypt's 72-byte maximum and drop incomplete UTF-8 tail.
    return raw[:MAX_BCRYPT_PASSWORD_BYTES].decode("utf-8", errors="ignore")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    normalized_password = truncate_password_for_bcrypt(plain_password)
    try:
        return pwd_context.verify(normalized_password, hashed_password)
    except ValueError:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


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


@app.post("/register", response_model=UserOut, status_code=201)
def register_user(payload: UserRegister, db: Session = Depends(get_db)) -> User:
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    normalized_password = truncate_password_for_bcrypt(payload.password)
    hashed_password = pwd_context.hash(normalized_password)
    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hashed_password,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenOut:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    return TokenOut(access_token=access_token)


@app.get("/token-check")
def token_check(token: str = Query(..., description="JWT token to validate")) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True, "payload": payload}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
