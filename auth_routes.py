from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Session as SessionLocal
from schemas import SignUpRequest, LoginRequest
from models import User
from werkzeug.security import generate_password_hash, check_password_hash 
from fastapi_jwt_auth import AuthJWT


from fastapi.encoders import jsonable_encoder

auth_router = APIRouter(prefix='/auth')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@auth_router.post('/signup', response_model=SignUpRequest, status_code=201)
async def signup(user: SignUpRequest, db: Session = Depends(get_db)):


    # check email
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # check username
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
async def login(user: LoginRequest, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()
):
    db_user = Session().query(User).filter(User.username == user.username).first()
    
    if db_user and check_password_hash(db_user.password, user.password):
        access_token = Authorize.create_access_token(subject=db_user.username)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username)
        
        response = {
            "access": access_token,
            "refresh": refresh_token  
        }
        
        return jsonable_encoder(response)
    
    raise HTTPException(status_code=401, detail="Invalid username or password")