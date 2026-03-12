from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from .. import models, schemas, database
from ..dependencies import require_role, get_current_user
from typing import List



router = APIRouter()

@router.post("/", response_model=schemas.Classroom)
def create_classroom(classroom_data: schemas.ClassroomCreate,
                     db: Session = Depends(database.get_db),
                     instructor: models.User = Depends(require_role("instructor"))):
    """
    Only instructors can create classrooms.
    """
    new_classroom = models.Classroom(
        name=classroom_data.name,
        instructor_id=instructor.id
    )
    db.add(new_classroom)
    db.commit()
    db.refresh(new_classroom)
    return new_classroom


@router.post("/{classroom_id}/join")
def join_classroom(
    classroom_id: int,
    db: Session = Depends(database.get_db),
    student: models.User = Depends(require_role("student"))
):
    classroom = db.query(models.Classroom).get(classroom_id)
    classroom.students.append(student)
    db.commit()
    return {"message": "Joined classroom"}

@router.post("/{classroom_id}/assign-student/{student_id}")
def assign_student_to_classroom(
    classroom_id: int,
    student_id: int,
    db: Session = Depends(database.get_db),
    instructor: models.User = Depends(require_role("instructor"))
):
    """
    Assign a student to a classroom. Instructor can only assign students to classrooms they own.
    """
    classroom = db.query(models.Classroom).filter(models.Classroom.id == classroom_id).first()
    student = db.query(models.User).filter(models.User.id == student_id).first()

    if not classroom or not student:
        raise HTTPException(status_code=404, detail="Classroom or student not found")

    if classroom.instructor_id != instructor.id:
        raise HTTPException(status_code=403, detail="You are not the instructor of this classroom")

    if student not in classroom.students:
        classroom.students.append(student)
        db.commit()

    return {"message": f"Student {student.username} assigned to classroom {classroom.name}"}

@router.get("/", response_model=List[schemas.Classroom])
def get_classrooms(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if any(role.name == "instructor" for role in current_user.roles):
        return db.query(models.Classroom).filter(
            models.Classroom.instructor_id == current_user.id
        ).all()
    else:
        return current_user.enrolled_classrooms
    
@router.get("/enrolled", response_model=List[schemas.Classroom])
def get_enrolled_classrooms(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # This returns classrooms where the student is in the 'students' list
    return current_user.enrolled_classrooms
    
@router.get("/{classroom_id}", response_model=schemas.Classroom)
def get_classroom_detail(
    classroom_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user) # Changed from require_role
):
    classroom = db.query(models.Classroom).options(joinedload(models.Classroom.courses).joinedload(models.Course.lessons)
    ).filter(models.Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="classroom not found")
    is_instructor = classroom.instructor_id == current_user.id
    is_enrolled = current_user in classroom.students
    # Fetch the classroom AND verify the instructor owns it
    

    if not (is_instructor or is_enrolled):
        raise HTTPException(status_code=403, detail="you do not have access to this classroom!")

    return classroom
