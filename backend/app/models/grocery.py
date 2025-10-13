"""
Grocery store models
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class GroceryStore(Base):
    __tablename__ = "grocery_stores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)  # 'iga', 'metro'
    website_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class GrocerySpecial(Base):
    __tablename__ = "grocery_specials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_id = Column(UUID(as_uuid=True), ForeignKey("grocery_stores.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(500), nullable=False)
    product_category = Column(String(100))
    original_price = Column(Numeric(10, 2))
    special_price = Column(Numeric(10, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2))
    unit = Column(String(50))  # 'lb', 'kg', 'unit', 'l'
    description = Column(Text)
    image_url = Column(Text)
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=False)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
