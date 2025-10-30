"""
Wine Data Enrichment Agent

AI-powered service to enrich and validate scraped wine data.
Uses OpenAI, Google AI, or Anthropic to improve data quality.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, UTC
import os
import json

logger = logging.getLogger(__name__)


class WineEnrichmentAgent:
    """AI-powered wine data enrichment and validation"""
    
    def __init__(
        self,
        provider: str = "openai",
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize enrichment agent.
        
        Args:
            provider: AI provider (openai, google, anthropic)
            model: Model name (provider-specific)
            api_key: API key (from environment if not provided)
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()
        self.model = model or self._get_default_model()
        self.client = self._initialize_client()
        
        logger.info(f"Wine Enrichment Agent initialized: provider={self.provider}, model={self.model}")
    
    def _get_api_key(self) -> str:
        """Get API key from environment"""
        if self.provider == "openai":
            return os.getenv('OPENAI_API_KEY', '')
        elif self.provider == "google":
            return os.getenv('GOOGLE_AI_API_KEY', '')
        elif self.provider == "anthropic":
            return os.getenv('ANTHROPIC_API_KEY', '')
        return ''
    
    def _get_default_model(self) -> str:
        """Get default model for provider"""
        defaults = {
            'openai': 'gpt-4o-mini',  # Cost-effective for batch processing
            'google': 'gemini-1.5-flash',  # Fast and economical
            'anthropic': 'claude-3-haiku-20240307'  # Fastest Claude model
        }
        return defaults.get(self.provider, 'gpt-4o-mini')
    
    def _initialize_client(self):
        """Initialize AI client based on provider"""
        if self.provider == "openai":
            try:
                from openai import AsyncOpenAI
                return AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                logger.error("OpenAI library not installed. Run: pip install openai")
                return None
        
        elif self.provider == "google":
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                return genai.GenerativeModel(self.model)
            except ImportError:
                logger.error("Google AI library not installed. Run: pip install google-generativeai")
                return None
        
        elif self.provider == "anthropic":
            try:
                from anthropic import AsyncAnthropic
                return AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                logger.error("Anthropic library not installed. Run: pip install anthropic")
                return None
        
        return None
    
    async def enrich_wine_data(self, raw_wine: Dict) -> Dict:
        """
        Main enrichment pipeline.
        
        Args:
            raw_wine: Raw wine data from scraper
            
        Returns:
            Enriched wine data with AI improvements
        """
        if not self.client:
            logger.warning("AI client not initialized. Skipping enrichment.")
            return raw_wine
        
        logger.info(f"Enriching wine: {raw_wine.get('name', 'Unknown')}")
        
        enriched = raw_wine.copy()
        enriched['enrichment_log'] = []
        
        try:
            # Step 1: Validate data
            validation = await self.validate_wine_data(raw_wine)
            enriched['validation_issues'] = validation['issues']
            enriched['confidence_score'] = validation['confidence']
            enriched['enrichment_log'].append({
                'step': 'validation',
                'timestamp': datetime.now(UTC).isoformat(),
                'status': 'completed'
            })
            
            # Step 2: Enhance description if needed
            if self._needs_description(raw_wine):
                description = await self.generate_description(raw_wine)
                if description:
                    enriched['description'] = description
                    enriched['description_ai_generated'] = True
                    enriched['enrichment_log'].append({
                        'step': 'description',
                        'timestamp': datetime.now(UTC).isoformat(),
                        'status': 'generated'
                    })
            
            # Step 3: Add tasting notes if missing
            if self._needs_tasting_notes(raw_wine):
                tasting_notes = await self.generate_tasting_notes(raw_wine)
                if tasting_notes:
                    enriched.update(tasting_notes)
                    enriched['tasting_notes_ai_generated'] = True
                    enriched['enrichment_log'].append({
                        'step': 'tasting_notes',
                        'timestamp': datetime.now(UTC).isoformat(),
                        'status': 'generated'
                    })
            
            # Step 4: Suggest food pairings if missing
            if not raw_wine.get('food_pairings') or len(raw_wine.get('food_pairings', [])) == 0:
                pairings = await self.suggest_food_pairings(raw_wine)
                if pairings:
                    enriched['food_pairings'] = pairings
                    enriched['food_pairings_ai_generated'] = True
                    enriched['enrichment_log'].append({
                        'step': 'food_pairings',
                        'timestamp': datetime.now(UTC).isoformat(),
                        'status': 'generated'
                    })
            
            # Step 5: Normalize grape varieties
            if raw_wine.get('grape_varieties'):
                normalized_grapes = await self.normalize_grape_varieties(
                    raw_wine['grape_varieties']
                )
                if normalized_grapes:
                    enriched['grape_varieties'] = normalized_grapes
                    enriched['enrichment_log'].append({
                        'step': 'grape_normalization',
                        'timestamp': datetime.now(UTC).isoformat(),
                        'status': 'normalized'
                    })
            
            enriched['enriched_at'] = datetime.now(UTC).isoformat()
            enriched['enrichment_provider'] = self.provider
            enriched['enrichment_model'] = self.model
            
            logger.info(f"Successfully enriched wine: {raw_wine.get('name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error enriching wine: {e}")
            enriched['enrichment_error'] = str(e)
        
        return enriched
    
    def _needs_description(self, wine: Dict) -> bool:
        """Check if wine needs description enrichment"""
        desc = wine.get('description', '')
        return not desc or len(desc) < 50
    
    def _needs_tasting_notes(self, wine: Dict) -> bool:
        """Check if wine needs tasting notes"""
        return not wine.get('tasting_notes') and not wine.get('nose') and not wine.get('palate')
    
    async def validate_wine_data(self, wine: Dict) -> Dict:
        """
        Validate wine data and identify issues.
        
        Args:
            wine: Wine data to validate
            
        Returns:
            Validation result with issues and confidence score
        """
        prompt = self._build_validation_prompt(wine)
        
        try:
            response = await self._call_ai(prompt, json_mode=True)
            result = json.loads(response)
            
            logger.info(f"Validation complete: confidence={result.get('confidence', 0)}")
            return result
            
        except Exception as e:
            logger.error(f"Error in validation: {e}")
            return {
                'issues': [f"Validation error: {str(e)}"],
                'confidence': 50,
                'recommendations': []
            }
    
    async def generate_description(self, wine: Dict) -> str:
        """
        Generate wine description.
        
        Args:
            wine: Wine data
            
        Returns:
            Generated description
        """
        prompt = self._build_description_prompt(wine)
        
        try:
            description = await self._call_ai(prompt)
            logger.info(f"Generated description for: {wine.get('name', 'Unknown')}")
            return description.strip()
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return ""
    
    async def generate_tasting_notes(self, wine: Dict) -> Dict:
        """
        Generate tasting notes.
        
        Args:
            wine: Wine data
            
        Returns:
            Dictionary with tasting note fields
        """
        prompt = self._build_tasting_notes_prompt(wine)
        
        try:
            response = await self._call_ai(prompt, json_mode=True)
            notes = json.loads(response)
            logger.info(f"Generated tasting notes for: {wine.get('name', 'Unknown')}")
            return notes
        except Exception as e:
            logger.error(f"Error generating tasting notes: {e}")
            return {}
    
    async def suggest_food_pairings(self, wine: Dict) -> List[str]:
        """
        Suggest food pairings.
        
        Args:
            wine: Wine data
            
        Returns:
            List of food pairing suggestions
        """
        prompt = self._build_food_pairing_prompt(wine)
        
        try:
            response = await self._call_ai(prompt, json_mode=True)
            pairings = json.loads(response)
            
            if isinstance(pairings, dict) and 'pairings' in pairings:
                pairings = pairings['pairings']
            
            logger.info(f"Generated {len(pairings)} food pairings")
            return pairings[:7]  # Limit to 7
        except Exception as e:
            logger.error(f"Error generating food pairings: {e}")
            return []
    
    async def normalize_grape_varieties(self, grape_varieties: List[str]) -> List[str]:
        """
        Normalize grape variety names.
        
        Args:
            grape_varieties: List of grape variety names
            
        Returns:
            Normalized list
        """
        if not grape_varieties:
            return []
        
        prompt = f"""Normalize these grape variety names to standard format.
Remove duplicates and fix spelling errors.

Grape varieties: {', '.join(grape_varieties)}

Return as JSON array: ["Cabernet Sauvignon", "Merlot", ...]
"""
        
        try:
            response = await self._call_ai(prompt, json_mode=True)
            normalized = json.loads(response)
            
            if isinstance(normalized, dict) and 'varieties' in normalized:
                normalized = normalized['varieties']
            
            return normalized
        except Exception as e:
            logger.error(f"Error normalizing grape varieties: {e}")
            return grape_varieties
    
    async def _call_ai(self, prompt: str, json_mode: bool = False) -> str:
        """
        Call AI provider API.
        
        Args:
            prompt: Prompt text
            json_mode: Request JSON response
            
        Returns:
            AI response text
        """
        if self.provider == "openai":
            return await self._call_openai(prompt, json_mode)
        elif self.provider == "google":
            return await self._call_google(prompt, json_mode)
        elif self.provider == "anthropic":
            return await self._call_anthropic(prompt, json_mode)
        
        raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _call_openai(self, prompt: str, json_mode: bool = False) -> str:
        """Call OpenAI API"""
        messages = [{"role": "user", "content": prompt}]
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        
        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    async def _call_google(self, prompt: str, json_mode: bool = False) -> str:
        """Call Google AI API"""
        if json_mode:
            prompt += "\n\nRespond with valid JSON only."
        
        response = await self.client.generate_content_async(prompt)
        return response.text
    
    async def _call_anthropic(self, prompt: str, json_mode: bool = False) -> str:
        """Call Anthropic API"""
        if json_mode:
            prompt += "\n\nRespond with valid JSON only."
        
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    # Prompt building methods
    
    def _build_validation_prompt(self, wine: Dict) -> str:
        """Build validation prompt"""
        return f"""You are a wine data validation expert. Review this wine data and identify any issues.

Wine Data:
- Name: {wine.get('name', 'N/A')}
- Winery: {wine.get('winery', 'N/A')}
- Type: {wine.get('wine_type', 'N/A')}
- Region: {wine.get('region', 'N/A')}
- Country: {wine.get('country', 'N/A')}
- Alcohol: {wine.get('alcohol_content', 'N/A')}%
- Vintage: {wine.get('vintage', 'N/A')}
- Grape varieties: {', '.join(wine.get('grape_varieties', [])) or 'N/A'}

Tasks:
1. Identify any inconsistencies (e.g., wrong region for winery)
2. Flag missing critical information
3. Verify alcohol content is reasonable for wine type
4. Check if grape varieties match the region
5. Provide confidence score (0-100)

Return JSON:
{{
  "issues": ["list of issues found"],
  "confidence": 85,
  "recommendations": ["suggested fixes"]
}}"""
    
    def _build_description_prompt(self, wine: Dict) -> str:
        """Build description generation prompt"""
        return f"""Generate a concise, professional wine description (2-3 sentences) based on:

Wine: {wine.get('name', 'Unknown')}
Winery: {wine.get('winery', 'Unknown')}
Type: {wine.get('wine_type', 'Unknown')}
Region: {wine.get('region', 'Unknown')}
Country: {wine.get('country', 'Unknown')}
Grape Varieties: {', '.join(wine.get('grape_varieties', [])) or 'Unknown'}
Vintage: {wine.get('vintage', 'N/A')}

Style: Informative, elegant, avoid marketing fluff.
Focus on: origin, winemaking style, key characteristics.
Write in French if the wine is French, otherwise in English."""
    
    def _build_tasting_notes_prompt(self, wine: Dict) -> str:
        """Build tasting notes generation prompt"""
        return f"""Generate tasting notes for this wine:

Wine: {wine.get('name', 'Unknown')} {wine.get('vintage', '')}
Type: {wine.get('wine_type', 'Unknown')}
Region: {wine.get('region', 'Unknown')}
Grapes: {', '.join(wine.get('grape_varieties', [])) or 'Unknown'}
Alcohol: {wine.get('alcohol_content', 'Unknown')}%

Provide notes in JSON format:
{{
  "color": "color and clarity description",
  "nose": "aroma characteristics",
  "palate": "taste profile",
  "finish": "aftertaste description"
}}

Keep each section to 1-2 sentences. Be specific and avoid generic terms."""
    
    def _build_food_pairing_prompt(self, wine: Dict) -> str:
        """Build food pairing generation prompt"""
        return f"""Suggest 5-7 specific food pairings for:

Wine: {wine.get('name', 'Unknown')}
Type: {wine.get('wine_type', 'Unknown')}
Region: {wine.get('region', 'Unknown')}
Characteristics: {wine.get('description', 'N/A')}

Return as JSON:
{{
  "pairings": ["Specific dish 1", "Specific dish 2", ...]
}}

Focus on specific dishes, not generic categories.
Use French names for French wines, English for others."""


# Convenience function
async def enrich_wine(wine: Dict, provider: str = "openai") -> Dict:
    """
    Enrich a single wine.
    
    Args:
        wine: Wine data
        provider: AI provider
        
    Returns:
        Enriched wine data
    """
    agent = WineEnrichmentAgent(provider=provider)
    return await agent.enrich_wine_data(wine)
