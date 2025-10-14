"""
Convert legacy recipes to structured format
Migrates recipes from text array ingredients to recipe_ingredients table
"""
import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal, init_mongodb
from app.models.recipe import Recipe
from app.models.ingredient import RecipeIngredient
from app.models.mongodb.ingredient import Ingredient
from app.services.ingredient_matcher import ingredient_matcher


async def convert_recipe(recipe: Recipe, db):
    """Convert a single recipe to structured format"""
    print(f"\n{'='*80}")
    print(f"Converting: {recipe.title}")
    print(f"{'='*80}")
    
    if not recipe.ingredients:
        print("  ⚠️  No ingredients to convert")
        return
    
    # Check if already converted
    existing = db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id == recipe.id
    ).first()
    
    if existing:
        print("  ⚠️  Already converted (has structured ingredients)")
        return
    
    print(f"  📝 Converting {len(recipe.ingredients)} ingredients...")
    
    # Match each ingredient
    matched = await ingredient_matcher.match_ingredients(recipe.ingredients, language='fr')
    
    # Create recipe_ingredients entries
    for idx, match in enumerate(matched):
        print(f"\n  {idx + 1}. '{match['original_text']}'")
        
        # Show parsed quantity/unit
        if match['quantity'] is not None:
            qty_str = f"{match['quantity']}"
            if match['quantity_max']:
                qty_str += f"-{match['quantity_max']}"
            if match['unit']:
                qty_str += f" {match['unit']}"
            print(f"     📊 Quantity: {qty_str}")
        
        if match['matched_ingredient']:
            ing = match['matched_ingredient']
            print(f"     ✅ Matched: {ing.names.get('fr', ing.names.get('en', 'N/A'))}")
            print(f"        OFF ID: {ing.off_id}")
        else:
            print(f"     ❌ No match found")
        
        # Create recipe_ingredient entry
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_off_id=match['off_id'],
            quantity=match['quantity'],
            quantity_max=match['quantity_max'],
            unit=match['unit'],
            preparation_notes=match['original_text'],  # Keep full text
            display_order=idx + 1,
            is_optional=False
        )
        
        db.add(recipe_ingredient)
    
    db.commit()
    print(f"\n  ✅ Converted successfully!")


async def main():
    """Main conversion function"""
    print("="*80)
    print("LEGACY RECIPE CONVERTER")
    print("="*80)
    print("\nThis script converts recipes from legacy format (text array)")
    print("to structured format (recipe_ingredients table)\n")
    
    # Initialize MongoDB
    await init_mongodb()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Find all recipes with legacy ingredients
        recipes = db.query(Recipe).filter(
            Recipe.ingredients.isnot(None)
        ).all()
        
        print(f"Found {len(recipes)} recipes with legacy ingredients\n")
        
        if not recipes:
            print("No recipes to convert!")
            return
        
        # Convert each recipe
        for recipe in recipes:
            await convert_recipe(recipe, db)
        
        print("\n" + "="*80)
        print("CONVERSION COMPLETE")
        print("="*80)
        print(f"\nConverted {len(recipes)} recipes to structured format")
        print("\nYou can now view them in the admin interface with proper ingredient matching!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
