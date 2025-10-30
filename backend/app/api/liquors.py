"""
Liquors API routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.mongodb import Liquor
from app.models.mongodb.liquor import ProfessionalRating

router = APIRouter()


class LiquorResponse(BaseModel):
    """Liquor response model"""
    id: str
    name: str
    brand: Optional[str]
    spirit_type: str
    region: str
    country: str
    current_quantity: int
    image_url: Optional[str]
    rating: Optional[float]
    alcohol_content: Optional[float] = None
    age_statement: Optional[str] = None
    tasting_notes: str = ""
    
    class Config:
        from_attributes = True


class LiquorCreate(BaseModel):
    """Liquor creation request"""
    name: str
    brand: Optional[str] = None
    distillery: Optional[str] = None
    country: str = ""
    region: str = ""
    spirit_type: str = "other"
    subtype: Optional[str] = None
    alcohol_content: Optional[float] = None
    age_statement: Optional[str] = None
    cask_type: Optional[str] = None
    finish: Optional[str] = None
    color: str = ""
    nose: List[str] = []
    palate: List[str] = []
    finish_notes: str = ""
    tasting_notes: str = ""
    cocktail_uses: List[str] = []
    food_pairings: List[str] = []
    serving_suggestion: str = ""
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    purchase_location: Optional[str] = None
    current_quantity: int = 100
    cellar_location: Optional[str] = None
    rating: Optional[float] = None
    image_url: Optional[str] = None
    barcode: Optional[str] = None
    is_public: bool = False


class LiquorUpdate(BaseModel):
    """Liquor update request"""
    name: Optional[str] = None
    brand: Optional[str] = None
    distillery: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    spirit_type: Optional[str] = None
    subtype: Optional[str] = None
    alcohol_content: Optional[float] = None
    age_statement: Optional[str] = None
    cask_type: Optional[str] = None
    finish: Optional[str] = None
    color: Optional[str] = None
    nose: Optional[List[str]] = None
    palate: Optional[List[str]] = None
    finish_notes: Optional[str] = None
    tasting_notes: Optional[str] = None
    cocktail_uses: Optional[List[str]] = None
    food_pairings: Optional[List[str]] = None
    serving_suggestion: Optional[str] = None
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    purchase_location: Optional[str] = None
    current_quantity: Optional[int] = None
    cellar_location: Optional[str] = None
    rating: Optional[float] = None
    image_url: Optional[str] = None
    barcode: Optional[str] = None
    is_public: Optional[bool] = None


@router.get("/", response_model=List[LiquorResponse])
async def list_liquors(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    spirit_type: Optional[str] = None,
    brand: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    in_stock: bool = False
):
    """List liquors with optional filtering"""
    query = {}
    
    if spirit_type:
        query["spirit_type"] = spirit_type
    if brand:
        query["brand"] = brand
    if country:
        query["country"] = country
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"brand": {"$regex": search, "$options": "i"}}
        ]
    if in_stock:
        query["current_quantity"] = {"$gt": 0}
    
    liquors = await Liquor.find(query).skip(skip).limit(limit).to_list()
    
    return [
        LiquorResponse(
            id=str(liquor.id),
            name=liquor.name,
            brand=liquor.brand,
            spirit_type=liquor.spirit_type,
            region=liquor.region,
            country=liquor.country,
            current_quantity=liquor.current_quantity,
            image_url=liquor.image_url,
            rating=liquor.rating,
            alcohol_content=liquor.alcohol_content,
            age_statement=liquor.age_statement,
            tasting_notes=liquor.tasting_notes
        )
        for liquor in liquors
    ]


@router.get("/{liquor_id}", response_model=LiquorResponse)
async def get_liquor(liquor_id: str):
    """Get specific liquor"""
    liquor = await Liquor.get(liquor_id)
    if not liquor:
        raise HTTPException(status_code=404, detail="Liquor not found")
    
    return LiquorResponse(
        id=str(liquor.id),
        name=liquor.name,
        brand=liquor.brand,
        spirit_type=liquor.spirit_type,
        region=liquor.region,
        country=liquor.country,
        current_quantity=liquor.current_quantity,
        image_url=liquor.image_url,
        rating=liquor.rating,
        alcohol_content=liquor.alcohol_content,
        age_statement=liquor.age_statement,
        tasting_notes=liquor.tasting_notes
    )


@router.post("/", response_model=LiquorResponse)
async def create_liquor(liquor_data: LiquorCreate):
    """Create new liquor"""
    liquor = Liquor(**liquor_data.dict())
    await liquor.insert()
    
    return LiquorResponse(
        id=str(liquor.id),
        name=liquor.name,
        brand=liquor.brand,
        spirit_type=liquor.spirit_type,
        region=liquor.region,
        country=liquor.country,
        current_quantity=liquor.current_quantity,
        image_url=liquor.image_url,
        rating=liquor.rating,
        alcohol_content=liquor.alcohol_content,
        age_statement=liquor.age_statement,
        tasting_notes=liquor.tasting_notes
    )


@router.put("/{liquor_id}", response_model=LiquorResponse)
async def update_liquor(liquor_id: str, liquor_data: LiquorUpdate):
    """Update liquor"""
    liquor = await Liquor.get(liquor_id)
    if not liquor:
        raise HTTPException(status_code=404, detail="Liquor not found")
    
    # Update fields
    update_dict = liquor_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(liquor, field, value)
    
    liquor.updated_at = datetime.utcnow()
    await liquor.save()
    
    return LiquorResponse(
        id=str(liquor.id),
        name=liquor.name,
        brand=liquor.brand,
        spirit_type=liquor.spirit_type,
        region=liquor.region,
        country=liquor.country,
        current_quantity=liquor.current_quantity,
        image_url=liquor.image_url,
        rating=liquor.rating,
        alcohol_content=liquor.alcohol_content,
        age_statement=liquor.age_statement,
        tasting_notes=liquor.tasting_notes
    )


@router.delete("/{liquor_id}")
async def delete_liquor(liquor_id: str):
    """Delete liquor"""
    liquor = await Liquor.get(liquor_id)
    if not liquor:
        raise HTTPException(status_code=404, detail="Liquor not found")
    
    await liquor.delete()
    return {"message": "Liquor deleted successfully"}


@router.get("/stats/summary")
async def get_liquor_stats():
    """Get liquor statistics"""
    total = await Liquor.count()
    
    # Aggregate by type
    pipeline = [
        {"$group": {"_id": "$spirit_type", "count": {"$sum": 1}}}
    ]
    by_type_cursor = Liquor.aggregate(pipeline)
    by_type_list = await by_type_cursor.to_list()
    by_type = {item["_id"]: item["count"] for item in by_type_list}
    
    # Count in stock
    in_stock = await Liquor.find({"current_quantity": {"$gt": 0}}).count()
    
    return {
        "total": total,
        "in_stock": in_stock,
        "by_type": by_type
    }
