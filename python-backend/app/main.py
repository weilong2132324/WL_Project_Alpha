"""Main FastAPI application"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_config
from app.database import get_db_manager
from app.utils.redis_client import get_redis_client
from app.middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    AuthenticationMiddleware,
    ErrorHandlingMiddleware,
    RateLimitMiddleware
)
from app.controllers import auth, users, groups, posts, rbac, docker, kubernetes

logger = logging.getLogger(__name__)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Application starting up...")
    config = get_config()
    
    # Initialize database
    db_manager = get_db_manager()
    db_manager.create_tables()
    logger.info("Database initialized")
    
    # Connect Redis
    redis_client = get_redis_client()
    if redis_client.is_enabled():
        logger.info("Redis connected")
    else:
        logger.warning("Redis is disabled or not available")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")
    redis_client.close()
    db_manager.close()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    config = get_config()
    
    app = FastAPI(
        title="Go Web Init - Python Backend",
        description="A complete web application backend with authentication, authorization, and more",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add middleware in correct order
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(AuthenticationMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(groups.router)
    app.include_router(posts.router)
    app.include_router(rbac.router)
    
    # Conditional routers based on config
    if config.docker.enable:
        app.include_router(docker.router)
    if config.kubernetes.enable:
        app.include_router(kubernetes.router)
    
    # Health check endpoint
    @app.get("/healthz")
    async def health_check():
        return {
            "status": "healthy",
            "version": "1.0.0",
            "environment": config.server.env
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Go Web Init - Python Backend",
            "version": "1.0.0",
            "docs": "/docs"
        }
    
    logger.info("FastAPI application created")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    config = get_config()
    
    uvicorn.run(
        "app.main:app",
        host=config.server.address,
        port=config.server.port,
        reload=config.server.env == "debug",
        log_level="info"
    )
