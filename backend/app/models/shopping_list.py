"""
Shopping list models
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shopping_list_id = Column(UUID(as_uuid=True), ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="SET NULL"))
    ingredient_off_id = Column(String(255), nullable=True)  # References MongoDB Ingredient.off_id (e.g., "en:tomato")
    ingredient_name = Column(String(500), nullable=False)  # Kept for backward compatibility and custom items
    quantity = Column(Numeric(10, 2))
    unit = Column(String(50))
    is_purchased = Column(Boolean, default=False)
    matched_special_id = Column(UUID(as_uuid=True), ForeignKey("grocery_specials.id", ondelete="SET NULL"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
