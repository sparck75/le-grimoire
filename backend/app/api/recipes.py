"""
Recipes API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from app.core.database import get_db
from app.models.recipe import Recipe

router = APIRouter()

class RecipeResponse(BaseModel):
    """Recipe response model"""
    id: str
    title: str
    description: Optional[str]
    ingredients: List[str]
    instructions: str
    servings: Optional[int]
    prep_time: Optional[int]
    cook_time: Optional[int]
    total_time: Optional[int]
    category: Optional[str]
    cuisine: Optional[str]
    image_url: Optional[str]
    is_public: bool
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[RecipeResponse])
async def list_recipes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    cuisine: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List public recipes with optional filtering
    """
    query = db.query(Recipe).filter(Recipe.is_public == True)
    
    if category:
        query = query.filter(Recipe.category == category)
    if cuisine:
        query = query.filter(Recipe.cuisine == cuisine)
    if search:
        query = query.filter(Recipe.title.ilike(f"%{search}%"))
    
    recipes = query.order_by(Recipe.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        RecipeResponse(
            id=str(recipe.id),
            title=recipe.title,
            description=recipe.description,
            ingredients=recipe.ingredients,
            instructions=recipe.instructions,
            servings=recipe.servings,
            prep_time=recipe.prep_time,
            cook_time=recipe.cook_time,
            total_time=recipe.total_time,
            category=recipe.category,
            cuisine=recipe.cuisine,
            image_url=recipe.image_url,
            is_public=recipe.is_public
        )
        for recipe in recipes
    ]

@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific recipe by ID
    """
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if not recipe.is_public:
        raise HTTPException(status_code=403, detail="Recipe is not public")
    
    return RecipeResponse(
        id=str(recipe.id),
        title=recipe.title,
        description=recipe.description,
        ingredients=recipe.ingredients,
        instructions=recipe.instructions,
        servings=recipe.servings,
        prep_time=recipe.prep_time,
        cook_time=recipe.cook_time,
        total_time=recipe.total_time,
        category=recipe.category,
        cuisine=recipe.cuisine,
        image_url=recipe.image_url,
        is_public=recipe.is_public
    )
