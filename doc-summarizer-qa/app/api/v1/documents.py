"""
Document upload and management endpoints.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from datetime import datetime
import uuid
import os

from app.core.config import settings
from app.models.document import DocumentUploadResponse

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF or Text file).
    
    - **file**: Document file to upload (PDF or TXT)
    
    Returns document ID and upload status.
    """
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
        )
    
    # Generate document ID
    doc_id = str(uuid.uuid4())
    
    # TODO: Store file, extract text, save to database
    # For now, return success response
    
    return DocumentUploadResponse(
        doc_id=doc_id,
        filename=file.filename,
        status="uploaded",
        message="Document uploaded successfully. Processing will begin shortly.",
        upload_time=datetime.utcnow()
    )


@router.get("/{doc_id}")
async def get_document(doc_id: str):
    """
    Get document metadata by ID.
    
    - **doc_id**: Document identifier
    """
    # TODO: Fetch from database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Document retrieval not yet implemented"
    )


@router.get("")
async def list_documents(skip: int = 0, limit: int = 100):
    """
    List all documents with pagination.
    
    - **skip**: Number of documents to skip
    - **limit**: Maximum number of documents to return
    """
    # TODO: Fetch from database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Document listing not yet implemented"
    )
