"""Group API endpoints"""

import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Group
from app.schemas import GroupCreate, GroupUpdate, GroupResponse
from app.repositories import GroupRepository
from app.utils.errors import NotFoundException, BadRequestException, success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/groups", tags=["groups"])


@router.post("", response_model=GroupResponse, status_code=201)
async def create_group(request: GroupCreate, db: Session = Depends(get_db)):
    """Create a new group"""
    repo = GroupRepository(db)
    
    if repo.get_by_name(request.name):
        raise BadRequestException("Group name already exists")
    
    group = Group(name=request.name, description=request.description)
    repo.create(group)
    
    db.refresh(group)
    return GroupResponse.model_validate(group)


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(group_id: int, db: Session = Depends(get_db)):
    """Get group by ID"""
    repo = GroupRepository(db)
    group = repo.get_by_id(group_id)
    
    if not group:
        raise NotFoundException(f"Group {group_id} not found")
    
    return GroupResponse.model_validate(group)


@router.get("", response_model=list[GroupResponse])
async def list_groups(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """List all groups"""
    repo = GroupRepository(db)
    groups = repo.list(skip=skip, limit=limit)
    return [GroupResponse.model_validate(g) for g in groups]


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(group_id: int, request: GroupUpdate, db: Session = Depends(get_db)):
    """Update group"""
    repo = GroupRepository(db)
    group = repo.get_by_id(group_id)
    
    if not group:
        raise NotFoundException(f"Group {group_id} not found")
    
    if request.name is not None:
        group.name = request.name
    if request.description is not None:
        group.description = request.description
    
    repo.update(group)
    return GroupResponse.model_validate(group)


@router.delete("/{group_id}", status_code=204)
async def delete_group(group_id: int, db: Session = Depends(get_db)):
    """Delete group"""
    repo = GroupRepository(db)
    
    if not repo.delete(group_id):
        raise NotFoundException(f"Group {group_id} not found")
    
    return None
