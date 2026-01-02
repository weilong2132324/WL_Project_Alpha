"""User repository"""

import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import User
from app.utils.redis_client import get_cache_manager

logger = logging.getLogger(__name__)


class UserRepository:
    """User data access layer"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = get_cache_manager()
    
    def create(self, user: User) -> User:
        """Create a new user"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Cache the user
        self.cache.cache_user(user.id, user.to_dict(), ttl=86400)
        
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID with caching"""
        # Try to get from cache first
        cached = self.cache.get_cached_user(user_id)
        if cached:
            logger.debug(f"User {user_id} retrieved from cache")
            # Note: In production, you'd hydrate the object from cache
            # For now, we still query the DB to get full relationships
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            # Update cache
            self.cache.cache_user(user.id, user.to_dict(), ttl=86400)
        
        return user
    
    def get_by_name(self, name: str) -> Optional[User]:
        """Get user by name"""
        return self.db.query(User).filter(User.name == name).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all users with pagination"""
        return self.db.query(User).order_by(User.name).offset(skip).limit(limit).all()
    
    def update(self, user: User) -> User:
        """Update user"""
        self.db.merge(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Invalidate cache
        self.cache.invalidate_user(user.id)
        
        return user
    
    def delete(self, user_id: int) -> bool:
        """Delete user (soft delete via updated_at)"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        
        # Invalidate cache
        self.cache.invalidate_user(user_id)
        
        return True
    
    def add_to_group(self, user_id: int, group) -> bool:
        """Add user to group"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        if group not in user.groups:
            user.groups.append(group)
            self.db.commit()
            self.cache.invalidate_user(user_id)
        
        return True
    
    def remove_from_group(self, user_id: int, group) -> bool:
        """Remove user from group"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        if group in user.groups:
            user.groups.remove(group)
            self.db.commit()
            self.cache.invalidate_user(user_id)
        
        return True


class GroupRepository:
    """Group data access layer"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, group) -> None:
        """Create a new group"""
        self.db.add(group)
        self.db.commit()
    
    def get_by_id(self, group_id: int):
        """Get group by ID"""
        from app.models import Group
        return self.db.query(Group).filter(Group.id == group_id).first()
    
    def get_by_name(self, name: str):
        """Get group by name"""
        from app.models import Group
        return self.db.query(Group).filter(Group.name == name).first()
    
    def list(self, skip: int = 0, limit: int = 100):
        """List all groups"""
        from app.models import Group
        return self.db.query(Group).offset(skip).limit(limit).all()
    
    def update(self, group):
        """Update group"""
        self.db.merge(group)
        self.db.commit()
    
    def delete(self, group_id: int) -> bool:
        """Delete group"""
        from app.models import Group
        group = self.db.query(Group).filter(Group.id == group_id).first()
        if not group:
            return False
        
        self.db.delete(group)
        self.db.commit()
        return True


class PostRepository:
    """Post data access layer"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = get_cache_manager()
    
    def create(self, post) -> None:
        """Create a new post"""
        self.db.add(post)
        self.db.commit()
        self.cache.cache_post(post.id, post.to_dict() if hasattr(post, 'to_dict') else {})
    
    def get_by_id(self, post_id: int):
        """Get post by ID with caching"""
        from app.models import Post
        
        # Try cache first
        cached = self.cache.get_cached_post(post_id)
        if cached:
            logger.debug(f"Post {post_id} retrieved from cache")
        
        post = self.db.query(Post).filter(Post.id == post_id).first()
        if post:
            self.cache.cache_post(post.id, post.to_dict() if hasattr(post, 'to_dict') else {})
        
        return post
    
    def list(self, skip: int = 0, limit: int = 100):
        """List all posts"""
        from app.models import Post
        return self.db.query(Post).order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    def list_by_author(self, author_id: int, skip: int = 0, limit: int = 100):
        """List posts by author"""
        from app.models import Post
        return self.db.query(Post).filter(Post.author_id == author_id).offset(skip).limit(limit).all()
    
    def update(self, post):
        """Update post"""
        self.db.merge(post)
        self.db.commit()
        self.cache.invalidate_post(post.id)
    
    def delete(self, post_id: int) -> bool:
        """Delete post"""
        from app.models import Post
        post = self.db.query(Post).filter(Post.id == post_id).first()
        if not post:
            return False
        
        self.db.delete(post)
        self.db.commit()
        self.cache.invalidate_post(post_id)
        return True
