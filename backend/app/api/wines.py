"""
API endpoints for wines using MongoDB.
"""
from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional
from app.models.mongodb import Wine, WineType, WineRegion
from pydantic import BaseModel

router = APIRouter()


class WineCreate(BaseModel):
    """Schema for creating a wine."""
    name: str
    winery: str = ""
    vintage: Optional[int] = None
    wine_type: WineType
    appellation: str = ""
    region: Optional[WineRegion] = None
    subregion: str = ""
    country: str = ""
    grape_varieties: List[str] = []
    alcohol_content: Optional[float] = None
    food_pairings: List[str] = []
    serving_temperature: Optional[str] = None
    description: str = ""
    price_range: Optional[str] = None
    saq_code: Optional[str] = None
    lcbo_code: Optional[str] = None
    custom: bool = False


class WineUpdate(BaseModel):
    """Schema for updating a wine."""
    name: Optional[str] = None
    winery: Optional[str] = None
    vintage: Optional[int] = None
    wine_type: Optional[WineType] = None
    appellation: Optional[str] = None
    region: Optional[WineRegion] = None
    subregion: Optional[str] = None
    country: Optional[str] = None
    grape_varieties: Optional[List[str]] = None
    alcohol_content: Optional[float] = None
    food_pairings: Optional[List[str]] = None
    serving_temperature: Optional[str] = None
    description: Optional[str] = None
    price_range: Optional[str] = None
    saq_code: Optional[str] = None
    lcbo_code: Optional[str] = None


@router.get("/", summary="Search wines")
async def search_wines(
    search: Optional[str] = Query(None, description="Search query"),
    wine_type: Optional[WineType] = Query(None, description="Filter by wine type"),
    region: Optional[WineRegion] = Query(None, description="Filter by region"),
    limit: int = Query(50, description="Maximum results", ge=1, le=1000),
    skip: int = Query(0, description="Number of records to skip", ge=0),
    custom_only: bool = Query(False, description="Only custom wines")
):
    """
    Search wines in the database with pagination.
    
    - **search**: Search query (optional). Searches by name, winery, appellation.
    - **wine_type**: Filter by wine type (red, white, rosé, etc.)
    - **region**: Filter by region (bordeaux, bourgogne, etc.)
    - **limit**: Maximum number of results (default: 50, max: 1000)
    - **skip**: Number of records to skip for pagination (default: 0)
    - **custom_only**: If true, only return custom wines
    """
    if search:
        wines = await Wine.search(
            query=search,
            wine_type=wine_type,
            region=region,
            limit=limit,
            skip=skip,
            custom_only=custom_only
        )
    else:
        # No search query - get wines with filters
        query_filter = {}
        if custom_only:
            query_filter["custom"] = True
        if wine_type:
            query_filter["wine_type"] = wine_type
        if region:
            query_filter["region"] = region
        
        wines = await Wine.find(query_filter).skip(skip).limit(limit).to_list()
    
    # Format response
    return [
        {
            "id": str(wine.id),
            "name": wine.name,
            "winery": wine.winery,
            "vintage": wine.vintage,
            "wine_type": wine.wine_type,
            "region": wine.region,
            "country": wine.country,
            "appellation": wine.appellation,
            "grape_varieties": wine.grape_varieties,
            "alcohol_content": wine.alcohol_content,
            "food_pairings": wine.food_pairings,
            "serving_temperature": wine.serving_temperature,
            "price_range": wine.price_range,
            "custom": wine.custom,
        }
        for wine in wines
    ]


@router.get("/{wine_id}", summary="Get wine by ID")
async def get_wine(wine_id: str):
    """
    Get a specific wine by its ID.
    
    - **wine_id**: Wine document ID
    """
    try:
        wine = await Wine.get(wine_id)
    except Exception:
        wine = None
    
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    return {
        "id": str(wine.id),
        "name": wine.name,
        "winery": wine.winery,
        "vintage": wine.vintage,
        "wine_type": wine.wine_type,
        "appellation": wine.appellation,
        "region": wine.region,
        "subregion": wine.subregion,
        "country": wine.country,
        "grape_varieties": wine.grape_varieties,
        "alcohol_content": wine.alcohol_content,
        "color": wine.color,
        "nose": wine.nose,
        "palate": wine.palate,
        "residual_sugar": wine.residual_sugar,
        "acidity": wine.acidity,
        "tannins": wine.tannins,
        "body": wine.body,
        "food_pairings": wine.food_pairings,
        "serving_temperature": wine.serving_temperature,
        "decanting_time": wine.decanting_time,
        "aging_potential": wine.aging_potential,
        "description": wine.description,
        "tasting_notes": wine.tasting_notes,
        "awards": wine.awards,
        "price_range": wine.price_range,
        "saq_code": wine.saq_code,
        "lcbo_code": wine.lcbo_code,
        "barcode": wine.barcode,
        "custom": wine.custom,
        "created_at": wine.created_at,
        "updated_at": wine.updated_at,
    }


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create wine")
async def create_wine(wine_data: WineCreate):
    """
    Create a new wine entry.
    
    - **wine_data**: Wine information
    """
    # Check if SAQ/LCBO code already exists
    if wine_data.saq_code:
        existing = await Wine.get_by_saq_code(wine_data.saq_code)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Wine with SAQ code {wine_data.saq_code} already exists"
            )
    
    if wine_data.lcbo_code:
        existing = await Wine.get_by_lcbo_code(wine_data.lcbo_code)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Wine with LCBO code {wine_data.lcbo_code} already exists"
            )
    
    # Create wine
    wine = Wine(**wine_data.model_dump())
    await wine.insert()
    
    return {
        "id": str(wine.id),
        "message": "Wine created successfully",
        "wine": {
            "name": wine.name,
            "winery": wine.winery,
            "wine_type": wine.wine_type,
            "vintage": wine.vintage,
        }
    }


@router.put("/{wine_id}", summary="Update wine")
async def update_wine(wine_id: str, wine_data: WineUpdate):
    """
    Update an existing wine entry.
    
    - **wine_id**: Wine document ID
    - **wine_data**: Updated wine information
    """
    try:
        wine = await Wine.get(wine_id)
    except Exception:
        wine = None
    
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    # Update fields
    update_data = wine_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(wine, field, value)
    
    await wine.save()
    
    return {
        "id": str(wine.id),
        "message": "Wine updated successfully",
    }


@router.delete("/{wine_id}", summary="Delete wine")
async def delete_wine(wine_id: str):
    """
    Delete a wine entry.
    
    - **wine_id**: Wine document ID
    """
    try:
        wine = await Wine.get(wine_id)
    except Exception:
        wine = None
    
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    await wine.delete()
    
    return {
        "message": "Wine deleted successfully",
        "id": wine_id
    }


@router.get("/saq/{saq_code}", summary="Get wine by SAQ code")
async def get_wine_by_saq(saq_code: str):
    """
    Get a wine by its SAQ product code.
    
    - **saq_code**: SAQ product code
    """
    wine = await Wine.get_by_saq_code(saq_code)
    
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    return {
        "id": str(wine.id),
        "name": wine.name,
        "winery": wine.winery,
        "wine_type": wine.wine_type,
        "saq_code": wine.saq_code,
        "price_range": wine.price_range,
    }


@router.get("/types/{wine_type}", summary="Get wines by type")
async def get_wines_by_type(
    wine_type: WineType,
    limit: int = Query(50, description="Maximum results", ge=1, le=1000)
):
    """
    Get wines by type.
    
    - **wine_type**: Wine type (red, white, rosé, etc.)
    - **limit**: Maximum number of results
    """
    wines = await Wine.get_by_type(wine_type, limit)
    
    return [
        {
            "id": str(wine.id),
            "name": wine.name,
            "winery": wine.winery,
            "vintage": wine.vintage,
            "wine_type": wine.wine_type,
            "region": wine.region,
        }
        for wine in wines
    ]


@router.get("/regions/{region}", summary="Get wines by region")
async def get_wines_by_region(
    region: WineRegion,
    limit: int = Query(50, description="Maximum results", ge=1, le=1000)
):
    """
    Get wines by region.
    
    - **region**: Wine region (bordeaux, bourgogne, etc.)
    - **limit**: Maximum number of results
    """
    wines = await Wine.get_by_region(region, limit)
    
    return [
        {
            "id": str(wine.id),
            "name": wine.name,
            "winery": wine.winery,
            "vintage": wine.vintage,
            "wine_type": wine.wine_type,
            "region": wine.region,
        }
        for wine in wines
    ]
