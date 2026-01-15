"""
Document storage service using PostgreSQL (metadata) and Firestore (content).
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models import Document, DocumentStatus
from app.services.firestore_service import firestore_service


class DocumentStorage:
    """
    Document storage service.
    Uses PostgreSQL for metadata and Firestore for content/chunks.
    """
    
    def __init__(self, db: Session):
        """
        Initialize storage with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def store_document(
        self,
        doc_id: str,
        filename: str,
        extracted_text: str,
        chunks: List[str],
        file_size: int
    ) -> dict:
        """
        Store document metadata and content.
        
        Args:
            doc_id: Document ID
            filename: Original filename
            extracted_text: Extracted text content
            chunks: Text chunks
            file_size: File size in bytes
            
        Returns:
            Document metadata dictionary
        """
        # Store metadata in PostgreSQL
        document = Document(
            id=doc_id,
            filename=filename,
            upload_time=datetime.utcnow(),
            status=DocumentStatus.PROCESSED,
            file_size=file_size,
            text_length=len(extracted_text),
            chunk_count=len(chunks),
            summary=None,
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        # Store content in Firestore (or fallback to in-memory if unavailable)
        firestore_success = firestore_service.store_document_content(
            doc_id=doc_id,
            extracted_text=extracted_text,
            chunks=chunks
        )
        
        # If Firestore fails, store in a temporary in-memory cache as fallback
        # This allows the app to work without Firestore for local development
        if not firestore_success:
            # Store in a simple in-memory cache as fallback
            # Note: This is temporary and will be lost on restart
            if not hasattr(firestore_service, '_fallback_cache'):
                firestore_service._fallback_cache = {}
            firestore_service._fallback_cache[doc_id] = {
                "text": extracted_text,
                "chunks": chunks
            }
        
        return document.to_dict()
    
    def get_document(self, doc_id: str) -> Optional[dict]:
        """
        Get document metadata.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document metadata dictionary or None
        """
        document = self.db.query(Document).filter(Document.id == doc_id).first()
        
        if document:
            return document.to_dict()
        return None
    
    def get_document_text(self, doc_id: str) -> Optional[str]:
        """
        Get document text content from Firestore.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document text or None
        """
        return firestore_service.get_document_text(doc_id)
    
    def get_document_chunks(self, doc_id: str) -> Optional[List[str]]:
        """
        Get document chunks from Firestore.
        
        Args:
            doc_id: Document ID
            
        Returns:
            List of chunks or None
        """
        return firestore_service.get_document_chunks(doc_id)
    
    def list_documents(self, skip: int = 0, limit: int = 100) -> tuple[List[dict], int]:
        """
        List documents with pagination.
        
        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            Tuple of (document list, total count)
        """
        # Get total count
        total = self.db.query(Document).count()
        
        # Get paginated documents, ordered by upload_time descending
        documents = (
            self.db.query(Document)
            .order_by(desc(Document.upload_time))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return [doc.to_dict() for doc in documents], total
    
    def update_document_summary(self, doc_id: str, summary: str) -> bool:
        """
        Update document summary.
        
        Args:
            doc_id: Document ID
            summary: Summary text
            
        Returns:
            True if updated, False if document not found
        """
        document = self.db.query(Document).filter(Document.id == doc_id).first()
        
        if document:
            document.summary = summary
            self.db.commit()
            return True
        return False
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete document (metadata and content).
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if deleted, False if document not found
        """
        document = self.db.query(Document).filter(Document.id == doc_id).first()
        
        if document:
            # Delete from PostgreSQL
            self.db.delete(document)
            self.db.commit()
            
            # Delete from Firestore
            firestore_service.delete_document_content(doc_id)
            
            return True
        return False
