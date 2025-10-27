"""
Admin Recipes API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_active_admin
from app.models.user import User
from app.models.recipe import Recipe
from app.models.ingredient import RecipeIngredient
from app.models.mongodb import Ingredient  # MongoDB ingredient model

router = APIRouter()


# Pydantic models
class RecipeIngredientItem(BaseModel):
    """Recipe ingredient item for requests"""
    ingredient_off_id: Optional[str] = None  # OpenFoodFacts ID like "en:tomato", optional if not linked
    quantity: Optional[float] = None
    quantity_max: Optional[float] = None
    unit: Optional[str] = None
    preparation_notes: Optional[str] = None
    is_optional: bool = False
    display_order: Optional[int] = None


class RecipeIngredientResponse(BaseModel):
    """Recipe ingredient response"""
    id: str
    ingredient_off_id: Optional[str]  # OpenFoodFacts ID, can be null if not linked
    ingredient_name: Optional[str]  # Name in requested language, can be null if not linked
    ingredient_name_en: Optional[str]  # English name, can be null if not linked
    ingredient_name_fr: Optional[str]  # French name, can be null if not linked
    quantity: Optional[float]
    quantity_max: Optional[float]
    unit: Optional[str]
    preparation_notes: Optional[str]
    is_optional: bool
    display_order: Optional[int]
    
    class Config:
        from_attributes = True


class RecipeCreateRequest(BaseModel):
    """Create recipe request with structured ingredients"""
    title: str
    description: Optional[str] = None
    servings: Optional[int] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None
    category: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty_level: Optional[str] = None
    temperature: Optional[int] = None
    temperature_unit: Optional[str] = None
    instructions: str
    notes: Optional[str] = None
    is_public: bool = True
    ingredients: List[RecipeIngredientItem] = []
    equipment: Optional[List[str]] = None


class RecipeUpdateRequest(BaseModel):
    """Update recipe request"""
    title: Optional[str] = None
    description: Optional[str] = None
    servings: Optional[int] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None
    category: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty_level: Optional[str] = None
    temperature: Optional[int] = None
    temperature_unit: Optional[str] = None
    instructions: Optional[str] = None
    notes: Optional[str] = None
    is_public: Optional[bool] = None
    ingredients: Optional[List[RecipeIngredientItem]] = None
    equipment: Optional[List[str]] = None


class RecipeDetailResponse(BaseModel):
    """Detailed recipe response with structured ingredients"""
    id: str
    title: str
    description: Optional[str]
    servings: Optional[int]
    prep_time: Optional[int]
    cook_time: Optional[int]
    total_time: Optional[int]
    category: Optional[str]
    cuisine: Optional[str]
    difficulty_level: Optional[str]
    temperature: Optional[int]
    temperature_unit: Optional[str]
    instructions: str
    notes: Optional[str]
    is_public: bool
    ingredients: List[RecipeIngredientResponse]
    equipment: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class RecipeListResponse(BaseModel):
    """Simple recipe list response"""
    id: str
    title: str
    description: Optional[str]
    category: Optional[str]
    cuisine: Optional[str]
    servings: Optional[int]
    total_time: Optional[int]
    is_public: bool
    
    class Config:
        from_attributes = True


@router.get("/recipes", response_model=List[RecipeListResponse])
async def list_all_recipes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """List all recipes (admin view - includes private recipes)"""
    recipes = db.query(Recipe).order_by(Recipe.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        RecipeListResponse(
            id=str(recipe.id),
            title=recipe.title,
            description=recipe.description,
            category=recipe.category,
            cuisine=recipe.cuisine,
            servings=recipe.servings,
            total_time=recipe.total_time,
            is_public=recipe.is_public
        )
        for recipe in recipes
    ]


@router.post("/recipes", response_model=RecipeDetailResponse)
async def create_recipe(
    recipe_data: RecipeCreateRequest,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Create a new recipe with structured ingredients"""
    
    # Create the recipe
    new_recipe = Recipe(
        title=recipe_data.title,
        description=recipe_data.description,
        servings=recipe_data.servings,
        prep_time=recipe_data.prep_time,
        cook_time=recipe_data.cook_time,
        total_time=recipe_data.total_time,
        category=recipe_data.category,
        cuisine=recipe_data.cuisine,
        difficulty_level=recipe_data.difficulty_level,
        temperature=recipe_data.temperature,
        temperature_unit=recipe_data.temperature_unit,
        instructions=recipe_data.instructions,
        notes=recipe_data.notes,
        is_public=recipe_data.is_public,
        ingredients=[],  # Keep empty array for backward compatibility
        equipment=recipe_data.equipment
    )
    
    db.add(new_recipe)
    db.flush()  # Get the recipe ID without committing
    
    # Add recipe ingredients
    recipe_ingredients = []
    for idx, ing_data in enumerate(recipe_data.ingredients):
        # Verify ingredient exists in MongoDB (only if ingredient_off_id is provided)
        if ing_data.ingredient_off_id:
            ingredient = await Ingredient.find_one({"off_id": ing_data.ingredient_off_id})
            
            if not ingredient:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ingredient {ing_data.ingredient_off_id} not found"
                )
        
        recipe_ingredient = RecipeIngredient(
            recipe_id=new_recipe.id,
            ingredient_off_id=ing_data.ingredient_off_id or None,  # Allow empty/null
            quantity=Decimal(str(ing_data.quantity)) if ing_data.quantity else None,
            quantity_max=Decimal(str(ing_data.quantity_max)) if ing_data.quantity_max else None,
            unit=ing_data.unit,
            preparation_notes=ing_data.preparation_notes,
            is_optional=ing_data.is_optional,
            display_order=ing_data.display_order if ing_data.display_order is not None else idx
        )
        
        db.add(recipe_ingredient)
        recipe_ingredients.append(recipe_ingredient)
    
    db.commit()
    db.refresh(new_recipe)
    
    # Build response
    ingredient_responses = []
    for ri in recipe_ingredients:
        db.refresh(ri)
        # Fetch ingredient from MongoDB (only if off_id is provided)
        ingredient = None
        if ri.ingredient_off_id:
            ingredient = await Ingredient.find_one({"off_id": ri.ingredient_off_id})
        
        ingredient_responses.append(RecipeIngredientResponse(
            id=str(ri.id),
            ingredient_off_id=ri.ingredient_off_id,
            ingredient_name=ingredient.get_name("fr") if ingredient else None,
            ingredient_name_en=ingredient.get_name("en") if ingredient else None,
            ingredient_name_fr=ingredient.get_name("fr") if ingredient else None,
            quantity=float(ri.quantity) if ri.quantity else None,
            quantity_max=float(ri.quantity_max) if ri.quantity_max else None,
            unit=ri.unit,
            preparation_notes=ri.preparation_notes,
            is_optional=ri.is_optional,
            display_order=ri.display_order
        ))
    
    return RecipeDetailResponse(
        id=str(new_recipe.id),
        title=new_recipe.title,
        description=new_recipe.description,
        servings=new_recipe.servings,
        prep_time=new_recipe.prep_time,
        cook_time=new_recipe.cook_time,
        total_time=new_recipe.total_time,
        category=new_recipe.category,
        cuisine=new_recipe.cuisine,
        difficulty_level=new_recipe.difficulty_level,
        temperature=new_recipe.temperature,
        temperature_unit=new_recipe.temperature_unit,
        instructions=new_recipe.instructions,
        notes=new_recipe.notes,
        is_public=new_recipe.is_public,
        ingredients=ingredient_responses,
        equipment=new_recipe.equipment
    )


@router.get("/recipes/{recipe_id}", response_model=RecipeDetailResponse)
async def get_admin_recipe(
    recipe_id: UUID,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Get recipe details with structured ingredients for admin"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Get recipe ingredients from recipe_ingredients table
    recipe_ingredients = db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id == recipe_id
    ).order_by(RecipeIngredient.display_order).all()
    
    # Build ingredient responses with MongoDB data
    ingredient_responses = []
    
    # Check if we have structured ingredients, otherwise use legacy text array
    if recipe_ingredients:
        # New format: structured ingredients from recipe_ingredients table
        for ri in recipe_ingredients:
            # Fetch ingredient from MongoDB (only if off_id is provided)
            ingredient = None
            if ri.ingredient_off_id:
                ingredient = await Ingredient.find_one({"off_id": ri.ingredient_off_id})
            
            ingredient_responses.append(
                RecipeIngredientResponse(
                    id=str(ri.id),
                    ingredient_off_id=ri.ingredient_off_id,
                    ingredient_name=ingredient.get_name("fr") if ingredient else None,
                    ingredient_name_en=ingredient.get_name("en") if ingredient else None,
                    ingredient_name_fr=ingredient.get_name("fr") if ingredient else None,
                    quantity=float(ri.quantity) if ri.quantity else None,
                    quantity_max=float(ri.quantity_max) if ri.quantity_max else None,
                    unit=ri.unit,
                    preparation_notes=ri.preparation_notes,
                    is_optional=ri.is_optional,
                    display_order=ri.display_order
                )
            )
    elif recipe.ingredients:
        # Legacy format: text array in recipes.ingredients column
        for idx, ing_text in enumerate(recipe.ingredients):
            ingredient_responses.append(
                RecipeIngredientResponse(
                    id=f"legacy-{idx}",
                    ingredient_off_id="",
                    ingredient_name=ing_text,
                    ingredient_name_en=ing_text,
                    ingredient_name_fr=ing_text,
                    quantity=None,
                    quantity_max=None,
                    unit=None,
                    preparation_notes=ing_text,  # Store full text here
                    is_optional=False,
                    display_order=idx
                )
            )
    
    return RecipeDetailResponse(
        id=str(recipe.id),
        title=recipe.title,
        description=recipe.description,
        servings=recipe.servings,
        prep_time=recipe.prep_time,
        cook_time=recipe.cook_time,
        total_time=recipe.total_time,
        category=recipe.category,
        cuisine=recipe.cuisine,
        difficulty_level=recipe.difficulty_level,
        temperature=recipe.temperature,
        temperature_unit=recipe.temperature_unit,
        instructions=recipe.instructions,
        notes=recipe.notes,
        is_public=recipe.is_public,
        ingredients=ingredient_responses,
        equipment=recipe.equipment
    )


@router.put("/recipes/{recipe_id}", response_model=RecipeDetailResponse)
async def update_recipe(
    recipe_id: UUID,
    recipe_data: RecipeUpdateRequest,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Update a recipe and its ingredients"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Update recipe fields
    if recipe_data.title is not None:
        recipe.title = recipe_data.title
    if recipe_data.description is not None:
        recipe.description = recipe_data.description
    if recipe_data.servings is not None:
        recipe.servings = recipe_data.servings
    if recipe_data.prep_time is not None:
        recipe.prep_time = recipe_data.prep_time
    if recipe_data.cook_time is not None:
        recipe.cook_time = recipe_data.cook_time
    if recipe_data.total_time is not None:
        recipe.total_time = recipe_data.total_time
    if recipe_data.category is not None:
        recipe.category = recipe_data.category
    if recipe_data.cuisine is not None:
        recipe.cuisine = recipe_data.cuisine
    if recipe_data.difficulty_level is not None:
        recipe.difficulty_level = recipe_data.difficulty_level
    if recipe_data.temperature is not None:
        recipe.temperature = recipe_data.temperature
    if recipe_data.temperature_unit is not None:
        recipe.temperature_unit = recipe_data.temperature_unit
    if recipe_data.instructions is not None:
        recipe.instructions = recipe_data.instructions
    if recipe_data.notes is not None:
        recipe.notes = recipe_data.notes
    if recipe_data.is_public is not None:
        recipe.is_public = recipe_data.is_public
    if recipe_data.equipment is not None:
        recipe.equipment = recipe_data.equipment
    
    # Update ingredients if provided
    if recipe_data.ingredients is not None:
        # Remove existing recipe ingredients
        db.query(RecipeIngredient).filter(
            RecipeIngredient.recipe_id == recipe_id
        ).delete()
        
        # Add new recipe ingredients
        for idx, ing_data in enumerate(recipe_data.ingredients):
            # Verify ingredient exists in MongoDB (only if ingredient_off_id is provided)
            if ing_data.ingredient_off_id:
                ingredient = await Ingredient.find_one({"off_id": ing_data.ingredient_off_id})
                
                if not ingredient:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Ingredient {ing_data.ingredient_off_id} not found"
                    )
            
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe_id,
                ingredient_off_id=ing_data.ingredient_off_id or None,  # Allow empty/null
                quantity=Decimal(str(ing_data.quantity)) if ing_data.quantity else None,
                quantity_max=Decimal(str(ing_data.quantity_max)) if ing_data.quantity_max else None,
                unit=ing_data.unit,
                preparation_notes=ing_data.preparation_notes,
                is_optional=ing_data.is_optional,
                display_order=ing_data.display_order if ing_data.display_order is not None else idx
            )
            
            db.add(recipe_ingredient)
    
    db.commit()
    db.refresh(recipe)
    
    # Get updated ingredients
    recipe_ingredients = db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id == recipe_id
    ).order_by(RecipeIngredient.display_order).all()
    
    # Build ingredient responses with MongoDB data
    ingredient_responses = []
    for ri in recipe_ingredients:
        # Fetch ingredient from MongoDB (only if off_id is provided)
        ingredient = None
        if ri.ingredient_off_id:
            ingredient = await Ingredient.find_one({"off_id": ri.ingredient_off_id})
        
        ingredient_responses.append(
            RecipeIngredientResponse(
                id=str(ri.id),
                ingredient_off_id=ri.ingredient_off_id,
                ingredient_name=ingredient.get_name("fr") if ingredient else None,
                ingredient_name_en=ingredient.get_name("en") if ingredient else None,
                ingredient_name_fr=ingredient.get_name("fr") if ingredient else None,
                quantity=float(ri.quantity) if ri.quantity else None,
                quantity_max=float(ri.quantity_max) if ri.quantity_max else None,
                unit=ri.unit,
                preparation_notes=ri.preparation_notes,
                is_optional=ri.is_optional,
                display_order=ri.display_order
            )
        )
    
    return RecipeDetailResponse(
        id=str(recipe.id),
        title=recipe.title,
        description=recipe.description,
        servings=recipe.servings,
        prep_time=recipe.prep_time,
        cook_time=recipe.cook_time,
        total_time=recipe.total_time,
        category=recipe.category,
        cuisine=recipe.cuisine,
        difficulty_level=recipe.difficulty_level,
        temperature=recipe.temperature,
        temperature_unit=recipe.temperature_unit,
        instructions=recipe.instructions,
        notes=recipe.notes,
        is_public=recipe.is_public,
        ingredients=ingredient_responses,
        equipment=recipe.equipment
    )


@router.delete("/recipes/{recipe_id}")
async def delete_recipe(
    recipe_id: UUID,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Delete a recipe"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    db.delete(recipe)
    db.commit()
    
    return {"message": "Recipe deleted successfully"}
