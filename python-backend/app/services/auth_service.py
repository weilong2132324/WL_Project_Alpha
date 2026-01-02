"""Authentication service"""

import logging
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models import User, AuthInfo
from app.utils.auth import hash_password, verify_password, create_access_token
from app.utils.redis_client import get_cache_manager

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user login, registration, and token management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = get_cache_manager()
    
    def register(self, username: str, email: str, password: str) -> Tuple[bool, Optional[User], str]:
        """Register a new user"""
        try:
            # Check if username already exists
            existing_user = self.db.query(User).filter(User.name == username).first()
            if existing_user:
                return False, None, "Username already exists"
            
            # Check if email already exists
            if email:
                existing_email = self.db.query(User).filter(User.email == email).first()
                if existing_email:
                    return False, None, "Email already exists"
            
            # Create new user
            hashed_password = hash_password(password)
            new_user = User(
                name=username,
                email=email,
                password=hashed_password
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            logger.info(f"New user registered: {username}")
            return True, new_user, "User registered successfully"
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to register user: {e}")
            return False, None, f"Registration failed: {str(e)}"
    
    def login(self, username: str, password: str) -> Tuple[bool, Optional[User], Optional[str], str]:
        """Login user and return access token"""
        try:
            # Find user by username
            user = self.db.query(User).filter(User.name == username).first()
            if not user:
                return False, None, None, "Invalid username or password"
            
            # Verify password
            if not verify_password(password, user.password or ""):
                return False, None, None, "Invalid username or password"
            
            # Create access token
            access_token = create_access_token(user.id, user.name)
            
            # Cache user data
            self.cache.cache_user(user.id, user.to_dict(), ttl=86400)  # 24 hours
            
            logger.info(f"User logged in: {username}")
            return True, user, access_token, "Login successful"
        
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False, None, None, f"Login failed: {str(e)}"
    
    def logout(self, user_id: int) -> Tuple[bool, str]:
        """Logout user - invalidate cache"""
        try:
            self.cache.invalidate_user(user_id)
            logger.info(f"User logged out: {user_id}")
            return True, "Logout successful"
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False, f"Logout failed: {str(e)}"
    
    def add_oauth_info(self, user_id: int, auth_type: str, auth_id: str, 
                       access_token: Optional[str] = None, refresh_token: Optional[str] = None) -> Tuple[bool, str]:
        """Link OAuth provider to user account"""
        try:
            # Check if OAuth info already exists
            existing = self.db.query(AuthInfo).filter(
                AuthInfo.user_id == user_id,
                AuthInfo.auth_type == auth_type
            ).first()
            
            if existing:
                # Update existing
                existing.auth_id = auth_id
                existing.access_token = access_token
                existing.refresh_token = refresh_token
            else:
                # Create new
                auth_info = AuthInfo(
                    user_id=user_id,
                    auth_type=auth_type,
                    auth_id=auth_id,
                    access_token=access_token,
                    refresh_token=refresh_token
                )
                self.db.add(auth_info)
            
            self.db.commit()
            
            # Invalidate user cache to refresh auth info
            self.cache.invalidate_user(user_id)
            
            logger.info(f"OAuth info added for user {user_id}: {auth_type}")
            return True, f"{auth_type} account linked successfully"
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add OAuth info: {e}")
            return False, f"Failed to link {auth_type} account: {str(e)}"
    
    def get_user_by_oauth(self, auth_type: str, auth_id: str) -> Optional[User]:
        """Get user by OAuth provider and ID"""
        try:
            auth_info = self.db.query(AuthInfo).filter(
                AuthInfo.auth_type == auth_type,
                AuthInfo.auth_id == auth_id
            ).first()
            
            if auth_info:
                return self.db.query(User).filter(User.id == auth_info.user_id).first()
            
            return None
        except Exception as e:
            logger.error(f"Failed to get user by OAuth: {e}")
            return None
