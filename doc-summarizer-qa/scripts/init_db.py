"""
Database initialization script.
Creates all database tables.

This script can be run locally (with .env file) or can initialize Cloud SQL tables
by setting DATABASE_URL environment variable.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.base import init_db, engine
from app.core.config import settings

def main():
    """Initialize database tables."""
    db_info = "local"
    if settings.DATABASE_URL:
        # Extract connection info for display
        if '@' in settings.DATABASE_URL:
            db_info = settings.DATABASE_URL.split('@')[-1]
        elif '/cloudsql/' in settings.DATABASE_URL:
            # Cloud SQL connection
            db_info = "Cloud SQL (via Unix socket)"
        else:
            db_info = settings.DATABASE_URL.split('//')[-1].split('/')[0] if '//' in settings.DATABASE_URL else "configured"
    
    print(f"Initializing database: {db_info}")
    print()
    
    if not settings.DATABASE_URL:
        print("❌ DATABASE_URL not set!")
        print("   Set it in .env file (for local) or Cloud Run environment variables")
        sys.exit(1)
    
    if engine is None:
        print("❌ Database engine not initialized!")
        print("   Check DATABASE_URL format")
        sys.exit(1)
    
    try:
        result = init_db()
        if result:
            print("✅ Database tables created successfully!")
            print()
            print("📋 Created tables:")
            print("   - documents (document metadata)")
            print("   - requests (request history)")
        else:
            print("⚠️  Database initialization returned False")
            print("   Check the error messages above")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nMake sure:")
        print("1. PostgreSQL is running (or Cloud SQL is accessible)")
        print("2. Database exists (create it if needed)")
        print("3. Connection settings are correct")
        print("4. User has CREATE TABLE permissions")
        sys.exit(1)

if __name__ == "__main__":
    main()
