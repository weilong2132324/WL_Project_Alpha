"""Post API endpoints"""

import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Post
from app.schemas import PostCreate, PostUpdate, PostResponse
from app.repositories import PostRepository
from app.utils.errors import NotFoundException, success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("", response_model=PostResponse, status_code=201)
async def create_post(request: PostCreate, db: Session = Depends(get_db)):
    """Create a new post"""
    repo = PostRepository(db)
    
    # Get author_id from request context
    # In real implementation, get from authenticated user
    post = Post(
        title=request.title,
        content=request.content,
        summary=request.summary,
        author_id=1  # Should come from authenticated user
    )
    
    repo.create(post)
    db.refresh(post)
    return PostResponse.model_validate(post)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get post by ID"""
    repo = PostRepository(db)
    post = repo.get_by_id(post_id)
    
    if not post:
        raise NotFoundException(f"Post {post_id} not found")
    
    # Increment view count
    post.view_count = (post.view_count or 0) + 1
    db.commit()
    
    return PostResponse.model_validate(post)


@router.get("", response_model=list[PostResponse])
async def list_posts(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """List all posts"""
    repo = PostRepository(db)
    posts = repo.list(skip=skip, limit=limit)
    return [PostResponse.model_validate(p) for p in posts]


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, request: PostUpdate, db: Session = Depends(get_db)):
    """Update post"""
    repo = PostRepository(db)
    post = repo.get_by_id(post_id)
    
    if not post:
        raise NotFoundException(f"Post {post_id} not found")
    
    if request.title is not None:
        post.title = request.title
    if request.content is not None:
        post.content = request.content
    if request.summary is not None:
        post.summary = request.summary
    
    repo.update(post)
    return PostResponse.model_validate(post)


@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    """Delete post"""
    repo = PostRepository(db)
    
    if not repo.delete(post_id):
        raise NotFoundException(f"Post {post_id} not found")
    
    return None
