"""
Liquor model for MongoDB using Beanie ODM.
Manages liquor/spirits database with detailed information.
"""

from datetime import datetime, UTC
from typing import Dict, List, Optional
from beanie import Document
from pydantic import Field
from enum import Enum


class LiquorType(str, Enum):
    """Liquor/spirits type classification."""
    VODKA = "vodka"
    GIN = "gin"
    RUM = "rum"
    WHISKY = "whisky"
    BOURBON = "bourbon"
    SCOTCH = "scotch"
    TEQUILA = "tequila"
    MEZCAL = "mezcal"
    BRANDY = "brandy"
    COGNAC = "cognac"
    ARMAGNAC = "armagnac"
    LIQUEUR = "liqueur"
    APERITIF = "apéritif"
    DIGESTIF = "digestif"
    VERMOUTH = "vermouth"
    SAKE = "sake"
    ABSINTHE = "absinthe"
    CACHAÇA = "cachaça"
    GRAPPA = "grappa"
    SCHNAPPS = "schnapps"
    AQUAVIT = "aquavit"
    BITTERS = "bitters"
    OTHER = "other"


class LiquorOrigin(str, Enum):
    """Country/region of origin."""
    FRANCE = "france"
    SCOTLAND = "scotland"
    IRELAND = "ireland"
    USA = "usa"
    CANADA = "canada"
    MEXICO = "mexico"
    CARIBBEAN = "caribbean"
    RUSSIA = "russia"
    SWEDEN = "sweden"
    JAPAN = "japan"
    ITALY = "italy"
    SPAIN = "spain"
    PORTUGAL = "portugal"
    GERMANY = "germany"
    NETHERLANDS = "netherlands"
    CZECH_REPUBLIC = "czech-republic"
    BRAZIL = "brazil"
    OTHER = "other"


class Liquor(Document):
    """
    Liquor/spirits document model for MongoDB.
    
    Stores detailed liquor information including characteristics,
    cocktail pairings, and metadata for recipe integration.
    """
    
    # Basic information
    name: str
    brand: str = ""
    liquor_type: LiquorType
    
    # Classification
    origin: Optional[LiquorOrigin] = None
    region: str = ""  # Specific region within country
    distillery: str = ""
    
    # Characteristics
    alcohol_content: Optional[float] = None  # ABV percentage
    age_statement: Optional[str] = None  # e.g., "12 years", "XO"
    color: str = ""
    aroma: str = ""
    taste: str = ""
    finish: str = ""
    
    # Production details
    base_ingredient: str = ""  # e.g., "grain", "grape", "agave", "sugarcane"
    distillation_type: Optional[str] = None  # e.g., "pot still", "column still"
    cask_type: Optional[str] = None  # e.g., "oak", "sherry cask"
    filtration: Optional[str] = None  # e.g., "charcoal filtered", "unfiltered"
    
    # Flavor profile
    flavor_notes: List[str] = Field(default_factory=list)
    sweetness_level: Optional[str] = None  # Dry, Semi-sweet, Sweet
    
    # Usage and pairings
    cocktail_suggestions: List[str] = Field(default_factory=list)
    serving_suggestions: str = ""  # Neat, on rocks, mixed, etc.
    food_pairings: List[str] = Field(default_factory=list)
    
    # Additional information
    description: str = ""
    tasting_notes: str = ""
    awards: List[str] = Field(default_factory=list)
    
    # Pricing and availability
    price_range: Optional[str] = None  # e.g., "30-50€"
    saq_code: Optional[str] = None  # SAQ product code (Quebec)
    lcbo_code: Optional[str] = None  # LCBO product code (Ontario)
    barcode: Optional[str] = None
    
    # Multilingual names
    names: Dict[str, str] = Field(default_factory=dict)
    
    # External identifiers
    distiller_id: Optional[str] = None
    proof: Optional[float] = None  # US proof (ABV * 2)
    
    # Certifications
    organic: bool = False
    kosher: bool = False
    gluten_free: bool = False
    
    # User-added or from official database
    custom: bool = False
    
    # Recipe associations (to be populated via queries)
    # recipes: List[str] = Field(default_factory=list)  # Recipe IDs
    # cocktails: List[str] = Field(default_factory=list)  # Cocktail IDs
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: Optional[str] = None  # User ID
    
    class Settings:
        name = "liquors"
        use_state_management = True
        use_revision = False
        # Indexes will be created via script
        indexes = [
            "name",
            "brand",
            "liquor_type",
            "origin",
            "distillery",
            "saq_code",
            "lcbo_code",
            "custom",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Hennessy X.O",
                "brand": "Hennessy",
                "liquor_type": "cognac",
                "origin": "france",
                "region": "Cognac",
                "distillery": "Hennessy",
                "alcohol_content": 40.0,
                "age_statement": "X.O (Extra Old)",
                "base_ingredient": "grape",
                "distillation_type": "pot still",
                "cask_type": "oak",
                "flavor_notes": ["vanilla", "oak", "dried fruit", "spice"],
                "serving_suggestions": "Neat or on rocks",
                "cocktail_suggestions": ["French Connection", "Sidecar"],
                "price_range": "150-200€",
                "custom": False
            }
        }
    
    def get_name(self, language: str = "fr") -> str:
        """
        Get liquor name in specified language.
        Falls back to original name if translation not available.
        """
        return self.names.get(language, self.name)
    
    @classmethod
    async def search(
        cls,
        query: str,
        liquor_type: Optional[LiquorType] = None,
        origin: Optional[LiquorOrigin] = None,
        limit: int = 50,
        skip: int = 0,
        custom_only: bool = False
    ) -> List["Liquor"]:
        """
        Search liquors by name, brand, or characteristics.
        
        Args:
            query: Search query string
            liquor_type: Filter by liquor type
            origin: Filter by origin
            limit: Maximum number of results
            skip: Number of results to skip (for pagination)
            custom_only: Only return custom liquors
        
        Returns:
            List of matching liquors
        """
        filters = {
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"brand": {"$regex": query, "$options": "i"}},
                {"distillery": {"$regex": query, "$options": "i"}},
            ]
        }
        
        if liquor_type:
            filters["liquor_type"] = liquor_type
        
        if origin:
            filters["origin"] = origin
        
        if custom_only:
            filters["custom"] = True
        
        return await cls.find(filters).skip(skip).limit(limit).to_list()
    
    @classmethod
    async def get_by_saq_code(cls, saq_code: str) -> Optional["Liquor"]:
        """Get liquor by SAQ product code."""
        return await cls.find_one({"saq_code": saq_code})
    
    @classmethod
    async def get_by_lcbo_code(cls, lcbo_code: str) -> Optional["Liquor"]:
        """Get liquor by LCBO product code."""
        return await cls.find_one({"lcbo_code": lcbo_code})
    
    @classmethod
    async def get_by_type(cls, liquor_type: LiquorType, limit: int = 50) -> List["Liquor"]:
        """Get liquors by type."""
        return await cls.find({"liquor_type": liquor_type}).limit(limit).to_list()
    
    @classmethod
    async def get_by_origin(cls, origin: LiquorOrigin, limit: int = 50) -> List["Liquor"]:
        """Get liquors by origin."""
        return await cls.find({"origin": origin}).limit(limit).to_list()
