"""
In-memory document storage (temporary until Step 3 - Firestore integration).
"""
from typing import Dict, Optional
from datetime import datetime
import uuid


class InMemoryDocumentStorage:
    """
    Temporary in-memory storage for documents.
    Will be replaced with Firestore in Step 3.
    """
    
    def __init__(self):
        """Initialize storage."""
        self._documents: Dict[str, dict] = {}
        self._document_texts: Dict[str, str] = {}
        self._document_chunks: Dict[str, list] = {}
    
    def store_document(
        self,
        doc_id: str,
        filename: str,
        extracted_text: str,
        chunks: list,
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
            Document metadata
        """
        document = {
            "id": doc_id,
            "filename": filename,
            "upload_time": datetime.utcnow(),
            "status": "processed",
            "file_size": file_size,
            "text_length": len(extracted_text),
            "chunk_count": len(chunks),
            "summary": None,
        }
        
        self._documents[doc_id] = document
        self._document_texts[doc_id] = extracted_text
        self._document_chunks[doc_id] = chunks
        
        return document
    
    def get_document(self, doc_id: str) -> Optional[dict]:
        """
        Get document metadata.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document metadata or None
        """
        return self._documents.get(doc_id)
    
    def get_document_text(self, doc_id: str) -> Optional[str]:
        """
        Get document text content.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document text or None
        """
        return self._document_texts.get(doc_id)
    
    def get_document_chunks(self, doc_id: str) -> Optional[list]:
        """
        Get document chunks.
        
        Args:
            doc_id: Document ID
            
        Returns:
            List of chunks or None
        """
        return self._document_chunks.get(doc_id)
    
    def list_documents(self, skip: int = 0, limit: int = 100) -> tuple[list, int]:
        """
        List documents with pagination.
        
        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            Tuple of (document list, total count)
        """
        all_docs = list(self._documents.values())
        total = len(all_docs)
        
        # Sort by upload_time descending
        all_docs.sort(key=lambda x: x["upload_time"], reverse=True)
        
        # Apply pagination
        paginated_docs = all_docs[skip:skip + limit]
        
        return paginated_docs, total
    
    def update_document_summary(self, doc_id: str, summary: str) -> bool:
        """
        Update document summary.
        
        Args:
            doc_id: Document ID
            summary: Summary text
            
        Returns:
            True if updated, False if document not found
        """
        if doc_id in self._documents:
            self._documents[doc_id]["summary"] = summary
            return True
        return False


# Global instance (will be replaced with Firestore client in Step 3)
document_storage = InMemoryDocumentStorage()
