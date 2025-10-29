"""
OCR Service for extracting text from recipe images
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from typing import Optional
import re
import cv2
import numpy as np

class OCRService:
    """Service for OCR processing of recipe images"""
    
    def __init__(self):
        # Configure Tesseract with better settings
        # PSM 3 = Fully automatic page segmentation, but no OSD
        # PSM 6 = Assume a single uniform block of text
        self.config = '--psm 3 --oem 3 -l fra+eng'
    
    def preprocess_image(self, image_path: str) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed PIL Image
        """
        # Read image with OpenCV
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding to handle varying lighting
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        # Convert back to PIL Image
        pil_img = Image.fromarray(denoised)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_img)
        enhanced = enhancer.enhance(2.0)
        
        # Sharpen
        sharpened = enhanced.filter(ImageFilter.SHARPEN)
        
        return sharpened
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from image using Tesseract OCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text
        """
        try:
            # Try with preprocessing
            preprocessed_image = self.preprocess_image(image_path)
            text_preprocessed = pytesseract.image_to_string(
                preprocessed_image, 
                config=self.config
            ).strip()
            
            # Also try with original image
            original_image = Image.open(image_path)
            text_original = pytesseract.image_to_string(
                original_image, 
                config=self.config
            ).strip()
            
            # Use whichever result is longer (usually better)
            text = text_preprocessed if len(text_preprocessed) > len(text_original) else text_original
            
            # If still empty or very short, try with different PSM mode
            if len(text) < 10:
                config_alt = '--psm 6 --oem 3 -l fra+eng'
                text_alt = pytesseract.image_to_string(
                    preprocessed_image,
                    config=config_alt
                ).strip()
                if len(text_alt) > len(text):
                    text = text_alt
            
            return text
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")
    
    def parse_recipe(self, text: str) -> dict:
        """
        Parse extracted text into recipe structure
        
        Args:
            text: Extracted text from image
            
        Returns:
            Dictionary with recipe components
        """
        # Basic recipe parsing logic
        # This is a simplified version - production would use NLP/AI
        
        lines = text.split('\n')
        recipe = {
            'title': '',
            'ingredients': [],
            'instructions': '',
            'servings': None,
            'prep_time': None,
            'cook_time': None
        }
        
        # Try to extract title (usually first line)
        if lines:
            recipe['title'] = lines[0].strip()
        
        # Try to find ingredients section
        ingredients_section = False
        instructions_section = False
        instructions_lines = []
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            if re.search(r'ingr[ée]dients?', line, re.IGNORECASE):
                ingredients_section = True
                instructions_section = False
                continue
            elif re.search(r'(instructions?|pr[ée]paration|[ée]tapes?)', line, re.IGNORECASE):
                instructions_section = True
                ingredients_section = False
                continue
            
            # Add to appropriate section
            if ingredients_section:
                recipe['ingredients'].append(line)
            elif instructions_section:
                # Each line becomes a separate instruction step
                instructions_lines.append(line)
        
        # Join instructions with newlines to ensure each step is on its own line
        recipe['instructions'] = '\n'.join(instructions_lines)
        
        return recipe

ocr_service = OCRService()
