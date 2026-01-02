"""Database connection and session management"""

from typing import Generator, Optional
from sqlalchemy import create_engine, inspect, event
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from app.config import get_config, DBConfig


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
    
    def create_tables(self):
        """Create all tables"""
        if self.engine is None:
            raise RuntimeError("Database not initialized. Call init_db first.")
        Base.metadata.create_all(bind=self.engine)
    
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
