"""
Recipe models
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    ingredients = Column(ARRAY(Text), nullable=False)
    equipment = Column(ARRAY(Text))  # cooking equipment/utensils needed
    instructions = Column(Text, nullable=False)
    servings = Column(Integer)
    prep_time = Column(Integer)  # in minutes
    cook_time = Column(Integer)  # in minutes
    total_time = Column(Integer)  # in minutes
    category = Column(String(100))
    cuisine = Column(String(100))
    difficulty_level = Column(String(50))  # easy, medium, hard
    temperature = Column(Integer)  # cooking temperature
    temperature_unit = Column(String(10))  # C or F
    notes = Column(Text)  # additional notes
    image_url = Column(Text)
    original_image_url = Column(Text)
    source = Column(String(255))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class RecipeTag(Base):
    __tablename__ = "recipe_tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    tag = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
