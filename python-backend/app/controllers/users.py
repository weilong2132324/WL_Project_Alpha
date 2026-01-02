"""User API endpoints"""

import logging
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse, StandardResponse
from app.repositories import UserRepository
from app.utils.errors import NotFoundException, BadRequestException, success_response
from app.utils.auth import hash_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(request: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    repo = UserRepository(db)
    
    # Check if user exists
    if repo.get_by_name(request.name):
        raise BadRequestException("Username already exists")
    
    # Create user
    user = User(
        name=request.name,
        email=request.email,
        password=hash_password(request.password),
        avatar=request.avatar
    )
    
    user = repo.create(user)
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    
    if not user:
        raise NotFoundException(f"User {user_id} not found")
    
    return UserResponse.model_validate(user)


@router.get("", response_model=list[UserResponse])
async def list_users(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """List all users"""
    repo = UserRepository(db)
    users = repo.list(skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, request: UserUpdate, db: Session = Depends(get_db)):
    """Update user"""
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    
    if not user:
        raise NotFoundException(f"User {user_id} not found")
    
    # Update fields
    if request.email is not None:
        user.email = request.email
    if request.avatar is not None:
        user.avatar = request.avatar
    if request.password is not None:
        user.password = hash_password(request.password)
    
    user = repo.update(user)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user"""
    repo = UserRepository(db)
    
    if not repo.delete(user_id):
        raise NotFoundException(f"User {user_id} not found")
    
    return None


@router.post("/{user_id}/groups/{group_id}")
async def add_user_to_group(user_id: int, group_id: int, db: Session = Depends(get_db)):
    """Add user to group"""
    from app.repositories import GroupRepository
    
    user_repo = UserRepository(db)
    group_repo = GroupRepository(db)
    
    group = group_repo.get_by_id(group_id)
    if not group:
        raise NotFoundException(f"Group {group_id} not found")
    
    if not user_repo.add_to_group(user_id, group):
        raise NotFoundException(f"User {user_id} not found")
    
    return success_response("User added to group")


@router.delete("/{user_id}/groups/{group_id}", status_code=204)
async def remove_user_from_group(user_id: int, group_id: int, db: Session = Depends(get_db)):
    """Remove user from group"""
    from app.repositories import GroupRepository
    
    user_repo = UserRepository(db)
    group_repo = GroupRepository(db)
    
    group = group_repo.get_by_id(group_id)
    if not group:
        raise NotFoundException(f"Group {group_id} not found")
    
    if not user_repo.remove_from_group(user_id, group):
        raise NotFoundException(f"User {user_id} not found")
    
    return None


@router.get("/{user_id}/groups")
async def get_user_groups(user_id: int, db: Session = Depends(get_db)):
    """Get user's groups"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise NotFoundException(f"User {user_id} not found")
    
    return {
        "success": True,
        "data": [{"id": g.id, "name": g.name} for g in user.groups]
    }
