from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

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

class SessionCreate(BaseModel):
    mentor_profile_id: int
    scheduled_time: datetime

class SessionUpdate(BaseModel):
    scheduled_time: Optional[datetime] = None
    status: Optional[str] = None

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

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
        user_id = int(subject)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


@app.get("/")
def root() -> dict:
    return {"message": "Nyelvcsere FastAPI backend is running"}

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
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
def login(payload: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> TokenOut:
    user = db.query(User).filter(User.email == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.get("/users", response_model=List[UserOut])
def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/languages", response_model=List[LanguageOut])
def list_languages(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[Language]:
    return db.query(Language).order_by(Language.name.asc()).all()

@app.get("/mentor-profiles", response_model=List[MentorProfileOut])
def list_mentor_profiles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[MentorProfile]:
    return db.query(MentorProfile).all()

@app.get("/sessions", response_model=List[SessionOut])
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[StudySession]:
    return db.query(StudySession).all()

@app.get("/progress-logs", response_model=List[ProgressLogOut])
def list_progress_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[ProgressLog]:
    return db.query(ProgressLog).all()



@app.post("/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(payload: SessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> StudySession:
    new_session = StudySession(
        student_id=current_user.id,
        mentor_profile_id=payload.mentor_profile_id,
        scheduled_time=payload.scheduled_time,
        status="scheduled"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@app.put("/sessions/{session_id}", response_model=SessionOut)
def update_session(session_id: int, payload: SessionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> StudySession:
    db_session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if payload.scheduled_time:
        db_session.scheduled_time = payload.scheduled_time
    if payload.status:
        db_session.status = payload.status
        
    db.commit()
    db.refresh(db_session)
    return db_session

@app.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(db_session)
    db.commit()
    return None