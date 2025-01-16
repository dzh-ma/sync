from pydantic import BaseModel, EmailStr
from datetime import datetime
from bson import ObjectId

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_verified: bool
    created_at: datetime

    class Config:
        orm_mode = True
