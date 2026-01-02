"""Authentication utilities and JWT handling"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from app.config import get_config

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """JWT token data"""
    user_id: int
    username: str
    exp: Optional[datetime] = None


class TokenClaims(BaseModel):
    """JWT token claims"""
    sub: str  # user_id
    name: str  # username
    iat: int  # issued at
    exp: int  # expiration
    aud: str = "weave-server"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    config = get_config()
    
    if expires_delta is None:
        expires_delta = timedelta(days=7)  # Default 7 days
    
    now = datetime.utcnow()
    expire = now + expires_delta
    
    to_encode = {
        "sub": str(user_id),
        "name": username,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "aud": "weave-server"
    }
    
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            config.server.jwt_secret,
            algorithm="HS256"
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create JWT token: {e}")
        raise


def verify_token(token: str) -> Optional[TokenData]:
    """Verify a JWT token and return the token data"""
    config = get_config()
    
    try:
        payload = jwt.decode(
            token,
            config.server.jwt_secret,
            algorithms=["HS256"],
            audience="weave-server"
        )
        
        user_id: str = payload.get("sub")
        username: str = payload.get("name")
        
        if user_id is None or username is None:
            logger.warning("Invalid token claims")
            return None
        
        return TokenData(
            user_id=int(user_id),
            username=username
        )
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        return None


def extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """Extract JWT token from Authorization header"""
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]
