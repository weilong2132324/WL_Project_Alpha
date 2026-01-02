"""Authentication API endpoints"""

import json
import logging
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, UserResponse, StandardResponse
from app.utils.errors import UnauthorizedException, BadRequestException, success_response, error_response
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/user", response_model=RegisterResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    auth_service = AuthService(db)
    
    success, user, message = auth_service.register(
        username=request.name,
        email=request.email,
        password=request.password
    )
    
    if not success:
        raise BadRequestException(message)
    
    return RegisterResponse(
        user=UserResponse.model_validate(user),
        message=message
    )


@router.post("/token")
async def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Login user and get access token"""
    auth_service = AuthService(db)
    
    success, user, token, message = auth_service.login(
        username=request.name,
        password=request.password
    )
    
    if not success:
        raise UnauthorizedException(message)
    
    user_response = UserResponse.model_validate(user)
    
    # Set cookie if requested
    if request.setCookie:
        import urllib.parse
        user_cookie = json.dumps({
            "id": user_response.id,
            "name": user_response.name,
            "email": user_response.email,
            "avatar": user_response.avatar,
        })
        # URL encode the JSON for cookie safety
        encoded_cookie = urllib.parse.quote(user_cookie)
        response.set_cookie(
            key="loginUser",
            value=encoded_cookie,
            max_age=86400,  # 1 day
            path="/",
            httponly=False,  # Allow JS access
            samesite="lax"
        )
    
    return LoginResponse(
        access_token=token,
        user=user_response
    )


@router.post("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    """Logout user"""
    user_id = request.state.user_id
    auth_service = AuthService(db)
    
    success, message = auth_service.logout(user_id)
    
    if not success:
        raise BadRequestException(message)
    
    return success_response(message)


@router.post("/refresh")
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    """Refresh access token"""
    from app.utils.auth import create_access_token
    
    user_id = request.state.user_id
    username = request.state.username
    
    # Create new token
    new_token = create_access_token(user_id, username)
    
    return success_response(
        "Token refreshed successfully",
        {"access_token": new_token, "token_type": "bearer"}
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current user info"""
    user_id = request.state.user_id
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException("User not found")
    
    return UserResponse.model_validate(user)
