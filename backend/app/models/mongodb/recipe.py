"""
Recipe MongoDB model using Beanie ODM.
"""
from beanie import Document
from pydantic import Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class Recipe(Document):
    """Recipe document in MongoDB."""
    
    model_config = ConfigDict(extra="allow")
    
    title: str
    description: str = ""
    ingredients: List[str] = Field(default_factory=list)
    instructions: str = ""
    servings: Optional[int] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None
    category: str = ""
    cuisine: str = ""
    image_url: Optional[str] = None
    is_public: bool = True
    equipment: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "recipes"
        use_state_management = False
        use_revision = False
    
    def __repr__(self) -> str:
        return f"Recipe(id={self.id}, title='{self.title}')"
    
    def __str__(self) -> str:
        return self.title
