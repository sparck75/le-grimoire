"""
OCR API routes
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
import os
from app.core.database import get_db
from app.core.config import settings
from app.models.ocr_job import OCRJob
from app.services.ocr_service import ocr_service

router = APIRouter()

class OCRJobResponse(BaseModel):
    """OCR job response"""
    id: str
    status: str
    image_url: Optional[str] = None
    extracted_text: Optional[str] = None
    parsed_recipe_id: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

@router.post("/upload", response_model=OCRJobResponse)
async def upload_recipe_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload recipe image for OCR processing
    Requires authentication in production
    """
    # Validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename or f"upload_{OCRJob.__tablename__}.jpg")
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Generate accessible URL (relative path from uploads directory)
    image_filename = os.path.basename(file_path)
    image_url = f"/uploads/{image_filename}"
    
    # Create OCR job
    ocr_job = OCRJob(
        image_path=file_path,
        status="processing"
    )
    db.add(ocr_job)
    db.commit()
    db.refresh(ocr_job)
    
    # Process OCR immediately (in production, use async task queue like Celery)
    try:
        extracted_text = ocr_service.extract_text(file_path)
        ocr_job.extracted_text = extracted_text
        ocr_job.status = "completed"
        
        # Parse recipe structure
        parsed_recipe = ocr_service.parse_recipe(extracted_text)
        # Note: In a full implementation, you would save this to Recipe model
        # For now, we just mark as completed
        
        db.commit()
        db.refresh(ocr_job)
    except Exception as e:
        ocr_job.status = "failed"
        ocr_job.error_message = str(e)
        db.commit()
        db.refresh(ocr_job)
    
    return OCRJobResponse(
        id=str(ocr_job.id),
        status=ocr_job.status,
        image_url=image_url,
        extracted_text=ocr_job.extracted_text,
        parsed_recipe_id=str(ocr_job.parsed_recipe_id) if ocr_job.parsed_recipe_id else None,
        error_message=ocr_job.error_message
    )

@router.get("/jobs/{job_id}", response_model=OCRJobResponse)
async def get_ocr_job(job_id: UUID, db: Session = Depends(get_db)):
    """
    Get OCR job status and results
    """
    job = db.query(OCRJob).filter(OCRJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="OCR job not found")
    
    # Generate accessible URL from stored image path
    image_filename = os.path.basename(job.image_path)
    image_url = f"/uploads/{image_filename}"
    
    return OCRJobResponse(
        id=str(job.id),
        status=job.status,
        image_url=image_url,
        extracted_text=job.extracted_text,
        parsed_recipe_id=str(job.parsed_recipe_id) if job.parsed_recipe_id else None,
        error_message=job.error_message
    )
