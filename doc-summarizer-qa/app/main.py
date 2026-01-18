"""
Main FastAPI application entry point.
"""
import os
import sys
from pathlib import Path

# Print startup message immediately
print("=" * 60)
print("🚀 Starting FastAPI application...")
print("=" * 60)

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
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
        app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
        app.include_router(ai.router, prefix="/api", tags=["AI"])
        print("✅ All routers included")
    except Exception as e:
        print(f"⚠️  Warning: Some routers failed to load: {e}")
        print("   Health endpoint will still work")

    # Serve frontend static files
    frontend_path = Path(__file__).parent.parent / "frontend"
    if frontend_path.exists():
        # Serve static files (CSS, JS, images)
        app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
        
        # Serve frontend HTML at root
        @app.get("/", include_in_schema=False)
        async def read_root():
            """Serve frontend index page."""
            from fastapi.responses import HTMLResponse
            index_path = frontend_path / "index.html"
            if index_path.exists():
                try:
                    with open(index_path, "r", encoding="utf-8") as f:
                        return HTMLResponse(content=f.read())
                except Exception as e:
                    print(f"Error reading index.html: {e}")
                    return HTMLResponse(content=f"<h1>Error loading frontend: {e}</h1>", status_code=500)
            return HTMLResponse(content="<h1>Frontend not found</h1>", status_code=404)
        
        print(f"✅ Frontend integrated from: {frontend_path}")
    else:
        print(f"⚠️  Frontend directory not found at: {frontend_path}, serving API only")

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
