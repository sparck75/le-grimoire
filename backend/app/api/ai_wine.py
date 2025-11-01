"""
AI-powered wine extraction API

Provides endpoints for extracting wine information from label images
using GPT-4 Vision, with automatic LWIN database matching and enrichment.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import Optional
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
    front_label: Optional[UploadFile] = File(None),
    back_label: Optional[UploadFile] = File(None),
    bottle: Optional[UploadFile] = File(None),
    enrich_with_lwin: bool = True,
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Extract structured wine data from wine images using AI
    
    Supports multiple image types for comprehensive extraction:
    - front_label: Front label image (primary source for extraction)
    - back_label: Back label image (additional details)
    - bottle: Full bottle image (visual reference)
    
    Args:
        front_label: Front label image file (recommended)
        back_label: Back label image file (optional)
        bottle: Full bottle image file (optional)
        enrich_with_lwin: Attempt to match and enrich with LWIN database (default: True)
        
    Returns:
        ExtractedWineData with structured wine information
    """
    # At least one image must be provided
    if not front_label and not back_label and not bottle:
        raise HTTPException(
            status_code=400,
            detail="At least one image (front_label, back_label, or bottle) must be provided"
        )
    
    # Prioritize front_label for extraction, fallback to back_label, then bottle
    primary_file = front_label or back_label or bottle
    file_type = "front_label" if front_label else ("back_label" if back_label else "bottle")
    
    # Track all uploaded image paths
    uploaded_images = {
        'front_label_image': None,
        'back_label_image': None,
        'bottle_image': None
    }
    
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
    
    # Validate primary file
    if not primary_file.content_type or \
       not primary_file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    contents = await primary_file.read()
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)
    if len(contents) > max_size:
        max_mb = max_size / (1024*1024)
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {max_mb:.1f}MB"
        )
    
    try:
        # Save ALL uploaded images
        upload_dir = Path(getattr(settings, 'UPLOAD_DIR', '/app/uploads'))
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Primary file will be saved as front_label
        temp_filename = None
        temp_path = None
        
        # Save front_label if provided (primary extraction image)
        if front_label:
            suffix = (Path(front_label.filename).suffix
                      if front_label.filename else '.jpg')
            front_filename = f"wine_front_label_{uuid4()}{suffix}"
            temp_filename = front_filename
            temp_path = upload_dir / front_filename
            with open(temp_path, 'wb') as f:
                f.write(contents)
            uploaded_images['front_label_image'] = (
                f"/uploads/{front_filename}")
        
        # Save back_label if provided
        if back_label:
            # Reuse contents if back_label is the primary file
            if back_label is primary_file:
                back_contents = contents
            else:
                back_contents = await back_label.read()
            
            suffix = (Path(back_label.filename).suffix
                      if back_label.filename else '.jpg')
            back_filename = f"wine_back_label_{uuid4()}{suffix}"
            back_path = upload_dir / back_filename
            with open(back_path, 'wb') as f:
                f.write(back_contents)
            uploaded_images['back_label_image'] = (
                f"/uploads/{back_filename}")
        
        # Save bottle if provided
        if bottle:
            # Reuse contents if bottle is the primary file
            if bottle is primary_file:
                bottle_contents = contents
            else:
                bottle_contents = await bottle.read()
            
            suffix = (Path(bottle.filename).suffix
                      if bottle.filename else '.jpg')
            bottle_filename = f"wine_bottle_{uuid4()}{suffix}"
            bottle_path = upload_dir / bottle_filename
            with open(bottle_path, 'wb') as f:
                f.write(bottle_contents)
            uploaded_images['bottle_image'] = (
                f"/uploads/{bottle_filename}")
        
        logger.info(f"Processing wine label image: {temp_filename}")
        
        # Prepare additional images for AI analysis
        additional_images = []
        if back_label and back_label is not primary_file:
            # Back label was read and saved, add to AI analysis
            logger.info("Including back label in AI analysis")
            additional_images.append(back_contents)
        
        # Extract wine data with timing and multiple images
        import time
        start_time = time.time()
        extracted = await ai_wine_service.extract_from_image(
            image_bytes=contents,
            additional_images=additional_images if additional_images
            else None
        )
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Set primary image URL and all uploaded images
        extracted.image_url = f"/uploads/{temp_filename}"
        extracted.front_label_image = uploaded_images['front_label_image']
        extracted.back_label_image = uploaded_images['back_label_image']
        extracted.bottle_image = uploaded_images['bottle_image']
        
        # Enrich with LWIN if requested
        if enrich_with_lwin:
            logger.info("Attempting LWIN enrichment")
            lwin_service = LWINService()
            
            lwin_wine = await ai_wine_service.match_to_lwin(
                extracted, lwin_service)
            
            if lwin_wine:
                logger.info("Found LWIN match, enriching data")
                extracted = await ai_wine_service.enrich_from_lwin(
                    extracted, lwin_wine)
        
        # Search for wine images from internet
        logger.info("Searching for wine images from internet")
        from app.services.wine_image_search import WineImageSearchService
        image_search_service = WineImageSearchService()
        
        try:
            image_results = await image_search_service.search_wine_images(
                wine_name=extracted.name,
                producer=extracted.producer,
                vintage=extracted.vintage,
                max_results=8
            )
            
            # Convert to SuggestedImage format
            from app.services.ai_wine_extraction import SuggestedImage
            extracted.suggested_images = [
                SuggestedImage(
                    url=img.url,
                    thumbnail_url=img.thumbnail_url,
                    source=img.source,
                    title=img.title,
                    context_url=img.context_url,
                    relevance_score=img.relevance_score
                )
                for img in image_results
            ]
            logger.info(f"Found {len(extracted.suggested_images)} wine images")
        except Exception as e:
            logger.warning(f"Image search failed: {e}")
            # Don't fail extraction if image search fails
        
        # Log extraction with LWIN match info
        try:
            metadata = extracted.model_metadata or {}
            if lwin_wine and extracted.suggested_lwin7:
                metadata['lwin_matched'] = True
                metadata['lwin7'] = extracted.suggested_lwin7
            
            log = AIExtractionLog(
                extraction_type='wine',
                extraction_method='ai',
                provider='openai',
                model_name=metadata.get('model'),
                user_id=str(current_user.id) if current_user else None,
                original_image_path=str(temp_path),
                wine_name=extracted.name,
                wine_producer=extracted.producer,
                success=True,
                confidence_score=extracted.confidence_score,
                processing_time_ms=processing_time_ms,
                prompt_tokens=metadata.get('prompt_tokens'),
                completion_tokens=metadata.get('completion_tokens'),
                total_tokens=metadata.get('total_tokens'),
                estimated_cost_usd=metadata.get('estimated_cost'),
                model_metadata=metadata
            )
            await log.insert()
            logger.info(
                f"Logged wine extraction: {extracted.name}, "
                f"tokens={metadata.get('total_tokens')}, "
                f"cost=${metadata.get('estimated_cost', 0):.4f}, "
                f"time={processing_time_ms}ms, "
                f"lwin_matched={metadata.get('lwin_matched', False)}"
            )
        except Exception as e:
            logger.error(f"Failed to log extraction: {e}")
        
        logger.info(f"Successfully extracted wine: {extracted.name}")
        return extracted
        
    except Exception as e:
        logger.error(f"Error extracting wine: {e}")
        
        # Log failure
        try:
            log = AIExtractionLog(
                extraction_type='wine',
                extraction_method='ai',
                provider='openai',
                user_id=str(current_user.id) if current_user else None,
                original_image_path=str(temp_path)
                if 'temp_path' in locals() else None,
                success=False,
                error_message=str(e)
            )
            await log.insert()
        except Exception as log_error:
            logger.error(f"Failed to log extraction failure: {log_error}")
        
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
        # Create master wine data (for global database)
        master_wine_data = {
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
            'front_label_image': extraction_data.front_label_image,
            'back_label_image': extraction_data.back_label_image,
            'bottle_image': extraction_data.bottle_image,
            'data_source': 'ai',
            'user_id': None,  # Master wine - no owner
            'is_public': True,  # Available to all users
            'current_quantity': 0,  # Master wines have no inventory
        }
        
        # User's cellar wine data (personal inventory)
        user_wine_data = {
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
            'front_label_image': extraction_data.front_label_image,
            'back_label_image': extraction_data.back_label_image,
            'bottle_image': extraction_data.bottle_image,
            'data_source': 'ai',
            'user_id': str(current_user.id),  # Personal wine
            'is_public': False,  # User's private inventory
        }
        
        # Add user-provided cellar information (only for user's wine)
        if extraction_data.current_quantity is not None:
            user_wine_data['current_quantity'] = extraction_data.current_quantity
        else:
            user_wine_data['current_quantity'] = 1  # Default
        
        if extraction_data.purchase_price:
            user_wine_data['purchase_price'] = extraction_data.purchase_price
        if extraction_data.purchase_location:
            user_wine_data['purchase_location'] = extraction_data.purchase_location
        if extraction_data.cellar_location:
            user_wine_data['cellar_location'] = extraction_data.cellar_location
        if extraction_data.rating:
            user_wine_data['rating'] = extraction_data.rating
        
        # Add LWIN code if available (to both wines)
        if extraction_data.suggested_lwin7:
            master_wine_data['lwin7'] = extraction_data.suggested_lwin7
            user_wine_data['lwin7'] = extraction_data.suggested_lwin7
        
        # Add grape varieties (to both wines)
        if extraction_data.grape_varieties:
            from app.models.mongodb.wine import GrapeVariety
            grape_list = [
                GrapeVariety(name=grape)
                for grape in extraction_data.grape_varieties
            ]
            master_wine_data['grape_varieties'] = grape_list
            user_wine_data['grape_varieties'] = grape_list
        
        # Add suggested images to image_sources (to both wines)
        if extraction_data.suggested_images:
            from app.models.mongodb.wine import ImageSource
            from datetime import datetime
            
            image_sources = {}
            for idx, img in enumerate(extraction_data.suggested_images):
                source_key = f"{img.source}_{idx}"
                image_sources[source_key] = ImageSource(
                    url=img.url,
                    quality='medium',
                    source=img.source,
                    updated=datetime.utcnow(),
                    note=img.title or f"Found via {img.source} search"
                )
            master_wine_data['image_sources'] = image_sources
            user_wine_data['image_sources'] = image_sources
            logger.info(f"Added {len(image_sources)} images to wines")
        
        # Check if master wine already exists (avoid duplicates)
        existing_master = None
        if extraction_data.suggested_lwin7:
            # Try to find by LWIN7
            existing_master = await Wine.find_one({
                'lwin7': extraction_data.suggested_lwin7,
                'user_id': None
            })
        
        if not existing_master and extraction_data.name:
            # Try to find by name, producer, vintage (fuzzy match)
            query = {
                'name': extraction_data.name,
                'user_id': None
            }
            if extraction_data.producer:
                query['producer'] = extraction_data.producer
            if extraction_data.vintage:
                query['vintage'] = extraction_data.vintage
            
            existing_master = await Wine.find_one(query)
        
        # Create or update master wine
        if existing_master:
            logger.info(
                f"Master wine exists: {existing_master.name}, "
                f"using ID {existing_master.id}"
            )
            master_wine_id = str(existing_master.id)
        else:
            # Create new master wine for global database
            master_wine = Wine(**master_wine_data)
            await master_wine.insert()
            master_wine_id = str(master_wine.id)
            logger.info(
                f"Created master wine: {master_wine.name} "
                f"(ID: {master_wine_id})"
            )
        
        # Link user wine to master wine
        user_wine_data['master_wine_id'] = master_wine_id
        
        # Create user's personal cellar entry
        user_wine = Wine(**user_wine_data)
        await user_wine.insert()
        
        logger.info(
            f"Created user wine: {user_wine.name} "
            f"for user {current_user.id}"
        )
        
        return {
            'success': True,
            'wine_id': str(user_wine.id),
            'master_wine_id': master_wine_id,
            'message': 'Wine added to cellar and database',
            'wine': {
                'id': str(user_wine.id),
                'name': user_wine.name,
                'producer': user_wine.producer,
                'vintage': user_wine.vintage,
                'wine_type': user_wine.wine_type
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
