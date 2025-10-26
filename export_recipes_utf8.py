#!/usr/bin/env python3
"""Export recipes with proper UTF-8 encoding"""
import json
import requests

def export_recipes():
    """Fetch and export all recipes with proper UTF-8 encoding"""
    all_recipes = []
    skip = 0
    limit = 100
    
    while True:
        response = requests.get(
            f"http://localhost:8000/api/v2/recipes/",
            params={"limit": limit, "skip": skip}
        )
        response.encoding = 'utf-8'
        recipes = response.json()
        
        if not recipes:
            break
            
        all_recipes.extend(recipes)
        
        if len(recipes) < limit:
            break
            
        skip += limit
    
    # Write with proper UTF-8 encoding
    with open("recipes_export_proper_utf8.json", "w", encoding="utf-8") as f:
        json.dump(all_recipes, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Exported {len(all_recipes)} recipes to recipes_export_proper_utf8.json")
    
    # Also create a readable summary
    with open("recipes_summary_utf8.txt", "w", encoding="utf-8") as f:
        f.write(f"=== RECIPES DATABASE EXPORT ===\n")
        f.write(f"Total Recipes: {len(all_recipes)}\n\n")
        
        for recipe in all_recipes:
            f.write(f"{'='*60}\n")
            f.write(f"Titre: {recipe['title']}\n")
            f.write(f"ID: {recipe['id']}\n")
            f.write(f"Description: {recipe.get('description', 'N/A')}\n")
            f.write(f"Catégorie: {recipe.get('category', 'N/A')}\n")
            f.write(f"Cuisine: {recipe.get('cuisine', 'N/A')}\n")
            f.write(f"Portions: {recipe.get('servings', 'N/A')}\n")
            f.write(f"Temps de préparation: {recipe.get('prep_time', 'N/A')} min\n")
            f.write(f"Temps de cuisson: {recipe.get('cook_time', 'N/A')} min\n")
            f.write(f"\nIngrédients ({len(recipe.get('ingredients', []))}):\n")
            for ing in recipe.get('ingredients', []):
                f.write(f"  • {ing}\n")
            f.write(f"\nInstructions:\n{recipe.get('instructions', 'N/A')}\n\n")
    
    print(f"✓ Created readable summary in recipes_summary_utf8.txt")

if __name__ == "__main__":
    export_recipes()
