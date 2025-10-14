"""
API endpoints for ingredients using MongoDB.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from app.models.mongodb import Ingredient

router = APIRouter()


@router.get("/", summary="Search ingredients")
async def search_ingredients(
    search: Optional[str] = Query(None, description="Search query"),
    language: str = Query("en", description="Language code (en, fr, etc.)"),
    limit: int = Query(50, description="Maximum results", ge=1, le=1000),
    skip: int = Query(0, description="Number of records to skip", ge=0),
    custom_only: bool = Query(False, description="Only custom ingredients")
):
    """
    Search ingredients in the database with pagination.
    
    - **search**: Search query (optional). Searches across all 5,942 ingredients.
    - **language**: Language code for results (default: en)
    - **limit**: Maximum number of results (default: 50, max: 1000)
    - **skip**: Number of records to skip for pagination (default: 0)
    - **custom_only**: If true, only return custom ingredients
    """
    if search:
        ingredients = await Ingredient.search(
            query=search,
            language=language,
            limit=limit,
            skip=skip,
            custom_only=custom_only
        )
    else:
        # No search query - get all ingredients with limit and skip
        query_filter = {"custom": True} if custom_only else {}
        ingredients = await Ingredient.find(query_filter).skip(skip).limit(limit).to_list()
    
    # Format response with localized names
    return [
        {
            "id": str(ing.id),
            "off_id": ing.off_id,
            "name": ing.get_name(language),
            "names": ing.names,
            "vegan": ing.is_vegan(),
            "vegetarian": ing.is_vegetarian(),
            "custom": ing.custom,
            "wikidata_id": ing.wikidata_id,
        }
        for ing in ingredients
    ]


@router.get("/{off_id}", summary="Get ingredient by ID")
async def get_ingredient(off_id: str):
    """
    Get a specific ingredient by its OpenFoodFacts ID.
    
    - **off_id**: OpenFoodFacts ingredient ID (e.g., "en:tomato")
    """
    ingredient = await Ingredient.get_by_off_id(off_id)
    
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    
    return {
        "id": str(ingredient.id),
        "off_id": ingredient.off_id,
        "names": ingredient.names,
        "parents": ingredient.parents,
        "children": ingredient.children,
        "properties": ingredient.properties,
        "vegan": ingredient.is_vegan(),
        "vegetarian": ingredient.is_vegetarian(),
        "wikidata_id": ingredient.wikidata_id,
        "ciqual_food_code": ingredient.ciqual_food_code,
        "e_number": ingredient.e_number,
        "custom": ingredient.custom,
        "created_at": ingredient.created_at,
        "updated_at": ingredient.updated_at,
    }


@router.get("/{off_id}/parents", summary="Get ingredient parents")
async def get_ingredient_parents(off_id: str, language: str = Query("en")):
    """
    Get parent ingredients in the taxonomy hierarchy.
    
    - **off_id**: OpenFoodFacts ingredient ID
    - **language**: Language code for names (default: en)
    """
    ingredient = await Ingredient.get_by_off_id(off_id)
    
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    
    parents = await ingredient.get_parent_ingredients()
    
    return [
        {
            "off_id": parent.off_id,
            "name": parent.get_name(language),
            "names": parent.names,
        }
        for parent in parents
    ]


@router.get("/{off_id}/children", summary="Get ingredient children")
async def get_ingredient_children(off_id: str, language: str = Query("en")):
    """
    Get child ingredients (more specific variants) in the taxonomy.
    
    - **off_id**: OpenFoodFacts ingredient ID
    - **language**: Language code for names (default: en)
    """
    ingredient = await Ingredient.get_by_off_id(off_id)
    
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    
    children = await ingredient.get_child_ingredients()
    
    return [
        {
            "off_id": child.off_id,
            "name": child.get_name(language),
            "names": child.names,
        }
        for child in children
    ]


@router.get("/stats/summary", summary="Get ingredient statistics")
async def get_ingredient_stats():
    """
    Get statistics about the ingredients database.
    """
    total = await Ingredient.count()
    custom = await Ingredient.find({"custom": True}).count()
    off = total - custom
    
    # Count ingredients with properties
    vegan_count = await Ingredient.find(
        {"properties.vegan": {"$exists": True}}
    ).count()
    
    vegetarian_count = await Ingredient.find(
        {"properties.vegetarian": {"$exists": True}}
    ).count()
    
    with_wikidata = await Ingredient.find(
        {"wikidata_id": {"$ne": None}}
    ).count()
    
    return {
        "total": total,
        "from_openfoodfacts": off,
        "custom": custom,
        "with_vegan_info": vegan_count,
        "with_vegetarian_info": vegetarian_count,
        "with_wikidata": with_wikidata,
    }
