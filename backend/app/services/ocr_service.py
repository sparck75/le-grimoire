"""
OCR Service for extracting text from recipe images
"""
import pytesseract
from PIL import Image
from typing import Optional
import re

class OCRService:
    """Service for OCR processing of recipe images"""
    
    def __init__(self):
        # Configure Tesseract for French language
        self.config = '--psm 6 -l fra+eng'
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from image using Tesseract OCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text
        """
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, config=self.config)
            return text.strip()
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
                recipe['instructions'] += line + '\n'
        
        return recipe

ocr_service = OCRService()
