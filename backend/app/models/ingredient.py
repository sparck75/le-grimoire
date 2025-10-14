"""
Ingredient models
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, Numeric, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class IngredientCategory(Base):
    __tablename__ = "ingredient_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)  # English name for backward compatibility
    name_en = Column(String(100), nullable=True)  # English name
    name_fr = Column(String(100), nullable=True)  # French name
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey("ingredient_categories.id"), nullable=True)
    display_order = Column(Integer, nullable=True)
    icon = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ingredients = relationship("Ingredient", back_populates="category")
    parent = relationship("IngredientCategory", remote_side=[id], backref="children")


class Unit(Base):
    __tablename__ = "units"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    abbreviation = Column(String(20), nullable=True)
    type = Column(String(50), nullable=True)  # 'volume', 'weight', 'unit', 'temperature'
    system = Column(String(20), nullable=True)  # 'metric', 'imperial', 'both'
    conversion_to_base = Column(Numeric(10, 6), nullable=True)
    base_unit = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Ingredient(Base):
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True)  # Using integer ID from CSV
    name = Column(String(255), nullable=False)  # For backward compatibility
    english_name = Column(String(255), nullable=False)
    french_name = Column(String(255), nullable=False)
    gender = Column(String(1), nullable=True)  # 'm' or 'f' for French
    name_plural = Column(String(255), nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("ingredient_categories.id"), nullable=True)
    subcategory = Column(String(100), nullable=True)
    default_unit = Column(String(50), nullable=True)
    aliases = Column(ARRAY(Text), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, server_default='true')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("IngredientCategory", back_populates="ingredients")
    recipe_ingredients = relationship("RecipeIngredient", back_populates="ingredient")
    # images = relationship("IngredientImage", back_populates="ingredient", cascade="all, delete-orphan")  # Deprecated - using MongoDB


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    # Changed from integer to string to reference MongoDB OpenFoodFacts off_id
    ingredient_off_id = Column(String(255), nullable=False)  # References MongoDB Ingredient.off_id
    # Keep old column for backward compatibility during migration
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="RESTRICT"), nullable=True)
    quantity = Column(Numeric(10, 3), nullable=True)
    quantity_max = Column(Numeric(10, 3), nullable=True)  # for ranges like "1-2 cups"
    unit = Column(String(50), nullable=True)
    preparation_notes = Column(Text, nullable=True)  # "chopped", "diced", "melted", etc.
    is_optional = Column(Boolean, default=False, server_default='false')
    display_order = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")  # Deprecated - using MongoDB
