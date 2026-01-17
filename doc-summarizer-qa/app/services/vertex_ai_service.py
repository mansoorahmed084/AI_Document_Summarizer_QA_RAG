"""
Vertex AI service for summarization and Q&A.
"""
from typing import Optional
import time
from app.core.config import settings

# Try to import Vertex AI, but allow graceful degradation
try:
    import vertexai
    # Try preview import first (newer API)
    try:
        from vertexai.preview.generative_models import GenerativeModel
    except ImportError:
        # Fallback to standard import if preview doesn't work
        from vertexai.generative_models import GenerativeModel
    VERTEX_AI_AVAILABLE = True
except ImportError as e:
    VERTEX_AI_AVAILABLE = False
    print(f"Warning: google-cloud-aiplatform not available: {str(e)}")
    print("   AI features will be disabled.")
except Exception as e:
    VERTEX_AI_AVAILABLE = False
    print(f"Warning: Error importing Vertex AI: {str(e)}")
    print("   AI features will be disabled.")


class VertexAIService:
    """Service for Vertex AI operations."""
    
    def __init__(self):
        """Initialize Vertex AI client."""
        self.model = None
        self.initialized = False
        
        if not VERTEX_AI_AVAILABLE:
            print("Warning: Vertex AI library not installed. AI features disabled.")
            return
        
        if not settings.GCP_PROJECT_ID:
            print("Warning: GCP_PROJECT_ID not set. AI features disabled.")
            return
        
        try:
            # Vertex AI will automatically use GOOGLE_APPLICATION_CREDENTIALS from environment
            vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.GCP_REGION)
            self.model = GenerativeModel(settings.VERTEX_AI_MODEL)
            self.initialized = True
            print(f"✅ Vertex AI initialized with model: {settings.VERTEX_AI_MODEL}")
        except Exception as e:
            error_msg = str(e)
            print(f"Warning: Failed to initialize Vertex AI: {error_msg}")
            if "credentials" in error_msg.lower() or "authentication" in error_msg.lower():
                print("   Check that GOOGLE_APPLICATION_CREDENTIALS points to a valid JSON file")
            elif "project" in error_msg.lower():
                print("   Check that GCP_PROJECT_ID is correct and you have access")
            print("   AI features will be disabled.")
    
    def summarize_text(
        self,
        text: str,
        max_length: int = 500
    ) -> Optional[str]:
        """
        Generate a summary of the given text.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length in words
            
        Returns:
            Generated summary or None if failed
        """
        if not self.initialized or not self.model:
            return None
        
        try:
            # Build prompt for summarization
            prompt = self._build_summarize_prompt(text, max_length)
            
            # Generate summary
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            
            return None
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return None
    
    def _build_summarize_prompt(self, text: str, max_length: int) -> str:
        """
        Build prompt for summarization.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length in words
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Please provide a concise summary of the following text in approximately {max_length} words or less.

Focus on:
- Key points and main ideas
- Important facts and details
- Main conclusions or takeaways

Text to summarize:
{text}

Summary:"""
        return prompt
    
    def answer_question(
        self,
        question: str,
        context: str
    ) -> Optional[str]:
        """
        Answer a question based on the given context.
        
        Args:
            question: Question to answer
            context: Context text to use for answering
            
        Returns:
            Generated answer or None if failed
        """
        if not self.initialized or not self.model:
            return None
        
        try:
            # Build prompt for Q&A
            prompt = self._build_qa_prompt(question, context)
            
            # Generate answer
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            
            return None
        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            return None
    
    def _build_qa_prompt(self, question: str, context: str) -> str:
        """
        Build prompt for question answering.
        
        Args:
            question: Question to answer
            context: Context text
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Based on the following context, please answer the question. If the answer cannot be found in the context, please say so.

Context:
{context}

Question: {question}

Answer:"""
        return prompt


# Global instance (will be initialized on startup)
vertex_ai_service = None

def get_vertex_ai_service() -> VertexAIService:
    """Get or create Vertex AI service instance."""
    global vertex_ai_service
    if vertex_ai_service is None:
        vertex_ai_service = VertexAIService()
    return vertex_ai_service
