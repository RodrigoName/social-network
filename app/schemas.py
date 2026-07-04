# app/schemas.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ----------------------------------------------------------------------
# Authentication schemas
# ----------------------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# ----------------------------------------------------------------------
# User schemas
# ----------------------------------------------------------------------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

    class Config:
        orm_mode = True


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


# ----------------------------------------------------------------------
# Post schemas
# ----------------------------------------------------------------------
class PostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)

    class Config:
        orm_mode = True


class PostRead(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: datetime

    class Config:
        orm_mode = True


# ----------------------------------------------------------------------
# Follow schemas
# ----------------------------------------------------------------------
class FollowCreate(BaseModel):
    followed_id: int

    class Config:
        orm_mode = True


class FollowRead(BaseModel):
    id: int
    follower_id: int
    followed_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ----------------------------------------------------------------------
# Like schemas
# ----------------------------------------------------------------------
class LikeCreate(BaseModel):
    post_id: int

    class Config:
        orm_mode = True


class LikeRead(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        orm_mode = True