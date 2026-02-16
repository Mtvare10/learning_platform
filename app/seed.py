from sqlalchemy.orm import Session
from .models import Role

def seed_roles(db: Session):
    roles = ["admin", "instructor", "student"]

    for role_name in roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            db.add(Role(name=role_name))
    db.commit()
