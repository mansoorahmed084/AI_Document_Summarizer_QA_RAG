"""
Document-related Pydantic models.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    doc_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    upload_time: datetime = Field(..., description="Upload timestamp")


class DocumentResponse(BaseModel):
    """Response model for a single document."""
    id: str = Field(..., description="Document ID")
    filename: str = Field(..., description="Original filename")
    upload_time: datetime = Field(..., description="Upload timestamp")
    status: str = Field(..., description="Processing status")
    summary: Optional[str] = Field(None, description="Document summary if available")
    file_size: Optional[int] = Field(None, description="File size in bytes")


class DocumentListResponse(BaseModel):
    """Response model for document list."""
    documents: list[DocumentResponse] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")
