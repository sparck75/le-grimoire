"""
Ingredient Image models
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class IngredientImage(Base):
    """
    Stores multiple images for each ingredient.
    Images can be sourced from various providers (Unsplash, Pexels, etc.)
    """
    __tablename__ = "ingredient_images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    
    # Image source and metadata
    image_url = Column(Text, nullable=False)  # Full resolution URL
    thumbnail_url = Column(Text, nullable=True)  # Thumbnail URL for performance
    source = Column(String(50), nullable=True)  # 'unsplash', 'pexels', 'pixabay', etc.
    source_id = Column(String(255), nullable=True)  # ID from the source API
    
    # Image details
    photographer = Column(String(255), nullable=True)  # Credit to photographer
    photographer_url = Column(Text, nullable=True)  # Link to photographer's profile
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    alt_text = Column(Text, nullable=True)  # Alternative text for accessibility
    
    # Image management
    is_primary = Column(Boolean, default=False)  # Primary image to display
    is_approved = Column(Boolean, default=True)  # Manual approval flag
    display_order = Column(Integer, default=0)  # Order for display
    
    # AI/Quality metrics
    relevance_score = Column(Integer, nullable=True)  # AI-determined relevance (0-100)
    quality_score = Column(Integer, nullable=True)  # Image quality score (0-100)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    ingredient = relationship("Ingredient", back_populates="images")
