from fastapi import APIRouter, Depends
from pydantic import BaseModel  # <--- Add this import
from app.dependencies import require_role 
from app.agent import get_tutor_response

# 1. Define the missing AIRequest model
class AIRequest(BaseModel):
    topic: str
    # Add other fields here if needed, e.g., question: str

router = APIRouter(prefix="/ai")

@router.post("/ask")
async def ask_ai(
    request: AIRequest,  # Now 'AIRequest' is defined above!
    user = Depends(require_role("student", "instructor"))
):
    role_name = user.roles[0].name 
    response = get_tutor_response(request.topic, role_name)
    return {"result": response}