"""
Admin API for AI extraction management
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import os

from app.core.config import settings
from app.services.ai_recipe_extraction import ai_recipe_service

router = APIRouter()


class AIStatusResponse(BaseModel):
    """AI service status response"""
    enabled: bool
    provider: str
    openai_configured: bool
    openai_model: Optional[str] = None
    gemini_configured: bool
    fallback_enabled: bool
    upload_dir: str
    max_upload_size: int


class AIConfigUpdate(BaseModel):
    """AI configuration update request"""
    enabled: Optional[bool] = None
    provider: Optional[str] = None
    fallback_enabled: Optional[bool] = None


class OpenAIUsageResponse(BaseModel):
    """OpenAI account usage information"""
    api_key_configured: bool
    api_key_prefix: Optional[str] = None
    model: str
    max_tokens: int
    service_available: bool
    # Note: OpenAI API doesn't provide usage/billing info via API
    # Users need to check platform.openai.com for detailed usage
    usage_dashboard_url: str = "https://platform.openai.com/usage"
    billing_url: str = "https://platform.openai.com/account/billing"


@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status():
    """
    Get current AI extraction service status and configuration
    
    Returns current settings and availability status
    """
    openai_configured = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())
    gemini_configured = bool(settings.GOOGLE_AI_API_KEY and settings.GOOGLE_AI_API_KEY.strip())
    
    return AIStatusResponse(
        enabled=settings.ENABLE_AI_EXTRACTION,
        provider=settings.AI_PROVIDER,
        openai_configured=openai_configured,
        openai_model=settings.OPENAI_MODEL if openai_configured else None,
        gemini_configured=gemini_configured,
        fallback_enabled=settings.AI_FALLBACK_ENABLED,
        upload_dir=settings.UPLOAD_DIR,
        max_upload_size=settings.MAX_UPLOAD_SIZE
    )


@router.get("/openai/usage", response_model=OpenAIUsageResponse)
async def get_openai_usage():
    """
    Get OpenAI account information and usage links
    
    Note: OpenAI API doesn't provide programmatic access to billing/usage data.
    This endpoint returns configuration info and links to the OpenAI dashboard.
    """
    api_key = settings.OPENAI_API_KEY
    api_key_configured = bool(api_key and api_key.strip())
    
    # Extract first few characters of API key for display (masked)
    api_key_prefix = None
    if api_key_configured:
        api_key_prefix = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "sk-..."
    
    service_available = ai_recipe_service.is_available()
    
    return OpenAIUsageResponse(
        api_key_configured=api_key_configured,
        api_key_prefix=api_key_prefix,
        model=settings.OPENAI_MODEL,
        max_tokens=settings.OPENAI_MAX_TOKENS,
        service_available=service_available
    )


@router.post("/config")
async def update_ai_config(config: AIConfigUpdate):
    """
    Update AI extraction configuration
    
    Note: This updates runtime settings only. For persistent changes,
    update the .env file and restart the service.
    
    Args:
        config: Configuration updates
        
    Returns:
        Updated configuration status
    """
    updates = {}
    
    if config.enabled is not None:
        settings.ENABLE_AI_EXTRACTION = config.enabled
        updates['enabled'] = config.enabled
    
    if config.provider is not None:
        if config.provider not in ['openai', 'gemini', 'tesseract', 'auto']:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider: {config.provider}. Must be one of: openai, gemini, tesseract, auto"
            )
        settings.AI_PROVIDER = config.provider
        updates['provider'] = config.provider
    
    if config.fallback_enabled is not None:
        settings.AI_FALLBACK_ENABLED = config.fallback_enabled
        updates['fallback_enabled'] = config.fallback_enabled
    
    return {
        "success": True,
        "message": "Configuration updated successfully. Note: Changes are runtime only. Update .env for persistence.",
        "updates": updates,
        "current_status": {
            "enabled": settings.ENABLE_AI_EXTRACTION,
            "provider": settings.AI_PROVIDER,
            "fallback_enabled": settings.AI_FALLBACK_ENABLED
        }
    }


@router.get("/providers")
async def list_available_providers():
    """
    List all available AI providers and their configuration status
    """
    openai_configured = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())
    gemini_configured = bool(settings.GOOGLE_AI_API_KEY and settings.GOOGLE_AI_API_KEY.strip())
    
    return {
        "providers": {
            "openai": {
                "name": "OpenAI GPT-4 Vision",
                "configured": openai_configured,
                "available": openai_configured and ai_recipe_service.is_available(),
                "model": settings.OPENAI_MODEL,
                "cost_per_1k_tokens": {
                    "input": 0.01,  # gpt-4o pricing
                    "output": 0.03
                },
                "estimated_cost_per_recipe": 0.04,
                "accuracy": "95%+",
                "setup_url": "https://platform.openai.com/api-keys"
            },
            "gemini": {
                "name": "Google Gemini Flash",
                "configured": gemini_configured,
                "available": False,  # Not implemented yet
                "model": settings.GEMINI_MODEL,
                "free_tier": "1500 requests/day",
                "cost_per_1k_tokens": {
                    "input": 0.00,  # Free tier
                    "output": 0.00
                },
                "estimated_cost_per_recipe": 0.0,
                "accuracy": "90%+",
                "setup_url": "https://aistudio.google.com/app/apikey",
                "status": "Coming in Phase 2"
            },
            "tesseract": {
                "name": "Tesseract OCR",
                "configured": True,
                "available": True,
                "model": "tesseract",
                "cost_per_1k_tokens": {
                    "input": 0.0,
                    "output": 0.0
                },
                "estimated_cost_per_recipe": 0.0,
                "accuracy": "60-70%",
                "setup_url": None
            }
        },
        "current_provider": settings.AI_PROVIDER,
        "fallback_enabled": settings.AI_FALLBACK_ENABLED
    }


@router.get("/stats")
async def get_extraction_stats():
    """
    Get extraction statistics (placeholder for future implementation)
    
    In a full implementation, this would track:
    - Total extractions performed
    - Extractions by provider (AI vs OCR)
    - Average confidence scores
    - Token usage over time
    - Cost tracking
    
    For now, returns basic info and notes for future enhancement.
    """
    return {
        "note": "Statistics tracking not yet implemented",
        "current_session": {
            "enabled": settings.ENABLE_AI_EXTRACTION,
            "provider": settings.AI_PROVIDER,
            "service_available": ai_recipe_service.is_available()
        },
        "future_features": [
            "Total extraction count",
            "Extractions by provider (AI/OCR)",
            "Average confidence scores",
            "Token usage tracking",
            "Cost estimation",
            "Success/failure rates"
        ],
        "implementation_note": "To track stats, implement logging in ai_extraction.py endpoint and store in database"
    }
