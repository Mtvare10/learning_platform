from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from ..dependencies import get_current_user

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/dashboard")
def dashboard(
    request: Request,
    user = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user
        }
    )

@router.get("/lessons-page")
def lessons_page(request: Request):
    return templates.TemplateResponse("lessons.html", {"request": request})

@router.get("/classrooms-page")
def classrooms_page(request: Request):
    return templates.TemplateResponse("classrooms.html", {"request": request})

@router.get("/ai-lesson-architect")
def create_course_page(
    request: Request,
    user = Depends(get_current_user) # Ensures only logged-in users can see the page
):
    return templates.TemplateResponse(
        "ai-lesson-architect.html", 
        {"request": request, "user": user}
    )

@router.get("/create-classroom-page")
def create_classroom_page(request: Request):
    return templates.TemplateResponse("create-classroom.html", {"request": request})

@router.get("/my-classrooms-page")
def my_classrooms_page(request: Request):
    return templates.TemplateResponse("my-classrooms.html", {"request": request})

@router.get("/classroom-detail-page")
def classroom_detail_page(request: Request):
    return templates.TemplateResponse("classroom-detail.html", {"request": request})

@router.get("/requests-page")
def requests_page(
    request: Request,
    user = Depends(get_current_user) # Security: User must be logged in
):
    return templates.TemplateResponse(
        "requests.html", 
        {"request": request, "user": user}
    )

@router.get("/my-enrolled-classrooms")
def my_enrolled_classrooms_page(request: Request):
    return templates.TemplateResponse("student-classrooms.html", {"request": request})

@router.get("/lesson-view")
def lesson_view_page(request: Request):
    return templates.TemplateResponse("lesson-view.html", {"request": request})

@router.get("/courses-page")
def courses_page(request: Request):
    return templates.TemplateResponse("courses.html", {"request": request})