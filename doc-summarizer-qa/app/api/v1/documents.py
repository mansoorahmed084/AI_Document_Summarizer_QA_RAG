"""
Document upload and management endpoints.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from datetime import datetime
from sqlalchemy.orm import Session
import uuid
import os

from app.core.config import settings
from app.models.document import DocumentUploadResponse, DocumentResponse, DocumentListResponse
from app.services.text_extractor import TextExtractor
from app.utils.chunking import TextChunker
from app.services.document_storage import DocumentStorage
from app.db.base import get_db

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
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
    file_size = len(file_content)
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
        )
    
    # Generate document ID
    doc_id = str(uuid.uuid4())
    
    try:
        # Extract text from document
        extracted_text = TextExtractor.extract(file_content, file_ext)
        
        if not extracted_text or len(extracted_text.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text content found in document"
            )
        
        # Chunk the text for large documents
        chunks = TextChunker.chunk_text(extracted_text)
        
        # Store document (PostgreSQL + Firestore)
        storage = DocumentStorage(db)
        document = storage.store_document(
            doc_id=doc_id,
            filename=file.filename,
            extracted_text=extracted_text,
            chunks=chunks,
            file_size=file_size
        )
        
        status_message = (
            f"Document processed successfully. "
            f"Extracted {len(extracted_text)} characters in {len(chunks)} chunk(s)."
        )
        
        return DocumentUploadResponse(
            doc_id=doc_id,
            filename=file.filename,
            status="processed",
            message=status_message,
            upload_time=document["upload_time"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    db: Session = Depends(get_db)
):
    """
    Get document metadata by ID.
    
    - **doc_id**: Document identifier
    """
    storage = DocumentStorage(db)
    document = storage.get_document(doc_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} not found"
        )
    
    return DocumentResponse(
        id=document["id"],
        filename=document["filename"],
        upload_time=document["upload_time"],
        status=document["status"],
        summary=document.get("summary"),
        file_size=document.get("file_size")
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all documents with pagination.
    
    - **skip**: Number of documents to skip
    - **limit**: Maximum number of documents to return
    """
    storage = DocumentStorage(db)
    documents, total = storage.list_documents(skip=skip, limit=limit)
    
    document_list = [
        DocumentResponse(
            id=doc["id"],
            filename=doc["filename"],
            upload_time=doc["upload_time"],
            status=doc["status"],
            summary=doc.get("summary"),
            file_size=doc.get("file_size")
        )
        for doc in documents
    ]
    
    return DocumentListResponse(
        documents=document_list,
        total=total
    )
