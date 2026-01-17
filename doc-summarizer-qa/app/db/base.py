"""
Database base configuration and session management.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app.core.config import settings

# Create database engine with connection timeout
# Use lazy initialization - don't connect until first use
# Only create engine if DATABASE_URL is configured
if settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        echo=False,  # Set to True for SQL query logging
        connect_args={"connect_timeout": 5},  # 5 second connection timeout
        poolclass=None,  # Use default pool
        pool_reset_on_return='commit'  # Reset connections properly
    )
else:
    # No database configured - create a dummy engine that will fail gracefully
    engine = None

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Use this in FastAPI route dependencies.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Call this on application startup.
    Does not raise exceptions - fails gracefully if database is unavailable.
    """
    try:
        # Test connection first with timeout
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        # Create tables if connection successful
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        # Don't raise - let the app start even if DB is unavailable
        print(f"⚠️  Database initialization failed: {str(e)}")
        print("   Application will start, but database features may not work")
        return False
