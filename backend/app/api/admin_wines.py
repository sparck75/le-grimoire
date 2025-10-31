"""
Admin API for managing wine database (metadata/master wines list)
Separate from user's personal cellier inventory
"""
from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
from pathlib import Path
from app.models.mongodb import Wine
from app.models.mongodb.wine import GrapeVariety
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.core.config import settings

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
    classification: Optional[str] = None
    color: str = ""
    alcohol_content: Optional[float] = None
    grape_varieties: List[GrapeVariety] = []
    tasting_notes: str = ""
    food_pairings: List[str] = []
    is_public: bool
    data_source: str
    barcode: Optional[str] = None
    
    # Images
    image_url: Optional[str] = None
    front_label_image: Optional[str] = None
    back_label_image: Optional[str] = None
    bottle_image: Optional[str] = None
    
    # LWIN codes
    lwin7: Optional[str] = None
    lwin11: Optional[str] = None
    lwin18: Optional[str] = None
    
    # Extended LWIN data
    lwin_status: Optional[str] = None
    lwin_display_name: Optional[str] = None
    producer_title: Optional[str] = None
    sub_region: Optional[str] = None
    site: Optional[str] = None
    parcel: Optional[str] = None
    sub_type: Optional[str] = None
    designation: Optional[str] = None
    vintage_config: Optional[str] = None
    lwin_first_vintage: Optional[str] = None
    lwin_final_vintage: Optional[str] = None
    lwin_date_added: Optional[datetime] = None
    lwin_date_updated: Optional[datetime] = None
    lwin_reference: Optional[str] = None
    
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
    # Label images for AI extraction
    front_label_image: Optional[str] = None
    back_label_image: Optional[str] = None
    bottle_image: Optional[str] = None
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
    # Label images for AI extraction
    front_label_image: Optional[str] = None
    back_label_image: Optional[str] = None
    bottle_image: Optional[str] = None


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
            classification=wine.classification,
            color=wine.color,
            alcohol_content=wine.alcohol_content,
            grape_varieties=wine.grape_varieties,
            tasting_notes=wine.tasting_notes,
            food_pairings=wine.food_pairings,
            is_public=wine.is_public,
            data_source=wine.data_source,
            barcode=wine.barcode,
            image_url=wine.image_url,
            front_label_image=wine.front_label_image,
            back_label_image=wine.back_label_image,
            bottle_image=wine.bottle_image,
            lwin7=wine.lwin7,
            lwin11=wine.lwin11,
            lwin18=wine.lwin18,
            lwin_status=wine.lwin_status,
            lwin_display_name=wine.lwin_display_name,
            producer_title=wine.producer_title,
            sub_region=wine.sub_region,
            site=wine.site,
            parcel=wine.parcel,
            sub_type=wine.sub_type,
            designation=wine.designation,
            vintage_config=wine.vintage_config,
            lwin_first_vintage=wine.lwin_first_vintage,
            lwin_final_vintage=wine.lwin_final_vintage,
            lwin_date_added=wine.lwin_date_added,
            lwin_date_updated=wine.lwin_date_updated,
            lwin_reference=wine.lwin_reference,
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
        image_url=wine.image_url,
        front_label_image=wine.front_label_image,
        back_label_image=wine.back_label_image,
        bottle_image=wine.bottle_image,
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
        image_url=wine.image_url,
        front_label_image=wine.front_label_image,
        back_label_image=wine.back_label_image,
        bottle_image=wine.bottle_image,
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
        image_url=wine.image_url,
        front_label_image=wine.front_label_image,
        back_label_image=wine.back_label_image,
        bottle_image=wine.bottle_image,
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
        image_url=wine.image_url,
        front_label_image=wine.front_label_image,
        back_label_image=wine.back_label_image,
        bottle_image=wine.bottle_image,
        created_at=wine.created_at,
        updated_at=wine.updated_at
    )


@router.get("/stats/summary")
async def get_master_wine_stats(
    current_user: User = Depends(require_admin)
):
    """Get master wine database statistics"""
    total = await Wine.find({"user_id": None}).count()
    
    # Count with barcodes
    with_barcode = await Wine.find({
        "user_id": None,
        "barcode": {"$exists": True, "$ne": ""}
    }).count()
    
    # TODO: Fix aggregation - Beanie's aggregate().to_list() has async issues
    # For now, return basic stats without type breakdown
    return {
        "total": total,
        "by_type": {},  # Temporarily disabled due to Beanie async issue
        "with_barcode": with_barcode
    }


class ImageUploadResponse(BaseModel):
    """Image upload response"""
    url: str
    filename: str


@router.post("/wines/{wine_id}/image", response_model=ImageUploadResponse)
async def upload_wine_image(
    wine_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin)
):
    """
    Upload image for a wine bottle
    """
    # Check if wine exists
    wine = await Wine.get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    # Validate file size (5MB max)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Image must not exceed 5 MB"
        )
    
    # Generate unique filename
    file_extension = Path(file.filename or "image.jpg").suffix
    unique_filename = f"wine_{wine_id}_{uuid.uuid4()}{file_extension}"
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR) / "wines"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / unique_filename
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Update wine with image URL
    image_url = f"/uploads/wines/{unique_filename}"
    wine.image_url = image_url
    wine.updated_at = datetime.utcnow()
    await wine.save()
    
    return ImageUploadResponse(
        url=image_url,
        filename=unique_filename
    )


class MultiImageUploadResponse(BaseModel):
    """Multi-image upload response"""
    front_label_image: Optional[str] = None
    back_label_image: Optional[str] = None
    bottle_image: Optional[str] = None
    front_label_thumbnail: Optional[str] = None
    back_label_thumbnail: Optional[str] = None
    bottle_thumbnail: Optional[str] = None


@router.post(
    "/wines/{wine_id}/images",
    response_model=MultiImageUploadResponse
)
async def upload_wine_images(
    wine_id: str,
    front_label: Optional[UploadFile] = File(None),
    back_label: Optional[UploadFile] = File(None),
    bottle: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_admin)
):
    """
    Upload multiple images for a wine (front label, back label, bottle).
    
    Accepts multipart/form-data with optional files:
    - front_label: Front label image for OCR/AI extraction
    - back_label: Back label image for OCR/AI extraction
    - bottle: Full bottle image for catalog display
    
    All images are validated, optimized, and stored in appropriate directories.
    Thumbnails are automatically generated for each image.
    
    Args:
        wine_id: Wine document ID
        front_label: Front label image file (optional)
        back_label: Back label image file (optional)
        bottle: Bottle image file (optional)
        current_user: Authenticated admin user
        
    Returns:
        URLs for uploaded images and their thumbnails
        
    Raises:
        404: Wine not found
        400: Invalid file format or size
        500: Storage error
    """
    from app.services.image_storage import image_storage_service
    
    # Check if wine exists
    wine = await Wine.get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    # Track uploaded images
    response = MultiImageUploadResponse()
    
    # Upload front label
    if front_label and front_label.filename:
        image_url, thumb_url = await image_storage_service.save_image(
            front_label,
            wine_id,
            "front_label"
        )
        wine.front_label_image = image_url
        response.front_label_image = image_url
        response.front_label_thumbnail = thumb_url
    
    # Upload back label
    if back_label and back_label.filename:
        image_url, thumb_url = await image_storage_service.save_image(
            back_label,
            wine_id,
            "back_label"
        )
        wine.back_label_image = image_url
        response.back_label_image = image_url
        response.back_label_thumbnail = thumb_url
    
    # Upload bottle image
    if bottle and bottle.filename:
        image_url, thumb_url = await image_storage_service.save_image(
            bottle,
            wine_id,
            "bottle"
        )
        wine.bottle_image = image_url
        response.bottle_image = image_url
        response.bottle_thumbnail = thumb_url
    
    # Save updated wine
    wine.updated_at = datetime.utcnow()
    await wine.save()
    
    return response
