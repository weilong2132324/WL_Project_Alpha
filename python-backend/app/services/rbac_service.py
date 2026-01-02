"""RBAC authorization system"""

import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import User, Role, Rule, Group

logger = logging.getLogger(__name__)


class RBACService:
    """Role-Based Access Control service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_role(self, name: str, description: Optional[str] = None) -> Tuple[bool, Optional[Role], str]:
        """Create a new role"""
        try:
            existing = self.db.query(Role).filter(Role.name == name).first()
            if existing:
                return False, None, "Role already exists"
            
            role = Role(name=name, description=description)
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
            
            logger.info(f"Role created: {name}")
            return True, role, "Role created successfully"
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create role: {e}")
            return False, None, str(e)
    
    def create_rule(self, name: str, resource: str, operation: str, 
                   description: Optional[str] = None) -> Tuple[bool, Optional[Rule], str]:
        """Create a new authorization rule"""
        try:
            rule = Rule(name=name, resource=resource, operation=operation, description=description)
            self.db.add(rule)
            self.db.commit()
            self.db.refresh(rule)
            
            logger.info(f"Rule created: {name} ({resource}:{operation})")
            return True, rule, "Rule created successfully"
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create rule: {e}")
            return False, None, str(e)
    
    def assign_role_to_user(self, user_id: int, role_id: int) -> Tuple[bool, str]:
        """Assign a role to a user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "User not found"
            
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if not role:
                return False, "Role not found"
            
            # Check if already assigned
            if role in user.roles:
                return False, "Role already assigned to user"
            
            user.roles.append(role)
            self.db.commit()
            
            logger.info(f"Role {role.name} assigned to user {user_id}")
            return True, "Role assigned successfully"
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to assign role: {e}")
            return False, str(e)
    
    def remove_role_from_user(self, user_id: int, role_id: int) -> Tuple[bool, str]:
        """Remove a role from a user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "User not found"
            
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if not role:
                return False, "Role not found"
            
            if role not in user.roles:
                return False, "Role not assigned to user"
            
            user.roles.remove(role)
            self.db.commit()
            
            logger.info(f"Role {role.name} removed from user {user_id}")
            return True, "Role removed successfully"
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to remove role: {e}")
            return False, str(e)
    
    def assign_rule_to_role(self, role_id: int, rule_id: int) -> Tuple[bool, str]:
        """Assign a rule to a role"""
        try:
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if not role:
                return False, "Role not found"
            
            rule = self.db.query(Rule).filter(Rule.id == rule_id).first()
            if not rule:
                return False, "Rule not found"
            
            if rule in role.rules:
                return False, "Rule already assigned to role"
            
            role.rules.append(rule)
            self.db.commit()
            
            logger.info(f"Rule {rule.name} assigned to role {role.name}")
            return True, "Rule assigned successfully"
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to assign rule: {e}")
            return False, str(e)
    
    def check_permission(self, user_id: int, resource: str, operation: str) -> bool:
        """Check if user has permission for a resource operation"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Get all roles for user (directly and through groups)
            roles = set(user.roles)
            for group in user.groups:
                roles.update(group.roles)
            
            # Check if any role has the required permission
            for role in roles:
                for rule in role.rules:
                    if rule.resource == resource and rule.operation == operation:
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to check permission: {e}")
            return False
    
    def get_user_permissions(self, user_id: int) -> List[Tuple[str, str]]:
        """Get all permissions for a user as (resource, operation) tuples"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            permissions = set()
            
            # Get permissions from direct roles
            for role in user.roles:
                for rule in role.rules:
                    permissions.add((rule.resource, rule.operation))
            
            # Get permissions from group roles
            for group in user.groups:
                for role in group.roles:
                    for rule in role.rules:
                        permissions.add((rule.resource, rule.operation))
            
            return list(permissions)
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return []
