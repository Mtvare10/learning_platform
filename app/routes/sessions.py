from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from .. import models, schemas, database
from ..dependencies import get_current_user, require_role
from typing import List

router = APIRouter(prefix="/sessions", tags=["sessions"])


# ----------------------------
# Create a session (Instructor only)
# ----------------------------
@router.post("/", response_model=schemas.Session)
def create_session(
    session_data: schemas.SessionCreate,
    db: Session = Depends(database.get_db),
    instructor: models.User = Depends(require_role("instructor"))
):
    """
    Instructors can create a new session for their lessons.
    """
    lesson = db.query(models.Lesson).filter(models.Lesson.id == session_data.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Ensure instructor owns the classroom of this lesson
    if lesson.classroom.instructor_id != instructor.id:
        raise HTTPException(status_code=403, detail="You are not the instructor of this classroom")

    session = models.Session(
        lesson_id=session_data.lesson_id,
        start_time=session_data.start_time,
        is_active=session_data.is_active
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    return session


# -----------------------------
# Student starts a session
# -----------------------------
@router.post("/start/{lesson_id}", response_model=schemas.Session)
def start_session(
    lesson_id: int,
    db: Session = Depends(database.get_db),
    student: models.User = Depends(require_role("student"))
):
    """
    Students can start a session for a lesson they are enrolled in.
    """
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Ensure student is enrolled in the classroom
    if lesson.classroom not in student.enrolled_classrooms:
        raise HTTPException(status_code=403, detail="You are not enrolled in this classroom")

    new_session = models.Session(
        lesson_id=lesson.id,
        start_time=datetime.utcnow(),
        is_active=True
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session

# -----------------------------
# Instructor views sessions for a lesson
# -----------------------------
@router.get("/lesson/{lesson_id}", response_model=list[schemas.Session])
def get_lesson_sessions(
    lesson_id: int,
    db: Session = Depends(database.get_db),
    instructor: models.User = Depends(require_role("instructor"))
):
    """
    Instructors can see all sessions of their lessons.
    """
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    if lesson.classroom.instructor_id != instructor.id:
        raise HTTPException(status_code=403, detail="You are not the instructor for this lesson")

    return lesson.sessions

# -----------------------------
# Admin can view all sessions (optional)
# -----------------------------
@router.get("/all", response_model=list[schemas.Session])
def get_all_sessions(
    db: Session = Depends(database.get_db),
    admin: models.User = Depends(require_role("admin"))
):
    """
    Admins can view all sessions.
    """
    return db.query(models.Session).all()

@router.get("/", response_model=List[schemas.Session])
def get_sessions(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    - Students: only sessions for lessons in classrooms they are enrolled in
    - Instructors: only sessions for lessons in classrooms they own
    """
    if any(role.name == "instructor" for role in current_user.roles):
        # Instructor sees sessions of lessons in classrooms they own
        sessions = db.query(models.Session).join(models.Lesson).join(models.Classroom).filter(
            models.Classroom.instructor_id == current_user.id
        ).all()
    else:
        # Student sees sessions only in enrolled classrooms
        sessions = db.query(models.Session).join(models.Lesson).join(models.Classroom).join(models.Classroom.students).filter(
            models.User.id == current_user.id
        ).all()

    return sessions

@router.put("/{session_id}", response_model=schemas.Session)
def update_session(session_id: int, session_data: schemas.SessionCreate, db: Session = Depends(database.get_db),
                   instructor: models.User = Depends(require_role("instructor"))):
    """
    Instructors can update session details for lessons they own.
    """
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    lesson = session.lesson
    if lesson.classroom.instructor_id != instructor.id:
        raise HTTPException(status_code=403, detail="You are not the instructor of this classroom")

    session.start_time = session_data.start_time
    session.is_active = session_data.is_active
    db.commit()
    db.refresh(session)
    return session


@router.delete("/{session_id}")
def delete_session(session_id: int, db: Session = Depends(database.get_db),
                   instructor: models.User = Depends(require_role("instructor"))):
    """
    Instructors can delete sessions for lessons they own.
    """
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    lesson = session.lesson
    if lesson.classroom.instructor_id != instructor.id:
        raise HTTPException(status_code=403, detail="You are not the instructor of this classroom")

    db.delete(session)
    db.commit()
    return {"message": f"Session {session.id} deleted successfully"}