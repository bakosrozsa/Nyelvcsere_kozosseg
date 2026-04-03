from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum as SAEnum, Boolean, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class UserRole(str, PyEnum):
    student = "student"
    mentor = "mentor"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(
        SAEnum(
            UserRole,
            name="user_role",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    learning_language_id = Column(Integer, ForeignKey("languages.id"), nullable=True)

    mentor_profile = relationship(
        "MentorProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    progress_logs = relationship(
        "ProgressLog",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    sessions_as_student = relationship("Session", back_populates="student")
    learning_language = relationship("Language", foreign_keys=[learning_language_id])

class Language(Base):
    __tablename__ = "languages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class MentorProfile(Base):
    __tablename__ = "mentor_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    offered_language_id = Column(Integer, ForeignKey("languages.id"))
    requested_language_id = Column(Integer, ForeignKey("languages.id"))
    session_length_minutes = Column(Integer, default=60)
    availability_details = Column(Text, nullable=True)
    exchange_terms = Column(Text, nullable=True)

    user = relationship("User", back_populates="mentor_profile")
    offered_language = relationship("Language", foreign_keys=[offered_language_id])
    requested_language = relationship("Language", foreign_keys=[requested_language_id])
    sessions = relationship("Session", back_populates="mentor_profile")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    mentor_profile_id = Column(Integer, ForeignKey("mentor_profiles.id"))
    scheduled_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="scheduled")
    is_group = Column(Boolean, default=False, nullable=False)
    max_students = Column(Integer, nullable=True)

    student = relationship("User", back_populates="sessions_as_student")
    mentor_profile = relationship("MentorProfile", back_populates="sessions")
    progress_log = relationship("ProgressLog", back_populates="session", uselist=False)
    participants = relationship("SessionParticipant", back_populates="session", cascade="all, delete-orphan")


class SessionParticipant(Base):
    __tablename__ = "session_participants"
    __table_args__ = (UniqueConstraint("session_id", "student_id", name="uq_session_participant"),)

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    session = relationship("Session", back_populates="participants")
    student = relationship("User")

class ProgressLog(Base):
    __tablename__ = "progress_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), unique=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    notes = Column(Text)
    rating = Column(Integer)

    session = relationship("Session", back_populates="progress_log")
    student = relationship("User", back_populates="progress_logs")


class SessionEvaluation(Base):
    __tablename__ = "session_evaluations"
    __table_args__ = (UniqueConstraint("session_id", "student_id", name="uq_session_student_evaluation"),)

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notes = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)

    session = relationship("Session")
    student = relationship("User")