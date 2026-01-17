"""
Main FastAPI application entry point.
"""
import os
import sys

# Print startup message immediately
print("=" * 60)
print("🚀 Starting FastAPI application...")
print("=" * 60)

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    print("✅ FastAPI imported")
    
    from app.api.v1 import health
    print("✅ Health router imported")
    
    from app.core.config import settings
    print("✅ Settings loaded")
    
    app = FastAPI(
        title="AI Document Summarizer & Q&A API",
        description="Production-ready backend for document processing, summarization, and Q&A",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Cloud Run sets PORT environment variable
    PORT = int(os.environ.get("PORT", 8080))
    print(f"✅ Port configured: {PORT}")
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("✅ CORS middleware configured")
    
    # Include routers (lazy import to avoid blocking)
    app.include_router(health.router, tags=["System"])
    print("✅ Health router included")
    
    # Import and include other routers
    try:
        from app.api.v1 import documents, ai
        app.include_router(documents.router, prefix="/documents", tags=["Documents"])
        app.include_router(ai.router, tags=["AI"])
        print("✅ All routers included")
    except Exception as e:
        print(f"⚠️  Warning: Some routers failed to load: {e}")
        print("   Health endpoint will still work")
    
    print("=" * 60)
    print("✅ Application initialized successfully!")
    print(f"🌐 Server ready on port {PORT}")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Fatal error during app initialization: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    # TODO: Close database connections, etc.
    pass
