"""
OpenAI Model Configurations and Pricing
Based on: https://platform.openai.com/docs/pricing
Last updated: October 2025
"""

from typing import Dict, Any

# OpenAI Model Pricing (per 1M tokens)
OPENAI_MODELS = {
    "gpt-4o": {
        "name": "GPT-4o",
        "description": "Most capable model, best for complex tasks",
        "input_price": 2.50,  # per 1M tokens
        "output_price": 10.00,  # per 1M tokens
        "context_window": 128000,
        "max_output_tokens": 16384,
        "vision": True,
        "recommended": True
    },
    "gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "description": ("Affordable and intelligent small model for fast, "
                        "lightweight tasks"),
        "input_price": 0.150,  # per 1M tokens
        "output_price": 0.600,  # per 1M tokens
        "context_window": 128000,
        "max_output_tokens": 16384,
        "vision": True,
        "recommended": True
    },
    "o1-preview": {
        "name": "o1-preview",
        "description": ("Reasoning model designed to solve hard problems "
                        "across domains"),
        "input_price": 15.00,  # per 1M tokens
        "output_price": 60.00,  # per 1M tokens
        "context_window": 128000,
        "max_output_tokens": 32768,
        "vision": False,
        "recommended": False
    },
    "o1-mini": {
        "name": "o1-mini",
        "description": "Fast reasoning model for coding, math, and science",
        "input_price": 3.00,  # per 1M tokens
        "output_price": 12.00,  # per 1M tokens
        "context_window": 128000,
        "max_output_tokens": 65536,
        "vision": False,
        "recommended": False
    },
    "gpt-4-turbo": {
        "name": "GPT-4 Turbo",
        "description": "Previous generation high-intelligence model",
        "input_price": 10.00,  # per 1M tokens
        "output_price": 30.00,  # per 1M tokens
        "context_window": 128000,
        "max_output_tokens": 4096,
        "vision": True,
        "recommended": False
    },
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "description": "Fast, inexpensive model for simple tasks",
        "input_price": 0.50,  # per 1M tokens
        "output_price": 1.50,  # per 1M tokens
        "context_window": 16385,
        "max_output_tokens": 4096,
        "vision": False,
        "recommended": False
    }
}


def get_model_info(model_id: str) -> Dict[str, Any]:
    """Get model information by ID"""
    return OPENAI_MODELS.get(model_id, OPENAI_MODELS["gpt-4o"])


def calculate_cost(
    model_id: str,
    prompt_tokens: int,
    completion_tokens: int
) -> float:
    """Calculate cost for a model based on token usage"""
    model = get_model_info(model_id)
    input_cost = prompt_tokens * model["input_price"] / 1_000_000
    output_cost = completion_tokens * model["output_price"] / 1_000_000
    return input_cost + output_cost


def get_available_models(
    vision_required: bool = True
) -> Dict[str, Dict[str, Any]]:
    """Get available models, optionally filtered by vision support"""
    if vision_required:
        return {k: v for k, v in OPENAI_MODELS.items() if v["vision"]}
    return OPENAI_MODELS


def get_recommended_models() -> Dict[str, Dict[str, Any]]:
    """Get recommended models for recipe extraction"""
    return {k: v for k, v in OPENAI_MODELS.items() if v["recommended"]}
