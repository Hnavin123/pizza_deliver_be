# from pydantic import BaseModel
# from typing import Optional
# from fastapi_jwt_auth import AuthJWT


# class SignUpModel(BaseModel):
#     id:Optional[int]
#     username: str
#     email: str
#     password: str
#     is_staff: Optional[bool] 
#     is_active: Optional[bool] 
    
    
    
#     class Config:
#         orm_mode = True
        
# class Settings(BaseModel):
#     authjwt_secret_key: str = "e8cd61e72cfba5ab215e3028cd4cd1770c01998e55941bcf60307d126ecf2ed6"
    
    
# @AuthJWT.load_config
# def get_config():
#     return Settings()

# class LoginModel(BaseModel):
#     username: str
#     password: str
        

from pydantic import BaseModel, EmailStr
from fastapi_jwt_auth import AuthJWT
import os


# -------- REQUEST SCHEMAS --------
class SignUpRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


# -------- RESPONSE SCHEMA --------
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_staff: bool
    is_active: bool

    class Config:
        orm_mode = True


# -------- JWT SETTINGS --------
class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-secret")


@AuthJWT.load_config
def get_config():
    return Settings()

