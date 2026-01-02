"""Database connection and session management"""

import os
import time
import logging
from typing import Generator, Optional
from sqlalchemy import create_engine, inspect, event, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.exc import OperationalError
from app.config import get_config, DBConfig

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
    
    def init_db(self, db_config: Optional[DBConfig] = None):
        """Initialize database connection"""
        config = get_config()
        
        # Prefer DATABASE_URL environment variable (used in Docker)
        db_url = os.environ.get("DATABASE_URL")
        
        if db_url:
            logger.info(f"Using DATABASE_URL from environment")
        else:
            # Fall back to config file
            if db_config is None:
                db_type = config.server.db_type
                if db_type == "mysql":
                    db_config = config.mysql
                elif db_type == "postgres":
                    db_config = config.postgres
                elif db_type == "sqlite":
                    db_config = config.sqlite
                else:
                    raise ValueError(f"Unsupported database type: {db_type}")
            
            # Build connection string
            if config.server.db_type == "sqlite":
                db_url = f"sqlite:///{db_config.file}"
            elif config.server.db_type == "postgres":
                db_url = f"postgresql://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.name}"
            else:  # mysql
                db_url = f"mysql+pymysql://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.name}"
            
            logger.info(f"Using database config from app.yaml")
        
        self.engine = create_engine(
            db_url,
            echo=config.server.env == "debug",
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def create_tables(self, max_retries: int = 30, retry_interval: int = 2):
        """Create all tables with retry logic for database availability"""
        if self.engine is None:
            raise RuntimeError("Database not initialized. Call init_db first.")
        
        for attempt in range(max_retries):
            try:
                # Test connection first
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                # Create tables if connection successful
                Base.metadata.create_all(bind=self.engine)
                logger.info("Database tables created successfully")
                return
            except OperationalError as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}. "
                        f"Retrying in {retry_interval}s..."
                    )
                    time.sleep(retry_interval)
                else:
                    logger.error(f"Failed to connect to database after {max_retries} attempts")
                    raise
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session"""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call init_db first.")
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get the database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.init_db()
    return _db_manager


def get_db() -> Generator[Session, None, None]:
    """Get database session for dependency injection"""
    manager = get_db_manager()
    yield from manager.get_session()
