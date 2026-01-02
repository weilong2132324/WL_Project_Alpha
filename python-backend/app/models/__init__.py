"""Database models for the application"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from app.database import Base


# Association tables for many-to-many relationships
user_groups = Table(
    'user_groups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
)

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

group_roles = Table(
    'group_roles',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

role_rules = Table(
    'role_rules',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('rule_id', Integer, ForeignKey('rules.id'), primary_key=True)
)

post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

post_categories = Table(
    'post_categories',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)


class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete


class User(BaseModel):
    """User model"""
    __tablename__ = 'users'
    
    name = Column(String(100), unique=True, nullable=False)
    email = Column(String(256), nullable=True)
    password = Column(String(256), nullable=True)
    avatar = Column(String(256), nullable=True)
    
    # Relationships
    auth_infos = relationship("AuthInfo", back_populates="user", cascade="all, delete-orphan")
    groups = relationship("Group", secondary=user_groups, back_populates="users")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    likes = relationship("Like", back_populates="user")
    
    def cache_key(self) -> str:
        """Get Redis cache key for this user"""
        return "users:id"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'avatar': self.avatar,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class AuthInfo(BaseModel):
    """OAuth authentication information"""
    __tablename__ = 'auth_infos'
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    url = Column(String(256), nullable=True)
    auth_type = Column(String(256), nullable=False)  # github, wechat, etc
    auth_id = Column(String(256), nullable=False)
    access_token = Column(String(256), nullable=True)
    refresh_token = Column(String(256), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="auth_infos")


class Group(BaseModel):
    """Group/Team model"""
    __tablename__ = 'groups'
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    users = relationship("User", secondary=user_groups, back_populates="groups")
    roles = relationship("Role", secondary=group_roles, back_populates="groups")


class Role(BaseModel):
    """Role model for RBAC"""
    __tablename__ = 'roles'
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    groups = relationship("Group", secondary=group_roles, back_populates="roles")
    rules = relationship("Rule", secondary=role_rules, back_populates="roles")


class Rule(BaseModel):
    """Authorization rule model"""
    __tablename__ = 'rules'
    
    name = Column(String(100), nullable=False)
    resource = Column(String(256), nullable=False)
    operation = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    roles = relationship("Role", secondary=role_rules, back_populates="rules")


class Post(BaseModel):
    """Blog post model"""
    __tablename__ = 'posts'
    
    title = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(500), nullable=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    view_count = Column(Integer, default=0)
    
    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")
    categories = relationship("Category", secondary=post_categories, back_populates="posts")


class Comment(BaseModel):
    """Comment model"""
    __tablename__ = 'comments'
    
    content = Column(Text, nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")


class Like(BaseModel):
    """Like model"""
    __tablename__ = 'likes'
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")


class Tag(BaseModel):
    """Tag model"""
    __tablename__ = 'tags'
    
    name = Column(String(100), unique=True, nullable=False)
    
    # Relationships
    posts = relationship("Post", secondary=post_tags, back_populates="tags")


class Category(BaseModel):
    """Category model"""
    __tablename__ = 'categories'
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    posts = relationship("Post", secondary=post_categories, back_populates="categories")
