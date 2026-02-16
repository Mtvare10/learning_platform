from fastapi import FastAPI
from . import models
from .database import SessionLocal, engine
from .routes import users, roles, classrooms, lessons, sessions
from .seed import seed_roles
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Learning Platform API",
    version="1.0.0",
    description="Role-based learning platform with students and instructors"
)

@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()


app.include_router(users.router)

app.include_router(classrooms.router)

app.include_router(roles.router)

app.include_router(sessions.router)

app.include_router(lessons.router)
