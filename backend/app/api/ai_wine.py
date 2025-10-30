"""
AI-powered wine extraction API

Provides endpoints for extracting wine information from label images
using GPT-4 Vision, with automatic LWIN database matching and enrichment.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import Optional
import os
from uuid import uuid4
from pathlib import Path
import logging

from app.core.config import settings
from app.services.ai_wine_extraction import ai_wine_service, ExtractedWineData
from app.services.lwin_service import LWINService
from app.models.mongodb import AIExtractionLog, Wine
from app.core.security import get_current_user, optional_current_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/extract", response_model=ExtractedWineData)
async def extract_wine_from_image(
    file: UploadFile = File(...),
    enrich_with_lwin: bool = True,
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Extract structured wine data from label image using AI
    
    Args:
        file: Wine label image file
        enrich_with_lwin: Attempt to match and enrich with LWIN database (default: True)
        
    Returns:
        ExtractedWineData with structured wine information
    """
    # Check if AI extraction is enabled
    enable_ai = getattr(settings, 'ENABLE_AI_EXTRACTION', False)
    if not enable_ai:
        raise HTTPException(
            status_code=503,
            detail="AI extraction is not enabled. Set ENABLE_AI_EXTRACTION=true in environment."
        )
    
    # Check if service is available
    if not ai_wine_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="AI wine extraction service is not available (missing OpenAI API key)"
        )
    
    # Validate file
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await file.read()
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)
    if len(contents) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {max_size / (1024*1024):.1f}MB"
        )
    
    try:
        # Save uploaded file temporarily
        upload_dir = Path(getattr(settings, 'UPLOAD_DIR', '/app/uploads'))
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        temp_filename = f"wine_label_{uuid4()}{Path(file.filename).suffix if file.filename else '.jpg'}"
        temp_path = upload_dir / temp_filename
        
        with open(temp_path, 'wb') as f:
            f.write(contents)
        
        logger.info(f"Processing wine label image: {temp_filename}")
        
        # Extract wine data
        extracted = await ai_wine_service.extract_from_image(
            image_bytes=contents
        )
        
        # Set image URL
        extracted.image_url = f"/uploads/{temp_filename}"
        
        # Enrich with LWIN if requested
        if enrich_with_lwin:
            logger.info("Attempting LWIN enrichment")
            lwin_service = LWINService()
            
            lwin_wine = await ai_wine_service.match_to_lwin(extracted, lwin_service)
            
            if lwin_wine:
                logger.info(f"Found LWIN match, enriching data")
                extracted = await ai_wine_service.enrich_from_lwin(extracted, lwin_wine)
        
        # Log extraction
        try:
            log = AIExtractionLog(
                user_id=str(current_user.id) if current_user else None,
                extraction_type='wine',
                image_path=str(temp_path),
                success=True,
                confidence_score=extracted.confidence_score,
                model_used=extracted.model_metadata.get('model') if extracted.model_metadata else None,
                tokens_used=extracted.model_metadata.get('tokens_used') if extracted.model_metadata else None,
                extracted_data=extracted.dict()
            )
            await log.insert()
        except Exception as e:
            logger.error(f"Failed to log extraction: {e}")
        
        logger.info(f"Successfully extracted wine: {extracted.name}")
        return extracted
        
    except Exception as e:
        logger.error(f"Error extracting wine: {e}")
        
        # Log failure
        try:
            log = AIExtractionLog(
                user_id=str(current_user.id) if current_user else None,
                extraction_type='wine',
                image_path=str(temp_path) if 'temp_path' in locals() else None,
                success=False,
                error_message=str(e)
            )
            await log.insert()
        except:
            pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract wine data: {str(e)}"
        )


@router.post("/create-from-extraction", response_model=dict)
async def create_wine_from_extraction(
    extraction_data: ExtractedWineData,
    current_user: User = Depends(get_current_user)
):
    """
    Create a wine in user's cellar from extracted data
    
    Args:
        extraction_data: Extracted wine data from AI
        current_user: Authenticated user
        
    Returns:
        Created wine information
    """
    try:
        # Convert extracted data to Wine model
        wine_data = {
            'name': extraction_data.name,
            'producer': extraction_data.producer,
            'vintage': extraction_data.vintage,
            'country': extraction_data.country or '',
            'region': extraction_data.region or '',
            'appellation': extraction_data.appellation,
            'wine_type': extraction_data.wine_type,
            'alcohol_content': extraction_data.alcohol_content,
            'classification': extraction_data.classification,
            'tasting_notes': extraction_data.tasting_notes or '',
            'image_url': extraction_data.image_url,
            'data_source': 'ai',
            'user_id': str(current_user.id),
            'is_public': False,
            'current_quantity': 1  # Default to 1 bottle
        }
        
        # Add LWIN code if available
        if extraction_data.suggested_lwin7:
            wine_data['lwin7'] = extraction_data.suggested_lwin7
        
        # Add grape varieties
        if extraction_data.grape_varieties:
            from app.models.mongodb.wine import GrapeVariety
            wine_data['grape_varieties'] = [
                GrapeVariety(name=grape) for grape in extraction_data.grape_varieties
            ]
        
        # Create wine
        wine = Wine(**wine_data)
        await wine.insert()
        
        logger.info(f"Created wine from extraction: {wine.name} for user {current_user.id}")
        
        return {
            'success': True,
            'wine_id': str(wine.id),
            'message': 'Wine added to cellar successfully',
            'wine': {
                'id': str(wine.id),
                'name': wine.name,
                'producer': wine.producer,
                'vintage': wine.vintage,
                'wine_type': wine.wine_type
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating wine from extraction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create wine: {str(e)}"
        )


@router.get("/status")
async def get_ai_wine_status():
    """
    Get status of AI wine extraction service
    
    Returns:
        Service availability and configuration
    """
    return {
        'available': ai_wine_service.is_available(),
        'enabled': getattr(settings, 'ENABLE_AI_EXTRACTION', False),
        'model': getattr(settings, 'OPENAI_MODEL', 'gpt-4o'),
        'features': {
            'label_extraction': ai_wine_service.is_available(),
            'lwin_matching': True,
            'auto_enrichment': True
        }
    }
