"""
Le Grimoire - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
from app.api import (
    recipes, auth, ocr, grocery, shopping_lists,
    admin_ingredients, admin_recipes,
    ingredients, categories
)
from app.core.config import settings
from app.core.database import init_mongodb, close_mongodb

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup: Initialize MongoDB
    await init_mongodb()
    yield
    # Shutdown: Close MongoDB connection
    await close_mongodb()

app = FastAPI(
    title="Le Grimoire API",
    description="API pour la gestion de recettes avec OCR et intégration des spéciaux d'épiceries",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(recipes.router, prefix="/api/v2/recipes", tags=["Recipes"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(grocery.router, prefix="/api/grocery", tags=["Grocery Specials"])
app.include_router(shopping_lists.router, prefix="/api/shopping-lists", tags=["Shopping Lists"])
app.include_router(admin_ingredients.router, prefix="/api/admin/ingredients", tags=["Admin - Ingredients"])
app.include_router(admin_recipes.router, prefix="/api/admin", tags=["Admin - Recipes"])

# New MongoDB-based endpoints
app.include_router(ingredients.router, prefix="/api/v2/ingredients", tags=["Ingredients v2"])
app.include_router(categories.router, prefix="/api/v2/categories", tags=["Categories v2"])

# Mount static files for ingredient images
data_path = Path("/app/data")
if data_path.exists():
    app.mount("/data", StaticFiles(directory="/app/data"), name="data")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Le Grimoire API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/api/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "services": {
            "ocr": "available",
            "scraper": "available"
        }
    }
