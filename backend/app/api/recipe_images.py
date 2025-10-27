"""
Recipe image upload endpoint
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import uuid
from pathlib import Path
from app.core.config import settings

router = APIRouter()


class ImageUploadResponse(BaseModel):
    """Image upload response"""
    url: str
    filename: str


@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_recipe_image(file: UploadFile = File(...)):
    """
    Upload recipe image
    Requires authentication (collaborator or admin)
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être une image"
        )
    
    # Validate file size (5MB max)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="L'image ne doit pas dépasser 5 MB"
        )
    
    # Generate unique filename
    file_extension = Path(file.filename or "image.jpg").suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR) / "recipes"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / unique_filename
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Return URL (relative path)
    image_url = f"/uploads/recipes/{unique_filename}"
    
    return ImageUploadResponse(
        url=image_url,
        filename=unique_filename
    )
