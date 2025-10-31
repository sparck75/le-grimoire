"""
LWIN API routes - Liv-ex Wine Identification Number integration
"""
from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from pathlib import Path

from app.models.mongodb import Wine
from app.services.lwin_service import LWINService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()
lwin_service = LWINService()


class LWINSearchResponse(BaseModel):
    """LWIN search response"""
    id: str
    lwin7: Optional[str]
    lwin11: Optional[str]
    lwin18: Optional[str]
    name: str
    producer: Optional[str]
    vintage: Optional[int]
    wine_type: str
    country: str
    region: str
    appellation: Optional[str]
    
    class Config:
        from_attributes = True


class LWINDetailResponse(BaseModel):
    """Complete LWIN wine details"""
    id: str
    lwin7: Optional[str]
    lwin11: Optional[str]
    lwin18: Optional[str]
    name: str
    producer: Optional[str]
    vintage: Optional[int]
    wine_type: str
    country: str
    region: str
    appellation: Optional[str]
    classification: Optional[str]
    color: Optional[str]
    alcohol_content: Optional[float]
    grape_varieties: List[Dict[str, Any]] = []
    tasting_notes: Optional[str]
    
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
    lwin_date_added: Optional[str] = None
    lwin_date_updated: Optional[str] = None
    lwin_reference: Optional[str] = None
    
    class Config:
        from_attributes = True


class LWINImportRequest(BaseModel):
    """Request to import LWIN data"""
    url: Optional[str] = None
    file_path: Optional[str] = None


class LWINImportResponse(BaseModel):
    """Response from LWIN import"""
    status: str
    message: str
    statistics: Dict[str, int]


@router.get("/search", response_model=List[LWINSearchResponse])
async def search_lwin_wines(
    search: Optional[str] = Query(None, description="Search by name or producer"),
    country: Optional[str] = None,
    region: Optional[str] = None,
    wine_type: Optional[str] = None,
    vintage: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Search LWIN master wine database
    
    This searches the imported LWIN wines (master wines with data_source='lwin')
    """
    query = {
        'data_source': 'lwin',
        'user_id': None  # Master wines only
    }
    
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'producer': {'$regex': search, '$options': 'i'}}
        ]
    
    if country:
        query['country'] = country
    if region:
        query['region'] = region
    if wine_type:
        query['wine_type'] = wine_type
    if vintage:
        query['vintage'] = vintage
    
    wines = await Wine.find(query).skip(skip).limit(limit).to_list()
    
    return [
        LWINSearchResponse(
            id=str(wine.id),
            lwin7=wine.lwin7,
            lwin11=wine.lwin11,
            lwin18=wine.lwin18,
            name=wine.name,
            producer=wine.producer,
            vintage=wine.vintage,
            wine_type=wine.wine_type,
            country=wine.country,
            region=wine.region,
            appellation=wine.appellation
        )
        for wine in wines
    ]


@router.get("/{wine_id}", response_model=LWINDetailResponse)
async def get_lwin_wine_details(
    wine_id: str
):
    """
    Get complete LWIN wine details by MongoDB ID
    
    Returns full wine information including grape varieties,
    tasting notes, and all LWIN codes.
    """
    wine = await Wine.get(wine_id)
    
    if not wine:
        raise HTTPException(
            status_code=404,
            detail=f"Wine not found with ID {wine_id}"
        )
    
    # Ensure this is a LWIN master wine
    if wine.data_source != 'lwin' or wine.user_id is not None:
        raise HTTPException(
            status_code=404,
            detail="Not a LWIN master wine"
        )
    
    return LWINDetailResponse(
        id=str(wine.id),
        lwin7=wine.lwin7,
        lwin11=wine.lwin11,
        lwin18=wine.lwin18,
        name=wine.name,
        producer=wine.producer,
        vintage=wine.vintage,
        wine_type=wine.wine_type,
        country=wine.country,
        region=wine.region,
        appellation=wine.appellation,
        classification=wine.classification,
        color=wine.color,
        alcohol_content=wine.alcohol_content,
        grape_varieties=[vars(gv) for gv in (wine.grape_varieties or [])],
        tasting_notes=wine.tasting_notes,
        # Extended LWIN fields
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
        lwin_date_added=wine.lwin_date_added.isoformat() if wine.lwin_date_added else None,
        lwin_date_updated=wine.lwin_date_updated.isoformat() if wine.lwin_date_updated else None,
        lwin_reference=wine.lwin_reference
    )


@router.get("/code/{lwin_code}", response_model=LWINSearchResponse)
async def get_wine_by_lwin(
    lwin_code: str
):
    """
    Get wine by LWIN code (LWIN7, LWIN11, or LWIN18)
    
    The code length determines which field to search:
    - 7 digits: LWIN7 (wine label)
    - 11 digits: LWIN11 (wine + vintage)
    - 18 digits: LWIN18 (wine + vintage + bottle size)
    """
    wine = await lwin_service.search_by_lwin(lwin_code)
    
    if not wine:
        raise HTTPException(
            status_code=404,
            detail=f"Wine not found with LWIN code {lwin_code}"
        )
    
    return LWINSearchResponse(
        id=str(wine.id),
        lwin7=wine.lwin7,
        lwin11=wine.lwin11,
        lwin18=wine.lwin18,
        name=wine.name,
        producer=wine.producer,
        vintage=wine.vintage,
        wine_type=wine.wine_type,
        country=wine.country,
        region=wine.region,
        appellation=wine.appellation
    )


@router.post("/enrich/{wine_id}")
async def enrich_wine(
    wine_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Enrich a user's wine with data from LWIN database
    
    This attempts to match the wine to the LWIN database and fill in
    missing information like LWIN codes, region, appellation, etc.
    """
    wine = await Wine.get(wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    
    # Check ownership
    if wine.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to modify this wine")
    
    enriched_wine = await lwin_service.enrich_wine_from_lwin(wine_id)
    
    if not enriched_wine:
        raise HTTPException(
            status_code=404,
            detail="Could not find matching wine in LWIN database"
        )
    
    return {
        "message": "Wine enriched successfully",
        "wine_id": str(enriched_wine.id),
        "lwin7": enriched_wine.lwin7,
        "lwin11": enriched_wine.lwin11,
        "lwin18": enriched_wine.lwin18
    }


@router.get("/statistics")
async def get_lwin_statistics():
    """
    Get statistics about LWIN wines in the database
    """
    stats = await lwin_service.get_lwin_statistics()
    return stats


@router.post("/import", response_model=LWINImportResponse)
async def import_lwin_database(
    request: LWINImportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Import LWIN database from URL or file
    
    Admin only endpoint - requires authentication
    
    Either provide a URL to download the CSV or a file_path to an already
    downloaded file.
    """
    # TODO: Add admin check here
    # For now, just require authentication
    
    try:
        if request.url:
            # Download from URL
            csv_path = await lwin_service.download_lwin_database(request.url)
        elif request.file_path:
            # Use existing file - validate path to prevent path traversal
            csv_path = Path(request.file_path)
            
            # Security: Only allow files within the LWIN data directory
            # This prevents path traversal attacks (e.g., ../../etc/passwd)
            lwin_data_dir = lwin_service.lwin_data_path.resolve()
            try:
                # Resolve to absolute path to prevent symlink attacks
                resolved_path = csv_path.resolve()
                # Verify path is within allowed directory - raises ValueError if not
                # This is the security check that prevents directory traversal
                resolved_path.relative_to(lwin_data_dir)
            except (ValueError, OSError):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file path. File must be in LWIN data directory."
                )
            
            # After validation, safe to check existence
            if not resolved_path.exists():
                raise HTTPException(status_code=400, detail="File not found")
            
            # Use validated path for parsing
            csv_path = resolved_path
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'url' or 'file_path' must be provided"
            )
        
        # Parse CSV
        wines_data = lwin_service.parse_lwin_csv(csv_path)
        
        if not wines_data:
            raise HTTPException(
                status_code=400,
                detail="No valid wine data found in CSV"
            )
        
        # Import to database
        stats = await lwin_service.import_wines_to_db(wines_data)
        
        return LWINImportResponse(
            status="success",
            message=f"Successfully imported LWIN database",
            statistics=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error importing LWIN database: {str(e)}"
        )


@router.post("/import/upload", response_model=LWINImportResponse)
async def upload_and_import_lwin(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and import LWIN database CSV file
    
    Admin only endpoint - requires authentication
    """
    # Validate file type
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Save uploaded file
        upload_path = lwin_service.lwin_data_path / file.filename
        contents = await file.read()
        upload_path.write_bytes(contents)
        
        # Parse and import
        wines_data = lwin_service.parse_lwin_csv(upload_path)
        
        if not wines_data:
            raise HTTPException(
                status_code=400,
                detail="No valid wine data found in CSV"
            )
        
        stats = await lwin_service.import_wines_to_db(wines_data)
        
        return LWINImportResponse(
            status="success",
            message=f"Successfully imported {file.filename}",
            statistics=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error importing file: {str(e)}"
        )
