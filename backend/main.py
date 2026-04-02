from datetime import datetime, timedelta, timezone
from typing import List, Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import bcrypt
from pydantic import BaseModel, ConfigDict
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base, Language, MentorProfile, ProgressLog, Session as StudySession, User, UserRole

app = FastAPI(
    title="Nyelvcsere Backend API",
    description="FastAPI server for the language exchange platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

SECRET_KEY = "change-this-secret-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
MAX_BCRYPT_PASSWORD_BYTES = 72
ROLE_GUEST = "guest"
ALLOWED_REGISTER_ROLES = {role.value for role in UserRole}


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    role: Literal["student", "mentor"]
    learning_language_id: Optional[int] = None

class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: Literal["student", "mentor"] = "student"
    learning_language_id: Optional[int] = None
    offered_language_id: Optional[int] = None
    requested_language_id: Optional[int] = None
    availability_details: Optional[str] = None
    exchange_terms: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    learning_language_id: Optional[int] = None

class CurrentUserOut(BaseModel):
    is_authenticated: bool
    role: Literal["guest", "student", "mentor"]
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    learning_language_id: Optional[int] = None

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
    availability_details: Optional[str] = None
    exchange_terms: Optional[str] = None

class MentorProfileMeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    offered_language_id: Optional[int]
    requested_language_id: Optional[int]
    session_length_minutes: int
    availability_details: Optional[str] = None
    exchange_terms: Optional[str] = None


class PairingSuggestionOut(BaseModel):
    pairing_type: str
    student_id: int
    student_name: str
    student_email: str
    learning_language_id: Optional[int]
    learning_language_name: Optional[str] = None
    mentor_profile_id: int
    mentor_name: str
    mentor_email: str
    mentor_language_id: Optional[int]
    mentor_language_name: Optional[str] = None
    mentor_availability_details: Optional[str] = None
    mentor_exchange_terms: Optional[str] = None
    match_reason: Optional[str] = None


class MentorPairingGroupOut(BaseModel):
    mentor_profile_id: int
    mentor_name: str
    mentor_email: str
    mentor_language_id: Optional[int]
    mentor_language_name: Optional[str] = None
    mentor_availability_details: Optional[str] = None
    mentor_exchange_terms: Optional[str] = None
    matched_students: List[PairingSuggestionOut]


class ResourceOut(BaseModel):
    title: str
    description: str
    url: str

class MentorProfileUpdate(BaseModel):
    offered_language_id: Optional[int] = None
    requested_language_id: Optional[int] = None
    session_length_minutes: Optional[int] = None
    availability_details: Optional[str] = None
    exchange_terms: Optional[str] = None

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

class ProgressLogUpsert(BaseModel):
    notes: Optional[str] = None
    rating: Optional[int] = None


def truncate_password_for_bcrypt(password: str) -> str:
    raw = password.encode("utf-8")
    if len(raw) <= MAX_BCRYPT_PASSWORD_BYTES:
        return password
    return raw[:MAX_BCRYPT_PASSWORD_BYTES].decode("utf-8", errors="ignore")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    normalized_password = truncate_password_for_bcrypt(plain_password)
    try:
        return bcrypt.checkpw(normalized_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def hash_password(password: str) -> str:
    normalized_password = truncate_password_for_bcrypt(password)
    return bcrypt.hashpw(normalized_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

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


def get_current_user_or_guest(
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None

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


def ensure_session_access(session: StudySession, current_user: User, db: Session) -> None:
    if current_user.id == session.student_id:
        return

    mentor_profile = db.query(MentorProfile).filter(MentorProfile.user_id == current_user.id).first()
    if mentor_profile is not None and mentor_profile.id == session.mentor_profile_id:
        return

    raise HTTPException(status_code=403, detail="Not enough permissions for this session")


def build_pairing_suggestions(db: Session) -> List[PairingSuggestionOut]:
    users = db.query(User).all()
    profiles = db.query(MentorProfile).all()
    languages = db.query(Language).all()

    users_by_id = {user.id: user for user in users}
    languages_by_id = {language.id: language for language in languages}

    suggestions: List[PairingSuggestionOut] = []

    for mentor_profile in profiles:
        mentor_user = users_by_id.get(mentor_profile.user_id)
        if mentor_user is None:
            continue

        mentor_language = languages_by_id.get(mentor_profile.offered_language_id)
        mentor_target_language = languages_by_id.get(mentor_profile.requested_language_id)

        for user in users:
            if user.id == mentor_user.id:
                continue
            if user.learning_language_id is None:
                continue

            learning_language = languages_by_id.get(user.learning_language_id)
            is_direct_match = mentor_profile.offered_language_id is not None and user.learning_language_id == mentor_profile.offered_language_id
            is_reverse_match = (
                mentor_profile.requested_language_id is not None
                and mentor_user.learning_language_id is not None
                and mentor_user.learning_language_id == user.learning_language_id
            )

            if not is_direct_match and not is_reverse_match:
                continue

            suggestions.append(
                PairingSuggestionOut(
                    pairing_type="mentor-to-student",
                    student_id=user.id,
                    student_name=user.name,
                    student_email=user.email,
                    learning_language_id=user.learning_language_id,
                    learning_language_name=learning_language.name if learning_language else None,
                    mentor_profile_id=mentor_profile.id,
                    mentor_name=mentor_user.name,
                    mentor_email=mentor_user.email,
                    mentor_language_id=mentor_profile.offered_language_id,
                    mentor_language_name=mentor_language.name if mentor_language else None,
                    mentor_availability_details=mentor_profile.availability_details,
                    mentor_exchange_terms=mentor_profile.exchange_terms,
                    match_reason=(
                        "Tanulási cél egyezik a mentor által kínált nyelvvel"
                        if is_direct_match
                        else "Kölcsönös nyelvi cserelehetőség"
                    ),
                )
            )

    return suggestions


def build_mentor_pairing_groups(db: Session) -> List[MentorPairingGroupOut]:
    suggestions = build_pairing_suggestions(db)
    grouped: dict[int, dict] = {}

    for suggestion in suggestions:
        mentor_group = grouped.setdefault(
            suggestion.mentor_profile_id,
            {
                "mentor_profile_id": suggestion.mentor_profile_id,
                "mentor_name": suggestion.mentor_name,
                "mentor_email": suggestion.mentor_email,
                "mentor_language_id": suggestion.mentor_language_id,
                "mentor_language_name": suggestion.mentor_language_name,
                "mentor_availability_details": suggestion.mentor_availability_details,
                "mentor_exchange_terms": suggestion.mentor_exchange_terms,
                "matched_students": [],
            },
        )
        mentor_group["matched_students"].append(suggestion)

    return [MentorPairingGroupOut(**group) for group in grouped.values()]


def ensure_mentor_profile_schema() -> None:
    inspector = inspect(engine)
    if "mentor_profiles" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("mentor_profiles")}
    alter_statements = []

    if "availability_details" not in existing_columns:
        alter_statements.append("ALTER TABLE mentor_profiles ADD COLUMN availability_details TEXT")
    if "exchange_terms" not in existing_columns:
        alter_statements.append("ALTER TABLE mentor_profiles ADD COLUMN exchange_terms TEXT")

    if not alter_statements:
        return

    with engine.begin() as connection:
        for statement in alter_statements:
            connection.execute(text(statement))


def ensure_user_schema() -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    if "learning_language_id" in existing_columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE users ADD COLUMN learning_language_id INTEGER"))


def sync_mentor_learning_goals(db: Session) -> None:
    mentors = db.query(User).filter(User.role == "mentor").all()
    changed = False
    for mentor in mentors:
        mentor_profile = db.query(MentorProfile).filter(MentorProfile.user_id == mentor.id).first()
        if not mentor_profile:
            continue
        if mentor_profile.requested_language_id is None:
            continue
        if mentor.learning_language_id != mentor_profile.requested_language_id:
            mentor.learning_language_id = mentor_profile.requested_language_id
            changed = True

    if changed:
        db.commit()


ensure_mentor_profile_schema()
ensure_user_schema()


with Session(engine) as bootstrap_db:
    sync_mentor_learning_goals(bootstrap_db)


@app.get("/")
def root() -> dict:
    return {"message": "Nyelvcsere FastAPI backend is running"}

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)) -> User:
    if payload.role not in ALLOWED_REGISTER_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role. Allowed roles: student, mentor")

    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    if payload.role != "mentor" and (
        payload.offered_language_id is not None or payload.requested_language_id is not None
    ):
        raise HTTPException(status_code=400, detail="Language preferences are only allowed for mentor role")

    if payload.role == "student" and payload.learning_language_id is not None:
        learning_language = db.query(Language).filter(Language.id == payload.learning_language_id).first()
        if not learning_language:
            raise HTTPException(status_code=400, detail="Invalid learning_language_id")

    if payload.role == "mentor" and payload.offered_language_id is not None and payload.requested_language_id is not None:
        if payload.offered_language_id == payload.requested_language_id:
            raise HTTPException(status_code=400, detail="A tanított és tanult nyelvek nem lehetnek azonosak")

    if payload.offered_language_id is not None:
        offered_language = db.query(Language).filter(Language.id == payload.offered_language_id).first()
        if not offered_language:
            raise HTTPException(status_code=400, detail="Invalid offered_language_id")

    if payload.requested_language_id is not None:
        requested_language = db.query(Language).filter(Language.id == payload.requested_language_id).first()
        if not requested_language:
            raise HTTPException(status_code=400, detail="Invalid requested_language_id")

    if payload.role == "mentor" and payload.learning_language_id is not None:
        learning_language = db.query(Language).filter(Language.id == payload.learning_language_id).first()
        if not learning_language:
            raise HTTPException(status_code=400, detail="Invalid learning_language_id")

    hashed_password = hash_password(payload.password)
    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hashed_password,
        role=payload.role,
        learning_language_id=(
            payload.requested_language_id if payload.role == "mentor" else payload.learning_language_id
        ),
    )
    try:
        db.add(user)
        db.flush()

        if payload.role == "mentor":
            mentor_profile = MentorProfile(
                user_id=user.id,
                offered_language_id=payload.offered_language_id,
                requested_language_id=payload.requested_language_id,
                session_length_minutes=60,
                availability_details=payload.availability_details,
                exchange_terms=payload.exchange_terms,
            )
            db.add(mentor_profile)

        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise

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
    db: Session = Depends(get_db)
) -> List[User]:
    sync_mentor_learning_goals(db)
    return db.query(User).offset(skip).limit(limit).all()

@app.get("/users/me", response_model=CurrentUserOut)
def read_current_user(
    current_user: Optional[User] = Depends(get_current_user_or_guest),
    db: Session = Depends(get_db),
) -> CurrentUserOut:
    if current_user is None:
        return CurrentUserOut(is_authenticated=False, role=ROLE_GUEST)

    sync_mentor_learning_goals(db)
    db.refresh(current_user)

    return CurrentUserOut(
        is_authenticated=True,
        role=current_user.role,
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        learning_language_id=current_user.learning_language_id,
    )


@app.put("/users/me", response_model=UserOut)
def update_current_user(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    if payload.name is not None:
        current_user.name = payload.name.strip() or current_user.name

    if payload.learning_language_id is not None:
        learning_language = db.query(Language).filter(Language.id == payload.learning_language_id).first()
        if not learning_language:
            raise HTTPException(status_code=400, detail="Invalid learning_language_id")
        current_user.learning_language_id = payload.learning_language_id

    db.commit()
    db.refresh(current_user)
    return current_user

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> User:
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


@app.get("/pairing-suggestions", response_model=List[PairingSuggestionOut])
def pairing_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[PairingSuggestionOut]:
    suggestions = build_pairing_suggestions(db)
    if current_user.role == "mentor":
        current_user_profile = db.query(MentorProfile).filter(MentorProfile.user_id == current_user.id).first()
        if current_user_profile:
            suggestions = [
                suggestion
                for suggestion in suggestions
                if suggestion.mentor_profile_id == current_user_profile.id
                or suggestion.student_id == current_user.id
            ]
    return suggestions


@app.get("/mentor-pairing-groups", response_model=List[MentorPairingGroupOut])
def mentor_pairing_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[MentorPairingGroupOut]:
    groups = build_mentor_pairing_groups(db)
    if current_user.role == "mentor":
        current_user_profile = db.query(MentorProfile).filter(MentorProfile.user_id == current_user.id).first()
        if current_user_profile:
            groups = [group for group in groups if group.mentor_profile_id == current_user_profile.id]
    return groups


@app.get("/pairing-suggestions", response_model=List[PairingSuggestionOut])
def list_pairing_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    if current_user.role not in {"mentor"}:
        raise HTTPException(status_code=403, detail="Only mentors can access pairing suggestions")

    languages = {language.id: language.name for language in db.query(Language).all()}
    students = db.query(User).filter(User.role == "student").all()
    mentor_profiles = db.query(MentorProfile).all()

    suggestions_with_score: List[tuple[int, dict]] = []
    for student in students:
        if student.learning_language_id is None:
            continue
        for mentor_profile in mentor_profiles:
            if mentor_profile.offered_language_id != student.learning_language_id:
                continue

            mentor = db.query(User).filter(User.id == mentor_profile.user_id).first()
            if mentor is None:
                continue

            availability_bonus = 1 if mentor_profile.availability_details else 0
            exchange_terms_bonus = 1 if mentor_profile.exchange_terms else 0
            score = 100 + availability_bonus + exchange_terms_bonus

            suggestions_with_score.append(
                (
                    score,
                    {
                        "student_id": student.id,
                        "student_name": student.name,
                        "student_email": student.email,
                        "learning_language_id": student.learning_language_id,
                        "learning_language_name": languages.get(student.learning_language_id),
                        "mentor_profile_id": mentor_profile.id,
                        "mentor_name": mentor.name,
                        "mentor_email": mentor.email,
                        "mentor_language_id": mentor_profile.offered_language_id,
                        "mentor_language_name": languages.get(mentor_profile.offered_language_id),
                        "mentor_availability_details": mentor_profile.availability_details,
                        "mentor_exchange_terms": mentor_profile.exchange_terms,
                        "match_reason": "Nyelvi cél egyezés"
                        + (" + elérhetőség" if mentor_profile.availability_details else "")
                        + (" + cserefeltételek" if mentor_profile.exchange_terms else ""),
                    },
                )
            )

    suggestions_with_score.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in suggestions_with_score]


@app.get("/mentor-resources", response_model=List[ResourceOut])
def list_mentor_resources(current_user: User = Depends(get_current_user)) -> List[dict]:
    if current_user.role not in {"mentor"}:
        raise HTTPException(status_code=403, detail="Only mentors can access mentor resources")

    return [
        {
            "title": "Párosítási útmutató",
            "description": "Tippek a nyelvi célok alapján történő párosításhoz és az optimális cserealkalmak kiválasztásához.",
            "url": "https://example.com/pairing-guide",
        },
        {
            "title": "Beszélgetési sablonok",
            "description": "Ötletek a kezdő és haladó nyelvi cserealkalmakhoz.",
            "url": "https://example.com/conversation-templates",
        },
        {
            "title": "Közösségi irányelvek",
            "description": "Útmutató a biztonságos és tiszteletteljes közösségi interakciókhoz.",
            "url": "https://example.com/community-guidelines",
        },
    ]


@app.get("/community-interactions")
def list_community_interactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    if current_user.role not in {"mentor"}:
        raise HTTPException(status_code=403, detail="Only mentors can access community interactions")

    recent_sessions = db.query(StudySession).order_by(StudySession.scheduled_time.desc()).limit(10).all()
    recent_progress_logs = db.query(ProgressLog).order_by(ProgressLog.id.desc()).limit(10).all()

    return {
        "recent_sessions": [
            {
                "id": session.id,
                "scheduled_time": session.scheduled_time,
                "status": session.status,
                "mentor_profile_id": session.mentor_profile_id,
                "student_id": session.student_id,
            }
            for session in recent_sessions
        ],
        "recent_progress_logs": [
            {
                "id": log.id,
                "session_id": log.session_id,
                "student_id": log.student_id,
                "notes": log.notes,
                "rating": log.rating,
            }
            for log in recent_progress_logs
        ],
    }


@app.get("/mentor-profile/me", response_model=MentorProfileMeOut)
def get_my_mentor_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MentorProfile:
    if current_user.role != "mentor":
        raise HTTPException(status_code=403, detail="Only mentors can access mentor profile settings")

    mentor_profile = db.query(MentorProfile).filter(MentorProfile.user_id == current_user.id).first()
    if mentor_profile is None:
        mentor_profile = MentorProfile(
            user_id=current_user.id,
            offered_language_id=None,
            requested_language_id=None,
            session_length_minutes=60,
            availability_details=None,
            exchange_terms=None,
        )
        db.add(mentor_profile)
        db.commit()
        db.refresh(mentor_profile)
    return mentor_profile


@app.put("/mentor-profile/me", response_model=MentorProfileMeOut)
def update_my_mentor_profile(
    payload: MentorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MentorProfile:
    if current_user.role != "mentor":
        raise HTTPException(status_code=403, detail="Only mentors can update mentor profile settings")

    mentor_profile = db.query(MentorProfile).filter(MentorProfile.user_id == current_user.id).first()
    if mentor_profile is None:
        mentor_profile = MentorProfile(
            user_id=current_user.id,
            offered_language_id=None,
            requested_language_id=None,
            session_length_minutes=60,
            availability_details=None,
            exchange_terms=None,
        )
        db.add(mentor_profile)
        db.flush()

    if payload.offered_language_id is not None:
        offered_language = db.query(Language).filter(Language.id == payload.offered_language_id).first()
        if not offered_language:
            raise HTTPException(status_code=400, detail="Invalid offered_language_id")
        mentor_profile.offered_language_id = payload.offered_language_id

    if payload.requested_language_id is not None:
        requested_language = db.query(Language).filter(Language.id == payload.requested_language_id).first()
        if not requested_language:
            raise HTTPException(status_code=400, detail="Invalid requested_language_id")
        mentor_profile.requested_language_id = payload.requested_language_id
        current_user.learning_language_id = payload.requested_language_id

    if mentor_profile.offered_language_id is not None and mentor_profile.requested_language_id is not None:
        if mentor_profile.offered_language_id == mentor_profile.requested_language_id:
            raise HTTPException(status_code=400, detail="A tanított és tanult nyelvek nem lehetnek azonosak")

    if payload.session_length_minutes is not None:
        if payload.session_length_minutes < 15 or payload.session_length_minutes > 240:
            raise HTTPException(status_code=400, detail="session_length_minutes must be between 15 and 240")
        mentor_profile.session_length_minutes = payload.session_length_minutes

    if payload.availability_details is not None:
        mentor_profile.availability_details = payload.availability_details.strip() or None

    if payload.exchange_terms is not None:
        mentor_profile.exchange_terms = payload.exchange_terms.strip() or None

    db.commit()
    db.refresh(mentor_profile)
    return mentor_profile


@app.get("/sessions", response_model=List[SessionOut])
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[StudySession]:
    query = db.query(StudySession)
    if current_user.role == "student":
        return query.filter(StudySession.student_id == current_user.id).all()

    if current_user.role == "mentor":
        return (
            query
            .join(MentorProfile, StudySession.mentor_profile_id == MentorProfile.id)
            .filter(MentorProfile.user_id == current_user.id)
            .all()
        )

    return []

@app.get("/progress-logs", response_model=List[ProgressLogOut])
def list_progress_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[ProgressLog]:
    query = db.query(ProgressLog)
    if current_user.role == "student":
        return query.filter(ProgressLog.student_id == current_user.id).all()

    if current_user.role == "mentor":
        return (
            query
            .join(StudySession, ProgressLog.session_id == StudySession.id)
            .join(MentorProfile, StudySession.mentor_profile_id == MentorProfile.id)
            .filter(MentorProfile.user_id == current_user.id)
            .all()
        )

    return []


@app.get("/sessions/{session_id}/progress-log", response_model=Optional[ProgressLogOut])
def get_session_progress_log(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Optional[ProgressLog]:
    db_session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    ensure_session_access(db_session, current_user, db)

    return db.query(ProgressLog).filter(ProgressLog.session_id == session_id).first()


@app.put("/sessions/{session_id}/progress-log", response_model=ProgressLogOut)
def upsert_session_progress_log(
    session_id: int,
    payload: ProgressLogUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressLog:
    db_session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    ensure_session_access(db_session, current_user, db)

    if payload.rating is not None and (payload.rating < 1 or payload.rating > 5):
        raise HTTPException(status_code=400, detail="rating must be between 1 and 5")

    if payload.rating is not None and db_session.status != "completed":
        raise HTTPException(status_code=400, detail="Rating is allowed only for completed sessions")

    progress_log = db.query(ProgressLog).filter(ProgressLog.session_id == session_id).first()
    if progress_log is None:
        progress_log = ProgressLog(
            session_id=session_id,
            student_id=db_session.student_id,
            notes=payload.notes,
            rating=payload.rating,
        )
        db.add(progress_log)
    else:
        progress_log.notes = payload.notes
        progress_log.rating = payload.rating

    db.commit()
    db.refresh(progress_log)
    return progress_log


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

    if db_session.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions for this session")
    
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

    ensure_session_access(db_session, current_user, db)
    
    db.delete(db_session)
    db.commit()
    return None