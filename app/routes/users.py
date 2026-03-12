from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..hash import hash_password, verify_password
from fastapi.security import OAuth2PasswordRequestForm
from ..dependencies import require_role, create_access_token, get_current_user
from ..models import Role
from typing import List


router = APIRouter()



@router.post("/", response_model=schemas.User)
def create_user(user_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pass = hash_password(user_data.password)

    
    target_role = db.query(Role).filter(Role.name == user_data.role).first()
    if not target_role:
        raise HTTPException(status_code=500, detail="Student role not initialized")
    new_user = models.User(
        username=user_data.username, 
        email=user_data.email,
        hashed_password=hashed_pass,
        roles = [target_role]
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/", response_model=list[schemas.User])
def get_users(db: Session = Depends(database.get_db)):
    return db.query(models.User).all()

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db :Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.User) # Adding the response_model helps catch errors
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user # FastAPI will automatically convert the DB model to the User schema

@router.post("/join-request/{instructor_id}")
def create_join_request(
    instructor_id: int,
    db: Session = Depends(database.get_db),
    current_student: models.User = Depends(get_current_user)
):
    # 1. Quick check: Is the target actually an instructor?
    instructor = db.query(models.User).filter(models.User.id == instructor_id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")

    # 2. Check if a request already exists to prevent spam
    existing_request = db.query(models.JoinRequest).filter(
        models.JoinRequest.student_id == current_student.id,
        models.JoinRequest.instructor_id == instructor_id,
        models.JoinRequest.status == "pending"
    ).first()
    
    if existing_request:
        raise HTTPException(status_code=400, detail="Request already pending")

    # 3. Create the request
    new_request = models.JoinRequest(
        student_id=current_student.id,
        instructor_id=instructor_id,
        status="pending"
    )
    
    db.add(new_request)
    db.commit()
    
    return {"message": "Request sent successfully!"}

@router.post("/requests/{request_id}/accept")
def accept_request(
    request_id: int, 
    classroom_id: int, 
    db: Session = Depends(database.get_db),
    instructor: models.User = Depends(require_role("instructor"))
):
    # 1. Find the request
    join_req = db.query(models.JoinRequest).filter(models.JoinRequest.id == request_id).first()
    if not join_req or join_req.instructor_id != instructor.id:
        raise HTTPException(status_code=404, detail="Request not found")

    # 2. Find the classroom
    classroom = db.query(models.Classroom).filter(models.Classroom.id == classroom_id).first()
    
    # 3. Perform assignment
    student = db.query(models.User).get(join_req.student_id)
    if student not in classroom.students:
        classroom.students.append(student)
    
    # 4. Finalize
    join_req.status = "accepted"
    db.commit()
    return {"message": "Student assigned successfully"}

@router.get("/my-requests", response_model=List[schemas.JoinRequestSchema]) # Add this!
def get_my_requests(
    db: Session = Depends(database.get_db),
    instructor: models.User = Depends(get_current_user)
):
    return db.query(models.JoinRequest).filter(
        models.JoinRequest.instructor_id == instructor.id,
        models.JoinRequest.status == "pending"
    ).all()