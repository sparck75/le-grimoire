"""
MongoDB models using Beanie ODM.
These models interface with the OpenFoodFacts data in MongoDB.
"""

from .ingredient import Ingredient
from .category import Category
from .recipe import Recipe
from .ai_extraction_log import AIExtractionLog
from .wine import Wine, WineType, WineRegion
from .liquor import Liquor, LiquorType, LiquorOrigin

__all__ = [
    "Ingredient",
    "Category",
    "Recipe",
    "AIExtractionLog",
    "Wine",
    "WineType",
    "WineRegion",
    "Liquor",
    "LiquorType",
    "LiquorOrigin",
]
