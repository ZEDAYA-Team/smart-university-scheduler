from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from jose import JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from app.database.base import get_db
from app.models.auth import User
from app.security import ALGORITHM, COOKIE_NAME, create_access_token, decode_access_token, verify_password

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str
    panel: str

class UserResponse(BaseModel):
    id: int
    name: str
    role: str

class LoginResponse(BaseModel):
    user: UserResponse

def current_user(token: str | None = Cookie(default=None, alias=COOKIE_NAME), db: Session = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        user_id = int(decode_access_token(token)["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user = db.query(User).options(joinedload(User.role)).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.query(User).options(joinedload(User.role)).filter(User.email == payload.email.strip().lower()).first()
    # Keep this deliberately generic: never disclose an account's portal role.
    if user is None or user.role.name != payload.panel or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    response.set_cookie(key=COOKIE_NAME, value=create_access_token(str(user.user_id), user.role.name), httponly=True, secure=False, samesite="lax", max_age=60 * 60, path="/")
    return LoginResponse(user=UserResponse(id=user.user_id, name=f"{user.first_name} {user.last_name}", role=user.role.name))

@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(current_user)) -> UserResponse:
    return UserResponse(id=user.user_id, name=f"{user.first_name} {user.last_name}", role=user.role.name)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    response.delete_cookie(COOKIE_NAME, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
