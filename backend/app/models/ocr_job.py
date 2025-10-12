"""
OCR job model
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class OCRJob(Base):
    __tablename__ = "ocr_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    image_path = Column(Text, nullable=False)
    status = Column(String(50), default="pending")  # 'pending', 'processing', 'completed', 'failed'
    extracted_text = Column(Text)
    parsed_recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="SET NULL"))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
