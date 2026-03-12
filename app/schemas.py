from pydantic import BaseModel, EmailStr, computed_field
from datetime import datetime
from typing import List, Optional


class RoleBase(BaseModel):
    name: str
    description: str | None = None

class Role(RoleBase):
    id: int
    class Config:
        from_attributes = True



    
class AssignRole(BaseModel):
    role_name: str


        

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str



class LessonCreate(BaseModel):
    title: str
    content: str | None = None
    course_id: int

class Lesson(BaseModel):
    id: int
    title: str
    content: str
    course_id: int
    class Config:
        from_attributes = True

class CourseCreate(BaseModel):
    title: str
    classroom_id: int

class Course(BaseModel):
    id: int
    title: str
    classroom_id: int
    lessons: List[Lesson] = []
    class Config:
        from_attributes = True


class ClassroomCreate(BaseModel):
    name: str

class Classroom(BaseModel):
    id: int
    name: str
    instructor_id: int
    courses: List[Course] = []

    class Config:
        from_attributes = True

class AIQuestionRequest(BaseModel):
    lesson_id: int
    question: str



class Session(BaseModel):
    id: int
    lesson_id: int
    start_time: datetime
    is_active: bool

    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    lesson_id: int

class SessionCreate(SessionBase):
    # Optional: you can let start_time be provided or default
    start_time: datetime = None


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    roles: list[Role] = [] 
    @computed_field
    @property
    def role(self) -> str:
        # If the user has roles, return the name of the first one
        # Otherwise, default to "student"
        return self.roles[0].name if self.roles else "student"

    class Config:
        from_attributes = True
  




class JoinRequestSchema(BaseModel):
    id: int
    student_id: int
    instructor_id: int
    status: str
    student: User # This allows req.student.username to work in JS

    class Config:
        from_attributes = True

class ContentGenerationRequest(BaseModel):
    prompt: str

class ContentGenerationResponse(BaseModel):
    content: str