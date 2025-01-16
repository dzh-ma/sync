from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    '''User account detaill.'''
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    '''User verification information details.'''
    id: str
    email: EmailStr
    is_verified: bool
    created_at: datetime

    class Config:
        orm_mode = True
