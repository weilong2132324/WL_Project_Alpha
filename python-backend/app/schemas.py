"""Pydantic schemas for request/response validation"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# User schemas
class UserBase(BaseModel):
    """Base user schema"""
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    avatar: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[str] = None
    avatar: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)


class UserResponse(UserBase):
    """User response schema"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Authentication schemas
class LoginRequest(BaseModel):
    """Login request schema"""
    name: str
    password: str
    setCookie: Optional[bool] = False


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterRequest(BaseModel):
    """Registration request schema"""
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    password: str = Field(..., min_length=6)


class RegisterResponse(BaseModel):
    """Registration response schema"""
    user: UserResponse
    message: str


# Group schemas
class GroupBase(BaseModel):
    """Base group schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class GroupCreate(GroupBase):
    """Group creation schema"""
    pass


class GroupUpdate(BaseModel):
    """Group update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class GroupResponse(GroupBase):
    """Group response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Post schemas
class PostBase(BaseModel):
    """Base post schema"""
    title: str = Field(..., min_length=1, max_length=256)
    content: str
    summary: Optional[str] = Field(None, max_length=500)


class PostCreate(PostBase):
    """Post creation schema"""
    pass


class PostUpdate(BaseModel):
    """Post update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=256)
    content: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=500)


class PostResponse(PostBase):
    """Post response schema"""
    id: int
    author_id: int
    view_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Role schemas
class RoleBase(BaseModel):
    """Base role schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Role creation schema"""
    pass


class RoleUpdate(BaseModel):
    """Role update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class RoleResponse(RoleBase):
    """Role response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Rule schemas
class RuleBase(BaseModel):
    """Base rule schema"""
    name: str
    resource: str
    operation: str
    description: Optional[str] = None


class RuleCreate(RuleBase):
    """Rule creation schema"""
    pass


class RuleResponse(RuleBase):
    """Rule response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Standard response schema
class StandardResponse(BaseModel):
    """Standard API response schema"""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated response schema"""
    success: bool
    message: str
    data: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
