from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..dependencies import require_role, get_current_user
from typing import List


router = APIRouter(prefix="/lessons", tags=["lessons"])

@router.post("/", response_model=schemas.Lesson)
def create_lesson(lesson_data: schemas.LessonCreate,
                  db: Session = Depends(database.get_db),
                  instructor: models.User = Depends(require_role("instructor"))):
    """
    Only users with the instructor role can create lessons.
    """
    # Check that the instructor owns the classroom where the lesson will be created
    classroom = db.query(models.Classroom).filter(models.Classroom.id == lesson_data.classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    if classroom.instructor_id != instructor.id:
        raise HTTPException(status_code=403, detail="You are not the instructor for this classroom")

    new_lesson = models.Lesson(
        title=lesson_data.title,
        content=lesson_data.content,
        classroom_id=lesson_data.classroom_id
    )
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)

    return new_lesson


@router.get("/{lesson_id}", response_model=schemas.Lesson)
def read_lesson(lesson_id: int, 
                db: Session = Depends(database.get_db),
                student: models.User = Depends(get_current_user)):
    """
    Students can view a lesson only if they are enrolled in the classroom.
    Instructors can view any lesson they created.
    """
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Admins can always access
    if any(role.name.lower() == "admin" for role in student.roles):
        return lesson

    # Instructors can access lessons they created
    if any(role.name.lower() == "instructor" for role in student.roles):
        if lesson.classroom.instructor_id == student.id:
            return lesson
        else:
            raise HTTPException(status_code=403, detail="Not your lesson")

    # Students can access lessons only if enrolled in the classroom
    if any(role.name.lower() == "student" for role in student.roles):
        if lesson.classroom in student.enrolled_classrooms:
            return lesson
        else:
            raise HTTPException(status_code=403, detail="You are not enrolled in this classroom")

    raise HTTPException(status_code=403, detail="Insufficient permissions")

@router.get("/", response_model=List[schemas.Lesson])
def get_lessons(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    Get all lessons a user can access:
    - Students: only lessons of classrooms they are enrolled in
    - Instructors: only lessons of classrooms they own
    """
    if any(role.name == "instructor" for role in current_user.roles):
        # Instructor sees lessons of classrooms they own
        lessons = db.query(models.Lesson).join(models.Classroom).filter(
            models.Classroom.instructor_id == current_user.id
        ).all()
    else:
        # Student sees lessons only in enrolled classrooms
        lessons = db.query(models.Lesson).join(models.Classroom).join(models.Classroom.students).filter(
            models.User.id == current_user.id
        ).all()

    return lessons
