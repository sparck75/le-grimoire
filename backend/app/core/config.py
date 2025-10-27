"""
Application configuration
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Le Grimoire"
    DEBUG: bool = False
    
    # Database - PostgreSQL (legacy)
    DATABASE_URL: str = "postgresql://grimoire:grimoire_password@db:5432/le_grimoire"
    
    # Database - MongoDB
    MONGODB_URL: str = "mongodb://legrimoire:grimoire_mongo_password@mongodb:27017/"
    MONGODB_DB_NAME: str = "legrimoire"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    APPLE_CLIENT_ID: str = ""
    APPLE_CLIENT_SECRET: str = ""
    
    # Redis
    REDIS_URL: str = "redis://redis:6379"
    
    # CORS - Allow setting via environment variable for production
    # In production, set ALLOWED_ORIGINS env var to:
    # "https://legrimoireonline.ca,https://www.legrimoireonline.ca"
    ALLOWED_ORIGINS: str = "*"  # Default to wildcard for development
    
    # OCR
    OCR_ENGINE: str = "tesseract"
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Scraper
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (compatible; LeGrimoire/1.0)"
    SCRAPER_RATE_LIMIT_SECONDS: int = 2
    
    # Unsplash API
    UNSPLASH_ACCESS_KEY: str = ""
    UNSPLASH_SECRET: str = ""
    
    # Pexels API
    PEXELS_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
