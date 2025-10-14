"""
Category model for MongoDB using Beanie ODM.
Based on OpenFoodFacts categories taxonomy.
"""

from datetime import datetime, UTC
from typing import Dict, List, Optional, Union
from beanie import Document
from pydantic import Field, field_validator


class Category(Document):
    """
    Category document model for MongoDB.
    
    Stores multilingual category data from OpenFoodFacts taxonomy,
    organized in a hierarchical structure.
    """
    
    # Unique OpenFoodFacts taxonomy identifier (e.g., "en:plant-based-foods")
    # Index already created manually in import script
    off_id: str
    
    # Multilingual names (ISO 639-1 language codes)
    # Example: {"en": "Plant-based foods", "fr": "Aliments d'origine végétale"}
    names: Dict[str, str] = Field(default_factory=dict)
    
    # Parent categories in taxonomy hierarchy
    parents: List[str] = Field(default_factory=list)
    
    # Child categories (subcategories)
    children: List[str] = Field(default_factory=list)
    
    # Emoji icon for UI display
    icon: Optional[str] = None
    
    # External identifiers
    wikidata_id: Optional[str] = None
    agribalyse_code: Optional[str] = None  # French environmental impact database
    
    # Product origins associated with this category
    # Can be a list of origin IDs or a dict with multilingual values
    origins: Union[List[str], Dict[str, str]] = Field(default_factory=list)
    
    @field_validator('origins', mode='before')
    @classmethod
    def normalize_origins(cls, v):
        """
        Normalize origins field to always be a list.
        OpenFoodFacts taxonomy sometimes has origins as dict.
        """
        if isinstance(v, dict):
            # Convert dict to list of values
            return list(v.values()) if v else []
        return v if v is not None else []
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    class Settings:
        name = "categories"
        # Indexes already created manually in import scripts
        # Don't recreate them to avoid conflicts
        use_state_management = True
        use_revision = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "off_id": "en:plant-based-foods",
                "names": {
                    "en": "Plant-based foods",
                    "fr": "Aliments d'origine végétale",
                    "es": "Alimentos de origen vegetal",
                    "de": "Pflanzliche Lebensmittel"
                },
                "parents": ["en:foods"],
                "children": [
                    "en:vegetables",
                    "en:fruits",
                    "en:cereals-and-potatoes",
                    "en:legumes"
                ],
                "icon": "🌱",
                "wikidata_id": "Q16587531"
            }
        }
    
    def get_name(self, language: str = "en") -> str:
        """
        Get category name in specified language.
        Falls back to English if language not available.
        """
        return self.names.get(language, self.names.get("en", self.off_id))
    
    def is_top_level(self) -> bool:
        """Check if this is a top-level category (no parents)."""
        return len(self.parents) == 0
    
    async def get_parent_categories(self) -> List["Category"]:
        """Fetch parent categories from database."""
        if not self.parents:
            return []
        return await Category.find({"off_id": {"$in": self.parents}}).to_list()
    
    async def get_child_categories(self) -> List["Category"]:
        """Fetch child categories from database."""
        if not self.children:
            return []
        return await Category.find({"off_id": {"$in": self.children}}).to_list()
    
    async def get_all_descendants(self) -> List["Category"]:
        """
        Recursively fetch all descendant categories.
        Returns a flat list of all categories in the subtree.
        """
        descendants = []
        children = await self.get_child_categories()
        
        for child in children:
            descendants.append(child)
            # Recursively get children's descendants
            child_descendants = await child.get_all_descendants()
            descendants.extend(child_descendants)
        
        return descendants
    
    @classmethod
    async def search(
        cls,
        query: str,
        language: str = "en",
        limit: int = 50
    ) -> List["Category"]:
        """
        Search categories by name in specified language.
        
        Args:
            query: Search query string
            language: Language code (default: "en")
            limit: Maximum number of results
        
        Returns:
            List of matching categories
        """
        return await cls.find({"$text": {"$search": query}}).limit(limit).to_list()
    
    @classmethod
    async def get_top_level_categories(cls) -> List["Category"]:
        """Get all top-level categories (no parents)."""
        return await cls.find({"parents": {"$size": 0}}).to_list()
    
    @classmethod
    async def get_by_off_id(cls, off_id: str) -> Optional["Category"]:
        """Get category by OpenFoodFacts ID."""
        return await cls.find_one({"off_id": off_id})
    
    @classmethod
    async def get_categories_with_icon(cls) -> List["Category"]:
        """Get all categories that have an icon defined."""
        return await cls.find({"icon": {"$ne": None}}).to_list()
