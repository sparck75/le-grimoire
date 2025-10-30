"""
API endpoints for liquors using MongoDB.
"""
from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional
from app.models.mongodb import Liquor, LiquorType, LiquorOrigin
from pydantic import BaseModel

router = APIRouter()


class LiquorCreate(BaseModel):
    """Schema for creating a liquor."""
    name: str
    brand: str = ""
    liquor_type: LiquorType
    origin: Optional[LiquorOrigin] = None
    region: str = ""
    distillery: str = ""
    alcohol_content: Optional[float] = None
    age_statement: Optional[str] = None
    base_ingredient: str = ""
    flavor_notes: List[str] = []
    cocktail_suggestions: List[str] = []
    serving_suggestions: str = ""
    food_pairings: List[str] = []
    description: str = ""
    price_range: Optional[str] = None
    saq_code: Optional[str] = None
    lcbo_code: Optional[str] = None
    custom: bool = False


class LiquorUpdate(BaseModel):
    """Schema for updating a liquor."""
    name: Optional[str] = None
    brand: Optional[str] = None
    liquor_type: Optional[LiquorType] = None
    origin: Optional[LiquorOrigin] = None
    region: Optional[str] = None
    distillery: Optional[str] = None
    alcohol_content: Optional[float] = None
    age_statement: Optional[str] = None
    base_ingredient: Optional[str] = None
    flavor_notes: Optional[List[str]] = None
    cocktail_suggestions: Optional[List[str]] = None
    serving_suggestions: Optional[str] = None
    food_pairings: Optional[List[str]] = None
    description: Optional[str] = None
    price_range: Optional[str] = None
    saq_code: Optional[str] = None
    lcbo_code: Optional[str] = None


@router.get("/", summary="Search liquors")
async def search_liquors(
    search: Optional[str] = Query(None, description="Search query"),
    liquor_type: Optional[LiquorType] = Query(None, description="Filter by liquor type"),
    origin: Optional[LiquorOrigin] = Query(None, description="Filter by origin"),
    limit: int = Query(50, description="Maximum results", ge=1, le=1000),
    skip: int = Query(0, description="Number of records to skip", ge=0),
    custom_only: bool = Query(False, description="Only custom liquors")
):
    """
    Search liquors in the database with pagination.
    
    - **search**: Search query (optional). Searches by name, brand, distillery.
    - **liquor_type**: Filter by liquor type (vodka, whisky, rum, etc.)
    - **origin**: Filter by origin (france, scotland, usa, etc.)
    - **limit**: Maximum number of results (default: 50, max: 1000)
    - **skip**: Number of records to skip for pagination (default: 0)
    - **custom_only**: If true, only return custom liquors
    """
    if search:
        liquors = await Liquor.search(
            query=search,
            liquor_type=liquor_type,
            origin=origin,
            limit=limit,
            skip=skip,
            custom_only=custom_only
        )
    else:
        # No search query - get liquors with filters
        query_filter = {}
        if custom_only:
            query_filter["custom"] = True
        if liquor_type:
            query_filter["liquor_type"] = liquor_type
        if origin:
            query_filter["origin"] = origin
        
        liquors = await Liquor.find(query_filter).skip(skip).limit(limit).to_list()
    
    # Format response
    return [
        {
            "id": str(liquor.id),
            "name": liquor.name,
            "brand": liquor.brand,
            "liquor_type": liquor.liquor_type,
            "origin": liquor.origin,
            "region": liquor.region,
            "distillery": liquor.distillery,
            "alcohol_content": liquor.alcohol_content,
            "age_statement": liquor.age_statement,
            "flavor_notes": liquor.flavor_notes,
            "cocktail_suggestions": liquor.cocktail_suggestions,
            "price_range": liquor.price_range,
            "custom": liquor.custom,
        }
        for liquor in liquors
    ]


@router.get("/{liquor_id}", summary="Get liquor by ID")
async def get_liquor(liquor_id: str):
    """
    Get a specific liquor by its ID.
    
    - **liquor_id**: Liquor document ID
    """
    try:
        liquor = await Liquor.get(liquor_id)
    except Exception:
        liquor = None
    
    if not liquor:
        raise HTTPException(status_code=404, detail="Liquor not found")
    
    return {
        "id": str(liquor.id),
        "name": liquor.name,
        "brand": liquor.brand,
        "liquor_type": liquor.liquor_type,
        "origin": liquor.origin,
        "region": liquor.region,
        "distillery": liquor.distillery,
        "alcohol_content": liquor.alcohol_content,
        "age_statement": liquor.age_statement,
        "color": liquor.color,
        "aroma": liquor.aroma,
        "taste": liquor.taste,
        "finish": liquor.finish,
        "base_ingredient": liquor.base_ingredient,
        "distillation_type": liquor.distillation_type,
        "cask_type": liquor.cask_type,
        "filtration": liquor.filtration,
        "flavor_notes": liquor.flavor_notes,
        "sweetness_level": liquor.sweetness_level,
        "cocktail_suggestions": liquor.cocktail_suggestions,
        "serving_suggestions": liquor.serving_suggestions,
        "food_pairings": liquor.food_pairings,
        "description": liquor.description,
        "tasting_notes": liquor.tasting_notes,
        "awards": liquor.awards,
        "price_range": liquor.price_range,
        "saq_code": liquor.saq_code,
        "lcbo_code": liquor.lcbo_code,
        "barcode": liquor.barcode,
        "organic": liquor.organic,
        "kosher": liquor.kosher,
        "gluten_free": liquor.gluten_free,
        "custom": liquor.custom,
        "created_at": liquor.created_at,
        "updated_at": liquor.updated_at,
    }


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create liquor")
async def create_liquor(liquor_data: LiquorCreate):
    """
    Create a new liquor entry.
    
    - **liquor_data**: Liquor information
    """
    # Check if SAQ/LCBO code already exists
    if liquor_data.saq_code:
        existing = await Liquor.get_by_saq_code(liquor_data.saq_code)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Liquor with SAQ code {liquor_data.saq_code} already exists"
            )
    
    if liquor_data.lcbo_code:
        existing = await Liquor.get_by_lcbo_code(liquor_data.lcbo_code)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Liquor with LCBO code {liquor_data.lcbo_code} already exists"
            )
    
    # Create liquor
    liquor = Liquor(**liquor_data.model_dump())
    await liquor.insert()
    
    return {
        "id": str(liquor.id),
        "message": "Liquor created successfully",
        "liquor": {
            "name": liquor.name,
            "brand": liquor.brand,
            "liquor_type": liquor.liquor_type,
            "origin": liquor.origin,
        }
    }


@router.put("/{liquor_id}", summary="Update liquor")
async def update_liquor(liquor_id: str, liquor_data: LiquorUpdate):
    """
    Update an existing liquor entry.
    
    - **liquor_id**: Liquor document ID
    - **liquor_data**: Updated liquor information
    """
    try:
        liquor = await Liquor.get(liquor_id)
    except Exception:
        liquor = None
    
    if not liquor:
        raise HTTPException(status_code=404, detail="Liquor not found")
    
    # Update fields
    update_data = liquor_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(liquor, field, value)
    
    await liquor.save()
    
    return {
        "id": str(liquor.id),
        "message": "Liquor updated successfully",
    }


@router.delete("/{liquor_id}", summary="Delete liquor")
async def delete_liquor(liquor_id: str):
    """
    Delete a liquor entry.
    
    - **liquor_id**: Liquor document ID
    """
    try:
        liquor = await Liquor.get(liquor_id)
    except Exception:
        liquor = None
    
    if not liquor:
        raise HTTPException(status_code=404, detail="Liquor not found")
    
    await liquor.delete()
    
    return {
        "message": "Liquor deleted successfully",
        "id": liquor_id
    }


@router.get("/saq/{saq_code}", summary="Get liquor by SAQ code")
async def get_liquor_by_saq(saq_code: str):
    """
    Get a liquor by its SAQ product code.
    
    - **saq_code**: SAQ product code
    """
    liquor = await Liquor.get_by_saq_code(saq_code)
    
    if not liquor:
        raise HTTPException(status_code=404, detail="Liquor not found")
    
    return {
        "id": str(liquor.id),
        "name": liquor.name,
        "brand": liquor.brand,
        "liquor_type": liquor.liquor_type,
        "saq_code": liquor.saq_code,
        "price_range": liquor.price_range,
    }


@router.get("/types/{liquor_type}", summary="Get liquors by type")
async def get_liquors_by_type(
    liquor_type: LiquorType,
    limit: int = Query(50, description="Maximum results", ge=1, le=1000)
):
    """
    Get liquors by type.
    
    - **liquor_type**: Liquor type (vodka, whisky, rum, etc.)
    - **limit**: Maximum number of results
    """
    liquors = await Liquor.get_by_type(liquor_type, limit)
    
    return [
        {
            "id": str(liquor.id),
            "name": liquor.name,
            "brand": liquor.brand,
            "liquor_type": liquor.liquor_type,
            "origin": liquor.origin,
            "alcohol_content": liquor.alcohol_content,
        }
        for liquor in liquors
    ]


@router.get("/origins/{origin}", summary="Get liquors by origin")
async def get_liquors_by_origin(
    origin: LiquorOrigin,
    limit: int = Query(50, description="Maximum results", ge=1, le=1000)
):
    """
    Get liquors by origin.
    
    - **origin**: Liquor origin (france, scotland, usa, etc.)
    - **limit**: Maximum number of results
    """
    liquors = await Liquor.get_by_origin(origin, limit)
    
    return [
        {
            "id": str(liquor.id),
            "name": liquor.name,
            "brand": liquor.brand,
            "liquor_type": liquor.liquor_type,
            "origin": liquor.origin,
            "distillery": liquor.distillery,
        }
        for liquor in liquors
    ]
