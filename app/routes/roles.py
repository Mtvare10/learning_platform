from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..dependencies import require_role, get_current_user

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/bootstrap-admin", response_model=schemas.Role)
def bootstrap_admin(db: Session = Depends(database.get_db)):
    """
    One-time setup: create the 'admin' role and first admin user.
    Call this only once when setting up the system.
    """
    # Check if admin role already exists
    admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
    if admin_role:
        raise HTTPException(status_code=400, detail="Admin role already exists")

    # Create admin role
    admin_role = models.Role(name="admin", description="Administrator role")
    db.add(admin_role)
    db.commit()
    db.refresh(admin_role)

    # Create first admin user
    existing_admin_user = db.query(models.User).filter(models.User.username == "admin").first()
    if not existing_admin_user:
        from ..hash import hash_password
        admin_user = models.User(
            username="admin",
            email="admin@example.com",
            hashed_password=hash_password("admin123")
        )
        admin_user.roles.append(admin_role)
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

    return admin_role

@router.post("/", response_model=schemas.Role)
def create_role(role: schemas.RoleBase, db: Session = Depends(database.get_db),
                admin: models.User = Depends(require_role("admin"))):
    existing_role = db.query(models.Role).filter(models.Role.name == role.name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role already exists")

    new_role = models.Role(name=role.name, description=role.description)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


@router.get("/", response_model=list[schemas.Role])
def list_roles(db: Session = Depends(database.get_db),
               user: models.User = Depends(get_current_user)):
    return db.query(models.Role).all()


@router.post("/assign/{user_id}/{role_id}")
def assign_role(user_id: int, role_id: int, db: Session = Depends(database.get_db),
                admin: models.User = Depends(require_role("admin"))):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    role = db.query(models.Role).filter(models.Role.id == role_id).first()

    if not user or not role:
        raise HTTPException(status_code=404, detail="User or role not found")

    if role not in user.roles:
        user.roles.append(role)
        db.commit()
    return {"message": f"Role '{role.name}' assigned to user '{user.username}'"}