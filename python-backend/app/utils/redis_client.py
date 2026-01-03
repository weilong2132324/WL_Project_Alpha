"""Redis client and caching utilities"""

import json
import logging
from typing import Optional, Any, TypeVar, Generic
import redis
from app.config import get_config

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RedisClient:
    """Redis client wrapper with hash operations"""
    
    def __init__(self):
        self.client = None
        self.enabled = False
    
    def connect(self) -> bool:
        """Connect to Redis"""
        config = get_config()
        redis_config = config.redis
        
        if not redis_config.enable:
            logger.info("Redis is disabled")
            self.enabled = False
            return True
        
        try:
            self.client = redis.Redis(
                host=redis_config.host,
                port=redis_config.port,
                password=redis_config.password if redis_config.password else None,
                db=0,
                decode_responses=False,

                socket_connect_timeout=5,
                socket_timeout=5,
                socket_keepalive=True,
                retry_on_timeout=True,
                health_check_interval=30

            )
            
            # Test connection
            self.client.ping()
            self.enabled = True
            logger.info(f"Connected to Redis at {redis_config.host}:{redis_config.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.enabled = False
            return False
    
    def is_enabled(self) -> bool:
        """Check if Redis is enabled and connected"""
        return self.enabled
    
    def hset(self, key: str, field: str, value: Any) -> bool:
        """Set a hash field value"""
        if not self.enabled:
            return False
        
        try:
            # Serialize value if it's not a string
            if not isinstance(value, str):
                if hasattr(value, 'to_dict'):
                    value = json.dumps(value.to_dict())
                elif isinstance(value, dict):
                    value = json.dumps(value)
                else:
                    value = json.dumps(value, default=str)
            
            self.client.hset(key, field, value)
            return True
        except Exception as e:
            logger.warning(f"Failed to set hash field {field} in key {key}: {e}")
            return False
    
    def hget(self, key: str, field: str) -> Optional[str]:
        """Get a hash field value"""
        if not self.enabled:
            return None
        
        try:
            value = self.client.hget(key, field)
            if value:
                return value.decode('utf-8') if isinstance(value, bytes) else value
            return None
        except Exception as e:
            logger.warning(f"Failed to get hash field {field} from key {key}: {e}")
            return None
    
    def hdel(self, key: str, *fields: str) -> bool:
        """Delete hash fields"""
        if not self.enabled:
            return False
        
        try:
            self.client.hdel(key, *fields)
            return True
        except Exception as e:
            logger.warning(f"Failed to delete hash fields from key {key}: {e}")
            return False
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration"""
        if not self.enabled:
            return False
        
        try:
            if not isinstance(value, str):
                if hasattr(value, 'to_dict'):
                    value = json.dumps(value.to_dict())
                elif isinstance(value, dict):
                    value = json.dumps(value)
                else:
                    value = json.dumps(value, default=str)
            
            self.client.set(key, value, ex=ex)
            return True
        except Exception as e:
            logger.warning(f"Failed to set key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[str]:
        """Get a key value"""
        if not self.enabled:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return value.decode('utf-8') if isinstance(value, bytes) else value
            return None
        except Exception as e:
            logger.warning(f"Failed to get key {key}: {e}")
            return None
    
    def delete(self, *keys: str) -> bool:
        """Delete keys"""
        if not self.enabled:
            return False
        
        try:
            self.client.delete(*keys)
            return True
        except Exception as e:
            logger.warning(f"Failed to delete keys: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.enabled:
            return False
        
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.warning(f"Failed to check key existence {key}: {e}")
            return False
    
    def close(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()
            self.enabled = False
            logger.info("Redis connection closed")


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """Get the Redis client instance"""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
        _redis_client.connect()
    return _redis_client


class CacheManager:
    """Cache manager for common caching operations"""
    
    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
    
    def cache_user(self, user_id: int, user_data: dict, ttl: Optional[int] = None) -> bool:
        """Cache user data"""
        return self.redis.set(f"user:{user_id}", user_data, ex=ttl)
    
    def get_cached_user(self, user_id: int) -> Optional[dict]:
        """Get cached user data"""
        data = self.redis.get(f"user:{user_id}")
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return None
        return None
    
    def invalidate_user(self, user_id: int) -> bool:
        """Invalidate user cache"""
        return self.redis.delete(f"user:{user_id}")
    
    def cache_post(self, post_id: int, post_data: dict, ttl: Optional[int] = 3600) -> bool:
        """Cache post data"""
        return self.redis.set(f"post:{post_id}", post_data, ex=ttl)
    
    def get_cached_post(self, post_id: int) -> Optional[dict]:
        """Get cached post data"""
        data = self.redis.get(f"post:{post_id}")
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return None
        return None
    
    def invalidate_post(self, post_id: int) -> bool:
        """Invalidate post cache"""
        return self.redis.delete(f"post:{post_id}")


def get_cache_manager() -> CacheManager:
    """Get cache manager instance"""
    return CacheManager(get_redis_client())
