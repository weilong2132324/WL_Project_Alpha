"""Configuration management for the application"""

import os
from typing import Optional, List, Dict, Any
import yaml
from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    """Database configuration"""
    host: str = "localhost"
    port: int = 3306
    name: str = "go-test"
    user: str = "root"
    password: str = "1234567"
    migrate: bool = True
    file: Optional[str] = None  # For SQLite


class RedisConfig(BaseSettings):
    """Redis configuration"""
    enable: bool = True
    host: str = "localhost"
    port: int = 6379
    password: str = "123456"


class RateLimitConfig(BaseSettings):
    """Rate limit configuration"""
    limit_type: str  # "server" or "ip"
    burst: int
    qps: int
    cache_size: int


class ServerConfig(BaseSettings):
    """Server configuration"""
    env: str = "debug"
    address: str = "127.0.0.1"
    port: int = 8000
    graceful_shutdown_period: int = 30
    rate_limits: List[RateLimitConfig] = []
    jwt_secret: str = "weaveserver"
    db_type: str = "mysql"


class DockerConfig(BaseSettings):
    """Docker configuration"""
    enable: bool = False
    host: str = "unix:///var/run/docker.sock"


class KubernetesConfig(BaseSettings):
    """Kubernetes configuration"""
    enable: bool = False
    watch_resources: List[str] = []


class OAuthConfig(BaseSettings):
    """OAuth configuration"""
    client_id: str = ""
    client_secret: str = ""


class AppConfig(BaseSettings):
    """Main application configuration"""
    server: ServerConfig = ServerConfig()
    postgres: DBConfig = DBConfig(port=5432, name="go-test-weave", user="go-test", password="go-test")
    sqlite: DBConfig = DBConfig(file="./config/sqlite.db")
    mysql: DBConfig = DBConfig()
    redis: RedisConfig = RedisConfig()
    docker: DockerConfig = DockerConfig()
    kubernetes: KubernetesConfig = KubernetesConfig()
    oauth: Dict[str, OAuthConfig] = {}


def load_config(config_path: str = "config/app.yaml") -> AppConfig:
    """Load configuration from YAML file"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Parse rate limits
    rate_limits = []
    if 'server' in data and 'rate_limits' in data['server']:
        for rl in data['server']['rate_limits']:
            rate_limits.append(RateLimitConfig(**rl))
    data['server']['rate_limits'] = rate_limits
    
    # Parse OAuth
    oauth_config = {}
    if 'oauth' in data:
        for provider, config in data['oauth'].items():
            oauth_config[provider] = OAuthConfig(**config)
    data['oauth'] = oauth_config
    
    # Create config objects
    if 'server' in data:
        data['server'] = ServerConfig(**data['server'])
    if 'mysql' in data:
        data['mysql'] = DBConfig(**data['mysql'])
    if 'postgres' in data:
        data['postgres'] = DBConfig(**data['postgres'])
    if 'sqlite' in data:
        data['sqlite'] = DBConfig(**data['sqlite'])
    if 'redis' in data:
        data['redis'] = RedisConfig(**data['redis'])
    if 'docker' in data:
        data['docker'] = DockerConfig(**data['docker'])
    if 'kubernetes' in data:
        data['kubernetes'] = KubernetesConfig(**data['kubernetes'])
    
    return AppConfig(**data)


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def set_config(config: AppConfig) -> None:
    """Set the global configuration instance"""
    global _config
    _config = config
