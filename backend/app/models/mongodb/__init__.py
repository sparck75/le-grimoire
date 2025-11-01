"""
MongoDB models using Beanie ODM.
These models interface with the OpenFoodFacts data in MongoDB.
"""

from .ingredient import Ingredient
from .category import Category
from .recipe import Recipe
from .ai_extraction_log import AIExtractionLog
from .wine import Wine
from .liquor import Liquor
from .barcode_mapping import BarcodeMapping

__all__ = [
    "Ingredient",
    "Category",
    "Recipe",
    "AIExtractionLog",
    "Wine",
    "Liquor",
    "BarcodeMapping"
]
