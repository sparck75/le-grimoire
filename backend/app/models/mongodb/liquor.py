"""
Liquor model for MongoDB using Beanie ODM.
"""
from beanie import Document
from pydantic import Field, BaseModel, validator
from typing import Optional, List, Literal
from datetime import datetime


class ProfessionalRating(BaseModel):
    """Professional liquor rating"""
    source: str
    score: float
    year: int


class Liquor(Document):
    """Liquor/spirit document for MongoDB"""
    
    # Basic Information
    name: str
    brand: Optional[str] = None
    distillery: Optional[str] = None
    country: str = ""
    region: str = ""
    
    # Classification
    spirit_type: Literal["whiskey", "vodka", "rum", "gin", "tequila", "brandy", "cognac", "liqueur", "other"] = "other"
    subtype: Optional[str] = None  # bourbon, scotch, etc.
    
    # Characteristics
    alcohol_content: Optional[float] = None
    age_statement: Optional[str] = None  # "12 years", "XO", etc.
    cask_type: Optional[str] = None
    finish: Optional[str] = None
    
    # Tasting
    color: str = ""
    nose: List[str] = Field(default_factory=list)
    palate: List[str] = Field(default_factory=list)
    finish_notes: str = ""
    tasting_notes: str = ""
    
    # Usage
    cocktail_uses: List[str] = Field(default_factory=list)
    food_pairings: List[str] = Field(default_factory=list)
    serving_suggestion: str = ""
    
    # Cellar Information
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    purchase_location: Optional[str] = None
    current_quantity: int = 100  # percentage remaining (0-100)
    cellar_location: Optional[str] = None
    
    # Ratings
    rating: Optional[float] = None
    professional_ratings: List[ProfessionalRating] = Field(default_factory=list)
    
    # Media
    image_url: Optional[str] = None
    qr_code: Optional[str] = None
    barcode: Optional[str] = None
    
    # External Data
    external_id: Optional[str] = None
    external_data: dict = Field(default_factory=dict)
    data_source: str = "manual"
    last_synced: Optional[datetime] = None
    sync_enabled: bool = False
    
    # Management
    is_public: bool = False
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "liquors"
        indexes = [
            "name",
            "spirit_type",
            "brand",
            "user_id"
        ]
    
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
        if v < 0 or v > 100:
            raise ValueError('Quantity must be between 0 and 100 (percentage)')
        return v
    
    def __repr__(self) -> str:
        return f"Liquor(id={self.id}, name='{self.name}', type={self.spirit_type})"
    
    def __str__(self) -> str:
        return self.name
