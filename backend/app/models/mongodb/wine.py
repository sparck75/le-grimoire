"""
Wine model for MongoDB using Beanie ODM.
Manages wine database with detailed information about wines.
"""

from datetime import datetime, UTC
from typing import Dict, List, Optional
from beanie import Document
from pydantic import Field
from enum import Enum


class WineType(str, Enum):
    """Wine type classification."""
    RED = "red"
    WHITE = "white"
    ROSE = "rosé"
    SPARKLING = "sparkling"
    DESSERT = "dessert"
    FORTIFIED = "fortified"


class WineRegion(str, Enum):
    """Major wine regions."""
    BORDEAUX = "bordeaux"
    BOURGOGNE = "bourgogne"
    CHAMPAGNE = "champagne"
    RHONE = "rhône"
    LOIRE = "loire"
    ALSACE = "alsace"
    LANGUEDOC = "languedoc-roussillon"
    PROVENCE = "provence"
    SOUTH_WEST = "sud-ouest"
    BEAUJOLAIS = "beaujolais"
    JURA = "jura"
    SAVOIE = "savoie"
    CORSICA = "corse"
    ITALY = "italy"
    SPAIN = "spain"
    PORTUGAL = "portugal"
    USA = "usa"
    AUSTRALIA = "australia"
    NEW_ZEALAND = "new-zealand"
    CHILE = "chile"
    ARGENTINA = "argentina"
    SOUTH_AFRICA = "south-africa"
    OTHER = "other"


class Wine(Document):
    """
    Wine document model for MongoDB.
    
    Stores detailed wine information including characteristics,
    pairings, and metadata for recipe integration.
    """
    
    # Basic information
    name: str
    winery: str = ""
    vintage: Optional[int] = None
    wine_type: WineType
    
    # Classification
    appellation: str = ""  # AOC, DOC, etc.
    region: Optional[WineRegion] = None
    subregion: str = ""
    country: str = ""
    
    # Characteristics
    grape_varieties: List[str] = Field(default_factory=list)
    alcohol_content: Optional[float] = None  # Percentage
    color: str = ""  # Visual description
    nose: str = ""  # Aroma description
    palate: str = ""  # Taste description
    
    # Technical details
    residual_sugar: Optional[float] = None  # g/L
    acidity: Optional[float] = None  # g/L
    tannins: Optional[str] = None  # Low, Medium, High
    body: Optional[str] = None  # Light, Medium, Full
    
    # Pairing and service
    food_pairings: List[str] = Field(default_factory=list)
    serving_temperature: Optional[str] = None  # e.g., "12-14°C"
    decanting_time: Optional[int] = None  # Minutes
    aging_potential: Optional[str] = None  # e.g., "5-10 years"
    
    # Additional information
    description: str = ""
    tasting_notes: str = ""
    awards: List[str] = Field(default_factory=list)
    
    # Pricing and availability
    price_range: Optional[str] = None  # e.g., "20-30€"
    saq_code: Optional[str] = None  # SAQ product code (Quebec)
    lcbo_code: Optional[str] = None  # LCBO product code (Ontario)
    barcode: Optional[str] = None
    
    # Multilingual names (for international wines)
    names: Dict[str, str] = Field(default_factory=dict)
    
    # External identifiers
    wine_searcher_id: Optional[str] = None
    vivino_id: Optional[str] = None
    wine_spectator_id: Optional[str] = None
    
    # User-added or from official database
    custom: bool = False
    
    # Recipe associations (to be populated via queries)
    # recipes: List[str] = Field(default_factory=list)  # Recipe IDs
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: Optional[str] = None  # User ID
    
    class Settings:
        name = "wines"
        use_state_management = True
        use_revision = False
        # Indexes will be created via script
        indexes = [
            "name",
            "winery",
            "wine_type",
            "region",
            "country",
            "saq_code",
            "lcbo_code",
            "custom",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Château Margaux",
                "winery": "Château Margaux",
                "vintage": 2015,
                "wine_type": "red",
                "appellation": "Margaux AOC",
                "region": "bordeaux",
                "subregion": "Médoc",
                "country": "France",
                "grape_varieties": ["Cabernet Sauvignon", "Merlot", "Cabernet Franc"],
                "alcohol_content": 13.5,
                "food_pairings": ["Filet mignon", "Agneau", "Fromages affinés"],
                "serving_temperature": "16-18°C",
                "aging_potential": "20-30 years",
                "price_range": "500-800€",
                "custom": False
            }
        }
    
    def get_name(self, language: str = "fr") -> str:
        """
        Get wine name in specified language.
        Falls back to original name if translation not available.
        """
        return self.names.get(language, self.name)
    
    @classmethod
    async def search(
        cls,
        query: str,
        wine_type: Optional[WineType] = None,
        region: Optional[WineRegion] = None,
        limit: int = 50,
        skip: int = 0,
        custom_only: bool = False
    ) -> List["Wine"]:
        """
        Search wines by name, winery, or characteristics.
        
        Args:
            query: Search query string
            wine_type: Filter by wine type
            region: Filter by region
            limit: Maximum number of results
            skip: Number of results to skip (for pagination)
            custom_only: Only return custom wines
        
        Returns:
            List of matching wines
        """
        filters = {
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"winery": {"$regex": query, "$options": "i"}},
                {"appellation": {"$regex": query, "$options": "i"}},
            ]
        }
        
        if wine_type:
            filters["wine_type"] = wine_type
        
        if region:
            filters["region"] = region
        
        if custom_only:
            filters["custom"] = True
        
        return await cls.find(filters).skip(skip).limit(limit).to_list()
    
    @classmethod
    async def get_by_saq_code(cls, saq_code: str) -> Optional["Wine"]:
        """Get wine by SAQ product code."""
        return await cls.find_one({"saq_code": saq_code})
    
    @classmethod
    async def get_by_lcbo_code(cls, lcbo_code: str) -> Optional["Wine"]:
        """Get wine by LCBO product code."""
        return await cls.find_one({"lcbo_code": lcbo_code})
    
    @classmethod
    async def get_by_type(cls, wine_type: WineType, limit: int = 50) -> List["Wine"]:
        """Get wines by type."""
        return await cls.find({"wine_type": wine_type}).limit(limit).to_list()
    
    @classmethod
    async def get_by_region(cls, region: WineRegion, limit: int = 50) -> List["Wine"]:
        """Get wines by region."""
        return await cls.find({"region": region}).limit(limit).to_list()
