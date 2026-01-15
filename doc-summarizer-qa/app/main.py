"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import health, documents
from app.core.config import settings

app = FastAPI(
    title="AI Document Summarizer & Q&A API",
    description="Production-ready backend for document processing, summarization, and Q&A",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["System"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Initialize database tables
    from app.db.base import init_db
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {str(e)}")
        print("   (This is normal if database doesn't exist yet or connection fails)")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    # TODO: Close database connections, etc.
    pass
