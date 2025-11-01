"""
Wine model for MongoDB using Beanie ODM.
"""
from beanie import Document
from pydantic import Field, BaseModel, validator
from typing import Optional, List, Literal
from datetime import datetime


class GrapeVariety(BaseModel):
    """Grape variety in wine composition"""
    name: str
    percentage: Optional[float] = None


class ProfessionalRating(BaseModel):
    """Professional wine rating"""
    source: str
    score: float
    year: int


class ImageSource(BaseModel):
    """Image from a specific data source"""
    url: str
    quality: Optional[str] = None  # low, medium, high
    source: str  # lwin, vivino, wine_searcher, manual
    updated: Optional[datetime] = None
    note: Optional[str] = None


class PriceInfo(BaseModel):
    """Price information from a source"""
    value: Optional[float] = None  # Single price or average
    min_price: Optional[float] = None  # For ranges
    max_price: Optional[float] = None
    currency: str = "CAD"
    source: str
    in_stock: Optional[bool] = None
    url: Optional[str] = None
    updated: Optional[datetime] = None


class RatingInfo(BaseModel):
    """Rating from a specific source"""
    score: float
    count: Optional[int] = None  # Number of ratings
    source: str
    updated: Optional[datetime] = None


class Wine(Document):
    """Wine document for MongoDB"""
    
    # Basic Information
    name: str
    producer: Optional[str] = None
    vintage: Optional[int] = None
    country: str = ""
    region: str = ""
    appellation: Optional[str] = None
    
    # Classification
    wine_type: Literal["red", "white", "rosé", "sparkling", "dessert", "fortified"] = "red"
    classification: Optional[str] = None
    
    # Composition
    grape_varieties: List[GrapeVariety] = Field(default_factory=list)
    alcohol_content: Optional[float] = None
    
    # Characteristics
    body: Optional[Literal["light", "medium", "full"]] = None
    sweetness: Optional[Literal["dry", "off-dry", "sweet", "very-sweet"]] = None
    acidity: Optional[Literal["low", "medium", "high"]] = None
    tannins: Optional[Literal["low", "medium", "high"]] = None
    
    # Tasting
    color: str = ""
    nose: List[str] = Field(default_factory=list)
    palate: List[str] = Field(default_factory=list)
    tasting_notes: str = ""
    
    # Pairing
    food_pairings: List[str] = Field(default_factory=list)
    suggested_recipe_ids: List[str] = Field(default_factory=list)
    
    # Cellar Information
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    purchase_location: Optional[str] = None
    current_quantity: int = 0
    cellar_location: Optional[str] = None
    
    # Drinking Window
    drink_from: Optional[int] = None
    drink_until: Optional[int] = None
    peak_drinking: Optional[str] = None
    
    # Ratings
    rating: Optional[float] = None
    professional_ratings: List[ProfessionalRating] = Field(default_factory=list)
    
    # Media
    image_url: Optional[str] = None  # Legacy field
    qr_code: Optional[str] = None
    barcode: Optional[str] = None
    
    # Label Images (for AI extraction and detailed view)
    front_label_image: Optional[str] = None  # Front label for OCR/AI
    back_label_image: Optional[str] = None   # Back label for OCR/AI
    bottle_image: Optional[str] = None       # Full bottle for catalog
    
    # LWIN (Liv-ex Wine Identification Number)
    lwin7: Optional[str] = None  # 7-digit code for wine label/producer
    lwin11: Optional[str] = None  # 11-digit code includes vintage
    lwin18: Optional[str] = None  # 18-digit code includes bottle size/pack
    
    # Extended LWIN Data (from LWIN database)
    lwin_status: Optional[str] = None  # Live, Combined, Deleted
    lwin_display_name: Optional[str] = None  # Official display name
    producer_title: Optional[str] = None  # Title prefix (Château, etc)
    sub_region: Optional[str] = None  # Sub-region (e.g., Pauillac)
    site: Optional[str] = None  # Specific site/vineyard
    parcel: Optional[str] = None  # Specific parcel within vineyard
    sub_type: Optional[str] = None  # Still, Sparkling, Fortified
    designation: Optional[str] = None  # AOP, IGP, DOC, DOCG
    vintage_config: Optional[str] = None  # sequential, non-vintage
    lwin_first_vintage: Optional[str] = None  # First vintage year
    lwin_final_vintage: Optional[str] = None  # Final vintage year
    lwin_date_added: Optional[datetime] = None  # Added to LWIN DB
    lwin_date_updated: Optional[datetime] = None  # Updated in LWIN DB
    lwin_reference: Optional[str] = None  # Reference to merged entries
    
    # Multi-Source Images
    image_sources: dict = Field(default_factory=dict)  # source -> ImageSource
    
    # Multi-Source Prices
    price_data: dict = Field(default_factory=dict)  # source -> PriceInfo
    
    # Multi-Source Ratings
    ratings: dict = Field(default_factory=dict)  # source -> RatingInfo
    
    # Tasting Notes by Source
    tasting_notes_sources: dict = Field(default_factory=dict)  # source -> str
    
    # External IDs
    vivino_id: Optional[str] = None
    wine_searcher_id: Optional[str] = None
    external_ids: dict = Field(default_factory=dict)  # source -> external_id
    
    # Data Provenance
    data_source: str = "manual"  # Primary source: manual, lwin, vivino, etc.
    enriched_by: List[str] = Field(default_factory=list)  # Sources used
    external_id: Optional[str] = None  # Legacy field
    
    # Sync Configuration (migrated from single values to multi-source dicts)
    last_synced: dict = Field(default_factory=dict)  # source -> datetime
    sync_enabled: dict = Field(default_factory=dict)  # source -> bool
    
    # Manual Overrides (admin edits)
    manual_overrides: dict = Field(default_factory=dict)  # field -> value
    
    # Legacy external data
    external_data: dict = Field(default_factory=dict)
    
    @validator('last_synced', pre=True)
    def migrate_last_synced(cls, v):
        """Migrate old datetime field to dict format"""
        if v is None:
            return {}
        if isinstance(v, datetime):
            # Old format: single datetime -> New format: dict with 'default' key
            return {'default': v}
        if isinstance(v, dict):
            return v
        return {}
    
    @validator('sync_enabled', pre=True)
    def migrate_sync_enabled(cls, v):
        """Migrate old bool field to dict format"""
        if v is None:
            return {}
        if isinstance(v, bool):
            # Old format: single bool -> New format: dict with 'default' key
            return {'default': v}
        if isinstance(v, dict):
            return v
        return {}
    
    # Management
    is_public: bool = False
    user_id: Optional[str] = None
    master_wine_id: Optional[str] = None  # Link to master wine (for user wines)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "wines"
        indexes = [
            "name",
            "wine_type",
            "region",
            "country",
            "vintage",
            "user_id",
            "lwin7",
            "lwin11",
            "lwin18"
        ]
    
    @validator('vintage')
    def validate_vintage(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1800 or v > current_year + 1:
                raise ValueError(f'Vintage must be between 1800 and {current_year + 1}')
        return v
    
    @validator('alcohol_content')
    def validate_alcohol(cls, v):
        if v is not None:
            if v < 0 or v > 100:
                raise ValueError('Alcohol content must be between 0 and 100')
        return v
    
    @validator('rating')
    def validate_rating(cls, v):
        if v is not None:
            if v < 0 or v > 5:
                raise ValueError('Rating must be between 0 and 5')
        return v
    
    @validator('current_quantity')
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('Quantity cannot be negative')
        return v
    
    @validator('lwin7')
    def validate_lwin7(cls, v):
        if v is not None:
            if not v.isdigit() or len(v) != 7:
                raise ValueError('LWIN7 must be exactly 7 digits')
        return v
    
    @validator('lwin11')
    def validate_lwin11(cls, v):
        if v is not None:
            if not v.isdigit() or len(v) != 11:
                raise ValueError('LWIN11 must be exactly 11 digits')
        return v
    
    @validator('lwin18')
    def validate_lwin18(cls, v):
        if v is not None:
            if not v.isdigit() or len(v) != 18:
                raise ValueError('LWIN18 must be exactly 18 digits')
        return v
    
    def __repr__(self) -> str:
        return f"Wine(id={self.id}, name='{self.name}', vintage={self.vintage})"
    
    def __str__(self) -> str:
        vintage_str = f" {self.vintage}" if self.vintage else ""
        return f"{self.name}{vintage_str}"
