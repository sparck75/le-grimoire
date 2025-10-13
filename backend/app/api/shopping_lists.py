"""
Shopping lists API routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db

router = APIRouter()

class ShoppingListResponse(BaseModel):
    """Shopping list response"""
    id: str
    name: str
    items_count: int
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[ShoppingListResponse])
async def list_shopping_lists(db: Session = Depends(get_db)):
    """
    List user's shopping lists
    Requires authentication in production
    """
    # This would filter by authenticated user
    return []

@router.post("/generate")
async def generate_shopping_list(recipe_ids: List[str], db: Session = Depends(get_db)):
    """
    Generate shopping list from recipes with matched grocery specials
    Requires authentication in production
    """
    return {
        "message": "Shopping list generation - to be implemented",
        "recipe_ids": recipe_ids
    }
