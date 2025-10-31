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
    admin_ingredients, admin_recipes, admin_users,
    ingredients, categories, recipe_images, ai_extraction, admin_ai,
    wines, liquors, admin_wines, lwin, ai_wine, barcodes
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
    lifespan=lifespan,
    redirect_slashes=False  # Disable automatic trailing slash redirects
)

# Configure CORS
# Parse ALLOWED_ORIGINS - can be "*" or comma-separated list
# Note: allow_credentials=True is incompatible with allow_origins=["*"]
# For development, we explicitly list allowed origins
if settings.ALLOWED_ORIGINS == "*":
    # Development: allow common local/network origins
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.1.100:3000",
        "http://192.168.1.101:3000",
        "http://192.168.1.133:3000",
        "http://192.168.1.205:3000",
    ]
else:
    allowed_origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(recipes.router, prefix="/api/v2/recipes", tags=["Recipes"])
app.include_router(recipe_images.router, prefix="/api/recipes", tags=["Recipe Images"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(ai_extraction.router, prefix="/api/ai", tags=["AI Extraction"])
app.include_router(grocery.router, prefix="/api/grocery", tags=["Grocery Specials"])
app.include_router(shopping_lists.router, prefix="/api/shopping-lists", tags=["Shopping Lists"])
app.include_router(admin_ingredients.router, prefix="/api/admin/ingredients", tags=["Admin - Ingredients"])
app.include_router(admin_recipes.router, prefix="/api/admin", tags=["Admin - Recipes"])
app.include_router(admin_users.router, prefix="/api/admin/users", tags=["Admin - Users"])
app.include_router(admin_ai.router, prefix="/api/admin/ai", tags=["Admin - AI"])
app.include_router(admin_wines.router, prefix="/api/admin", tags=["Admin - Wines"])

# New MongoDB-based endpoints
app.include_router(ingredients.router, prefix="/api/v2/ingredients", tags=["Ingredients v2"])
app.include_router(categories.router, prefix="/api/v2/categories", tags=["Categories v2"])
app.include_router(wines.router, prefix="/api/v2/wines", tags=["Wines"])
app.include_router(liquors.router, prefix="/api/v2/liquors", tags=["Liquors"])
app.include_router(lwin.router, prefix="/api/v2/lwin", tags=["LWIN"])
app.include_router(ai_wine.router, prefix="/api/v2/ai-wine", tags=["AI Wine"])
app.include_router(barcodes.router, prefix="/api/v2/barcodes", tags=["Barcodes"])

# Mount static files for ingredient images
data_path = Path("/app/data")
if data_path.exists():
    app.mount("/data", StaticFiles(directory="/app/data"), name="data")

# Mount uploads directory for recipe images
upload_path = Path(settings.UPLOAD_DIR)
if upload_path.exists():
    app.mount(
        "/uploads",
        StaticFiles(directory=settings.UPLOAD_DIR),
        name="uploads"
    )


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
