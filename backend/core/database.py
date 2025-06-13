"""
Enhanced database configuration with connection pooling and error handling
"""
from contextlib import contextmanager
from typing import Generator
import logging

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy.exc import SQLAlchemyError

from backend.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Create database engine with connection pooling
engine = create_engine(
    settings.database_url,
    # Connection pool settings
    poolclass=QueuePool,
    pool_size=10,          # Number of connections to maintain in pool
    max_overflow=20,       # Maximum overflow connections
    pool_timeout=30,       # Timeout before giving up on getting connection
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True,    # Test connections before using
    echo=settings.debug,   # Log SQL statements if in debug mode
    echo_pool=settings.debug,
    connect_args={
        "connect_timeout": 10,
        "application_name": "kpath_enterprise",
        "options": "-c statement_timeout=30000"  # 30 second statement timeout
    }
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Don't expire objects after commit
)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    Ensures session is closed after use.
    Includes error handling and logging.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Use this when not in a FastAPI dependency context.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error in context: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


# Event listeners for connection pool monitoring
@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Log new database connections"""
    logger.debug(f"New database connection established: {id(dbapi_connection)}")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkouts from pool"""
    logger.debug(f"Connection checked out from pool: {id(dbapi_connection)}")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log connection returns to pool"""
    logger.debug(f"Connection returned to pool: {id(dbapi_connection)}")


class DatabaseError(Exception):
    """Custom database error"""
    pass


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise DatabaseError(f"Database initialization failed: {str(e)}")


def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False
