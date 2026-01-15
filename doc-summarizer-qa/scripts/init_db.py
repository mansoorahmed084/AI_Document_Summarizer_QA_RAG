"""
Database initialization script.
Creates all database tables.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.base import init_db, engine
from app.core.config import settings

def main():
    """Initialize database tables."""
    print(f"Initializing database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'local'}")
    
    try:
        init_db()
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        print("\nMake sure:")
        print("1. PostgreSQL is running")
        print("2. Database exists (create it if needed)")
        print("3. Connection settings in .env are correct")
        sys.exit(1)

if __name__ == "__main__":
    main()
