"""
MongoDB models using Beanie ODM.
These models interface with the OpenFoodFacts data in MongoDB.
"""

from .ingredient import Ingredient
from .category import Category

__all__ = ["Ingredient", "Category"]
