"""
Admin API for AI extraction management
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import os

from app.core.config import settings
from app.services.ai_recipe_extraction import ai_recipe_service
from app.core.openai_models import (
    get_available_models,
    get_recommended_models,
    OPENAI_MODELS
)

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
    model: Optional[str] = None
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


class ExtractionLogResponse(BaseModel):
    """Single extraction log entry"""
    id: str
    extraction_type: str
    extraction_method: str
    provider: Optional[str] = None
    model_name: Optional[str] = None
    
    # Recipe fields
    recipe_title: Optional[str] = None
    recipe_id: Optional[str] = None
    
    # Wine fields
    wine_name: Optional[str] = None
    wine_producer: Optional[str] = None
    wine_id: Optional[str] = None
    
    # Common fields
    confidence_score: Optional[float] = None
    success: bool
    error_message: Optional[str] = None
    total_tokens: Optional[int] = None
    estimated_cost_usd: Optional[float] = None
    processing_time_ms: Optional[int] = None
    image_url: Optional[str] = None
    created_at: datetime


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
        valid_providers = ['openai', 'gemini', 'tesseract', 'auto']
        if config.provider not in valid_providers:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid provider: {config.provider}. "
                    f"Must be one of: {', '.join(valid_providers)}"
                )
            )
        settings.AI_PROVIDER = config.provider
        updates['provider'] = config.provider
    
    if config.model is not None:
        # Validate model exists
        if config.model not in OPENAI_MODELS:
            available = ', '.join(OPENAI_MODELS.keys())
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid model: {config.model}. "
                    f"Available models: {available}"
                )
            )
        settings.OPENAI_MODEL = config.model
        updates['model'] = config.model
    
    if config.fallback_enabled is not None:
        settings.AI_FALLBACK_ENABLED = config.fallback_enabled
        updates['fallback_enabled'] = config.fallback_enabled
    
    return {
        "success": True,
        "message": (
            "Configuration updated successfully. "
            "Note: Changes are runtime only. Update .env for persistence."
        ),
        "updates": updates,
        "current_status": {
            "enabled": settings.ENABLE_AI_EXTRACTION,
            "provider": settings.AI_PROVIDER,
            "model": settings.OPENAI_MODEL,
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
async def get_extraction_stats(
    days: int = 30,
    provider: Optional[str] = None,
    extraction_type: Optional[str] = None
):
    """
    Get AI extraction usage statistics
    
    Args:
        days: Number of days to include in stats (default: 30)
        provider: Filter by provider (openai, tesseract, etc.)
        extraction_type: Filter by type (recipe, wine, or null for all)
        
    Returns:
        Comprehensive usage statistics including costs, tokens, and success rates
    """
    from datetime import datetime, timedelta
    from app.models.mongodb import AIExtractionLog
    
    # Calculate date range
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Build query
    query = {"created_at": {"$gte": start_date}}
    if provider:
        query["provider"] = provider
    if extraction_type:
        query["extraction_type"] = extraction_type
    
    # Get all logs in date range
    logs = await AIExtractionLog.find(query).to_list()
    
    # Calculate statistics
    total_extractions = len(logs)
    successful_extractions = sum(1 for log in logs if log.success)
    failed_extractions = sum(1 for log in logs if not log.success)
    
    # By provider
    by_provider = {}
    for log in logs:
        prov = log.provider or "unknown"
        if prov not in by_provider:
            by_provider[prov] = {
                "count": 0,
                "successful": 0,
                "failed": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0
            }
        by_provider[prov]["count"] += 1
        if log.success:
            by_provider[prov]["successful"] += 1
        else:
            by_provider[prov]["failed"] += 1
        if log.total_tokens:
            by_provider[prov]["total_tokens"] += log.total_tokens
        if log.estimated_cost_usd:
            by_provider[prov]["total_cost_usd"] += log.estimated_cost_usd
    
    # Token usage (AI only)
    ai_logs = [log for log in logs if log.extraction_method == 'ai' and log.total_tokens]
    total_tokens = sum(log.total_tokens for log in ai_logs)
    total_prompt_tokens = sum(log.prompt_tokens or 0 for log in ai_logs)
    total_completion_tokens = sum(log.completion_tokens or 0 for log in ai_logs)
    
    # Cost calculation
    total_cost = sum(log.estimated_cost_usd or 0 for log in logs)
    
    # Average confidence
    confidence_logs = [log for log in logs if log.confidence_score is not None]
    avg_confidence = sum(log.confidence_score for log in confidence_logs) / len(confidence_logs) if confidence_logs else 0
    
    # Average processing time
    processing_logs = [log for log in logs if log.processing_time_ms is not None]
    avg_processing_time = sum(log.processing_time_ms for log in processing_logs) / len(processing_logs) if processing_logs else 0
    
    # By extraction method
    by_method = {}
    for log in logs:
        method = log.extraction_method or "unknown"
        if method not in by_method:
            by_method[method] = 0
        by_method[method] += 1
    
    # By extraction type (recipe vs wine)
    by_type = {}
    for log in logs:
        ext_type = log.extraction_type or "recipe"
        if ext_type not in by_type:
            by_type[ext_type] = {
                "count": 0,
                "successful": 0,
                "failed": 0,
                "total_tokens": 0,
                "total_cost_usd": 0,
                "total_processing_time_ms": 0,
                "average_confidence": 0,
                "confidence_sum": 0,
                "confidence_count": 0
            }
        by_type[ext_type]["count"] += 1
        if log.success:
            by_type[ext_type]["successful"] += 1
        else:
            by_type[ext_type]["failed"] += 1
        
        # Aggregate metrics
        if log.total_tokens:
            by_type[ext_type]["total_tokens"] += log.total_tokens
        if log.estimated_cost_usd:
            by_type[ext_type]["total_cost_usd"] += log.estimated_cost_usd
        if log.processing_time_ms:
            by_type[ext_type]["total_processing_time_ms"] += (
                log.processing_time_ms
            )
        if log.confidence_score is not None:
            by_type[ext_type]["confidence_sum"] += log.confidence_score
            by_type[ext_type]["confidence_count"] += 1

    # Calculate averages per type
    for ext_type in by_type:
        count = by_type[ext_type]["count"]
        total_cost = by_type[ext_type]["total_cost_usd"]
        total_tokens = by_type[ext_type]["total_tokens"]
        total_time = by_type[ext_type]["total_processing_time_ms"]

        if count > 0:
            by_type[ext_type]["average_cost_usd"] = round(
                total_cost / count, 4
            )
            by_type[ext_type]["average_tokens"] = round(
                total_tokens / count, 0
            )
            by_type[ext_type]["average_processing_time_ms"] = round(
                total_time / count, 0
            )
        else:
            by_type[ext_type]["average_cost_usd"] = 0
            by_type[ext_type]["average_tokens"] = 0
            by_type[ext_type]["average_processing_time_ms"] = 0

        conf_count = by_type[ext_type]["confidence_count"]
        conf_sum = by_type[ext_type]["confidence_sum"]
        if conf_count > 0:
            by_type[ext_type]["average_confidence"] = round(
                conf_sum / conf_count, 3
            )
        else:
            by_type[ext_type]["average_confidence"] = 0

        # Clean up temporary fields
        del by_type[ext_type]["confidence_sum"]
        del by_type[ext_type]["confidence_count"]
    
    # Daily breakdown (last 7 days for chart)
    daily_stats = []
    for i in range(min(7, days)):
        day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        day_logs = [log for log in logs if day_start <= log.created_at < day_end]
        daily_stats.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "total": len(day_logs),
            "successful": sum(1 for log in day_logs if log.success),
            "failed": sum(1 for log in day_logs if not log.success),
            "cost_usd": sum(log.estimated_cost_usd or 0 for log in day_logs)
        })
    daily_stats.reverse()
    
    return {
        "period": {
            "days": days,
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat()
        },
        "summary": {
            "total_extractions": total_extractions,
            "successful": successful_extractions,
            "failed": failed_extractions,
            "success_rate": (successful_extractions / total_extractions * 100) if total_extractions > 0 else 0,
            "average_confidence": round(avg_confidence, 3),
            "average_processing_time_ms": round(avg_processing_time, 0)
        },
        "by_provider": by_provider,
        "by_method": by_method,
        "by_type": by_type,
        "tokens": {
            "total": total_tokens,
            "prompt": total_prompt_tokens,
            "completion": total_completion_tokens,
            "ai_extractions": len(ai_logs)
        },
        "costs": {
            "total_usd": round(total_cost, 4),
            "average_per_extraction_usd": round(total_cost / total_extractions, 4) if total_extractions > 0 else 0,
            "by_provider": {
                prov: round(stats["total_cost_usd"], 4) 
                for prov, stats in by_provider.items()
            }
        },
        "daily_breakdown": daily_stats,
        "current_config": {
            "enabled": settings.ENABLE_AI_EXTRACTION,
            "provider": settings.AI_PROVIDER,
            "fallback_enabled": settings.AI_FALLBACK_ENABLED
        }
    }


@router.get("/logs", response_model=List[ExtractionLogResponse])
async def get_extraction_logs(
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    success_only: Optional[bool] = None,
    provider: Optional[str] = None,
    extraction_type: Optional[str] = None
):
    """
    Get recent extraction logs with full details
    
    Args:
        limit: Maximum number of logs to return (1-500)
        skip: Number of logs to skip for pagination
        success_only: Filter by success status (true/false/null for all)
        provider: Filter by provider (openai, tesseract, etc.)
        extraction_type: Filter by type (recipe, wine, or null for all)
        
    Returns:
        List of extraction log entries with full details
    """
    from app.models.mongodb import AIExtractionLog
    
    # Build query
    query = {}
    if success_only is not None:
        query["success"] = success_only
    if provider:
        query["provider"] = provider
    if extraction_type:
        query["extraction_type"] = extraction_type
    
    # Get logs sorted by most recent first
    logs = await AIExtractionLog.find(query).sort("-created_at").skip(skip).limit(limit).to_list()
    
    # Convert to response format
    return [
        ExtractionLogResponse(
            id=str(log.id),
            extraction_type=log.extraction_type or "recipe",
            extraction_method=log.extraction_method,
            provider=log.provider,
            model_name=log.model_name,
            recipe_title=log.recipe_title,
            recipe_id=log.recipe_id,
            wine_name=log.wine_name,
            wine_producer=log.wine_producer,
            wine_id=log.wine_id,
            confidence_score=log.confidence_score,
            success=log.success,
            error_message=log.error_message,
            total_tokens=log.total_tokens,
            estimated_cost_usd=log.estimated_cost_usd,
            processing_time_ms=log.processing_time_ms,
            image_url=log.image_url,
            created_at=log.created_at
        )
        for log in logs
    ]


@router.get("/models")
async def list_available_models(
    vision_only: bool = Query(
        True,
        description="Only return models with vision capabilities"
    )
):
    """
    List available OpenAI models with pricing information
    
    Returns models that can be used for recipe extraction.
    Vision models are required for image-based extraction.
    """
    if vision_only:
        models = get_available_models(vision_required=True)
    else:
        models = OPENAI_MODELS
    
    return {
        "models": models,
        "current_model": settings.OPENAI_MODEL,
        "recommended": get_recommended_models()
    }


