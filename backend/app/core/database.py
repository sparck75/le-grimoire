"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings

# PostgreSQL database (legacy)
engine = create_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"),
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get PostgreSQL database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# MongoDB connection
mongodb_client: AsyncIOMotorClient = None

def get_mongodb():
    """Get MongoDB client"""
    return mongodb_client

async def init_mongodb():
    """
    Initialize MongoDB connection and Beanie ODM.
    Call this function on application startup.
    """
    global mongodb_client
    
    # Import here to avoid circular imports
    from app.models.mongodb import Ingredient, Category, Recipe, AIExtractionLog, Wine, Liquor
    
    # Get MongoDB connection details from settings
    mongodb_url = getattr(settings, 'MONGODB_URL', 'mongodb://localhost:27017')
    mongodb_db_name = getattr(settings, 'MONGODB_DB_NAME', 'legrimoire')
    
    # Create MongoDB client
    mongodb_client = AsyncIOMotorClient(mongodb_url)
    
    print(f"✅ MongoDB client created: {mongodb_client is not None}")
    print(f"✅ MongoDB initialized: {mongodb_db_name}")
    
    # Initialize Beanie with document models
    await init_beanie(
        database=mongodb_client[mongodb_db_name],
        document_models=[Ingredient, Category, Recipe, AIExtractionLog, Wine, Liquor]
    )

async def close_mongodb():
    """
    Close MongoDB connection.
    Call this function on application shutdown.
    """
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("✅ MongoDB connection closed")
