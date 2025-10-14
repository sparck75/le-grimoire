"""
Ingredient model for MongoDB using Beanie ODM.
Based on OpenFoodFacts ingredients taxonomy.
"""

from datetime import datetime, UTC
from typing import Dict, List, Optional
from beanie import Document
from pydantic import Field


class Ingredient(Document):
    """
    Ingredient document model for MongoDB.
    
    Stores multilingual ingredient data from OpenFoodFacts taxonomy,
    with support for custom user-added ingredients.
    """
    
    # Unique OpenFoodFacts taxonomy identifier (e.g., "en:tomato")
    # Index already created manually in import script
    off_id: str
    
    # Multilingual names (ISO 639-1 language codes)
    # Example: {"en": "Tomato", "fr": "Tomate", "es": "Tomate"}
    names: Dict[str, str] = Field(default_factory=dict)
    
    # Parent ingredients in taxonomy hierarchy
    parents: List[str] = Field(default_factory=list)
    
    # Child ingredients (more specific variants)
    children: List[str] = Field(default_factory=list)
    
    # Properties from OpenFoodFacts
    properties: Dict[str, str] = Field(default_factory=dict)  # vegan, vegetarian, etc.
    
    # External identifiers
    wikidata_id: Optional[str] = None
    ciqual_food_code: Optional[str] = None  # French food composition database
    e_number: Optional[str] = None  # E-number for additives
    
    # Indicates if this is a custom ingredient (not from OpenFoodFacts)
    custom: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    class Settings:
        name = "ingredients"
        # Indexes already created manually in import scripts
        # Don't recreate them to avoid conflicts
        use_state_management = True
        use_revision = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "off_id": "en:tomato",
                "names": {
                    "en": "Tomato",
                    "fr": "Tomate",
                    "es": "Tomate",
                    "de": "Tomate"
                },
                "parents": ["en:fruit-vegetable"],
                "children": ["en:cherry-tomato", "en:roma-tomato"],
                "properties": {
                    "vegan": "yes",
                    "vegetarian": "yes"
                },
                "wikidata_id": "Q23501",
                "ciqual_food_code": "20047",
                "custom": False
            }
        }
    
    def get_name(self, language: str = "en") -> str:
        """
        Get ingredient name in specified language.
        Falls back to English if language not available.
        """
        return self.names.get(language, self.names.get("en", self.off_id))
    
    def is_vegan(self) -> Optional[bool]:
        """Check if ingredient is vegan."""
        vegan = self.properties.get("vegan", "").lower()
        if vegan == "yes":
            return True
        elif vegan == "no":
            return False
        return None
    
    def is_vegetarian(self) -> Optional[bool]:
        """Check if ingredient is vegetarian."""
        vegetarian = self.properties.get("vegetarian", "").lower()
        if vegetarian == "yes":
            return True
        elif vegetarian == "no":
            return False
        return None
    
    async def get_parent_ingredients(self) -> List["Ingredient"]:
        """Fetch parent ingredients from database."""
        if not self.parents:
            return []
        return await Ingredient.find({"off_id": {"$in": self.parents}}).to_list()
    
    async def get_child_ingredients(self) -> List["Ingredient"]:
        """Fetch child ingredients from database."""
        if not self.children:
            return []
        return await Ingredient.find({"off_id": {"$in": self.children}}).to_list()
    
    @classmethod
    async def search(
        cls,
        query: str,
        language: str = "en",
        limit: int = 50,
        skip: int = 0,
        custom_only: bool = False
    ) -> List["Ingredient"]:
        """
        Search ingredients by name in specified language.
        Uses regex for short queries (1-2 chars) and text search for longer queries.
        Searches across all 5,942 ingredients in the database.
        
        Args:
            query: Search query string
            language: Language code (default: "en")
            limit: Maximum number of results
            skip: Number of results to skip (for pagination)
            custom_only: Only return custom ingredients
        
        Returns:
            List of matching ingredients
        """
        # Use case-insensitive regex for partial matching on ALL query lengths
        # This enables true autocomplete behavior (e.g., "oeu" finds "oeuf")
        # Note: For very large datasets, consider text search for complete words
        field_name = f"names.{language}"
        filters = {field_name: {"$regex": f"^{query}", "$options": "i"}}
        
        if custom_only:
            filters["custom"] = True
        
        return await cls.find(filters).skip(skip).limit(limit).to_list()
    
    @classmethod
    async def get_by_off_id(cls, off_id: str) -> Optional["Ingredient"]:
        """Get ingredient by OpenFoodFacts ID."""
        return await cls.find_one({"off_id": off_id})
