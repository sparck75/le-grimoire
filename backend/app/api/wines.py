"""
Wines API routes (User's personal cellier)
"""
from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import uuid
from app.models.mongodb import Wine
from app.models.mongodb.wine import GrapeVariety, ProfessionalRating
from app.core.security import get_current_user, optional_current_user
from app.models.user import User

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
    in_stock: bool = False,
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    List wines in user's personal cellier
    Requires authentication to see personal wines
    """
    # If no user, return empty list (cellier is personal)
    if not current_user:
        return []
    
    query = {"user_id": str(current_user.id)}  # Only user's wines
    
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


@router.get("/master", response_model=List[WineResponse])
async def list_master_wines(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    wine_type: Optional[str] = None,
    region: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    List master wines (admin wines with user_id=None)
    These are the reference wines that users can add to their cellier
    """
    query = {"user_id": None}  # Only master wines
    
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
            current_quantity=wine.current_quantity or 0,
            image_url=wine.image_url,
            rating=wine.rating,
            appellation=wine.appellation,
            alcohol_content=wine.alcohol_content,
            tasting_notes=wine.tasting_notes or ""
        )
        for wine in wines
    ]


@router.get("/{wine_id}", response_model=WineResponse)
async def get_wine(
    wine_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific wine from user's cellier"""
    wine = await Wine.get(wine_id)
    if not wine or wine.user_id != str(current_user.id):
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
async def create_wine(
    wine_data: WineCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new wine in user's cellier"""
    # Convert to dict and override is_public for user wines
    wine_dict = wine_data.dict()
    wine_dict['is_public'] = False  # User wines are always private
    wine_dict['user_id'] = str(current_user.id)  # Associate with user
    
    wine = Wine(**wine_dict)
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
async def update_wine(
    wine_id: str,
    wine_data: WineUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update wine in user's cellier"""
    wine = await Wine.get(wine_id)
    if not wine or wine.user_id != str(current_user.id):
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
async def delete_wine(
    wine_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete wine from user's cellier"""
    wine = await Wine.get(wine_id)
    if not wine or wine.user_id != str(current_user.id):
        raise HTTPException(status_code=404, detail="Wine not found")
    
    await wine.delete()
    return {"message": "Wine deleted successfully"}


@router.post("/add-from-master/{wine_id}", response_model=WineResponse)
async def add_master_wine_to_cellier(
    wine_id: str,
    quantity: int = Query(1, ge=0, description="Initial quantity in cellier"),
    current_user: User = Depends(get_current_user)
):
    """
    Add a master wine to user's personal cellier
    Creates a copy of the master wine with user_id set
    """
    # Get master wine
    master_wine = await Wine.get(wine_id)
    if not master_wine or master_wine.user_id is not None:
        raise HTTPException(status_code=404, detail="Master wine not found")
    
    # Create a copy for user's cellier
    user_wine_data = master_wine.dict(exclude={"id", "user_id", "created_at", "updated_at"})
    user_wine_data["user_id"] = str(current_user.id)
    user_wine_data["current_quantity"] = quantity
    user_wine_data["is_public"] = False  # User wines are private
    
    user_wine = Wine(**user_wine_data)
    await user_wine.insert()
    
    return WineResponse(
        id=str(user_wine.id),
        name=user_wine.name,
        producer=user_wine.producer,
        vintage=user_wine.vintage,
        wine_type=user_wine.wine_type,
        region=user_wine.region,
        country=user_wine.country,
        current_quantity=user_wine.current_quantity,
        image_url=user_wine.image_url,
        rating=user_wine.rating,
        appellation=user_wine.appellation,
        alcohol_content=user_wine.alcohol_content,
        tasting_notes=user_wine.tasting_notes
    )


@router.get("/stats/summary")
async def get_wine_stats(
    current_user: Optional[User] = Depends(optional_current_user)
):
    """Get wine statistics for user's cellier"""
    if not current_user:
        return {"total": 0, "in_stock": 0, "by_type": {}, "by_country": {}}
    
    query = {"user_id": str(current_user.id)}
    total = await Wine.find(query).count()
    
    # Aggregate by type
    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$wine_type", "count": {"$sum": 1}}}
    ]
    by_type_cursor = Wine.aggregate(pipeline)
    by_type_list = await by_type_cursor.to_list()
    by_type = {item["_id"]: item["count"] for item in by_type_list}
    
    # Aggregate by country
    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$country", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    by_country_cursor = Wine.aggregate(pipeline)
    by_country_list = await by_country_cursor.to_list()
    by_country = {item["_id"]: item["count"] for item in by_country_list if item["_id"]}
    
    # Count in stock
    in_stock_query = {**query, "current_quantity": {"$gt": 0}}
    in_stock = await Wine.find(in_stock_query).count()
    
    return {
        "total": total,
        "in_stock": in_stock,
        "by_type": by_type,
        "by_country": by_country
    }


class AddToCellierRequest(BaseModel):
    """Request to add wine from master database to user's cellier"""
    master_wine_id: str
    current_quantity: int = 1
    purchase_price: Optional[float] = None
    purchase_location: Optional[str] = None
    cellar_location: Optional[str] = None
    rating: Optional[float] = None


@router.post("/from-master", response_model=WineResponse)
async def add_wine_from_master(
    request: AddToCellierRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Add a wine from master database to user's cellier
    Used after barcode scanning or browsing master wines
    """
    # Get master wine
    master_wine = await Wine.get(request.master_wine_id)
    if not master_wine or master_wine.user_id is not None:
        raise HTTPException(status_code=404, detail="Master wine not found")
    
    # Create user's copy with inventory info
    user_wine = Wine(
        # Copy all wine metadata from master
        name=master_wine.name,
        producer=master_wine.producer,
        vintage=master_wine.vintage,
        country=master_wine.country,
        region=master_wine.region,
        appellation=master_wine.appellation,
        wine_type=master_wine.wine_type,
        classification=master_wine.classification,
        grape_varieties=master_wine.grape_varieties,
        alcohol_content=master_wine.alcohol_content,
        body=master_wine.body,
        sweetness=master_wine.sweetness,
        acidity=master_wine.acidity,
        tannins=master_wine.tannins,
        color=master_wine.color,
        nose=master_wine.nose,
        palate=master_wine.palate,
        tasting_notes=master_wine.tasting_notes,
        food_pairings=master_wine.food_pairings,
        image_url=master_wine.image_url,
        barcode=master_wine.barcode,
        # Add user-specific inventory info
        user_id=str(current_user.id),
        current_quantity=request.current_quantity,
        purchase_price=request.purchase_price,
        purchase_location=request.purchase_location,
        cellar_location=request.cellar_location,
        rating=request.rating,
        is_public=False
    )
    
    await user_wine.insert()
    
    return WineResponse(
        id=str(user_wine.id),
        name=user_wine.name,
        producer=user_wine.producer,
        vintage=user_wine.vintage,
        wine_type=user_wine.wine_type,
        region=user_wine.region,
        country=user_wine.country,
        current_quantity=user_wine.current_quantity,
        image_url=user_wine.image_url,
        rating=user_wine.rating,
        appellation=user_wine.appellation,
        alcohol_content=user_wine.alcohol_content,
        tasting_notes=user_wine.tasting_notes
    )


@router.get("/search/barcode/{barcode}")
async def search_wine_by_barcode(
    barcode: str,
    current_user: User = Depends(get_current_user)
):
    """
    Search for wine by barcode in master database
    Returns wine info if found, 404 if not
    """
    wine = await Wine.find_one({
        "barcode": barcode,
        "user_id": None  # Search only master wines
    })
    
    if not wine:
        raise HTTPException(
            status_code=404,
            detail="Wine not found with this barcode. You can create it using AI."
        )
    
    return {
        "id": str(wine.id),
        "name": wine.name,
        "producer": wine.producer,
        "vintage": wine.vintage,
        "wine_type": wine.wine_type,
        "region": wine.region,
        "country": wine.country,
        "image_url": wine.image_url,
        "barcode": wine.barcode
    }


class ImageUploadResponse(BaseModel):
    """Response model for image upload"""
    url: str
    filename: str


@router.post("/{wine_id}/image", response_model=ImageUploadResponse)
async def upload_wine_image(
    wine_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload an image for a user wine"""
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Check file size (5MB limit)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 5MB)")
    
    # Verify wine belongs to user
    wine = await Wine.get(wine_id)
    if not wine or wine.user_id != str(current_user.id):
        raise HTTPException(status_code=404, detail="Wine not found")
    
    # Create uploads directory
    upload_dir = Path("/uploads/wines")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix if file.filename else '.jpg'
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Update wine with image URL
    wine.image_url = f"/uploads/wines/{unique_filename}"
    await wine.save()
    
    return ImageUploadResponse(
        url=wine.image_url,
        filename=unique_filename
    )
