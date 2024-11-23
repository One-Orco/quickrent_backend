# schemas.py

from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    agent = "agent"
    manager = "manager"
    admin = "admin"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
