"""
AI-related Pydantic models for summarization and Q&A.
"""
from pydantic import BaseModel, Field
from typing import Optional


class SummarizeRequest(BaseModel):
    """Request model for document summarization."""
    doc_id: str = Field(..., description="Document ID to summarize")
    max_length: Optional[int] = Field(500, description="Maximum summary length in words")


class SummarizeResponse(BaseModel):
    """Response model for summarization."""
    doc_id: str = Field(..., description="Document ID")
    summary: str = Field(..., description="Generated summary")
    word_count: int = Field(..., description="Summary word count")


class QARequest(BaseModel):
    """Request model for Q&A."""
    doc_id: str = Field(..., description="Document ID")
    question: str = Field(..., min_length=1, description="Question to answer")


class QAResponse(BaseModel):
    """Response model for Q&A."""
    doc_id: str = Field(..., description="Document ID")
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Generated answer")
    sources: Optional[list[str]] = Field(None, description="Source chunks used for answer")
