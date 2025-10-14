import sys
import os
import uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.database import SessionLocal
from app.models.recipe import Recipe

db = SessionLocal()
try:
    print('Adding 5 recipes...')
    
    # Recipe 1
    r1 = Recipe(
        id=uuid.uuid4(),
        title='Ailes de Poulet à l Asiatique',
        description='Délicieuses ailes marinées sauce asiatique',
        servings=4,
        prep_time=15,
        cook_time=40,
        total_time=55,
        category='Plat principal',
        cuisine='Asiatique',
        ingredients=['2 lb ailes de poulet', '1/4 tasse sauce soya', '2 c. soupe miel', '1 c. soupe huile sésame', '3 gousses ail hachées', '1 c. soupe gingembre râpé', 'graines sésame', 'oignons verts'],
        instructions='1. Préchauffer four 375F\\n2. Mélanger sauce\\n3. Mariner ailes\\n4. Cuire 40 min\\n5. Garnir et servir',
        is_public=True
    )
    db.add(r1)
    
    # Recipe 2
    r2 = Recipe(
        id=uuid.uuid4(),
        title='Crevettes à l Ail et Citron',
        description='Crevettes sautées ail citron persil',
        servings=4,
        prep_time=10,
        cook_time=8,
        total_time=18,
        category='Plat principal',
        cuisine='Méditerranéenne',
        ingredients=['1.5 lb crevettes', '3 c. soupe huile olive', '4 gousses ail', '2 citrons', '1/4 tasse persil', 'sel', 'poivre'],
        instructions='1. Chauffer huile\\n2. Faire revenir ail\\n3. Cuire crevettes 2-3 min\\n4. Ajouter citron\\n5. Ajouter persil\\n6. Servir',
        is_public=True
    )
    db.add(r2)
    
    # Recipe 3
    r3 = Recipe(
        id=uuid.uuid4(),
        title='Soupe Minestrone',
        description='Soupe italienne légumes haricots',
        servings=6,
        prep_time=20,
        cook_time=45,
        total_time=65,
        category='Soupe',
        cuisine='Italienne',
        ingredients=['2 c. soupe huile olive', '1 oignon', '2 carottes', '2 céleri', '3 gousses ail', '1 boite tomates', '4 tasses bouillon', 'haricots blancs', 'pâtes', 'épinards', 'basilic', 'origan', 'parmesan'],
        instructions='1. Faire revenir légumes\\n2. Ajouter ail\\n3. Ajouter tomates bouillon haricots pâtes\\n4. Mijoter 30 min\\n5. Ajouter épinards\\n6. Servir avec parmesan',
        is_public=True
    )
    db.add(r3)
    
    # Recipe 4
    r4 = Recipe(
        id=uuid.uuid4(),
        title='Poulet au Beurre',
        description='Butter chicken indien crémeux épicé',
        servings=6,
        prep_time=30,
        cook_time=30,
        total_time=60,
        category='Plat principal',
        cuisine='Indienne',
        ingredients=['1.5 lb poulet cubes', '1 tasse yogourt', '4 c. soupe beurre', '1 oignon', '4 gousses ail', '1 c. soupe gingembre', '1 boite tomates', '1 tasse crème', 'garam masala', 'cumin', 'coriandre', 'paprika', 'sel'],
        instructions='1. Mariner poulet yaourt épices\\n2. Griller poulet\\n3. Faire revenir oignon ail\\n4. Ajouter épices\\n5. Ajouter tomates mijoter\\n6. Ajouter crème et poulet\\n7. Servir avec riz',
        is_public=True
    )
    db.add(r4)
    
    # Recipe 5
    r5 = Recipe(
        id=uuid.uuid4(),
        title='Saumon Grillé à l Érable',
        description='Saumon glacé sirop érable moutarde Dijon',
        servings=4,
        prep_time=10,
        cook_time=15,
        total_time=25,
        category='Plat principal',
        cuisine='Canadienne',
        ingredients=['4 filets saumon', '1/4 tasse sirop érable', '2 c. soupe moutarde Dijon', '2 gousses ail', '1 c. soupe sauce soya', 'sel', 'poivre'],
        instructions='1. Préchauffer four 400F\\n2. Mélanger sirop moutarde ail soya\\n3. Badigeonner saumon\\n4. Cuire 12-15 min\\n5. Servir avec légumes',
        is_public=True
    )
    db.add(r5)
    
    db.commit()
    print(' 5 recipes added successfully!')
except Exception as e:
    print(f' Error: {e}')
    db.rollback()
finally:
    db.close()
