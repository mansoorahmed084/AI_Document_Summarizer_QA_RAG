"""
Text chunking utilities for splitting large documents.
"""
from typing import List
from app.core.config import settings


class TextChunker:
    """Utility for chunking text into smaller pieces."""
    
    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> List[str]:
        """
        Split text into chunks with optional overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk (default from config)
            chunk_overlap: Number of characters to overlap between chunks (default from config)
            
        Returns:
            List of text chunks
        """
        if chunk_size is None:
            chunk_size = settings.CHUNK_SIZE
        if chunk_overlap is None:
            chunk_overlap = settings.CHUNK_OVERLAP
        
        if not text or len(text) <= chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = start + chunk_size
            
            # If not the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 20% of the chunk
                search_start = max(start, end - int(chunk_size * 0.2))
                sentence_endings = ['. ', '.\n', '! ', '!\n', '? ', '?\n', '\n\n']
                
                best_break = end
                for ending in sentence_endings:
                    # Find last occurrence of sentence ending
                    pos = text.rfind(ending, search_start, end)
                    if pos != -1:
                        best_break = pos + len(ending)
                        break
                
                # If no sentence boundary found, try word boundary
                if best_break == end:
                    word_break = text.rfind(' ', search_start, end)
                    if word_break != -1:
                        best_break = word_break + 1
                
                end = best_break
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = max(start + 1, end - chunk_overlap)
        
        return chunks
    
    @staticmethod
    def get_chunk_count(text: str, chunk_size: int = None) -> int:
        """
        Get the number of chunks that would be created.
        
        Args:
            text: Text to analyze
            chunk_size: Maximum characters per chunk (default from config)
            
        Returns:
            Number of chunks
        """
        if chunk_size is None:
            chunk_size = settings.CHUNK_SIZE
        
        if not text or len(text) <= chunk_size:
            return 1 if text else 0
        
        return len(TextChunker.chunk_text(text, chunk_size, 0))
