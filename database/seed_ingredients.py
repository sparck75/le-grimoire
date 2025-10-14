"""
Seed data for ingredient categories and units
Run this after running the migration
"""

INGREDIENT_CATEGORIES = [
    {"name": "Produits Laitiers", "icon": "🥛", "order": 1},
    {"name": "Fromages", "icon": "🧀", "order": 2, "parent": "Produits Laitiers"},
    {"name": "Viandes", "icon": "🥩", "order": 3},
    {"name": "Viandes Hachées", "icon": "🥩", "order": 4, "parent": "Viandes"},
    {"name": "Légumes", "icon": "🥬", "order": 5},
    {"name": "Fruits", "icon": "🍎", "order": 6},
    {"name": "Fruits de Mer", "icon": "🦐", "order": 7},
    {"name": "Œufs", "icon": "🥚", "order": 8},
    {"name": "Noix et Graines", "icon": "🥜", "order": 9},
    {"name": "Condiments", "icon": "🍯", "order": 10},
    {"name": "Épices et Aromates", "icon": "🌶️", "order": 11},
    {"name": "Produits de Base", "icon": "🍚", "order": 12},
    {"name": "Farines et Féculents", "icon": "🌾", "order": 13, "parent": "Produits de Base"},
    {"name": "Sucres et Édulcorants", "icon": "🍯", "order": 14, "parent": "Produits de Base"},
    {"name": "Huiles et Matières Grasses", "icon": "🧈", "order": 15},
    {"name": "Pâtes et Produits de Boulangerie", "icon": "🥖", "order": 16},
    {"name": "Sirops", "icon": "🍯", "order": 17},
]

UNITS = [
    # Volume - Metric
    {"name": "millilitre", "abbr": "ml", "type": "volume", "system": "metric", "base": "ml", "conversion": 1.0},
    {"name": "litre", "abbr": "l", "type": "volume", "system": "metric", "base": "ml", "conversion": 1000.0},
    {"name": "centilitre", "abbr": "cl", "type": "volume", "system": "metric", "base": "ml", "conversion": 10.0},
    {"name": "décilitre", "abbr": "dl", "type": "volume", "system": "metric", "base": "ml", "conversion": 100.0},
    
    # Volume - Imperial/US
    {"name": "tasse", "abbr": "tasse", "type": "volume", "system": "imperial", "base": "ml", "conversion": 250.0},
    {"name": "cup", "abbr": "cup", "type": "volume", "system": "imperial", "base": "ml", "conversion": 236.588},
    {"name": "cuillère à soupe", "abbr": "c. à soupe", "type": "volume", "system": "imperial", "base": "ml", "conversion": 15.0},
    {"name": "tablespoon", "abbr": "tbsp", "type": "volume", "system": "imperial", "base": "ml", "conversion": 14.787},
    {"name": "cuillère à thé", "abbr": "c. à thé", "type": "volume", "system": "imperial", "base": "ml", "conversion": 5.0},
    {"name": "teaspoon", "abbr": "tsp", "type": "volume", "system": "imperial", "base": "ml", "conversion": 4.929},
    {"name": "cuillère à table", "abbr": "c. à table", "type": "volume", "system": "imperial", "base": "ml", "conversion": 15.0},
    {"name": "pinte", "abbr": "pinte", "type": "volume", "system": "imperial", "base": "ml", "conversion": 1136.5},
    {"name": "gallon", "abbr": "gal", "type": "volume", "system": "imperial", "base": "ml", "conversion": 3785.41},
    {"name": "once liquide", "abbr": "fl oz", "type": "volume", "system": "imperial", "base": "ml", "conversion": 29.574},
    
    # Weight - Metric
    {"name": "gramme", "abbr": "g", "type": "weight", "system": "metric", "base": "g", "conversion": 1.0},
    {"name": "kilogramme", "abbr": "kg", "type": "weight", "system": "metric", "base": "g", "conversion": 1000.0},
    {"name": "milligramme", "abbr": "mg", "type": "weight", "system": "metric", "base": "g", "conversion": 0.001},
    
    # Weight - Imperial
    {"name": "livre", "abbr": "lb", "type": "weight", "system": "imperial", "base": "g", "conversion": 453.592},
    {"name": "once", "abbr": "oz", "type": "weight", "system": "imperial", "base": "g", "conversion": 28.3495},
    
    # Unit/Count
    {"name": "unité", "abbr": "unité", "type": "unit", "system": "both", "base": None, "conversion": 1.0},
    {"name": "pièce", "abbr": "pièce", "type": "unit", "system": "both", "base": None, "conversion": 1.0},
    {"name": "portion", "abbr": "portion", "type": "unit", "system": "both", "base": None, "conversion": 1.0},
    {"name": "boîte", "abbr": "boîte", "type": "unit", "system": "both", "base": None, "conversion": 1.0},
    {"name": "paquet", "abbr": "paquet", "type": "unit", "system": "both", "base": None, "conversion": 1.0},
    {"name": "botte", "abbr": "botte", "type": "unit", "system": "both", "base": None, "conversion": 1.0},
    {"name": "pincée", "abbr": "pincée", "type": "unit", "system": "both", "base": None, "conversion": 1.0},
    
    # Temperature
    {"name": "Celsius", "abbr": "°C", "type": "temperature", "system": "metric", "base": "C", "conversion": 1.0},
    {"name": "Fahrenheit", "abbr": "°F", "type": "temperature", "system": "imperial", "base": "F", "conversion": 1.0},
]

INITIAL_INGREDIENTS = [
    # Dairy Products
    {"name": "lait", "category": "Produits Laitiers", "unit": "ml", "aliases": ["lait 2%", "lait entier"]},
    {"name": "beurre", "category": "Huiles et Matières Grasses", "unit": "g", "aliases": []},
    {"name": "margarine", "category": "Huiles et Matières Grasses", "unit": "g", "aliases": []},
    
    # Cheeses
    {"name": "brie", "category": "Fromages", "unit": "g", "aliases": []},
    {"name": "mozzarella", "category": "Fromages", "unit": "g", "aliases": ["mozzarella râpée"]},
    {"name": "cheddar", "category": "Fromages", "unit": "g", "aliases": ["cheddar doux", "cheddar râpé"]},
    
    # Meats
    {"name": "veau haché", "category": "Viandes Hachées", "unit": "g", "aliases": ["veau"]},
    {"name": "porc haché", "category": "Viandes Hachées", "unit": "g", "aliases": ["porc"]},
    
    # Vegetables
    {"name": "oignon", "category": "Légumes", "unit": "unité", "aliases": ["oignons"]},
    {"name": "échalote", "category": "Légumes", "unit": "unité", "aliases": ["échalotes"]},
    {"name": "céleri", "category": "Légumes", "unit": "g", "aliases": []},
    {"name": "piment vert", "category": "Légumes", "unit": "unité", "aliases": ["piment"]},
    {"name": "poivron vert", "category": "Légumes", "unit": "unité", "aliases": ["poivron"]},
    {"name": "piment rouge", "category": "Légumes", "unit": "unité", "aliases": []},
    {"name": "tomate verte", "category": "Légumes", "unit": "g", "aliases": ["tomates vertes"]},
    {"name": "épinard", "category": "Légumes", "unit": "g", "aliases": ["épinards", "épinards hachés"]},
    
    # Fruits
    {"name": "poire", "category": "Fruits", "unit": "unité", "aliases": ["poires"]},
    {"name": "pomme", "category": "Fruits", "unit": "unité", "aliases": ["pommes"]},
    
    # Seafood
    {"name": "crevette", "category": "Fruits de Mer", "unit": "g", "aliases": ["crevettes"]},
    {"name": "crabe", "category": "Fruits de Mer", "unit": "g", "aliases": []},
    {"name": "pétoncle", "category": "Fruits de Mer", "unit": "g", "aliases": ["pétoncles"]},
    
    # Eggs
    {"name": "œuf", "category": "Œufs", "unit": "unité", "aliases": ["œufs", "oeuf", "oeufs"]},
    
    # Nuts
    {"name": "pacane", "category": "Noix et Graines", "unit": "g", "aliases": ["pacanes"]},
    
    # Condiments
    {"name": "ketchup", "category": "Condiments", "unit": "ml", "aliases": []},
    {"name": "mayonnaise", "category": "Condiments", "unit": "ml", "aliases": []},
    {"name": "relish verte", "category": "Condiments", "unit": "ml", "aliases": ["relish"]},
    {"name": "sauce chili", "category": "Condiments", "unit": "ml", "aliases": []},
    {"name": "vinaigre", "category": "Condiments", "unit": "ml", "aliases": []},
    
    # Spices
    {"name": "sel", "category": "Épices et Aromates", "unit": "g", "aliases": ["gros sel"]},
    {"name": "poivre", "category": "Épices et Aromates", "unit": "g", "aliases": []},
    {"name": "épices à marinades", "category": "Épices et Aromates", "unit": "g", "aliases": []},
    
    # Basics
    {"name": "farine tout usage", "category": "Farines et Féculents", "unit": "g", "aliases": ["farine"]},
    {"name": "sucre", "category": "Sucres et Édulcorants", "unit": "g", "aliases": ["sucre blanc"]},
    
    # Syrups
    {"name": "sirop d'érable", "category": "Sirops", "unit": "ml", "aliases": []},
    
    # Bakery
    {"name": "baguette", "category": "Pâtes et Produits de Boulangerie", "unit": "unité", "aliases": []},
    {"name": "abaisse de pâte", "category": "Pâtes et Produits de Boulangerie", "unit": "unité", "aliases": ["abaisse", "pâte"]},
    {"name": "croûte à tarte", "category": "Pâtes et Produits de Boulangerie", "unit": "unité", "aliases": ["croûte"]},
]


def get_seed_sql():
    """Generate SQL insert statements for seeding"""
    sql_statements = []
    
    # Insert categories
    sql_statements.append("-- Insert ingredient categories")
    category_map = {}
    
    # First pass: insert parent categories
    for cat in INGREDIENT_CATEGORIES:
        if "parent" not in cat:
            sql_statements.append(
                f"INSERT INTO ingredient_categories (name, icon, display_order) "
                f"VALUES ('{cat['name']}', '{cat['icon']}', {cat['order']}) "
                f"ON CONFLICT (name) DO NOTHING;"
            )
    
    # Second pass: insert child categories
    for cat in INGREDIENT_CATEGORIES:
        if "parent" in cat:
            sql_statements.append(
                f"INSERT INTO ingredient_categories (name, icon, display_order, parent_category_id) "
                f"VALUES ('{cat['name']}', '{cat['icon']}', {cat['order']}, "
                f"(SELECT id FROM ingredient_categories WHERE name = '{cat['parent']}')) "
                f"ON CONFLICT (name) DO NOTHING;"
            )
    
    # Insert units
    sql_statements.append("\n-- Insert units")
    for unit in UNITS:
        base_unit = f"'{unit['base']}'" if unit['base'] else "NULL"
        sql_statements.append(
            f"INSERT INTO units (name, abbreviation, type, system, conversion_to_base, base_unit) "
            f"VALUES ('{unit['name']}', '{unit['abbr']}', '{unit['type']}', "
            f"'{unit['system']}', {unit['conversion']}, {base_unit}) "
            f"ON CONFLICT (name) DO NOTHING;"
        )
    
    # Insert ingredients
    sql_statements.append("\n-- Insert initial ingredients")
    for ing in INITIAL_INGREDIENTS:
        aliases_str = "ARRAY[" + ", ".join([f"'{alias}'" for alias in ing['aliases']]) + "]" if ing['aliases'] else "NULL"
        sql_statements.append(
            f"INSERT INTO ingredients (name, category_id, default_unit, aliases) "
            f"VALUES ('{ing['name']}', "
            f"(SELECT id FROM ingredient_categories WHERE name = '{ing['category']}'), "
            f"'{ing['unit']}', {aliases_str}) "
            f"ON CONFLICT (name) DO NOTHING;"
        )
    
    return "\n".join(sql_statements)


if __name__ == "__main__":
    print(get_seed_sql())
