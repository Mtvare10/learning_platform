from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.dependencies import require_role # Ensure get_db is imported
from app.agent import get_tutor_response, get_student_tutor_response
from app import models, schemas, database
# 1. Define the missing AIRequest model
class AIRequest(BaseModel):
    topic: str
    classroom_id: int
    # Add other fields here if needed, e.g., question: str

router = APIRouter()

@router.post("/generate-lesson/{course_id}")
async def generate_ai_lesson(
    course_id: int,
    request: AIRequest,  # Now 'AIRequest' is defined above!
    db: Session = Depends(database.get_db),
    user = Depends(require_role("instructor"))
):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    role_name = user.roles[0].name 
    instruction = f"Create a full, structured educational lesson about {request.topic}."
    ai_content = get_tutor_response(instruction, role_name)
    # try:
    #     new_lesson = models.Lesson(
    #         title=f"AI Generated: {request.topic}",
    #         content=ai_content,
    #         classroom_id=request.classroom_id
    #     )
    #     db.add(new_lesson)
    #     db.commit()
    #     db.refresh(new_lesson)
        
    #     return {
    #         "message": "Course generated and saved!",
    #         "lesson_id": new_lesson.id,
    #         "content": ai_content
    #     }
    # except Exception as e:
    #     db.rollback()
    #     raise HTTPException(status_code=500, detail="Failed to save generated lesson")
    return {
        "content": ai_content
    }

@router.post("/ask-tutor")
def ask_tutor(
    request: schemas.AIQuestionRequest, # You'll need to define this in schemas
    db: Session = Depends(database.get_db)
):
    # 1. Fetch the lesson from the database
    lesson = db.query(models.Lesson).filter(models.Lesson.id == request.lesson_id).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")

    # 2. Get the answer from your new student agent
    try:
        answer = get_student_tutor_response(
            student_question=request.question,
            lesson_title=lesson.title,
            lesson_content=lesson.content
        )
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))