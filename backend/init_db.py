from datetime import datetime, timedelta

from database import SessionLocal, engine
from models import Base, Language, MentorProfile, ProgressLog, Session, User


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(User).first():
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
            hashed_password="demo_hash_mentor",
            role="mentor",
        )
        student_user = User(
            name="Nagy Peter",
            email="peter.student@example.com",
            hashed_password="demo_hash_student",
            role="student",
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
