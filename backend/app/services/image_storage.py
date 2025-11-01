"""
Image storage service for wine images.

Handles uploading, validation, optimization, and storage of wine images
(front labels, back labels, and full bottle images).
"""

import uuid
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import aiofiles
from fastapi import UploadFile, HTTPException


class ImageStorageService:
    """Service for managing wine image storage."""
    
    # Supported image formats
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }
    
    # Size limits (in bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    # Image optimization settings
    MAX_WIDTH = 2048
    MAX_HEIGHT = 2048
    THUMBNAIL_SIZE = (400, 400)
    JPEG_QUALITY = 85
    
    # Storage directories
    BASE_UPLOAD_DIR = Path("uploads/wines")
    LABEL_FRONT_DIR = BASE_UPLOAD_DIR / "labels" / "front"
    LABEL_BACK_DIR = BASE_UPLOAD_DIR / "labels" / "back"
    BOTTLE_DIR = BASE_UPLOAD_DIR / "bottles"
    THUMBNAIL_DIR = BASE_UPLOAD_DIR / "thumbnails"
    
    def __init__(self):
        """Initialize storage directories."""
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create storage directories if they don't exist."""
        for directory in [
            self.LABEL_FRONT_DIR,
            self.LABEL_BACK_DIR,
            self.BOTTLE_DIR,
            self.THUMBNAIL_DIR
        ]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _validate_file_extension(self, filename: str) -> None:
        """
        Validate file extension.
        
        Args:
            filename: Name of the file to validate
            
        Raises:
            HTTPException: If file extension is not allowed
        """
        ext = Path(filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: "
                       f"{', '.join(self.ALLOWED_EXTENSIONS)}"
            )
    
    def _validate_mime_type(self, content_type: str) -> None:
        """
        Validate MIME type.
        
        Args:
            content_type: MIME type to validate
            
        Raises:
            HTTPException: If MIME type is not allowed
        """
        if content_type not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content type. Allowed: "
                       f"{', '.join(self.ALLOWED_MIME_TYPES)}"
            )
    
    async def _validate_file_size(self, file: UploadFile) -> None:
        """
        Validate file size.
        
        Args:
            file: File to validate
            
        Raises:
            HTTPException: If file is too large
        """
        # Read file to check size
        content = await file.read()
        size = len(content)
        
        # Reset file position for later reading
        await file.seek(0)
        
        if size > self.MAX_FILE_SIZE:
            max_mb = self.MAX_FILE_SIZE / (1024 * 1024)
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {max_mb} MB"
            )
    
    def _generate_filename(self, wine_id: str, original_filename: str) -> str:
        """
        Generate unique filename for storage.
        
        Args:
            wine_id: Wine document ID
            original_filename: Original uploaded filename
            
        Returns:
            Generated filename with format: {wine_id}_{uuid}.{ext}
        """
        ext = Path(original_filename).suffix.lower()
        unique_id = uuid.uuid4().hex[:8]
        return f"{wine_id}_{unique_id}{ext}"
    
    def _optimize_image(self, image_path: Path) -> None:
        """
        Optimize image by resizing and compressing.
        
        Args:
            image_path: Path to image file
        """
        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode == "RGBA":
                    # Create white background
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")
                
                # Resize if too large
                if img.width > self.MAX_WIDTH or img.height > self.MAX_HEIGHT:
                    img.thumbnail(
                        (self.MAX_WIDTH, self.MAX_HEIGHT),
                        Image.Resampling.LANCZOS
                    )
                
                # Save optimized image
                img.save(
                    image_path,
                    "JPEG",
                    quality=self.JPEG_QUALITY,
                    optimize=True
                )
        except Exception as e:
            # If optimization fails, log and continue
            # (file is still valid, just not optimized)
            print(f"Warning: Image optimization failed for {image_path}: {e}")
    
    def _create_thumbnail(
        self,
        image_path: Path,
        wine_id: str
    ) -> Optional[str]:
        """
        Create thumbnail for image.
        
        Args:
            image_path: Path to original image
            wine_id: Wine document ID
            
        Returns:
            Relative path to thumbnail or None if creation fails
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB
                if img.mode != "RGB":
                    img = img.convert("RGB")
                
                # Create thumbnail
                img.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                
                # Generate thumbnail filename
                thumb_filename = f"{wine_id}_thumb_{uuid.uuid4().hex[:8]}.jpg"
                thumb_path = self.THUMBNAIL_DIR / thumb_filename
                
                # Save thumbnail
                img.save(thumb_path, "JPEG", quality=80, optimize=True)
                
                return f"uploads/wines/thumbnails/{thumb_filename}"
        except Exception as e:
            print(f"Warning: Thumbnail creation failed for {image_path}: {e}")
            return None
    
    async def save_image(
        self,
        file: UploadFile,
        wine_id: str,
        image_type: str
    ) -> Tuple[str, Optional[str]]:
        """
        Save and optimize uploaded image.
        
        Args:
            file: Uploaded file
            wine_id: Wine document ID
            image_type: Type of image (front_label, back_label, bottle)
            
        Returns:
            Tuple of (image_url, thumbnail_url)
            
        Raises:
            HTTPException: If validation fails or image type is invalid
        """
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        self._validate_file_extension(file.filename)
        
        if file.content_type:
            self._validate_mime_type(file.content_type)
        
        await self._validate_file_size(file)
        
        # Determine storage directory
        if image_type == "front_label":
            storage_dir = self.LABEL_FRONT_DIR
            url_prefix = "uploads/wines/labels/front"
        elif image_type == "back_label":
            storage_dir = self.LABEL_BACK_DIR
            url_prefix = "uploads/wines/labels/back"
        elif image_type == "bottle":
            storage_dir = self.BOTTLE_DIR
            url_prefix = "uploads/wines/bottles"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type: {image_type}. "
                       f"Allowed: front_label, back_label, bottle"
            )
        
        # Generate filename
        filename = self._generate_filename(wine_id, file.filename)
        file_path = storage_dir / filename
        
        # Save file
        try:
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Optimize image
        self._optimize_image(file_path)
        
        # Create thumbnail (optional, non-blocking)
        thumbnail_url = self._create_thumbnail(file_path, wine_id)
        
        # Return relative URL
        image_url = f"{url_prefix}/{filename}"
        
        return image_url, thumbnail_url
    
    def delete_image(self, image_url: str) -> bool:
        """
        Delete image file from storage.
        
        Args:
            image_url: Relative URL of image to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            file_path = Path(image_url)
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception as e:
            print(f"Warning: Failed to delete image {image_url}: {e}")
        
        return False


# Global instance
image_storage_service = ImageStorageService()
