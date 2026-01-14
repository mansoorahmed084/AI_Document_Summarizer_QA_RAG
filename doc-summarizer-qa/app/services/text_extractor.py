"""
Text extraction service for PDF and text files.
"""
import io
from typing import Optional
from PyPDF2 import PdfReader
from fastapi import HTTPException, status


class TextExtractor:
    """Service for extracting text from various document formats."""
    
    @staticmethod
    def extract_from_pdf(file_content: bytes) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_content: PDF file content as bytes
            
        Returns:
            Extracted text as string
            
        Raises:
            HTTPException: If PDF extraction fails
        """
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
            
            text_parts = []
            for page_num, page in enumerate(reader.pages, start=1):
                try:
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(text)
                except Exception as e:
                    # Log warning but continue with other pages
                    print(f"Warning: Failed to extract text from page {page_num}: {str(e)}")
                    continue
            
            if not text_parts:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No text content found in PDF. The PDF might be image-based or corrupted."
                )
            
            extracted_text = "\n\n".join(text_parts)
            return extracted_text.strip()
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract text from PDF: {str(e)}"
            )
    
    @staticmethod
    def extract_from_text(file_content: bytes, encoding: str = "utf-8") -> str:
        """
        Extract text from plain text file.
        
        Args:
            file_content: Text file content as bytes
            encoding: Text encoding (default: utf-8)
            
        Returns:
            Extracted text as string
            
        Raises:
            HTTPException: If text extraction fails
        """
        try:
            # Try UTF-8 first
            try:
                text = file_content.decode(encoding)
            except UnicodeDecodeError:
                # Fallback to latin-1 (most permissive)
                text = file_content.decode("latin-1")
            
            return text.strip()
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract text from file: {str(e)}"
            )
    
    @staticmethod
    def extract(file_content: bytes, file_extension: str) -> str:
        """
        Extract text from file based on extension.
        
        Args:
            file_content: File content as bytes
            file_extension: File extension (e.g., '.pdf', '.txt')
            
        Returns:
            Extracted text as string
        """
        file_ext = file_extension.lower()
        
        if file_ext == ".pdf":
            return TextExtractor.extract_from_pdf(file_content)
        elif file_ext == ".txt":
            return TextExtractor.extract_from_text(file_content)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_extension}"
            )
