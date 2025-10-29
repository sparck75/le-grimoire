"""
AI Extraction Log MongoDB model for tracking AI usage.
"""
from beanie import Document
from pydantic import Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class AIExtractionLog(Document):
    """Log entry for AI extraction usage tracking."""
    
    model_config = ConfigDict(extra="allow")
    
    # Extraction metadata
    extraction_method: str  # "ai", "ocr", "ocr_fallback"
    provider: Optional[str] = None  # "openai", "gemini", "tesseract"
    model_name: Optional[str] = None  # e.g., "gpt-4o"
    
    # User information (if available)
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    
    # Original image information
    original_image_path: Optional[str] = None
    image_url: Optional[str] = None
    image_size_bytes: Optional[int] = None
    
    # Extraction results
    recipe_id: Optional[str] = None  # ID of created recipe (if saved)
    recipe_title: Optional[str] = None
    confidence_score: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    
    # Token usage (for AI providers)
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    
    # Cost estimation
    estimated_cost_usd: Optional[float] = None
    
    # Processing information
    processing_time_ms: Optional[int] = None
    
    # Raw data for debugging
    raw_response: Optional[str] = None
    model_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "ai_extraction_logs"
        use_state_management = False
        use_revision = False
        indexes = [
            "extraction_method",
            "provider",
            "user_id",
            "recipe_id",
            "created_at",
            "success"
        ]
    
    def __repr__(self) -> str:
        return f"AIExtractionLog(id={self.id}, method={self.extraction_method}, recipe={self.recipe_title})"
    
    def __str__(self) -> str:
        return f"{self.extraction_method} - {self.recipe_title or 'Untitled'}"
