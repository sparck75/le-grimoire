"""
Script to reload recipes from recettes folder
Deletes current recipes and loads recipes from .docx files
"""
import os
import sys
from pathlib import Path
from docx import Document
import re
from sqlalchemy.orm import Session

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.recipe import Recipe

def extract_recipe_from_docx(file_path: str) -> dict:
    """Extract recipe information from a .docx file"""
    doc = Document(file_path)
    
    # Initialize recipe data
    recipe_data = {
        'title': Path(file_path).stem,  # Use filename as default title
        'description': '',
        'ingredients': [],
        'instructions': '',
        'servings': None,
        'prep_time': None,
        'cook_time': None,
        'total_time': None,
        'category': 'Plat principal',
        'cuisine': 'Autre',
        'difficulty': 'Moyenne',
        'is_public': True
    }
    
    # Extract all text from document
    full_text = []
    current_section = None
    ingredients_section = []
    instructions_section = []
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        full_text.append(text)
        
        # Detect title (usually first non-empty paragraph or largest text)
        if not recipe_data['description'] and len(full_text) == 1:
            recipe_data['title'] = text
            continue
        
        # Detect sections
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['ingrédient', 'ingredient']):
            current_section = 'ingredients'
            continue
        elif any(keyword in text_lower for keyword in ['préparation', 'preparation', 'instruction', 'étape', 'methode', 'méthode']):
            current_section = 'instructions'
            continue
        elif any(keyword in text_lower for keyword in ['portion', 'serving', 'rendement', 'donne']):
            # Try to extract servings
            numbers = re.findall(r'\d+', text)
            if numbers:
                recipe_data['servings'] = int(numbers[0])
            continue
        elif any(keyword in text_lower for keyword in ['temps', 'durée', 'duree', 'cuisson', 'préparation']):
            # Try to extract time
            numbers = re.findall(r'\d+', text)
            if numbers and 'cuisson' in text_lower:
                recipe_data['cook_time'] = int(numbers[0])
            elif numbers and 'préparation' in text_lower:
                recipe_data['prep_time'] = int(numbers[0])
            elif numbers:
                recipe_data['total_time'] = int(numbers[0])
            continue
        
        # Add to appropriate section
        if current_section == 'ingredients':
            # Clean and add ingredient
            if text and not any(keyword in text_lower for keyword in ['ingrédient', 'ingredient']):
                ingredients_section.append(text)
        elif current_section == 'instructions':
            # Clean and add instruction
            if text and not any(keyword in text_lower for keyword in ['préparation', 'preparation', 'instruction']):
                instructions_section.append(text)
        elif not recipe_data['description'] and len(text) > 20:
            # Use first substantial paragraph as description
            recipe_data['description'] = text
    
    # Format ingredients and instructions
    recipe_data['ingredients'] = ingredients_section if ingredients_section else ['Ingrédients à définir']
    recipe_data['instructions'] = '\n'.join(instructions_section) if instructions_section else 'Instructions à définir'
    
    # Calculate total time if not set
    if not recipe_data['total_time'] and (recipe_data['prep_time'] or recipe_data['cook_time']):
        recipe_data['total_time'] = (recipe_data['prep_time'] or 0) + (recipe_data['cook_time'] or 0)
    
    # Set default description if empty
    if not recipe_data['description']:
        recipe_data['description'] = f"Délicieuse recette de {recipe_data['title']}"
    
    # Determine category and cuisine from title
    title_lower = recipe_data['title'].lower()
    
    if any(word in title_lower for word in ['brie', 'fromage', 'quiche', 'oeufs', 'œufs']):
        recipe_data['category'] = 'Entrée'
    elif any(word in title_lower for word in ['dessert', 'gâteau', 'tarte', 'poire']):
        recipe_data['category'] = 'Dessert'
    elif any(word in title_lower for word in ['soupe', 'potage']):
        recipe_data['category'] = 'Soupe'
    elif any(word in title_lower for word in ['pâté', 'mexicain']):
        recipe_data['category'] = 'Plat principal'
    elif any(word in title_lower for word in ['relish', 'sauce', 'condiment']):
        recipe_data['category'] = 'Accompagnement'
    
    if any(word in title_lower for word in ['mexicain', 'mexico']):
        recipe_data['cuisine'] = 'Mexicaine'
    elif any(word in title_lower for word in ['florentin', 'italien']):
        recipe_data['cuisine'] = 'Italienne'
    elif any(word in title_lower for word in ['français', 'francais', 'brie', 'quiche']):
        recipe_data['cuisine'] = 'Française'
    
    return recipe_data

def delete_all_recipes(db: Session):
    """Delete all recipes from the database"""
    count = db.query(Recipe).delete()
    db.commit()
    print(f"✓ Deleted {count} existing recipes")
    return count

def load_recipes_from_folder(db: Session, folder_path: str):
    """Load all recipes from .docx files in the specified folder"""
    recettes_path = Path(folder_path)
    
    if not recettes_path.exists():
        print(f"Error: Folder {folder_path} does not exist")
        return
    
    docx_files = list(recettes_path.glob('*.docx'))
    
    if not docx_files:
        print(f"No .docx files found in {folder_path}")
        return
    
    print(f"\nFound {len(docx_files)} recipe files")
    print("=" * 60)
    
    loaded_count = 0
    for docx_file in docx_files:
        try:
            print(f"\nProcessing: {docx_file.name}")
            
            # Extract recipe data
            recipe_data = extract_recipe_from_docx(str(docx_file))
            
            # Create recipe in database
            recipe = Recipe(
                title=recipe_data['title'],
                description=recipe_data['description'],
                ingredients=recipe_data['ingredients'],
                instructions=recipe_data['instructions'],
                servings=recipe_data['servings'],
                prep_time=recipe_data['prep_time'],
                cook_time=recipe_data['cook_time'],
                total_time=recipe_data['total_time'],
                category=recipe_data['category'],
                cuisine=recipe_data['cuisine'],
                is_public=recipe_data['is_public']
            )
            
            db.add(recipe)
            db.commit()
            db.refresh(recipe)
            
            print(f"  ✓ Loaded: {recipe.title}")
            print(f"    - Category: {recipe.category}")
            print(f"    - Cuisine: {recipe.cuisine}")
            print(f"    - Ingredients: {len(recipe.ingredients)} items")
            print(f"    - Servings: {recipe.servings or 'N/A'}")
            print(f"    - Time: {recipe.total_time or 'N/A'} min")
            
            loaded_count += 1
            
        except Exception as e:
            print(f"  ✗ Error loading {docx_file.name}: {str(e)}")
            db.rollback()
    
    print("\n" + "=" * 60)
    print(f"Successfully loaded {loaded_count} out of {len(docx_files)} recipes")

def main():
    """Main function to reload recipes"""
    print("=" * 60)
    print("RECIPE RELOAD SCRIPT")
    print("=" * 60)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Delete all existing recipes
        print("\nStep 1: Deleting existing recipes...")
        delete_all_recipes(db)
        
        # Load recipes from recettes folder
        print("\nStep 2: Loading recipes from recettes folder...")
        # Use local recettes folder in /app
        recettes_folder = Path('/app/recettes')
        load_recipes_from_folder(db, str(recettes_folder))
        
        print("\n" + "=" * 60)
        print("RELOAD COMPLETE!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
