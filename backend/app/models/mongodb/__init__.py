"""
MongoDB models using Beanie ODM.
These models interface with the OpenFoodFacts data in MongoDB.
"""

from .ingredient import Ingredient
from .category import Category
from .recipe import Recipe

__all__ = ["Ingredient", "Category", "Recipe"]
