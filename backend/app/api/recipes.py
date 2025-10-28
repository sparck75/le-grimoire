"""
Recipes API routes
"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from bson import ObjectId
from app.models.mongodb import Recipe

router = APIRouter()
logger = logging.getLogger(__name__)

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
    search: Optional[str] = None
):
    """
    List public recipes with optional filtering
    """
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.core.config import settings
    
    # Direct MongoDB connection (same as working import script)
    mongo_url = getattr(settings, 'MONGODB_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db_name = getattr(settings, 'MONGODB_DB_NAME', 'legrimoire')
    db = client[db_name]
    
    # Build query
    query = {}
    if category:
        query["category"] = category
    if cuisine:
        query["cuisine"] = cuisine
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Query MongoDB directly
    cursor = db.recipes.find(query).skip(skip).limit(limit)
    raw_recipes = await cursor.to_list(length=limit)
    
    client.close()
    
    # Convert to response format
    return [
        RecipeResponse(
            id=str(recipe["_id"]),
            title=recipe.get("title", ""),
            description=recipe.get("description", ""),
            ingredients=recipe.get("ingredients", []),
            equipment=recipe.get("equipment", []),
            instructions=recipe.get("instructions", ""),
            servings=recipe.get("servings"),
            prep_time=recipe.get("prep_time"),
            cook_time=recipe.get("cook_time"),
            total_time=recipe.get("total_time"),
            category=recipe.get("category", ""),
            cuisine=recipe.get("cuisine", ""),
            image_url=recipe.get("image_url"),
            is_public=recipe.get("is_public", True)
        )
        for recipe in raw_recipes
    ]

@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: str):
    """
    Get a specific recipe by ID
    """
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.core.config import settings
    
    # Direct MongoDB connection
    mongo_url = getattr(settings, 'MONGODB_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db_name = getattr(settings, 'MONGODB_DB_NAME', 'legrimoire')
    db = client[db_name]
    
    try:
        recipe = await db.recipes.find_one({"_id": ObjectId(recipe_id)})
    except Exception:
        recipe = None
    finally:
        client.close()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if not recipe.get("is_public", True):
        raise HTTPException(status_code=403, detail="Recipe is not public")
    
    return RecipeResponse(
        id=str(recipe["_id"]),
        title=recipe.get("title", ""),
        description=recipe.get("description", ""),
        ingredients=recipe.get("ingredients", []),
        equipment=recipe.get("equipment", []),
        instructions=recipe.get("instructions", ""),
        servings=recipe.get("servings"),
        prep_time=recipe.get("prep_time"),
        cook_time=recipe.get("cook_time"),
        total_time=recipe.get("total_time"),
        category=recipe.get("category", ""),
        cuisine=recipe.get("cuisine", ""),
        image_url=recipe.get("image_url"),
        is_public=recipe.get("is_public", True)
    )


@router.post("/", response_model=RecipeResponse)
async def create_recipe(recipe_data: RecipeCreate):
    """
    Create a new recipe
    """
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.core.config import settings
    
    # Direct MongoDB connection
    mongo_url = getattr(settings, 'MONGODB_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db_name = getattr(settings, 'MONGODB_DB_NAME', 'legrimoire')
    db = client[db_name]
    
    try:
        # Prepare recipe document
        recipe_doc = {
            "title": recipe_data.title,
            "description": recipe_data.description or "",
            "ingredients": recipe_data.ingredients,
            "equipment": recipe_data.equipment or [],
            "instructions": recipe_data.instructions,
            "servings": recipe_data.servings,
            "prep_time": recipe_data.prep_time,
            "cook_time": recipe_data.cook_time,
            "total_time": recipe_data.total_time,
            "category": recipe_data.category or "",
            "cuisine": recipe_data.cuisine or "",
            "image_url": recipe_data.image_url,
            "is_public": recipe_data.is_public,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.recipes.insert_one(recipe_doc)
        recipe_doc["_id"] = result.inserted_id
        
    finally:
        client.close()
    
    return RecipeResponse(
        id=str(recipe_doc["_id"]),
        title=recipe_doc["title"],
        description=recipe_doc["description"],
        ingredients=recipe_doc["ingredients"],
        equipment=recipe_doc["equipment"],
        instructions=recipe_doc["instructions"],
        servings=recipe_doc["servings"],
        prep_time=recipe_doc["prep_time"],
        cook_time=recipe_doc["cook_time"],
        total_time=recipe_doc["total_time"],
        category=recipe_doc["category"],
        cuisine=recipe_doc["cuisine"],
        image_url=recipe_doc["image_url"],
        is_public=recipe_doc["is_public"]
    )


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: str,
    recipe_data: RecipeUpdate
):
    """
    Update an existing recipe
    """
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.core.config import settings
    
    # Direct MongoDB connection
    mongo_url = getattr(settings, 'MONGODB_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db_name = getattr(settings, 'MONGODB_DB_NAME', 'legrimoire')
    db = client[db_name]
    
    try:
        recipe = await db.recipes.find_one({"_id": ObjectId(recipe_id)})
        
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        # Update only provided fields
        update_data = recipe_data.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await db.recipes.update_one(
                {"_id": ObjectId(recipe_id)},
                {"$set": update_data}
            )
            # Fetch updated recipe
            recipe = await db.recipes.find_one({"_id": ObjectId(recipe_id)})
        
    finally:
        client.close()
    
    return RecipeResponse(
        id=str(recipe["_id"]),
        title=recipe.get("title", ""),
        description=recipe.get("description", ""),
        ingredients=recipe.get("ingredients", []),
        equipment=recipe.get("equipment", []),
        instructions=recipe.get("instructions", ""),
        servings=recipe.get("servings"),
        prep_time=recipe.get("prep_time"),
        cook_time=recipe.get("cook_time"),
        total_time=recipe.get("total_time"),
        category=recipe.get("category", ""),
        cuisine=recipe.get("cuisine", ""),
        image_url=recipe.get("image_url"),
        is_public=recipe.get("is_public", True)
    )


@router.delete("/{recipe_id}")
async def delete_recipe(recipe_id: str):
    """
    Delete a recipe
    """
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.core.config import settings
    
    # Direct MongoDB connection
    mongo_url = getattr(settings, 'MONGODB_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db_name = getattr(settings, 'MONGODB_DB_NAME', 'legrimoire')
    db = client[db_name]
    
    try:
        result = await db.recipes.delete_one({"_id": ObjectId(recipe_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Recipe not found")
    finally:
        client.close()
    
    return {"message": "Recipe deleted successfully", "id": recipe_id}
