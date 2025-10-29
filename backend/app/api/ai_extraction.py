"""
AI-powered recipe extraction API
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import os
from uuid import uuid4

from app.core.database import get_db
from app.core.config import settings
from app.services.ai_recipe_extraction import ai_recipe_service, ExtractedRecipe
from app.services.ocr_service import ocr_service

router = APIRouter()


@router.post("/extract", response_model=ExtractedRecipe)
async def extract_recipe_from_image(
    file: UploadFile = File(...),
    provider: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Extract structured recipe data from image using AI
    
    Args:
        file: Recipe image file
        provider: AI provider to use (openai, tesseract) - defaults to settings
        
    Returns:
        ExtractedRecipe with structured data
    """
    # Check if AI extraction is enabled
    enable_ai = getattr(settings, 'ENABLE_AI_EXTRACTION', False)
    if not enable_ai:
        raise HTTPException(
            status_code=503,
            detail="AI extraction is not enabled. Use /api/ocr/upload instead."
        )
    
    # Validate file
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await file.read()
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)
    if len(contents) > max_size:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Save file
    upload_dir = getattr(settings, 'UPLOAD_DIR', '/tmp/uploads')
    os.makedirs(upload_dir, exist_ok=True)
    file_id = str(uuid4())
    filename = file.filename or 'upload.jpg'
    file_path = os.path.join(upload_dir, f"{file_id}_{filename}")
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Generate image URL for frontend
    image_url = f"/uploads/{file_id}_{filename}"
    
    try:
        # Determine provider
        ai_provider = getattr(settings, 'AI_PROVIDER', 'openai')
        use_provider = provider or ai_provider
        
        if use_provider == "tesseract":
            # Fallback to Tesseract OCR
            text = ocr_service.extract_text(file_path)
            parsed = ocr_service.parse_recipe(text)
            
            # Convert to ExtractedRecipe format
            result = ExtractedRecipe(
                title=parsed.get('title', 'Recette sans titre'),
                ingredients=[
                    {
                        "ingredient_name": ing,
                        "quantity": None,
                        "unit": None,
                        "preparation_notes": ing
                    }
                    for ing in parsed.get('ingredients', [])
                ],
                instructions=parsed.get('instructions', ''),
                confidence_score=0.5,
                image_url=image_url,
                extraction_method='ocr',
                raw_text=text,  # Include raw OCR text
                model_metadata={'engine': 'tesseract'}
            )
            return result
        
        elif use_provider == "openai":
            # Use AI extraction
            result = await ai_recipe_service.extract_recipe(file_path)
            # Add image URL and method to the result
            result.image_url = image_url
            result.extraction_method = 'ai'
            return result
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown provider: {use_provider}"
            )
            
    except Exception as e:
        # Try fallback if enabled
        ai_fallback = getattr(settings, 'AI_FALLBACK_ENABLED', True)
        if ai_fallback and use_provider != "tesseract":
            try:
                text = ocr_service.extract_text(file_path)
                parsed = ocr_service.parse_recipe(text)
                return ExtractedRecipe(
                    title=parsed.get('title', 'Recette sans titre'),
                    ingredients=[
                        {
                            "ingredient_name": ing,
                            "quantity": None,
                            "unit": None,
                            "preparation_notes": ing
                        }
                        for ing in parsed.get('ingredients', [])
                    ],
                    instructions=parsed.get('instructions', ''),
                    confidence_score=0.3,
                    image_url=image_url,
                    extraction_method='ocr_fallback',
                    raw_text=text,  # Include raw OCR text
                    model_metadata={'engine': 'tesseract', 'fallback': True, 'original_error': str(e)}
                )
            except Exception as fallback_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Extraction failed: {str(e)}. Fallback also failed: {str(fallback_error)}"
                )
        
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )


@router.get("/providers")
async def list_providers():
    """List available extraction providers and their status"""
    providers = {
        "tesseract": {
            "available": True,
            "type": "ocr",
            "cost": "free",
            "accuracy": "medium",
            "description": "Tesseract OCR - Free but lower accuracy"
        }
    }
    
    # Check if OpenAI is available
    if ai_recipe_service.is_available():
        providers["openai"] = {
            "available": True,
            "type": "ai",
            "cost": "paid",
            "accuracy": "high",
            "description": "GPT-4 Vision - High accuracy, paid service"
        }
    
    ai_provider = getattr(settings, 'AI_PROVIDER', 'openai')
    enable_ai = getattr(settings, 'ENABLE_AI_EXTRACTION', False)
    
    return {
        "providers": providers,
        "default": ai_provider,
        "ai_enabled": enable_ai,
        "fallback_enabled": getattr(settings, 'AI_FALLBACK_ENABLED', True)
    }


@router.get("/status")
async def ai_extraction_status():
    """Get status of AI extraction service"""
    enable_ai = getattr(settings, 'ENABLE_AI_EXTRACTION', False)
    
    return {
        "enabled": enable_ai,
        "provider": getattr(settings, 'AI_PROVIDER', 'openai'),
        "openai_available": ai_recipe_service.is_available(),
        "fallback_enabled": getattr(settings, 'AI_FALLBACK_ENABLED', True),
        "model": getattr(settings, 'OPENAI_MODEL', 'gpt-4o') if ai_recipe_service.is_available() else None
    }
