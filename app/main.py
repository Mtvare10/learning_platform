from fastapi import FastAPI
from . import models
from .database import SessionLocal, engine
from .routes import users, roles, classrooms, lessons, sessions, ai
from .seed import seed_roles
from app import models
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Learning Platform API",
    version="1.0.0",
    description="Role-based learning platform with students and instructors"
)

origins = [
    "http://localhost:8000",  # Example for the same machine
    "http://127.0.0.1:8000",  # Example for the same machine
    "http://your-frontend-url.com", # Replace with your actual HTML page URL and port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Set to True to allow cookies/auth headers for login
    allow_methods=["*"],     # Allows all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],     # Allows all headers
)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

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

app.include_router(ai.router)