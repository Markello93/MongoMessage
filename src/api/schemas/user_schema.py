from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserAuth(BaseModel):
    email: EmailStr = Field(..., description="user email")
    username: str = Field(..., min_length=5, max_length=50, description="user username")
    password: str = Field(..., min_length=5, max_length=24, description="user password")


class UserCreate(BaseModel):
    user_id: UUID
    username: str
    email: EmailStr


class UserOut(BaseModel):
    user_id: UUID
    username: str
    email: EmailStr
    first_name: Optional[str]
    phone: Optional[str] = None
    picture: Optional[str] = None
    last_name: Optional[str]


class UserFind(BaseModel):
    username: str
    first_name: Optional[str]
    phone: Optional[str] = None
    picture: Optional[str] = None
    last_name: Optional[str]


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    picture: Optional[str] = None
