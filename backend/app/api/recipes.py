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
    equipment: Optional[List[str]] = None
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


class RecipeCreate(BaseModel):
    """Recipe creation request"""
    title: str
    description: Optional[str] = None
    ingredients: List[str]
    equipment: Optional[List[str]] = None
    instructions: str
    servings: Optional[int] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None
    category: Optional[str] = None
    cuisine: Optional[str] = None
    image_url: Optional[str] = None
    is_public: bool = True


class RecipeUpdate(BaseModel):
    """Recipe update request"""
    title: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    equipment: Optional[List[str]] = None
    instructions: Optional[str] = None
    servings: Optional[int] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None
    category: Optional[str] = None
    cuisine: Optional[str] = None
    image_url: Optional[str] = None
    is_public: Optional[bool] = None

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
            equipment=recipe.equipment,
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
        equipment=recipe.equipment,
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


@router.post("/", response_model=RecipeResponse)
async def create_recipe(
    recipe_data: RecipeCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new recipe
    """
    # Create the recipe
    recipe = Recipe(
        title=recipe_data.title,
        description=recipe_data.description,
        ingredients=recipe_data.ingredients,
        equipment=recipe_data.equipment,
        instructions=recipe_data.instructions,
        servings=recipe_data.servings,
        prep_time=recipe_data.prep_time,
        cook_time=recipe_data.cook_time,
        total_time=recipe_data.total_time,
        category=recipe_data.category,
        cuisine=recipe_data.cuisine,
        image_url=recipe_data.image_url,
        is_public=recipe_data.is_public
    )
    
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    
    return RecipeResponse(
        id=str(recipe.id),
        title=recipe.title,
        description=recipe.description,
        ingredients=recipe.ingredients,
        equipment=recipe.equipment,
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


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: UUID,
    recipe_data: RecipeUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing recipe
    """
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Update only provided fields
    update_data = recipe_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(recipe, field, value)
    
    db.commit()
    db.refresh(recipe)
    
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


@router.delete("/{recipe_id}")
async def delete_recipe(
    recipe_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a recipe
    """
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    db.delete(recipe)
    db.commit()
    
    return {"message": "Recipe deleted successfully", "id": str(recipe_id)}
