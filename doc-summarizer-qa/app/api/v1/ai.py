"""
AI endpoints for summarization and Q&A.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
import time

from app.models.ai import SummarizeRequest, SummarizeResponse, QARequest, QAResponse
from app.services.document_storage import DocumentStorage
from app.services.vertex_ai_service import vertex_ai_service
from app.db.base import get_db
from app.db.models import Request, RequestType

router = APIRouter()


@router.post("/documents/{doc_id}/summarize", response_model=SummarizeResponse)
async def summarize_document(
    doc_id: str,
    max_length: int = 500,
    db: Session = Depends(get_db)
):
    """
    Summarize a document using Vertex AI.
    
    - **doc_id**: Document ID to summarize
    - **max_length**: Maximum summary length in words (default: 500, query parameter)
    
    Returns the generated summary.
    """
    start_time = time.time()
    
    # Get document
    storage = DocumentStorage(db)
    document = storage.get_document(doc_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} not found"
        )
    
    # Check if summary already exists
    if document.get("summary"):
        # Return existing summary
        summary = document["summary"]
        word_count = len(summary.split())
        
        return SummarizeResponse(
            doc_id=doc_id,
            summary=summary,
            word_count=word_count
        )
    
    # Get document text
    document_text = storage.get_document_text(doc_id)
    
    if not document_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document content not found for ID {doc_id}"
        )
    
    # Check if Vertex AI is available
    if not vertex_ai_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not available. Please configure GCP_PROJECT_ID and Vertex AI credentials."
        )
    
    # Generate summary
    summary = vertex_ai_service.summarize_text(
        text=document_text,
        max_length=max_length
    )
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate summary. Please try again later."
        )
    
    # Calculate latency
    latency_ms = int((time.time() - start_time) * 1000)
    
    # Store summary in database
    storage.update_document_summary(doc_id, summary)
    
    # Track request
    try:
        request_record = Request(
            doc_id=doc_id,
            request_type=RequestType.SUMMARIZE,
            latency_ms=latency_ms
        )
        db.add(request_record)
        db.commit()
    except Exception as e:
        # Log but don't fail the request
        print(f"Warning: Failed to track request: {str(e)}")
    
    word_count = len(summary.split())
    
    return SummarizeResponse(
        doc_id=doc_id,
        summary=summary,
        word_count=word_count
    )


@router.post("/documents/{doc_id}/qa", response_model=QAResponse)
async def ask_question(
    doc_id: str,
    request: QARequest,
    db: Session = Depends(get_db)
):
    """
    Answer a question about a document using Vertex AI.
    
    - **doc_id**: Document ID (from path)
    - **question**: Question to answer (from request body)
    
    Returns the answer with source chunks.
    """
    # Validate doc_id matches
    if request.doc_id != doc_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document ID in path must match document ID in request body"
        )
    start_time = time.time()
    
    # Get document
    storage = DocumentStorage(db)
    document = storage.get_document(doc_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} not found"
        )
    
    # Get document chunks for context
    chunks = storage.get_document_chunks(doc_id)
    
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document chunks not found for ID {doc_id}"
        )
    
    # Check if Vertex AI is available
    if not vertex_ai_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not available. Please configure GCP_PROJECT_ID and Vertex AI credentials."
        )
    
    # Use all chunks as context (for RAG-lite)
    # In a full RAG system, you'd do semantic search to find relevant chunks
    context = "\n\n".join(chunks)
    
    # Limit context size to avoid token limits (approximately 8000 chars)
    if len(context) > 8000:
        context = context[:8000] + "..."
    
    # Generate answer
    answer = vertex_ai_service.answer_question(
        question=request.question,
        context=context
    )
    
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate answer. Please try again later."
        )
    
    # Calculate latency
    latency_ms = int((time.time() - start_time) * 1000)
    
    # Track request
    try:
        request_record = Request(
            doc_id=doc_id,
            request_type=RequestType.QA,
            latency_ms=latency_ms
        )
        db.add(request_record)
        db.commit()
    except Exception as e:
        # Log but don't fail the request
        print(f"Warning: Failed to track request: {str(e)}")
    
    # Return answer with source chunks (first 3 chunks as sources)
    sources = chunks[:3] if len(chunks) >= 3 else chunks
    
    return QAResponse(
        doc_id=doc_id,
        question=request.question,
        answer=answer,
        sources=sources
    )
