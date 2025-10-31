"""
Barcode to LWIN mapping model

Stores associations between UPC/EAN barcodes and LWIN codes.
Built progressively as users scan wine bottles.
"""
from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class BarcodeMapping(Document):
    """Association between barcode and LWIN wine"""
    
    barcode: str = Field(..., description="UPC/EAN barcode")
    lwin7: str = Field(..., description="LWIN7 code")
    lwin11: Optional[str] = Field(None, description="LWIN11 code (with vintage)")
    
    # Confidence and source tracking
    confidence: float = Field(default=1.0, description="Confidence score (0-1)")
    source: str = Field(default="manual", description="Source: manual, ai_scan, api, user_confirmed")
    verified: bool = Field(default=False, description="Human verified")
    
    # Additional wine info for quick lookup
    wine_name: str = Field(..., description="Wine name")
    producer: Optional[str] = Field(None, description="Producer name")
    vintage: Optional[int] = Field(None, description="Vintage year")
    
    # Usage tracking
    scan_count: int = Field(default=1, description="Number of times scanned")
    last_scanned: datetime = Field(default_factory=datetime.utcnow)
    
    # User who created the mapping
    created_by: Optional[str] = Field(None, description="User ID who created this mapping")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "barcode_mappings"
        indexes = [
            "barcode",
            "lwin7",
            "lwin11",
            ["barcode", "lwin7"],  # Compound index
            "verified",
            "confidence"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "barcode": "3760046480014",
                "lwin7": "1012361",
                "lwin11": "10123612015",
                "wine_name": "Château Léoville Barton",
                "producer": "Château Léoville Barton",
                "vintage": 2015,
                "confidence": 0.95,
                "source": "ai_scan",
                "verified": False,
                "scan_count": 1
            }
        }
