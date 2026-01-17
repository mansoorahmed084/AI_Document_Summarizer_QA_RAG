"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import health, documents, ai
from app.core.config import settings
import os

app = FastAPI(
    title="AI Document Summarizer & Q&A API",
    description="Production-ready backend for document processing, summarization, and Q&A",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Cloud Run sets PORT environment variable
PORT = int(os.environ.get("PORT", 8080))

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
app.include_router(ai.router, tags=["AI"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    import os
    from app.core.config import settings
    
    # Set GOOGLE_APPLICATION_CREDENTIALS from .env if present
    # This MUST happen before any Google Cloud services are initialized
    if settings.GOOGLE_APPLICATION_CREDENTIALS:
        creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        # Verify the file exists
        if os.path.exists(creds_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
            print(f"✅ Set GOOGLE_APPLICATION_CREDENTIALS: {creds_path}")
        else:
            print(f"⚠️  Warning: Credentials file not found: {creds_path}")
            print("   GCP services will use default credentials or fail gracefully")
    
    # Pre-initialize services now that credentials are set
    # This ensures they're ready when first used
    from app.services.firestore_service import get_firestore_service
    from app.services.vertex_ai_service import get_vertex_ai_service
    
    # Initialize Firestore (will use credentials if set)
    get_firestore_service()
    
    # Initialize Vertex AI (will use credentials if set)
    get_vertex_ai_service()
    
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
