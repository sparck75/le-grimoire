"""
Seed test data for CI/CD testing.

This script creates a clean dataset with:
- Test users (admin, collaborator, reader)
- Sample recipes with various properties
- Sample ingredients (if MongoDB is used)
- Sample categories

Usage:
    python -m scripts.seed_test_data
"""
import sys
import os
import asyncio
from datetime import datetime, UTC

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.core.database import SessionLocal, engine
from app.models.user import User, UserRole
from app.models.recipe import Recipe
import uuid

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test password for all users (NEVER use in production!)
TEST_PASSWORD = "Test123!@#"
TEST_PASSWORD_HASH = pwd_context.hash(TEST_PASSWORD)


def clear_existing_data(db: Session):
    """Clear all existing test data."""
    print("🗑️  Clearing existing data...")
    
    try:
        # Delete in correct order (respecting foreign keys)
        db.query(Recipe).delete()
        db.query(User).delete()
        db.commit()
        print("✅ Existing data cleared")
    except Exception as e:
        print(f"⚠️  Warning clearing data: {e}")
        db.rollback()


def create_test_users(db: Session):
    """Create test users with different roles."""
    print("\n👥 Creating test users...")
    
    users = [
        {
            "email": "admin@test.com",
            "username": "admin_test",
            "password_hash": TEST_PASSWORD_HASH,
            "role": "admin",
            "is_active": True,
            "name": "Test Admin"
        },
        {
            "email": "collab@test.com",
            "username": "collab_test",
            "password_hash": TEST_PASSWORD_HASH,
            "role": "collaborator",
            "is_active": True,
            "name": "Test Collaborator"
        },
        {
            "email": "reader@test.com",
            "username": "reader_test",
            "password_hash": TEST_PASSWORD_HASH,
            "role": "reader",
            "is_active": True,
            "name": "Test Reader"
        },
        {
            "email": "inactive@test.com",
            "username": "inactive_test",
            "password_hash": TEST_PASSWORD_HASH,
            "role": "reader",
            "is_active": False,
            "name": "Inactive User"
        }
    ]
    
    created_users = []
    for user_data in users:
        user = User(**user_data)
        db.add(user)
        created_users.append(user)
        print(f"   ✓ {user_data['username']} ({user_data['role']})")
    
    db.commit()
    print(f"✅ Created {len(created_users)} test users")
    print(f"   Password for all users: {TEST_PASSWORD}")
    
    return created_users


def create_test_recipes(db: Session, users: list):
    """Create diverse test recipes."""
    print("\n🍳 Creating test recipes...")
    
    admin_user = next(u for u in users if u.role == "admin")
    collab_user = next(u for u in users if u.role == "collaborator")
    
    recipes = [
        {
            "title": "Tomates Vertes Frites",
            "description": "Des tomates vertes panées et frites, croustillantes à l'extérieur et juteuses à l'intérieur.",
            "ingredients": [
                "4 tomates vertes de taille moyenne",
                "1 tasse de farine tout usage",
                "2 oeufs battus",
                "1 tasse de chapelure panko",
                "1/2 tasse de parmesan râpé",
                "1 c. à thé de sel",
                "1/2 c. à thé de poivre noir",
                "1/2 c. à thé de paprika",
                "Huile végétale pour la friture"
            ],
            "equipment": ["Poêle profonde", "Assiettes", "Bols pour panure"],
            "instructions": "1. Trancher les tomates en rondelles de 1/2 pouce\n2. Préparer 3 bols: farine, oeufs battus, et mélange panko-parmesan\n3. Assaisonner la farine avec sel, poivre et paprika\n4. Paner chaque tranche: farine, oeuf, puis chapelure\n5. Chauffer 1/2 pouce d'huile à feu moyen-élevé\n6. Frire 3-4 minutes par côté jusqu'à doré\n7. Égoutter sur papier absorbant\n8. Servir immédiatement",
            "servings": 4,
            "prep_time": 15,
            "cook_time": 20,
            "total_time": 35,
            "category": "Accompagnement",
            "cuisine": "Américaine du Sud",
            "difficulty_level": "Facile",
            "temperature": 375,
            "temperature_unit": "F",
            "notes": "Ne pas utiliser de tomates trop mûres. Les tomates vertes fermes fonctionnent mieux.",
            "user_id": admin_user.id,
            "is_public": True
        },
        {
            "title": "Pâtes à l'Ail et aux Crevettes",
            "description": "Des linguines avec des crevettes sautées à l'ail, citron et persil.",
            "ingredients": [
                "400g de linguines",
                "500g de crevettes décortiquées",
                "6 gousses d'ail hachées",
                "1/4 tasse d'huile d'olive extra vierge",
                "1 citron (jus et zeste)",
                "1/2 tasse de persil frais haché",
                "1/2 c. à thé de flocons de piment rouge",
                "Sel et poivre au goût",
                "1/4 tasse de vin blanc sec"
            ],
            "equipment": ["Grande casserole", "Poêle", "Râpe à zeste"],
            "instructions": "1. Cuire les pâtes selon les instructions de l'emballage\n2. Chauffer l'huile d'olive dans une grande poêle\n3. Faire revenir l'ail 1 minute jusqu'à parfumé\n4. Ajouter les crevettes, cuire 2-3 minutes par côté\n5. Ajouter le vin blanc, laisser réduire 2 minutes\n6. Ajouter le jus de citron, le zeste et les flocons de piment\n7. Mélanger les pâtes égouttées avec la sauce\n8. Ajouter le persil, saler et poivrer\n9. Servir immédiatement avec du parmesan",
            "servings": 4,
            "prep_time": 10,
            "cook_time": 15,
            "total_time": 25,
            "category": "Plat principal",
            "cuisine": "Italienne",
            "difficulty_level": "Facile",
            "notes": "Utiliser des crevettes fraîches pour un meilleur résultat.",
            "user_id": collab_user.id,
            "is_public": True
        },
        {
            "title": "Soupe Minestrone Classique",
            "description": "Soupe italienne traditionnelle aux légumes, haricots et pâtes.",
            "ingredients": [
                "2 c. à soupe d'huile d'olive",
                "1 oignon haché",
                "2 carottes en dés",
                "2 branches de céleri en dés",
                "3 gousses d'ail hachées",
                "1 boîte (796ml) de tomates en dés",
                "6 tasses de bouillon de légumes",
                "1 boîte de haricots blancs égouttés",
                "1 tasse de pâtes ditalini",
                "2 tasses d'épinards frais",
                "1 c. à thé de basilic séché",
                "1 c. à thé d'origan séché",
                "Sel et poivre",
                "Parmesan râpé pour servir"
            ],
            "equipment": ["Grande marmite", "Cuillère en bois", "Planche à découper"],
            "instructions": "1. Chauffer l'huile dans une grande marmite\n2. Faire revenir oignon, carottes et céleri 5 minutes\n3. Ajouter l'ail, cuire 1 minute\n4. Ajouter tomates, bouillon, haricots et épices\n5. Porter à ébullition, réduire et mijoter 20 minutes\n6. Ajouter les pâtes, cuire 8-10 minutes\n7. Ajouter les épinards, cuire 2 minutes jusqu'à flétris\n8. Ajuster l'assaisonnement\n9. Servir avec parmesan râpé",
            "servings": 6,
            "prep_time": 15,
            "cook_time": 35,
            "total_time": 50,
            "category": "Soupe",
            "cuisine": "Italienne",
            "difficulty_level": "Facile",
            "notes": "Peut être congelée jusqu'à 3 mois. Les pâtes peuvent devenir molles après congélation.",
            "user_id": admin_user.id,
            "is_public": True
        },
        {
            "title": "Poulet au Beurre (Butter Chicken)",
            "description": "Poulet indien crémeux dans une sauce tomate épicée et beurrée.",
            "ingredients": [
                "1kg de poitrines de poulet en cubes",
                "1 tasse de yogourt nature",
                "2 c. à soupe de jus de citron",
                "2 c. à thé de garam masala",
                "1 c. à thé de curcuma",
                "1 c. à thé de cumin",
                "1 c. à thé de coriandre moulue",
                "4 c. à soupe de beurre",
                "1 oignon haché",
                "4 gousses d'ail hachées",
                "1 c. à soupe de gingembre râpé",
                "1 boîte (796ml) de purée de tomates",
                "1 tasse de crème 35%",
                "2 c. à thé de paprika",
                "1 c. à thé de sel",
                "Coriandre fraîche pour garnir"
            ],
            "equipment": ["Bol pour marinade", "Grande poêle ou wok", "Gril ou four"],
            "instructions": "1. Mariner le poulet avec yogourt, citron et épices 30 minutes\n2. Griller le poulet mariné jusqu'à cuit (ou au four 400°F, 20 min)\n3. Dans une poêle, faire fondre le beurre\n4. Faire revenir oignon, ail et gingembre 5 minutes\n5. Ajouter paprika, garam masala, cumin, coriandre\n6. Ajouter la purée de tomates, mijoter 10 minutes\n7. Ajouter la crème et le poulet grillé\n8. Mijoter 10 minutes pour épaissir\n9. Garnir de coriandre, servir avec riz basmati et naan",
            "servings": 6,
            "prep_time": 45,
            "cook_time": 35,
            "total_time": 80,
            "category": "Plat principal",
            "cuisine": "Indienne",
            "difficulty_level": "Moyen",
            "temperature": 400,
            "temperature_unit": "F",
            "notes": "La marinade peut être faite la veille pour plus de saveur.",
            "user_id": collab_user.id,
            "is_public": True
        },
        {
            "title": "Saumon Grillé au Sirop d'Érable",
            "description": "Filets de saumon glacés avec un mélange de sirop d'érable et moutarde de Dijon.",
            "ingredients": [
                "4 filets de saumon (environ 170g chacun)",
                "1/4 tasse de sirop d'érable pur",
                "2 c. à soupe de moutarde de Dijon",
                "2 gousses d'ail hachées",
                "1 c. à soupe de sauce soya",
                "1 c. à thé de gingembre râpé",
                "Sel et poivre noir",
                "1 c. à soupe d'huile d'olive",
                "Graines de sésame pour garnir",
                "Oignons verts tranchés"
            ],
            "equipment": ["Plaque de cuisson", "Pinceau à badigeonner", "Papier parchemin"],
            "instructions": "1. Préchauffer le four à 400°F (200°C)\n2. Tapisser une plaque de papier parchemin\n3. Dans un bol, mélanger sirop d'érable, moutarde, ail, sauce soya et gingembre\n4. Placer les filets de saumon sur la plaque\n5. Badigeonner généreusement avec le mélange d'érable\n6. Saler et poivrer\n7. Cuire 12-15 minutes jusqu'à ce que le saumon soit cuit\n8. Badigeonner à nouveau à mi-cuisson\n9. Garnir de graines de sésame et oignons verts\n10. Servir avec légumes grillés et riz",
            "servings": 4,
            "prep_time": 10,
            "cook_time": 15,
            "total_time": 25,
            "category": "Plat principal",
            "cuisine": "Canadienne",
            "difficulty_level": "Facile",
            "temperature": 400,
            "temperature_unit": "F",
            "notes": "Ne pas trop cuire le saumon - il doit être légèrement rosé au centre.",
            "user_id": admin_user.id,
            "is_public": True
        },
        {
            "title": "Brownies au Chocolat Fondant",
            "description": "Brownies riches et fudgy avec une texture fondante au centre.",
            "ingredients": [
                "1 tasse (225g) de beurre",
                "2 tasses (400g) de sucre",
                "4 gros oeufs",
                "1 1/2 tasse (130g) de poudre de cacao non sucrée",
                "1 tasse (125g) de farine tout usage",
                "1 c. à thé de sel",
                "1 c. à thé d'extrait de vanille",
                "1 tasse de pépites de chocolat (optionnel)"
            ],
            "equipment": ["Moule 9x13 pouces", "Bols à mélanger", "Fouet", "Spatule"],
            "instructions": "1. Préchauffer le four à 350°F (175°C)\n2. Graisser un moule 9x13 pouces\n3. Faire fondre le beurre dans une casserole\n4. Retirer du feu, ajouter le sucre et bien mélanger\n5. Incorporer les oeufs un à la fois\n6. Ajouter la vanille\n7. Tamiser le cacao et la farine, ajouter le sel\n8. Incorporer les ingrédients secs au mélange humide\n9. Ajouter les pépites de chocolat si désiré\n10. Verser dans le moule\n11. Cuire 25-30 minutes (un cure-dent doit ressortir avec des miettes humides)\n12. Laisser refroidir complètement avant de couper",
            "servings": 16,
            "prep_time": 15,
            "cook_time": 30,
            "total_time": 45,
            "category": "Dessert",
            "cuisine": "Américaine",
            "difficulty_level": "Facile",
            "temperature": 350,
            "temperature_unit": "F",
            "notes": "Ne pas trop cuire pour garder la texture fondante. Les brownies durcissent en refroidissant.",
            "user_id": collab_user.id,
            "is_public": True
        },
        {
            "title": "Recette Privée - Test",
            "description": "Cette recette est privée et ne devrait pas apparaître dans les recherches publiques.",
            "ingredients": [
                "Ingrédient secret 1",
                "Ingrédient secret 2"
            ],
            "instructions": "Instructions secrètes",
            "servings": 1,
            "prep_time": 5,
            "cook_time": 5,
            "total_time": 10,
            "category": "Test",
            "cuisine": "Test",
            "difficulty_level": "Facile",
            "user_id": admin_user.id,
            "is_public": False
        },
        {
            "title": "Salade César Classique",
            "description": "Salade César avec croûtons maison et vinaigrette crémeuse.",
            "ingredients": [
                "2 têtes de laitue romaine",
                "1 tasse de parmesan râpé",
                "2 tasses de croûtons",
                "Pour la vinaigrette:",
                "3 gousses d'ail",
                "2 filets d'anchois",
                "2 jaunes d'oeufs",
                "2 c. à soupe de jus de citron",
                "1 c. à thé de moutarde de Dijon",
                "1/2 tasse d'huile d'olive",
                "1/4 tasse de parmesan râpé",
                "Sel et poivre"
            ],
            "equipment": ["Mélangeur ou robot culinaire", "Grand bol à salade", "Fouet"],
            "instructions": "1. Laver et essorer la laitue, déchirer en morceaux\n2. Pour la vinaigrette: mixer ail, anchois, jaunes d'oeufs, citron, moutarde\n3. Ajouter l'huile en filet en mélangeant jusqu'à émulsion\n4. Incorporer le parmesan, saler et poivrer\n5. Dans un grand bol, mélanger laitue et vinaigrette\n6. Ajouter les croûtons et le parmesan\n7. Servir immédiatement",
            "servings": 4,
            "prep_time": 20,
            "cook_time": 0,
            "total_time": 20,
            "category": "Salade",
            "cuisine": "Américaine",
            "difficulty_level": "Moyen",
            "notes": "Pour des croûtons maison: cubes de pain avec huile d'olive, ail et parmesan, au four 375°F 10 minutes.",
            "user_id": admin_user.id,
            "is_public": True
        }
    ]
    
    created_recipes = []
    for recipe_data in recipes:
        recipe = Recipe(
            id=uuid.uuid4(),
            **recipe_data
        )
        db.add(recipe)
        created_recipes.append(recipe)
        visibility = "🔒 Privée" if not recipe_data.get("is_public") else "🌍 Publique"
        print(f"   ✓ {recipe_data['title']} - {visibility}")
    
    db.commit()
    print(f"✅ Created {len(created_recipes)} test recipes")
    
    return created_recipes


async def seed_mongodb_ingredients():
    """Seed MongoDB with test ingredients (if MongoDB is configured)."""
    print("\n🥕 Seeding MongoDB ingredients...")
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from app.models.mongodb.ingredient import Ingredient
        from beanie import init_beanie
        import os
        
        # Connect to MongoDB
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        client = AsyncIOMotorClient(mongodb_url)
        database = client.le_grimoire
        
        # Initialize Beanie
        await init_beanie(database=database, document_models=[Ingredient])
        
        # Check if ingredients already exist
        count = await Ingredient.count()
        if count > 0:
            print(f"   ℹ️  MongoDB already has {count} ingredients, skipping seed")
            return
        
        # Sample ingredients for testing
        test_ingredients = [
            {
                "off_id": "en:tomato",
                "names": {"en": "Tomato", "fr": "Tomate", "es": "Tomate"},
                "properties": {"vegan": "yes", "vegetarian": "yes"},
                "custom": False
            },
            {
                "off_id": "en:garlic",
                "names": {"en": "Garlic", "fr": "Ail", "es": "Ajo"},
                "properties": {"vegan": "yes", "vegetarian": "yes"},
                "custom": False
            },
            {
                "off_id": "en:olive-oil",
                "names": {"en": "Olive oil", "fr": "Huile d'olive", "es": "Aceite de oliva"},
                "properties": {"vegan": "yes", "vegetarian": "yes"},
                "custom": False
            },
            {
                "off_id": "en:chicken",
                "names": {"en": "Chicken", "fr": "Poulet", "es": "Pollo"},
                "properties": {"vegan": "no", "vegetarian": "no"},
                "custom": False
            },
            {
                "off_id": "en:shrimp",
                "names": {"en": "Shrimp", "fr": "Crevette", "es": "Camarón"},
                "properties": {"vegan": "no", "vegetarian": "no"},
                "custom": False
            }
        ]
        
        for ing_data in test_ingredients:
            ingredient = Ingredient(**ing_data)
            await ingredient.insert()
            print(f"   ✓ {ing_data['names']['en']}")
        
        print(f"✅ Created {len(test_ingredients)} test ingredients in MongoDB")
        
    except ImportError:
        print("   ⚠️  MongoDB dependencies not available, skipping")
    except Exception as e:
        print(f"   ⚠️  Could not seed MongoDB: {e}")


def main():
    """Main function to seed all test data."""
    print("=" * 60)
    print("🌱 SEEDING TEST DATA FOR CI/CD")
    print("=" * 60)
    
    # PostgreSQL data
    db = SessionLocal()
    try:
        # Clear existing data
        clear_existing_data(db)
        
        # Create test data
        users = create_test_users(db)
        recipes = create_test_recipes(db, users)
        
        print("\n" + "=" * 60)
        print("✅ POSTGRESQL DATA SEEDED SUCCESSFULLY")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   • Users: {len(users)}")
        print(f"   • Recipes: {len(recipes)}")
        print(f"\n🔑 Test Credentials:")
        print(f"   • Admin: admin@test.com / {TEST_PASSWORD}")
        print(f"   • Collaborator: collab@test.com / {TEST_PASSWORD}")
        print(f"   • Reader: reader@test.com / {TEST_PASSWORD}")
        
    except Exception as e:
        print(f"\n❌ Error seeding PostgreSQL data: {e}")
        db.rollback()
        raise
    finally:
        db.close()
    
    # MongoDB data (async)
    try:
        asyncio.run(seed_mongodb_ingredients())
    except Exception as e:
        print(f"\n⚠️  MongoDB seeding skipped or failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 ALL TEST DATA SEEDED")
    print("=" * 60)


if __name__ == "__main__":
    main()
