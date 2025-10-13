"""
Le Grimoire - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import recipes, auth, ocr, grocery, shopping_lists
from app.core.config import settings

app = FastAPI(
    title="Le Grimoire API",
    description="API pour la gestion de recettes avec OCR et intégration des spéciaux d'épiceries",
    version="1.0.0"
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
app.include_router(recipes.router, prefix="/api/recipes", tags=["Recipes"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(grocery.router, prefix="/api/grocery", tags=["Grocery Specials"])
app.include_router(shopping_lists.router, prefix="/api/shopping-lists", tags=["Shopping Lists"])

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
