"""
Admin API for managing wine database (metadata/master wines list)
Separate from user's personal cellier inventory
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.mongodb import Wine
from app.models.mongodb.wine import GrapeVariety
from app.core.security import get_current_user
from app.models.user import User, UserRole

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)):
    """Require user to be admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


class AdminWineResponse(BaseModel):
    """Admin wine response model"""
    id: str
    name: str
    producer: Optional[str]
    vintage: Optional[int]
    wine_type: str
    region: str
    country: str
    appellation: Optional[str] = None
    alcohol_content: Optional[float] = None
    grape_varieties: List[GrapeVariety] = []
    tasting_notes: str = ""
    food_pairings: List[str] = []
    is_public: bool
    data_source: str
    barcode: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AdminWineCreate(BaseModel):
    """Admin wine creation (master database)"""
    name: str
    producer: Optional[str] = None
    vintage: Optional[int] = None
    wine_type: str = "red"
    country: str = ""
    region: str = ""
    appellation: Optional[str] = None
    classification: Optional[str] = None
    grape_varieties: List[GrapeVariety] = []
    alcohol_content: Optional[float] = None
    body: Optional[str] = None
    sweetness: Optional[str] = None
    acidity: Optional[str] = None
    tannins: Optional[str] = None
    color: str = ""
    nose: List[str] = []
    palate: List[str] = []
    tasting_notes: str = ""
    food_pairings: List[str] = []
    image_url: Optional[str] = None
    barcode: Optional[str] = None
    is_public: bool = True  # Master wines are public by default


class AdminWineUpdate(BaseModel):
    """Admin wine update"""
    name: Optional[str] = None
    producer: Optional[str] = None
    vintage: Optional[int] = None
    wine_type: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    appellation: Optional[str] = None
    classification: Optional[str] = None
    grape_varieties: Optional[List[GrapeVariety]] = None
    alcohol_content: Optional[float] = None
    body: Optional[str] = None
    sweetness: Optional[str] = None
    acidity: Optional[str] = None
    tannins: Optional[str] = None
    color: Optional[str] = None
    nose: Optional[List[str]] = None
    palate: Optional[List[str]] = None
    tasting_notes: Optional[str] = None
    food_pairings: Optional[List[str]] = None
    image_url: Optional[str] = None
    barcode: Optional[str] = None
    is_public: Optional[bool] = None


@router.get("/wines", response_model=List[AdminWineResponse])
async def list_master_wines(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    wine_type: Optional[str] = None,
    region: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    barcode: Optional[str] = None,
    current_user: User = Depends(require_admin)
):
    """
    List master wine database (admin only)
    These are the wine templates users can add to their cellier
    """
    query = {"user_id": None}  # Master wines have no user_id
    
    if wine_type:
        query["wine_type"] = wine_type
    if region:
        query["region"] = region
    if country:
        query["country"] = country
    if barcode:
        query["barcode"] = barcode
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"producer": {"$regex": search, "$options": "i"}}
        ]
    
    wines = await Wine.find(query).skip(skip).limit(limit).to_list()
    
    return [
        AdminWineResponse(
            id=str(wine.id),
            name=wine.name,
            producer=wine.producer,
            vintage=wine.vintage,
            wine_type=wine.wine_type,
            region=wine.region,
            country=wine.country,
            appellation=wine.appellation,
            alcohol_content=wine.alcohol_content,
            grape_varieties=wine.grape_varieties,
            tasting_notes=wine.tasting_notes,
            food_pairings=wine.food_pairings,
            is_public=wine.is_public,
            data_source=wine.data_source,
            barcode=wine.barcode,
            created_at=wine.created_at,
            updated_at=wine.updated_at
        )
        for wine in wines
    ]


@router.get("/wines/{wine_id}", response_model=AdminWineResponse)
async def get_master_wine(
    wine_id: str,
    current_user: User = Depends(require_admin)
):
    """Get specific master wine"""
    wine = await Wine.get(wine_id)
    if not wine or wine.user_id is not None:
        raise HTTPException(status_code=404, detail="Master wine not found")
    
    return AdminWineResponse(
        id=str(wine.id),
        name=wine.name,
        producer=wine.producer,
        vintage=wine.vintage,
        wine_type=wine.wine_type,
        region=wine.region,
        country=wine.country,
        appellation=wine.appellation,
        alcohol_content=wine.alcohol_content,
        grape_varieties=wine.grape_varieties,
        tasting_notes=wine.tasting_notes,
        food_pairings=wine.food_pairings,
        is_public=wine.is_public,
        data_source=wine.data_source,
        barcode=wine.barcode,
        created_at=wine.created_at,
        updated_at=wine.updated_at
    )


@router.post("/wines", response_model=AdminWineResponse)
async def create_master_wine(
    wine_data: AdminWineCreate,
    current_user: User = Depends(require_admin)
):
    """Create new master wine (admin only)"""
    wine = Wine(
        **wine_data.dict(),
        user_id=None,  # Master wines have no user
        current_quantity=0,  # Master wines don't have inventory
        data_source="admin"
    )
    await wine.insert()
    
    return AdminWineResponse(
        id=str(wine.id),
        name=wine.name,
        producer=wine.producer,
        vintage=wine.vintage,
        wine_type=wine.wine_type,
        region=wine.region,
        country=wine.country,
        appellation=wine.appellation,
        alcohol_content=wine.alcohol_content,
        grape_varieties=wine.grape_varieties,
        tasting_notes=wine.tasting_notes,
        food_pairings=wine.food_pairings,
        is_public=wine.is_public,
        data_source=wine.data_source,
        barcode=wine.barcode,
        created_at=wine.created_at,
        updated_at=wine.updated_at
    )


@router.put("/wines/{wine_id}", response_model=AdminWineResponse)
async def update_master_wine(
    wine_id: str,
    wine_data: AdminWineUpdate,
    current_user: User = Depends(require_admin)
):
    """Update master wine (admin only)"""
    wine = await Wine.get(wine_id)
    if not wine or wine.user_id is not None:
        raise HTTPException(status_code=404, detail="Master wine not found")
    
    # Update fields
    update_dict = wine_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(wine, field, value)
    
    wine.updated_at = datetime.utcnow()
    await wine.save()
    
    return AdminWineResponse(
        id=str(wine.id),
        name=wine.name,
        producer=wine.producer,
        vintage=wine.vintage,
        wine_type=wine.wine_type,
        region=wine.region,
        country=wine.country,
        appellation=wine.appellation,
        alcohol_content=wine.alcohol_content,
        grape_varieties=wine.grape_varieties,
        tasting_notes=wine.tasting_notes,
        food_pairings=wine.food_pairings,
        is_public=wine.is_public,
        data_source=wine.data_source,
        barcode=wine.barcode,
        created_at=wine.created_at,
        updated_at=wine.updated_at
    )


@router.delete("/wines/{wine_id}")
async def delete_master_wine(
    wine_id: str,
    current_user: User = Depends(require_admin)
):
    """Delete master wine (admin only)"""
    wine = await Wine.get(wine_id)
    if not wine or wine.user_id is not None:
        raise HTTPException(status_code=404, detail="Master wine not found")
    
    await wine.delete()
    return {"message": "Master wine deleted successfully"}


@router.get("/wines/barcode/{barcode}", response_model=AdminWineResponse)
async def find_wine_by_barcode(
    barcode: str,
    current_user: User = Depends(get_current_user)
):
    """
    Find wine by barcode (available to all authenticated users)
    Used for barcode scanning feature
    """
    wine = await Wine.find_one({
        "barcode": barcode,
        "user_id": None  # Only search master wines
    })
    
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found with this barcode")
    
    return AdminWineResponse(
        id=str(wine.id),
        name=wine.name,
        producer=wine.producer,
        vintage=wine.vintage,
        wine_type=wine.wine_type,
        region=wine.region,
        country=wine.country,
        appellation=wine.appellation,
        alcohol_content=wine.alcohol_content,
        grape_varieties=wine.grape_varieties,
        tasting_notes=wine.tasting_notes,
        food_pairings=wine.food_pairings,
        is_public=wine.is_public,
        data_source=wine.data_source,
        barcode=wine.barcode,
        created_at=wine.created_at,
        updated_at=wine.updated_at
    )


@router.get("/stats/summary")
async def get_master_wine_stats(
    current_user: User = Depends(require_admin)
):
    """Get master wine database statistics"""
    total = await Wine.find({"user_id": None}).count()
    
    # Aggregate by type
    pipeline = [
        {"$match": {"user_id": None}},
        {"$group": {"_id": "$wine_type", "count": {"$sum": 1}}}
    ]
    by_type_cursor = Wine.aggregate(pipeline)
    by_type_list = await by_type_cursor.to_list()
    by_type = {item["_id"]: item["count"] for item in by_type_list}
    
    # Count with barcodes
    with_barcode = await Wine.find({
        "user_id": None,
        "barcode": {"$exists": True, "$ne": None, "$ne": ""}
    }).count()
    
    return {
        "total": total,
        "by_type": by_type,
        "with_barcode": with_barcode
    }
