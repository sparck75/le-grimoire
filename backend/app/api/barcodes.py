"""
Barcode API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel

from app.services.barcode_service import BarcodeService
from app.models.mongodb import BarcodeMapping
from app.core.security import get_current_user, optional_current_user
from app.models.user import User

router = APIRouter()
barcode_service = BarcodeService()


class BarcodeMappingCreate(BaseModel):
    """Request to create barcode mapping"""
    barcode: str
    lwin7: str
    lwin11: Optional[str] = None
    wine_name: str
    producer: Optional[str] = None
    vintage: Optional[int] = None
    source: str = "manual"
    confidence: float = 1.0


class BarcodeMappingResponse(BaseModel):
    """Barcode mapping response"""
    id: str
    barcode: str
    lwin7: str
    lwin11: Optional[str]
    wine_name: str
    producer: Optional[str]
    vintage: Optional[int]
    confidence: float
    source: str
    verified: bool
    scan_count: int
    
    class Config:
        from_attributes = True


@router.get("/lookup/{barcode}")
async def lookup_barcode(
    barcode: str,
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Look up a wine by barcode
    
    Returns the LWIN wine if a mapping exists
    """
    wine = await barcode_service.get_wine_by_barcode(barcode)
    
    if not wine:
        raise HTTPException(
            status_code=404,
            detail="No wine found for this barcode"
        )
    
    return {
        "id": str(wine.id),
        "lwin7": wine.lwin7,
        "lwin11": wine.lwin11,
        "name": wine.name,
        "producer": wine.producer,
        "vintage": wine.vintage,
        "country": wine.country,
        "region": wine.region,
        "wine_type": wine.wine_type,
        "barcode": barcode
    }


@router.post("/", response_model=BarcodeMappingResponse)
async def create_barcode_mapping(
    mapping_data: BarcodeMappingCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new barcode to LWIN mapping
    
    Requires authentication
    """
    mapping = await barcode_service.create_mapping(
        barcode=mapping_data.barcode,
        lwin7=mapping_data.lwin7,
        lwin11=mapping_data.lwin11,
        wine_name=mapping_data.wine_name,
        producer=mapping_data.producer,
        vintage=mapping_data.vintage,
        source=mapping_data.source,
        confidence=mapping_data.confidence,
        user_id=str(current_user.id)
    )
    
    return BarcodeMappingResponse(
        id=str(mapping.id),
        barcode=mapping.barcode,
        lwin7=mapping.lwin7,
        lwin11=mapping.lwin11,
        wine_name=mapping.wine_name,
        producer=mapping.producer,
        vintage=mapping.vintage,
        confidence=mapping.confidence,
        source=mapping.source,
        verified=mapping.verified,
        scan_count=mapping.scan_count
    )


@router.post("/{barcode}/verify")
async def verify_barcode_mapping(
    barcode: str,
    current_user: User = Depends(get_current_user)
):
    """
    Mark a barcode mapping as verified
    """
    mapping = await barcode_service.verify_mapping(
        barcode=barcode,
        user_id=str(current_user.id)
    )
    
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    return {"message": "Mapping verified", "barcode": barcode}


@router.get("/search", response_model=List[BarcodeMappingResponse])
async def search_barcode_mappings(
    barcode: Optional[str] = None,
    lwin7: Optional[str] = None,
    verified_only: bool = False,
    min_confidence: float = 0.0,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    Search barcode mappings
    """
    mappings = await barcode_service.search_mappings(
        barcode=barcode,
        lwin7=lwin7,
        verified_only=verified_only,
        min_confidence=min_confidence,
        limit=limit
    )
    
    return [
        BarcodeMappingResponse(
            id=str(m.id),
            barcode=m.barcode,
            lwin7=m.lwin7,
            lwin11=m.lwin11,
            wine_name=m.wine_name,
            producer=m.producer,
            vintage=m.vintage,
            confidence=m.confidence,
            source=m.source,
            verified=m.verified,
            scan_count=m.scan_count
        )
        for m in mappings
    ]


@router.get("/statistics")
async def get_barcode_statistics(
    current_user: User = Depends(get_current_user)
):
    """Get barcode mapping statistics"""
    stats = await barcode_service.get_statistics()
    return stats
