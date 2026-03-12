from fastapi import FastAPI, Request
from . import models
from .database import SessionLocal, engine
from .routes import users, roles, classrooms, lessons, sessions, ai, pages, courses
from .seed import seed_roles
from app import models
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Learning Platform API",
    version="1.0.0",
    description="Role-based learning platform with students and instructors"
)
# 1. Get the directory where THIS file (main.py) lives
current_file_path = os.path.dirname(os.path.realpath(__file__))

# 2. Join it with 'static' to get the full folder path
static_abs_path = os.path.join(current_file_path, "static")

# 3. Mount it so /static/logo.png works
app.mount("/static", StaticFiles(directory=static_abs_path), name="static")
templates = Jinja2Templates(directory="app/templates")


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


@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()

app.include_router(pages.router, tags=["Pages"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(classrooms.router, prefix="/classrooms", tags=["Classrooms"])
app.include_router(roles.router, prefix="/roles", tags=["Roles"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])
app.include_router(courses.router, prefix="/courses", tags=["courses"])
