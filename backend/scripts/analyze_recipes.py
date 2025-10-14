"""
Script to analyze recipes from Word documents and extract ingredients
"""
import os
import re
from pathlib import Path

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("python-docx not available. Install it with: pip install python-docx")

def extract_text_from_docx(file_path):
    """Extract all text from a Word document"""
    if not DOCX_AVAILABLE:
        return None
    
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def analyze_recipe_structure(text, filename):
    """Analyze the structure of a recipe"""
    print(f"\n{'='*80}")
    print(f"RECIPE: {filename}")
    print(f"{'='*80}")
    
    # Look for common recipe sections
    sections = {
        'ingredients': [],
        'instructions': [],
        'title': filename.replace('.docx', ''),
        'servings': None,
        'time': None
    }
    
    # Split by lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    current_section = None
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Detect section headers
        if any(keyword in line_lower for keyword in ['ingrédient', 'ingredient']):
            current_section = 'ingredients'
            print(f"\n📝 INGREDIENTS SECTION FOUND at line {i}")
            continue
        elif any(keyword in line_lower for keyword in ['préparation', 'instruction', 'méthode', 'étape']):
            current_section = 'instructions'
            print(f"\n👨‍🍳 INSTRUCTIONS SECTION FOUND at line {i}")
            continue
        
        # Extract portions/servings
        if any(keyword in line_lower for keyword in ['portion', 'serving', 'personne']):
            sections['servings'] = line
            print(f"👥 Servings: {line}")
        
        # Collect content based on current section
        if current_section == 'ingredients' and line:
            sections['ingredients'].append(line)
        elif current_section == 'instructions' and line:
            sections['instructions'].append(line)
    
    # Print findings
    print(f"\n📋 INGREDIENTS ({len(sections['ingredients'])} items):")
    for ing in sections['ingredients'][:10]:  # Show first 10
        print(f"  - {ing}")
    if len(sections['ingredients']) > 10:
        print(f"  ... and {len(sections['ingredients']) - 10} more")
    
    print(f"\n📖 INSTRUCTIONS ({len(sections['instructions'])} steps):")
    for inst in sections['instructions'][:3]:  # Show first 3
        print(f"  {inst[:100]}...")
    
    return sections

def main():
    """Main function to analyze all recipes"""
    # Check multiple possible paths
    possible_paths = [
        Path(__file__).parent.parent.parent / 'recettes',
        Path('/app/recettes'),
        Path('recettes')
    ]
    
    recipes_dir = None
    for path in possible_paths:
        if path.exists():
            recipes_dir = path
            break
    
    if not recipes_dir:
        recipes_dir = Path(__file__).parent.parent.parent / 'recettes'
    
    if not recipes_dir.exists():
        print(f"Recipes directory not found: {recipes_dir}")
        return
    
    print(f"Analyzing recipes in: {recipes_dir}")
    print(f"DOCX support available: {DOCX_AVAILABLE}")
    
    # Get all .docx files
    recipe_files = list(recipes_dir.glob('*.docx'))
    
    if not recipe_files:
        print("No .docx files found in recipes directory")
        return
    
    print(f"\nFound {len(recipe_files)} recipe files")
    
    all_recipes = []
    all_ingredients = set()
    
    for recipe_file in recipe_files:
        if DOCX_AVAILABLE:
            text = extract_text_from_docx(recipe_file)
            if text:
                sections = analyze_recipe_structure(text, recipe_file.name)
                all_recipes.append(sections)
                
                # Collect unique ingredients
                for ing in sections['ingredients']:
                    # Extract just the ingredient name (before quantity/measurement)
                    all_ingredients.add(ing)
        else:
            print(f"\nFile: {recipe_file.name}")
            print("  (Cannot read - python-docx not installed)")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total recipes analyzed: {len(all_recipes)}")
    print(f"Unique ingredient lines: {len(all_ingredients)}")
    
    # Show sample ingredients
    if all_ingredients:
        print(f"\nSample ingredient lines:")
        for ing in list(all_ingredients)[:20]:
            print(f"  - {ing}")

if __name__ == "__main__":
    main()
