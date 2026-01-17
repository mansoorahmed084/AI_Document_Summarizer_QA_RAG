"""
Firestore service for storing document content and chunks.
"""
from typing import Optional, List
from app.core.config import settings

# Try to import Firestore, but allow graceful degradation
try:
    from google.cloud import firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    print("Warning: google-cloud-firestore not available. Firestore operations will be disabled.")


class FirestoreService:
    """Service for Firestore operations."""
    
    def __init__(self):
        """Initialize Firestore client."""
        self.db = None
        
        if not FIRESTORE_AVAILABLE:
            print("Warning: Firestore library not installed. Using in-memory fallback for content.")
            return
        
        if settings.GCP_PROJECT_ID and FIRESTORE_AVAILABLE:
            try:
                # Firestore client will automatically use GOOGLE_APPLICATION_CREDENTIALS from environment
                # Verify credentials file exists and is valid before initializing
                import os
                creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
                if creds_path and os.path.exists(creds_path):
                    # Verify it's valid JSON
                    try:
                        import json
                        with open(creds_path, 'r') as f:
                            json.load(f)  # Validate JSON
                    except json.JSONDecodeError:
                        print(f"Warning: Credentials file is not valid JSON: {creds_path}")
                        print("   Using in-memory fallback for content storage.")
                        return
                
                self.db = firestore.Client(project=settings.GCP_PROJECT_ID)
                print("✅ Firestore client initialized")
            except Exception as e:
                error_details = str(e)
                # Provide more helpful error message
                if "'str' object has no attribute 'get'" in error_details:
                    print(f"Warning: Failed to initialize Firestore: Credentials parsing issue")
                    print(f"   Error: {error_details}")
                    print("   This usually means the credentials file format is incorrect")
                    print("   Check that GOOGLE_APPLICATION_CREDENTIALS points to a valid service account JSON file")
                    print("   Using in-memory fallback for content storage.")
                else:
                    print(f"Warning: Failed to initialize Firestore: {error_details}")
                    print("   Using in-memory fallback for content storage.")
        else:
            if not FIRESTORE_AVAILABLE:
                print("Warning: Firestore library not installed. Using in-memory fallback for content.")
            else:
                print("Warning: GCP_PROJECT_ID not set. Using in-memory fallback for content.")
    
    def store_document_content(
        self,
        doc_id: str,
        extracted_text: str,
        chunks: List[str]
    ) -> bool:
        """
        Store document text and chunks in Firestore.
        
        Args:
            doc_id: Document ID
            extracted_text: Full extracted text
            chunks: List of text chunks
            
        Returns:
            True if successful, False otherwise
        """
        if not self.db:
            return False
        
        try:
            doc_ref = self.db.collection(settings.FIRESTORE_COLLECTION_DOCUMENTS).document(doc_id)
            
            # Store full text
            from google.cloud.firestore import SERVER_TIMESTAMP
            doc_ref.set({
                "text": extracted_text,
                "chunks": chunks,
                "updated_at": SERVER_TIMESTAMP,
            })
            
            return True
        except Exception as e:
            print(f"Error storing document content in Firestore: {str(e)}")
            return False
    
    def get_document_text(self, doc_id: str) -> Optional[str]:
        """
        Get document text from Firestore.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document text or None
        """
        # Try Firestore first
        if self.db:
            try:
                doc_ref = self.db.collection(settings.FIRESTORE_COLLECTION_DOCUMENTS).document(doc_id)
                doc = doc_ref.get()
                
                if doc.exists:
                    return doc.to_dict().get("text")
            except Exception as e:
                print(f"Error getting document text from Firestore: {str(e)}")
        
        # Fallback to in-memory cache
        if hasattr(self, '_fallback_cache') and doc_id in self._fallback_cache:
            return self._fallback_cache[doc_id].get("text")
        
        return None
    
    def get_document_chunks(self, doc_id: str) -> Optional[List[str]]:
        """
        Get document chunks from Firestore.
        
        Args:
            doc_id: Document ID
            
        Returns:
            List of chunks or None
        """
        # Try Firestore first
        if self.db:
            try:
                doc_ref = self.db.collection(settings.FIRESTORE_COLLECTION_DOCUMENTS).document(doc_id)
                doc = doc_ref.get()
                
                if doc.exists:
                    return doc.to_dict().get("chunks")
            except Exception as e:
                print(f"Error getting document chunks from Firestore: {str(e)}")
        
        # Fallback to in-memory cache
        if hasattr(self, '_fallback_cache') and doc_id in self._fallback_cache:
            return self._fallback_cache[doc_id].get("chunks")
        
        return None
    
    def delete_document_content(self, doc_id: str) -> bool:
        """
        Delete document content from Firestore.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.db:
            return False
        
        try:
            doc_ref = self.db.collection(settings.FIRESTORE_COLLECTION_DOCUMENTS).document(doc_id)
            doc_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting document content from Firestore: {str(e)}")
            return False


# Global instance (will be initialized on startup)
firestore_service = None

def get_firestore_service() -> FirestoreService:
    """Get or create Firestore service instance."""
    global firestore_service
    if firestore_service is None:
        firestore_service = FirestoreService()
    return firestore_service
