"""
Ingredient Matcher Service
Matches ingredient text to MongoDB ingredients using fuzzy matching
Extracts quantities, units, and ingredient names
"""
import re
from typing import Optional, List, Dict, Tuple
from fractions import Fraction
from app.models.mongodb.ingredient import Ingredient


class IngredientMatcher:
    """Service to match ingredient text to MongoDB ingredients"""
    
    def __init__(self):
        # Common measurement units (order matters - check longer ones first)
        self.units = [
            # Spoons
            ('c. à soupe', 'tbsp'), ('c. soupe', 'tbsp'), ('c.à soupe', 'tbsp'),
            ('c. à table', 'tbsp'), ('c. table', 'tbsp'), ('c.à table', 'tbsp'),
            ('tablespoon', 'tbsp'), ('tbsp', 'tbsp'),
            ('c. à thé', 'tsp'), ('c. thé', 'tsp'), ('c.à thé', 'tsp'),
            ('teaspoon', 'tsp'), ('tsp', 'tsp'),
            # Volume
            ('tasse', 'cup'), ('tasses', 'cup'), ('cup', 'cup'), ('cups', 'cup'),
            ('litre', 'l'), ('litres', 'l'), ('liter', 'l'), ('liters', 'l'), ('l', 'l'),
            ('millilitre', 'ml'), ('millilitres', 'ml'), ('ml', 'ml'),
            ('décilitre', 'dl'), ('décilitres', 'dl'), ('dl', 'dl'),
            ('centilitre', 'cl'), ('centilitres', 'cl'), ('cl', 'cl'),
            # Weight
            ('kilogramme', 'kg'), ('kilogrammes', 'kg'), ('kg', 'kg'),
            ('gramme', 'g'), ('grammes', 'g'), ('g', 'g'),
            ('milligramme', 'mg'), ('milligrammes', 'mg'), ('mg', 'mg'),
            ('livre', 'lb'), ('livres', 'lb'), ('pound', 'lb'), ('pounds', 'lb'), ('lb', 'lb'),
            ('once', 'oz'), ('onces', 'oz'), ('ounce', 'oz'), ('ounces', 'oz'), ('oz', 'oz'),
            # Pieces
            ('boite', 'can'), ('boîte', 'can'), ('boites', 'can'), ('boîtes', 'can'),
            ('can', 'can'), ('cans', 'can'),
            ('paquet', 'package'), ('paquets', 'package'), ('package', 'package'),
            ('tranche', 'slice'), ('tranches', 'slice'), ('slice', 'slice'), ('slices', 'slice'),
            ('gousse', 'clove'), ('gousses', 'clove'), ('clove', 'clove'), ('cloves', 'clove'),
            ('filet', 'fillet'), ('filets', 'fillet'), ('fillet', 'fillet'), ('fillets', 'fillet'),
            ('cube', 'cube'), ('cubes', 'cube'),
            ('pincée', 'pinch'), ('pincées', 'pinch'), ('pinch', 'pinch'),
        ]
        
        # Just unit names for stripping (normalized versions)
        self.unit_names = [u[1] for u in self.units]
        
        # Words to remove for better matching
        self.stop_words = [
            'de', 'du', 'des', 'le', 'la', 'les', 'un', 'une',
            'à', 'au', 'aux',
            'frais', 'fraîche', 'fraîches', 'fresh',
            'haché', 'hachée', 'hachés', 'hachées', 'chopped', 'diced',
            'râpé', 'râpée', 'râpés', 'râpées', 'grated',
            'tranché', 'tranchée', 'tranchés', 'tranchées', 'sliced',
            'coupé', 'coupée', 'coupés', 'coupées', 'cut',
            'égoutté', 'égouttée', 'égouttés', 'égouttées', 'drained',
        ]
    
    def parse_quantity(self, text: str) -> Tuple[Optional[float], Optional[float], Optional[str], str]:
        """
        Extract quantity, unit, and clean ingredient name from text
        
        Examples:
            '2 lb ailes de poulet' -> (2.0, None, 'lb', 'ailes de poulet')
            '1/4 tasse sauce soya' -> (0.25, None, 'cup', 'sauce soya')
            '1-2 c. à soupe miel' -> (1.0, 2.0, 'tbsp', 'miel')
            '3 gousses ail' -> (3.0, None, 'clove', 'ail')
        
        Returns:
            Tuple of (quantity, quantity_max, unit, remaining_text)
        """
        original_text = text
        text = text.strip()
        
        quantity = None
        quantity_max = None
        unit = None
        
        # Pattern to match quantities at the beginning:
        # - Simple numbers: "2", "1.5", "0.5"
        # - Fractions: "1/4", "1/2", "3/4"
        # - Mixed numbers: "1 1/2", "2 3/4"
        # - Ranges: "1-2", "1 à 2", "1 to 2"
        
        # Try to match quantity at start
        # Match: optional number, optional space, optional fraction, optional range
        pattern = r'^([\d.,]+(?:\s+\d+/\d+)?|\d+/\d+)(?:\s*(?:-|à|to|or)\s*([\d.,]+(?:\s+\d+/\d+)?|\d+/\d+))?\s*'
        match = re.match(pattern, text, re.IGNORECASE)
        
        if match:
            qty_str = match.group(1)
            qty_max_str = match.group(2)
            
            # Parse first quantity
            try:
                quantity = self._parse_number(qty_str)
            except:
                pass
            
            # Parse max quantity if range
            if qty_max_str:
                try:
                    quantity_max = self._parse_number(qty_max_str)
                except:
                    pass
            
            # Remove quantity from text
            text = text[match.end():].strip()
        
        # Now try to match unit at the beginning of remaining text
        for unit_pattern, normalized_unit in self.units:
            # Match unit at start of text (with optional parentheses for volume)
            unit_regex = r'^' + re.escape(unit_pattern) + r'\b'
            if re.match(unit_regex, text, re.IGNORECASE):
                unit = normalized_unit
                text = text[len(unit_pattern):].strip()
                break
        
        # Clean remaining text (remove "de", "d'", etc.)
        text = re.sub(r"^(?:de|d'|of)\s+", '', text, flags=re.IGNORECASE).strip()
        
        return quantity, quantity_max, unit, text
    
    def _parse_number(self, text: str) -> float:
        """
        Parse a number string that might contain fractions
        
        Examples:
            '2' -> 2.0
            '1.5' -> 1.5
            '1/4' -> 0.25
            '1 1/2' -> 1.5
            '2,5' -> 2.5 (European notation)
        """
        text = text.strip()
        
        # Handle European decimal notation (comma instead of dot)
        text = text.replace(',', '.')
        
        # Handle mixed fractions (e.g., "1 1/2")
        mixed_match = re.match(r'(\d+)\s+(\d+)/(\d+)', text)
        if mixed_match:
            whole = int(mixed_match.group(1))
            numerator = int(mixed_match.group(2))
            denominator = int(mixed_match.group(3))
            return float(whole) + float(numerator) / float(denominator)
        
        # Handle simple fractions (e.g., "1/4")
        if '/' in text:
            frac = Fraction(text)
            return float(frac)
        
        # Handle simple decimals
        return float(text)
    
    def extract_ingredient_name(self, text: str) -> str:
        """
        Extract the core ingredient name from a recipe ingredient line
        
        Examples:
            '2 lb ailes de poulet' -> 'ailes poulet'
            '1/4 tasse sauce soya' -> 'sauce soya'
            '3 gousses ail hachées' -> 'ail'
        """
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove numbers and fractions at the beginning
        text = re.sub(r'^[\d/.,\s]+', '', text)
        
        # Remove measurement units (using normalized unit names)
        for unit in self.unit_names:
            text = re.sub(r'\b' + re.escape(unit) + r'\b', '', text, flags=re.IGNORECASE)
        
        # Remove stop words
        words = text.split()
        words = [w for w in words if w not in self.stop_words]
        
        # Clean up extra spaces
        text = ' '.join(words).strip()
        
        return text
    
    async def find_best_match(self, ingredient_text: str, language: str = "fr") -> Optional[Ingredient]:
        """
        Find the best matching ingredient in MongoDB
        
        Args:
            ingredient_text: Raw ingredient text (e.g., '2 lb ailes de poulet')
            language: Language to search in ('fr' or 'en')
            
        Returns:
            Best matching Ingredient or None
        """
        # Extract core ingredient name
        clean_name = self.extract_ingredient_name(ingredient_text)
        
        if not clean_name:
            return None
        
        # Try exact match first
        field_name = f"names.{language}"
        exact_match = await Ingredient.find_one({
            field_name: {"$regex": f"^{re.escape(clean_name)}$", "$options": "i"}
        })
        
        if exact_match:
            return exact_match
        
        # Try partial match with all words
        partial_match = await Ingredient.find_one({
            field_name: {"$regex": re.escape(clean_name), "$options": "i"}
        })
        
        if partial_match:
            return partial_match
        
        # Try searching for individual keywords
        words = clean_name.split()
        if len(words) > 1:
            # Try with most significant word (usually the last one)
            for word in reversed(words):
                if len(word) >= 3:  # Only meaningful words
                    keyword_match = await Ingredient.find_one({
                        field_name: {"$regex": re.escape(word), "$options": "i"}
                    })
                    if keyword_match:
                        return keyword_match
        
        # Try text search as last resort
        try:
            results = await Ingredient.search(clean_name, language=language, limit=1)
            if results:
                return results[0]
        except:
            pass
        
        return None
    
    async def match_ingredients(self, ingredient_texts: List[str], language: str = "fr") -> List[Dict]:
        """
        Match a list of ingredient texts to MongoDB ingredients
        
        Args:
            ingredient_texts: List of raw ingredient text
            language: Language to search in
            
        Returns:
            List of dicts with:
                - original_text: Original ingredient line
                - quantity: Parsed quantity (float)
                - quantity_max: Max quantity for ranges (float)
                - unit: Normalized unit string
                - matched_ingredient: Ingredient object or None
                - off_id: OFF ID if matched
                - ingredient_name_fr/en: Names if matched
                - preparation_notes: Full original text for display
        """
        results = []
        
        for text in ingredient_texts:
            # Parse quantity and unit
            quantity, quantity_max, unit, clean_text = self.parse_quantity(text)
            
            # Match ingredient
            matched = await self.find_best_match(clean_text, language)
            
            result = {
                'original_text': text,
                'quantity': quantity,
                'quantity_max': quantity_max,
                'unit': unit,
                'preparation_notes': text,  # Keep full text for display
                'matched_ingredient': matched,
                'off_id': matched.off_id if matched else None,
                'ingredient_name_fr': matched.names.get('fr', '') if matched else '',
                'ingredient_name_en': matched.names.get('en', '') if matched else '',
            }
            
            results.append(result)
        
        return results


# Global instance
ingredient_matcher = IngredientMatcher()
