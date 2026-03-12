import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from .models import User
from . import database, models




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login", auto_error=False)

def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, "SUPER_SECRET_KEY", algorithm="HS256")
    
    return encoded_jwt


def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db)
):
    # 1. DEFINE THIS FIRST so it doesn't crash
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    print(f"DEBUG: Token from Header: {token}")
    
    # 2. Check cookie if header is missing
    if not token:
        token = request.cookies.get("access_token")
        print(f"DEBUG: Token from Cookie: {token}")

    # 3. If still None, raise the error (now it will work because it's defined!)
    if not token:
        print("DEBUG: No token found anywhere")
        raise credentials_exception

    try:
        payload = jwt.decode(token, "SUPER_SECRET_KEY", algorithms=["HS256"])
        username: str = payload.get("sub")
        print(f"DEBUG: Decoded username: {username}")
    except Exception as e:
        print(f"DEBUG: JWT Decode Failed: {e}")
        raise credentials_exception
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception
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