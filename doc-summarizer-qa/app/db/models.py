"""
SQLAlchemy database models for PostgreSQL.
"""
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum as SQLEnum
from datetime import datetime
import enum
import uuid

from app.db.base import Base


class DocumentStatus(str, enum.Enum):
    """Document processing status."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class RequestType(str, enum.Enum):
    """Request type for tracking."""
    SUMMARIZE = "summarize"
    QA = "qa"


class Document(Base):
    """Document metadata model."""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False, index=True)
    upload_time = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    status = Column(SQLEnum(DocumentStatus), nullable=False, default=DocumentStatus.PROCESSED, index=True)
    file_size = Column(Integer, nullable=True)
    text_length = Column(Integer, nullable=True)  # Length of extracted text
    chunk_count = Column(Integer, nullable=True)  # Number of chunks
    summary = Column(Text, nullable=True)  # AI-generated summary
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "upload_time": self.upload_time,
            "status": self.status.value,
            "file_size": self.file_size,
            "text_length": self.text_length,
            "chunk_count": self.chunk_count,
            "summary": self.summary,
        }


class Request(Base):
    """Request history model for tracking API usage."""
    __tablename__ = "requests"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    doc_id = Column(String, nullable=False, index=True)
    request_type = Column(SQLEnum(RequestType), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    latency_ms = Column(Integer, nullable=True)  # Request latency in milliseconds
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "doc_id": self.doc_id,
            "request_type": self.request_type.value,
            "timestamp": self.timestamp,
            "latency_ms": self.latency_ms,
        }
