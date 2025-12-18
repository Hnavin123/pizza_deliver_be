
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from schemas import SignUpModel, LoginModel, UserResponse 
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT

auth_router = APIRouter(prefix="/auth")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@auth_router.post("/signup", response_model=UserResponse, status_code=201)
async def signup(user: SignUpModel, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



@auth_router.post("/login")
async def login(
    user: LoginModel,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user or not check_password_hash(db_user.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = Authorize.create_access_token(subject=db_user.username)
    refresh_token = Authorize.create_refresh_token(subject=db_user.username)

    return {
        "access": access_token,
        "refresh": refresh_token
    }
