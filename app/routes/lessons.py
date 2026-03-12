from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..dependencies import require_role, get_current_user
from typing import List

router = APIRouter()

# 1. FIXED AI CONTENT GENERATION
@router.post("/generate-content-only", response_model=schemas.ContentGenerationResponse)
async def generate_ai_content(
    data: schemas.ContentGenerationRequest,
    instructor: models.User = Depends(require_role("instructor"))
):
    try:
        # Safer way to get the role name
        role_name = instructor.roles[0].name if instructor.roles else "instructor"
        
        # This assumes your agent is imported correctly
        from app.agent import get_tutor_response 
        ai_draft = get_tutor_response(data.prompt, role_name)
        
        return {"content": ai_draft}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent Error: {str(e)}")

# 2. FIXED LESSON CREATION (The source of your AttributeError)
@router.post("/", response_model=schemas.Lesson)
def create_lesson(
    lesson_data: schemas.LessonCreate,
    db: Session = Depends(database.get_db),
    instructor: models.User = Depends(require_role("instructor"))
):
    # Fetch the COURSE that this lesson belongs to
    course = db.query(models.Course).filter(models.Course.id == lesson_data.course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Security Check: Does this instructor own the classroom that owns this course?
    if course.classroom.instructor_id != instructor.id:
        raise HTTPException(status_code=403, detail="You do not have permission to add lessons to this course")

    # Save the lesson using course_id
    new_lesson = models.Lesson(
        title=lesson_data.title,
        content=lesson_data.content or "New Lesson Content",
        course_id=lesson_data.course_id  # FIXED: Match your schema attribute
    )
    
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)

    return new_lesson

# 3. FIXED PERMISSIONS FOR VIEWING
@router.get("/{lesson_id}", response_model=schemas.Lesson)
def read_lesson(lesson_id: int, 
                db: Session = Depends(database.get_db),
                current_user: models.User = Depends(get_current_user)):
    
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Check roles
    user_roles = [r.name.lower() for r in current_user.roles]

    # Admins or the Instructor who owns the classroom
    if "admin" in user_roles:
        return lesson
        
    if "instructor" in user_roles:
        if lesson.course.classroom.instructor_id == current_user.id:
            return lesson
        raise HTTPException(status_code=403, detail="Not your lesson")

    # Students must be enrolled in the classroom that owns the course
    if "student" in user_roles:
        classroom = lesson.course.classroom
        if classroom in current_user.enrolled_classrooms:
            return lesson
        raise HTTPException(status_code=403, detail="Not enrolled in this classroom")

    raise HTTPException(status_code=403, detail="Insufficient permissions")