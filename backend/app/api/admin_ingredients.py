"""
Admin Ingredients API routes - MongoDB Version

This endpoint now uses the OpenFoodFacts MongoDB data.
Old PostgreSQL-based ingredients have been replaced.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.models.mongodb import Ingredient, Category

router = APIRouter()


# Response models
class IngredientResponse(BaseModel):
    """Ingredient response for admin panel"""
    id: str
    off_id: str
    name: str
    english_name: str
    french_name: str
    is_vegan: Optional[bool] = None
    is_vegetarian: Optional[bool] = None
    custom: bool
    wikidata_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    """Category response for admin panel"""
    off_id: str
    name: str
    english_name: str
    french_name: str
    icon: Optional[str] = None
    parent_count: int
    children_count: int
    
    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Paginated response"""
    items: List[IngredientResponse]
    total: int
    page: int
    limit: int
    pages: int


# Categories endpoints (must be before /{ingredient_id} to avoid route conflict)
@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(
    language: str = Query("en", description="Language"),
    top_level_only: bool = Query(False, description="Only top-level categories"),
    sort_by: str = Query("children_count", description="Sort by: children_count, name, off_id"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of categories")
):
    """
    List ingredient categories.
    
    Returns categories sorted by number of children (most useful categories first).
    Set top_level_only=true to only get root categories.
    """
    if top_level_only:
        categories = await Category.find({"parents": {"$size": 0}}).to_list()
    else:
        # Get all categories
        categories = await Category.find_all().to_list()
    
    # Convert to response format
    category_responses = [
        CategoryResponse(
            off_id=cat.off_id,
            name=cat.get_name(language),
            english_name=cat.get_name("en"),
            french_name=cat.get_name("fr"),
            icon=cat.icon,
            parent_count=len(cat.parents),
            children_count=len(cat.children)
        )
        for cat in categories
    ]
    
    # Sort by requested field
    if sort_by == "children_count":
        category_responses.sort(key=lambda x: x.children_count, reverse=True)
    elif sort_by == "name":
        category_responses.sort(key=lambda x: x.name.lower())
    elif sort_by == "off_id":
        category_responses.sort(key=lambda x: x.off_id)
    
    # Apply limit
    return category_responses[:limit]


@router.get("/categories/{category_id}")
async def get_category(
    category_id: str,
    language: str = Query("en")
):
    """
    Get specific category details.
    """
    category = await Category.find_one({"off_id": category_id})
    
    if not category:
        try:
            category = await Category.get(category_id)
        except:
            raise HTTPException(status_code=404, detail="Category not found")
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {
        "id": str(category.id),
        "off_id": category.off_id,
        "name": category.get_name(language),
        "names": category.names,
        "english_name": category.get_name("en"),
        "french_name": category.get_name("fr"),
        "icon": category.icon,
        "parents": category.parents,
        "children": category.children,
        "wikidata_id": category.wikidata_id,
        "is_top_level": category.is_top_level()
    }


@router.get("/stats")
async def get_simple_stats():
    """
    Get simple ingredient statistics for admin dashboard.
    Simplified version for frontend compatibility.
    """
    total_ingredients = await Ingredient.count()
    
    return {
        "total_ingredients": total_ingredients,
    }


@router.get("/stats/summary")
async def get_stats():
    """
    Get detailed ingredient and category statistics for admin dashboard.
    """
    total_ingredients = await Ingredient.count()
    custom_ingredients = await Ingredient.find({"custom": True}).count()
    total_categories = await Category.count()
    top_level_categories = await Category.find({"parents": {"$size": 0}}).count()
    
    return {
        "ingredients": {
            "total": total_ingredients,
            "from_openfoodfacts": total_ingredients - custom_ingredients,
            "custom": custom_ingredients
        },
        "categories": {
            "total": total_categories,
            "top_level": top_level_categories
        }
    }


# Ingredients endpoints
@router.get("/", response_model=PaginatedResponse)
async def list_ingredients(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    search: Optional[str] = Query(None, description="Search query"),
    language: str = Query("en", description="Language for names"),
    custom_only: bool = Query(False, description="Only custom ingredients")
):
    """
    List ingredients with pagination.
    
    This endpoint provides backward compatibility with the old admin panel
    while using the new MongoDB data structure.
    """
    # Calculate skip
    skip = (page - 1) * limit
    
    # Build query
    if search:
        ingredients = await Ingredient.search(
            query=search,
            language=language,
            limit=limit,
            custom_only=custom_only
        )
        total = len(ingredients)
    else:
        query_filter = {"custom": True} if custom_only else {}
        total = await Ingredient.find(query_filter).count()
        ingredients = await Ingredient.find(query_filter).skip(skip).limit(limit).to_list()
    
    # Format response
    items = [
        IngredientResponse(
            id=str(ing.id),
            off_id=ing.off_id,
            name=ing.get_name(language),
            english_name=ing.get_name("en"),
            french_name=ing.get_name("fr"),
            is_vegan=ing.is_vegan(),
            is_vegetarian=ing.is_vegetarian(),
            custom=ing.custom,
            wikidata_id=ing.wikidata_id
        )
        for ing in ingredients
    ]
    
    pages = (total + limit - 1) // limit
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get("/search")
async def search_ingredients(
    q: str = Query(..., description="Search query"),
    language: str = Query("en", description="Language"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Search ingredients for autocomplete.
    
    Returns minimal ingredient data for frontend autocomplete components.
    """
    ingredients = await Ingredient.search(
        query=q,
        language=language,
        limit=limit
    )
    
    return [
        {
            "id": str(ing.id),
            "off_id": ing.off_id,
            "name": ing.get_name(language),
            "english_name": ing.get_name("en"),
            "french_name": ing.get_name("fr")
        }
        for ing in ingredients
    ]


@router.get("/{ingredient_id}")
async def get_ingredient(
    ingredient_id: str,
    language: str = Query("en")
):
    """
    Get specific ingredient details.
    
    Accepts either MongoDB ObjectId or OpenFoodFacts off_id.
    """
    # Try to find by off_id first
    ingredient = await Ingredient.find_one({"off_id": ingredient_id})
    
    # If not found, try by MongoDB ID
    if not ingredient:
        try:
            ingredient = await Ingredient.get(ingredient_id)
        except:
            raise HTTPException(status_code=404, detail="Ingredient not found")
    
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    
    return {
        "id": str(ingredient.id),
        "off_id": ingredient.off_id,
        "name": ingredient.get_name(language),
        "names": ingredient.names,
        "english_name": ingredient.get_name("en"),
        "french_name": ingredient.get_name("fr"),
        "parents": ingredient.parents,
        "children": ingredient.children,
        "properties": ingredient.properties,
        "is_vegan": ingredient.is_vegan(),
        "is_vegetarian": ingredient.is_vegetarian(),
        "wikidata_id": ingredient.wikidata_id,
        "ciqual_food_code": ingredient.ciqual_food_code,
        "custom": ingredient.custom
    }
