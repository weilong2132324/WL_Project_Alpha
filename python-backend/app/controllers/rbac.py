"""RBAC API endpoints"""

import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import RoleCreate, RoleUpdate, RoleResponse, RuleCreate, RuleResponse
from app.services.rbac_service import RBACService
from app.utils.errors import NotFoundException, BadRequestException, success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rbac", tags=["rbac"])


# Role endpoints
@router.post("/roles", response_model=RoleResponse, status_code=201)
async def create_role(request: RoleCreate, db: Session = Depends(get_db)):
    """Create a new role"""
    rbac_service = RBACService(db)
    success, role, message = rbac_service.create_role(request.name, request.description)
    
    if not success:
        raise BadRequestException(message)
    
    return RoleResponse.model_validate(role)


@router.get("/roles")
async def list_roles(skip: int = Query(0, ge=0), limit: int = Query(100), db: Session = Depends(get_db)):
    """List all roles"""
    from app.models import Role
    roles = db.query(Role).offset(skip).limit(limit).all()
    return {"data": [RoleResponse.model_validate(r).model_dump() for r in roles]}


@router.get("/roles/{role_id}")
async def get_role(role_id: int, db: Session = Depends(get_db)):
    """Get role by ID"""
    from app.models import Role
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not role:
        raise NotFoundException(f"Role {role_id} not found")
    
    return RoleResponse.model_validate(role)


# Rule endpoints
@router.post("/rules", response_model=RuleResponse, status_code=201)
async def create_rule(request: RuleCreate, db: Session = Depends(get_db)):
    """Create a new authorization rule"""
    rbac_service = RBACService(db)
    success, rule, message = rbac_service.create_rule(
        request.name,
        request.resource,
        request.operation,
        request.description
    )
    
    if not success:
        raise BadRequestException(message)
    
    return RuleResponse.model_validate(rule)


@router.get("/rules")
async def list_rules(skip: int = Query(0, ge=0), limit: int = Query(100), db: Session = Depends(get_db)):
    """List all rules"""
    from app.models import Rule
    rules = db.query(Rule).offset(skip).limit(limit).all()
    return {"data": [RuleResponse.model_validate(r).model_dump() for r in rules]}


@router.get("/rules/{rule_id}")
async def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get rule by ID"""
    from app.models import Rule
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    
    if not rule:
        raise NotFoundException(f"Rule {rule_id} not found")
    
    return RuleResponse.model_validate(rule)


# Permission endpoints
@router.post("/users/{user_id}/roles/{role_id}")
async def assign_role_to_user(user_id: int, role_id: int, db: Session = Depends(get_db)):
    """Assign role to user"""
    rbac_service = RBACService(db)
    success, message = rbac_service.assign_role_to_user(user_id, role_id)
    
    if not success:
        raise BadRequestException(message)
    
    return success_response(message)


@router.delete("/users/{user_id}/roles/{role_id}", status_code=204)
async def remove_role_from_user(user_id: int, role_id: int, db: Session = Depends(get_db)):
    """Remove role from user"""
    rbac_service = RBACService(db)
    success, message = rbac_service.remove_role_from_user(user_id, role_id)
    
    if not success:
        raise BadRequestException(message)
    
    return None


@router.post("/roles/{role_id}/rules/{rule_id}")
async def assign_rule_to_role(role_id: int, rule_id: int, db: Session = Depends(get_db)):
    """Assign rule to role"""
    rbac_service = RBACService(db)
    success, message = rbac_service.assign_rule_to_role(role_id, rule_id)
    
    if not success:
        raise BadRequestException(message)
    
    return success_response(message)


@router.get("/users/{user_id}/permissions")
async def get_user_permissions(user_id: int, db: Session = Depends(get_db)):
    """Get user permissions"""
    rbac_service = RBACService(db)
    permissions = rbac_service.get_user_permissions(user_id)
    
    return {
        "success": True,
        "data": [{"resource": r, "operation": o} for r, o in permissions]
    }


@router.post("/check")
async def check_permission(user_id: int, resource: str, operation: str, db: Session = Depends(get_db)):
    """Check if user has permission"""
    rbac_service = RBACService(db)
    has_permission = rbac_service.check_permission(user_id, resource, operation)
    
    return {
        "success": True,
        "has_permission": has_permission
    }
