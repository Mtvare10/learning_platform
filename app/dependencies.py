import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from .models import User
from . import database, models




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, "SUPER_SECRET_KEY", algorithm="HS256")
    
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, "SUPER_SECRET_KEY", algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = (
        db.query(models.User)
        .options(joinedload(models.User.roles))  # 🔥 THIS LINE
        .filter(models.User.username == username)
        .first()
    )

    if user is None:
        raise credentials_exception

    return user
def require_role(*allowed_roles: str):
    def checker(current_user: User = Depends(get_current_user)):
        user_roles = {role.name for role in current_user.roles}
        if not user_roles.intersection(set(allowed_roles)):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
        return current_user
    return checker