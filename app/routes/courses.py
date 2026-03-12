from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..dependencies import get_current_user, require_role

router = APIRouter()

@router.post("/", response_model=schemas.Course)
def create_new_course(
    course: schemas.CourseCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(require_role("instructor")) #
):
    # Verify the instructor owns this classroom
    classroom = db.query(models.Classroom).filter(
        models.Classroom.id == course.classroom_id,
        models.Classroom.instructor_id == current_user.id
    ).first()
    
    if not classroom:
        raise HTTPException(status_code=403, detail="You do not have permission to modify this classroom.")
    
    new_course = models.Course(title=course.title, classroom_id=course.classroom_id)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.get("/{course_id}", response_model=schemas.Course)
def get_course_details(course_id: int, db: Session = Depends(database.get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course