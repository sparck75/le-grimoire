"""
API endpoints for categories using MongoDB.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.models.mongodb import Category

router = APIRouter()


@router.get("/", summary="List categories")
async def list_categories(
    search: Optional[str] = Query(None, description="Search query"),
    language: str = Query("en", description="Language code (en, fr, etc.)"),
    top_level_only: bool = Query(False, description="Only top-level categories"),
    with_icon_only: bool = Query(False, description="Only categories with icons"),
    limit: int = Query(100, description="Maximum results", ge=1, le=500)
):
    """
    List or search categories.
    
    - **search**: Search query (optional)
    - **language**: Language code for results (default: en)
    - **top_level_only**: If true, only return top-level categories (no parents)
    - **with_icon_only**: If true, only return categories with emoji icons
    - **limit**: Maximum number of results (default: 100, max: 500)
    """
    if top_level_only:
        categories = await Category.get_top_level_categories()
    elif with_icon_only:
        categories = await Category.get_categories_with_icon()
    elif search:
        categories = await Category.search(
            query=search,
            language=language,
            limit=limit
        )
    else:
        # Get all categories with limit
        categories = await Category.find_all().limit(limit).to_list()
    
    # Format response
    return [
        {
            "off_id": cat.off_id,
            "name": cat.get_name(language),
            "names": cat.names,
            "icon": cat.icon,
            "is_top_level": cat.is_top_level(),
            "parent_count": len(cat.parents),
            "children_count": len(cat.children),
        }
        for cat in categories
    ]


@router.get("/top-level", summary="Get top-level categories")
async def get_top_level_categories(language: str = Query("en")):
    """
    Get all top-level categories (no parents).
    
    - **language**: Language code for names (default: en)
    """
    categories = await Category.get_top_level_categories()
    
    return [
        {
            "off_id": cat.off_id,
            "name": cat.get_name(language),
            "icon": cat.icon,
            "children_count": len(cat.children),
        }
        for cat in categories
    ]


@router.get("/{off_id}", summary="Get category by ID")
async def get_category(off_id: str, language: str = Query("en")):
    """
    Get a specific category by its OpenFoodFacts ID.
    
    - **off_id**: OpenFoodFacts category ID (e.g., "en:plant-based-foods")
    - **language**: Language code for names (default: en)
    """
    category = await Category.get_by_off_id(off_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {
        "id": str(category.id),
        "off_id": category.off_id,
        "name": category.get_name(language),
        "names": category.names,
        "icon": category.icon,
        "parents": category.parents,
        "children": category.children,
        "wikidata_id": category.wikidata_id,
        "agribalyse_code": category.agribalyse_code,
        "origins": category.origins,
        "is_top_level": category.is_top_level(),
        "created_at": category.created_at,
        "updated_at": category.updated_at,
    }


@router.get("/{off_id}/parents", summary="Get category parents")
async def get_category_parents(off_id: str, language: str = Query("en")):
    """
    Get parent categories in the taxonomy hierarchy.
    
    - **off_id**: OpenFoodFacts category ID
    - **language**: Language code for names (default: en)
    """
    category = await Category.get_by_off_id(off_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    parents = await category.get_parent_categories()
    
    return [
        {
            "off_id": parent.off_id,
            "name": parent.get_name(language),
            "icon": parent.icon,
        }
        for parent in parents
    ]


@router.get("/{off_id}/children", summary="Get category children")
async def get_category_children(off_id: str, language: str = Query("en")):
    """
    Get child categories (subcategories) in the taxonomy.
    
    - **off_id**: OpenFoodFacts category ID
    - **language**: Language code for names (default: en)
    """
    category = await Category.get_by_off_id(off_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    children = await category.get_child_categories()
    
    return [
        {
            "off_id": child.off_id,
            "name": child.get_name(language),
            "icon": child.icon,
            "children_count": len(child.children),
        }
        for child in children
    ]


@router.get("/{off_id}/descendants", summary="Get all descendants")
async def get_category_descendants(off_id: str, language: str = Query("en")):
    """
    Get all descendant categories (entire subtree).
    
    - **off_id**: OpenFoodFacts category ID
    - **language**: Language code for names (default: en)
    """
    category = await Category.get_by_off_id(off_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    descendants = await category.get_all_descendants()
    
    return {
        "category": {
            "off_id": category.off_id,
            "name": category.get_name(language),
            "icon": category.icon,
        },
        "total_descendants": len(descendants),
        "descendants": [
            {
                "off_id": desc.off_id,
                "name": desc.get_name(language),
                "icon": desc.icon,
            }
            for desc in descendants[:100]  # Limit to first 100
        ]
    }


@router.get("/stats/summary", summary="Get category statistics")
async def get_category_stats():
    """
    Get statistics about the categories database.
    """
    total = await Category.count()
    top_level = await Category.find({"parents": {"$size": 0}}).count()
    with_icon = await Category.find({"icon": {"$ne": None}}).count()
    with_wikidata = await Category.find({"wikidata_id": {"$ne": None}}).count()
    
    return {
        "total": total,
        "top_level": top_level,
        "with_icon": with_icon,
        "with_wikidata": with_wikidata,
    }
