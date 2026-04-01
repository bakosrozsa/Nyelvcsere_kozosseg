from datetime import datetime, timedelta

from passlib.context import CryptContext
from database import SessionLocal, engine
from models import Base, Language, MentorProfile, ProgressLog, Session, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing_user = db.query(User).first()
        if existing_user:
            english = db.query(Language).filter(Language.name == "English").first()
            peter = db.query(User).filter(User.email == "peter.student@example.com").first()

            if peter and english and peter.learning_language_id is None:
                peter.learning_language_id = english.id
                db.commit()
                print("Demo tanulo nyelvi cel frissitve.")
            else:
                print("Demo adatok mar leteznek, seed kihagyva.")
            return

        english = Language(name="English")
        hungarian = Language(name="Hungarian")
        german = Language(name="German")
        db.add_all([english, hungarian, german])
        db.flush()

        mentor_user = User(
            name="Kovacs Anna",
            email="anna.mentor@example.com",
            hashed_password=pwd_context.hash("demo123"),
            role="mentor",
        )
        student_user = User(
            name="Nagy Peter",
            email="peter.student@example.com",
            hashed_password=pwd_context.hash("demo123"),
            role="student",
            learning_language_id=english.id,
        )
        db.add_all([mentor_user, student_user])
        db.flush()

        mentor_profile = MentorProfile(
            user_id=mentor_user.id,
            offered_language_id=english.id,
            requested_language_id=hungarian.id,
            session_length_minutes=60,
        )
        db.add(mentor_profile)
        db.flush()

        session = Session(
            student_id=student_user.id,
            mentor_profile_id=mentor_profile.id,
            scheduled_time=datetime.utcnow() + timedelta(days=1),
            status="scheduled",
        )
        db.add(session)
        db.flush()

        progress_log = ProgressLog(
            session_id=session.id,
            student_id=student_user.id,
            notes="A2 szintu beszedgyakorlat, uj szokincs a munkaval kapcsolatban.",
            rating=4,
        )
        db.add(progress_log)

        db.commit()
        print("Demo adatok sikeresen betoltve.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
