"""
Application configuration using Pydantic settings.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI Document Summarizer & Q&A"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "docsummarizer"
    DATABASE_URL: str = ""
    
    # GCP
    GCP_PROJECT_ID: str = ""
    GCP_REGION: str = "us-central1"
    
    # Firestore
    FIRESTORE_COLLECTION_DOCUMENTS: str = "documents"
    
    # Vertex AI
    VERTEX_AI_MODEL: str = "gemini-pro"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".txt"]
    
    # Text Processing
    CHUNK_SIZE: int = 1000  # Characters per chunk
    CHUNK_OVERLAP: int = 200  # Overlap between chunks
    
    # Security
    API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Build DATABASE_URL if not provided
if not settings.DATABASE_URL:
    settings.DATABASE_URL = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
