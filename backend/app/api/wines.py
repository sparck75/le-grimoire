"""
Wines API routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.mongodb import Wine
from app.models.mongodb.wine import GrapeVariety, ProfessionalRating

router = APIRouter()


class WineResponse(BaseModel):
    """Wine response model"""
    id: str
    name: str
    producer: Optional[str]
    vintage: Optional[int]
    wine_type: str
    region: str
    country: str
    current_quantity: int
    image_url: Optional[str]
    rating: Optional[float]
    appellation: Optional[str] = None
    alcohol_content: Optional[float] = None
    tasting_notes: str = ""
    
    class Config:
        from_attributes = True


class WineCreate(BaseModel):
    """Wine creation request"""
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
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    purchase_location: Optional[str] = None
    current_quantity: int = 0
    cellar_location: Optional[str] = None
    drink_from: Optional[int] = None
    drink_until: Optional[int] = None
    peak_drinking: Optional[str] = None
    rating: Optional[float] = None
    image_url: Optional[str] = None
    barcode: Optional[str] = None
    is_public: bool = False


class WineUpdate(BaseModel):
    """Wine update request"""
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
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    purchase_location: Optional[str] = None
    current_quantity: Optional[int] = None
    cellar_location: Optional[str] = None
    drink_from: Optional[int] = None
    drink_until: Optional[int] = None
    peak_drinking: Optional[str] = None
    rating: Optional[float] = None
    image_url: Optional[str] = None
    barcode: Optional[str] = None
    is_public: Optional[bool] = None


@router.get("/", response_model=List[WineResponse])
async def list_wines(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    wine_type: Optional[str] = None,
    region: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    in_stock: bool = False
):
    """List wines with optional filtering"""
    query = {}
    
    if wine_type:
        query["wine_type"] = wine_type
    if region:
        query["region"] = region
    if country:
        query["country"] = country
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"producer": {"$regex": search, "$options": "i"}}
        ]
    if in_stock:
        query["current_quantity"] = {"$gt": 0}
    
    wines = await Wine.find(query).skip(skip).limit(limit).to_list()
    
    return [
        WineResponse(
            id=str(wine.id),
            name=wine.name,
            producer=wine.producer,
            vintage=wine.vintage,
            wine_type=wine.wine_type,
            region=wine.region,
            country=wine.country,
            current_quantity=wine.current_quantity,
            image_url=wine.image_url,
            rating=wine.rating,
            appellation=wine.appellation,
            alcohol_content=wine.alcohol_content,
            tasting_notes=wine.tasting_notes
        )
        for wine in wines
    ]


@router.get("/{wine_id}", response_model=WineResponse)
async def get_wine(wine_id: str):
    """Get specific wine"""
    wine = await Wine.get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    return WineResponse(
        id=str(wine.id),
        name=wine.name,
        producer=wine.producer,
        vintage=wine.vintage,
        wine_type=wine.wine_type,
        region=wine.region,
        country=wine.country,
        current_quantity=wine.current_quantity,
        image_url=wine.image_url,
        rating=wine.rating,
        appellation=wine.appellation,
        alcohol_content=wine.alcohol_content,
        tasting_notes=wine.tasting_notes
    )


@router.post("/", response_model=WineResponse)
async def create_wine(wine_data: WineCreate):
    """Create new wine"""
    wine = Wine(**wine_data.dict())
    await wine.insert()
    
    return WineResponse(
        id=str(wine.id),
        name=wine.name,
        producer=wine.producer,
        vintage=wine.vintage,
        wine_type=wine.wine_type,
        region=wine.region,
        country=wine.country,
        current_quantity=wine.current_quantity,
        image_url=wine.image_url,
        rating=wine.rating,
        appellation=wine.appellation,
        alcohol_content=wine.alcohol_content,
        tasting_notes=wine.tasting_notes
    )


@router.put("/{wine_id}", response_model=WineResponse)
async def update_wine(wine_id: str, wine_data: WineUpdate):
    """Update wine"""
    wine = await Wine.get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    # Update fields
    update_dict = wine_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(wine, field, value)
    
    wine.updated_at = datetime.utcnow()
    await wine.save()
    
    return WineResponse(
        id=str(wine.id),
        name=wine.name,
        producer=wine.producer,
        vintage=wine.vintage,
        wine_type=wine.wine_type,
        region=wine.region,
        country=wine.country,
        current_quantity=wine.current_quantity,
        image_url=wine.image_url,
        rating=wine.rating,
        appellation=wine.appellation,
        alcohol_content=wine.alcohol_content,
        tasting_notes=wine.tasting_notes
    )


@router.delete("/{wine_id}")
async def delete_wine(wine_id: str):
    """Delete wine"""
    wine = await Wine.get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    await wine.delete()
    return {"message": "Wine deleted successfully"}


@router.get("/stats/summary")
async def get_wine_stats():
    """Get wine statistics"""
    total = await Wine.count()
    
    # Aggregate by type
    pipeline = [
        {"$group": {"_id": "$wine_type", "count": {"$sum": 1}}}
    ]
    by_type_cursor = Wine.aggregate(pipeline)
    by_type_list = await by_type_cursor.to_list()
    by_type = {item["_id"]: item["count"] for item in by_type_list}
    
    # Aggregate by country
    pipeline = [
        {"$group": {"_id": "$country", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    by_country_cursor = Wine.aggregate(pipeline)
    by_country_list = await by_country_cursor.to_list()
    by_country = {item["_id"]: item["count"] for item in by_country_list if item["_id"]}
    
    # Count in stock
    in_stock = await Wine.find({"current_quantity": {"$gt": 0}}).count()
    
    return {
        "total": total,
        "in_stock": in_stock,
        "by_type": by_type,
        "by_country": by_country
    }
