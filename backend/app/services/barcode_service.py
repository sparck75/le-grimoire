"""
Barcode service for managing barcode to LWIN mappings
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.mongodb import BarcodeMapping, Wine
import logging

logger = logging.getLogger(__name__)


class BarcodeService:
    """Service for barcode to LWIN mapping operations"""
    
    async def get_wine_by_barcode(self, barcode: str) -> Optional[Wine]:
        """
        Get wine by barcode
        
        Returns the associated LWIN wine if mapping exists
        """
        mapping = await BarcodeMapping.find_one({"barcode": barcode})
        
        if not mapping:
            return None
        
        # Update scan count and last scanned
        mapping.scan_count += 1
        mapping.last_scanned = datetime.utcnow()
        await mapping.save()
        
        # Get the wine from LWIN database
        query = {"lwin7": mapping.lwin7, "user_id": None}
        wine = await Wine.find_one(query)
        
        return wine
    
    async def create_mapping(
        self,
        barcode: str,
        lwin7: str,
        lwin11: Optional[str] = None,
        wine_name: str = "",
        producer: Optional[str] = None,
        vintage: Optional[int] = None,
        source: str = "manual",
        confidence: float = 1.0,
        user_id: Optional[str] = None
    ) -> BarcodeMapping:
        """
        Create a new barcode to LWIN mapping
        """
        # Check if mapping already exists
        existing = await BarcodeMapping.find_one({"barcode": barcode})
        
        if existing:
            # Update existing mapping
            existing.lwin7 = lwin7
            existing.lwin11 = lwin11
            existing.wine_name = wine_name
            existing.producer = producer
            existing.vintage = vintage
            existing.source = source
            existing.confidence = confidence
            existing.updated_at = datetime.utcnow()
            await existing.save()
            return existing
        
        # Create new mapping
        mapping = BarcodeMapping(
            barcode=barcode,
            lwin7=lwin7,
            lwin11=lwin11,
            wine_name=wine_name,
            producer=producer,
            vintage=vintage,
            source=source,
            confidence=confidence,
            created_by=user_id
        )
        
        await mapping.insert()
        logger.info(f"Created barcode mapping: {barcode} -> {lwin7}")
        
        return mapping
    
    async def create_mapping_from_ai_scan(
        self,
        barcode: str,
        extracted_wine_data: Dict[str, Any],
        confidence: float,
        user_id: Optional[str] = None
    ) -> Optional[BarcodeMapping]:
        """
        Create barcode mapping from AI wine extraction
        
        Attempts to match extracted wine data to LWIN database
        """
        # Try to find matching wine in LWIN database
        wine_name = extracted_wine_data.get("name", "")
        producer = extracted_wine_data.get("producer", "")
        vintage = extracted_wine_data.get("vintage")
        
        # Build search query
        query = {
            "data_source": "lwin",
            "user_id": None
        }
        
        # Search by name and producer
        if wine_name and producer:
            query["$or"] = [
                {
                    "name": {"$regex": wine_name, "$options": "i"},
                    "producer": {"$regex": producer, "$options": "i"}
                },
                {
                    "producer": {"$regex": f"{producer}.*{wine_name}", "$options": "i"}
                }
            ]
        elif wine_name:
            query["name"] = {"$regex": wine_name, "$options": "i"}
        
        # Try to find matching wine
        wines = await Wine.find(query).limit(5).to_list()
        
        if not wines:
            logger.warning(f"No LWIN match found for barcode {barcode}")
            return None
        
        # Use the best match (first result)
        best_match = wines[0]
        
        # Create mapping
        mapping = await self.create_mapping(
            barcode=barcode,
            lwin7=best_match.lwin7,
            lwin11=best_match.lwin11,
            wine_name=best_match.name,
            producer=best_match.producer,
            vintage=vintage or best_match.vintage,
            source="ai_scan",
            confidence=confidence * 0.8,  # Reduce confidence for AI
            user_id=user_id
        )
        
        logger.info(
            f"Created AI mapping: {barcode} -> {best_match.lwin7} "
            f"({best_match.name})"
        )
        
        return mapping
    
    async def verify_mapping(
        self,
        barcode: str,
        user_id: str
    ) -> Optional[BarcodeMapping]:
        """Mark a mapping as verified by a user"""
        mapping = await BarcodeMapping.find_one({"barcode": barcode})
        
        if not mapping:
            return None
        
        mapping.verified = True
        mapping.confidence = 1.0
        mapping.updated_at = datetime.utcnow()
        await mapping.save()
        
        logger.info(f"Verified mapping: {barcode} by user {user_id}")
        
        return mapping
    
    async def search_mappings(
        self,
        barcode: Optional[str] = None,
        lwin7: Optional[str] = None,
        verified_only: bool = False,
        min_confidence: float = 0.0,
        limit: int = 50
    ) -> List[BarcodeMapping]:
        """Search barcode mappings"""
        query = {}
        
        if barcode:
            query["barcode"] = {"$regex": barcode, "$options": "i"}
        
        if lwin7:
            query["lwin7"] = lwin7
        
        if verified_only:
            query["verified"] = True
        
        if min_confidence > 0:
            query["confidence"] = {"$gte": min_confidence}
        
        mappings = await BarcodeMapping.find(query).limit(limit).to_list()
        
        return mappings
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get barcode mapping statistics"""
        total = await BarcodeMapping.find({}).count()
        verified = await BarcodeMapping.find({"verified": True}).count()
        
        # Count by source
        pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}}
        ]
        by_source_cursor = BarcodeMapping.aggregate(pipeline)
        by_source_list = await by_source_cursor.to_list()
        by_source = {item["_id"]: item["count"] for item in by_source_list}
        
        return {
            "total_mappings": total,
            "verified_mappings": verified,
            "by_source": by_source,
            "unverified": total - verified
        }
