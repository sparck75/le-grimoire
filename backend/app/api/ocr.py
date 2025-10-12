"""
OCR API routes
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
import os
from app.core.database import get_db
from app.core.config import settings
from app.models.ocr_job import OCRJob

router = APIRouter()

class OCRJobResponse(BaseModel):
    """OCR job response"""
    id: str
    status: str
    extracted_text: str = None
    parsed_recipe_id: str = None
    error_message: str = None
    
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
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Create OCR job
    ocr_job = OCRJob(
        image_path=file_path,
        status="pending"
    )
    db.add(ocr_job)
    db.commit()
    db.refresh(ocr_job)
    
    # In production, this would trigger an async task to process the image
    # For now, just return the job
    
    return OCRJobResponse(
        id=str(ocr_job.id),
        status=ocr_job.status,
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
    
    return OCRJobResponse(
        id=str(job.id),
        status=job.status,
        extracted_text=job.extracted_text,
        parsed_recipe_id=str(job.parsed_recipe_id) if job.parsed_recipe_id else None,
        error_message=job.error_message
    )
