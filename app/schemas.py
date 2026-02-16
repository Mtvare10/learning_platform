from pydantic import BaseModel, EmailStr
from datetime import datetime


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





class ClassroomCreate(BaseModel):
    name: str

class Classroom(BaseModel):
    id: int
    name: str
    instructor_id: int

    class Config:
        from_attributes = True

class LessonBase(BaseModel):
    title: str
    content: str | None = None
    classroom_id: int

    class Config:
        from_attributes = True

class LessonCreate(BaseModel):
    title: str
    content: str | None = None
    classroom_id: int

class Lesson(LessonBase):
    id: int
    class Config:
        from_attributes = True

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
    items: list[Lesson] = []
    roles: list[Role] = [] 
    class Config:
        from_attributes = True