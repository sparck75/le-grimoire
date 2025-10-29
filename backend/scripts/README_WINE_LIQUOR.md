# Wine & Liquor Database Import Scripts

Scripts pour importer et gérer la base de données de vins et spiritueux dans MongoDB.

## Scripts disponibles

### `import_wines.py`
Importe des vins depuis des fichiers JSON/CSV ou permet l'ajout manuel.

### `import_liquors.py`
Importe des spiritueux depuis des fichiers JSON/CSV ou permet l'ajout manuel.

### `sample_wines.json`
Fichier d'exemple contenant 5 vins français classiques.

### `sample_liquors.json`
Fichier d'exemple contenant 6 spiritueux populaires.

## Installation des dépendances

```bash
pip install pymongo
```

## Utilisation

### Import de vins

#### Depuis le fichier d'exemple
```bash
python import_wines.py --file sample_wines.json
```

#### Depuis votre propre fichier JSON
```bash
python import_wines.py --file /path/to/your/wines.json
```

#### Depuis un fichier CSV
```bash
python import_wines.py --file wines.csv --format csv
```

#### Ajout manuel interactif
```bash
python import_wines.py --manual
```

Le script vous guidera à travers les champs :
- Nom du vin
- Domaine/producteur
- Millésime
- Type (red, white, rosé, sparkling, dessert, fortified)
- Pays et région
- Cépages
- Degré d'alcool
- Description
- Gamme de prix
- Code SAQ/LCBO

#### Remplacer la collection existante
```bash
python import_wines.py --file wines.json --drop
```

⚠️ **Attention:** `--drop` supprime toutes les données existantes avant l'import.

### Import de spiritueux

Les commandes sont identiques, en utilisant `import_liquors.py` :

```bash
# Exemple
python import_liquors.py --file sample_liquors.json

# Manuel
python import_liquors.py --manual

# CSV
python import_liquors.py --file liquors.csv --format csv

# Avec suppression
python import_liquors.py --file liquors.json --drop
```

### Dans Docker

Si vous utilisez Docker Compose :

```bash
# Import de vins
docker-compose exec backend python scripts/import_wines.py --file scripts/sample_wines.json

# Import de spiritueux
docker-compose exec backend python scripts/import_liquors.py --file scripts/sample_liquors.json

# Import manuel
docker-compose exec -it backend python scripts/import_wines.py --manual
```

## Format des fichiers

### JSON pour vins

```json
[
  {
    "name": "Château Margaux",
    "winery": "Château Margaux",
    "vintage": 2015,
    "wine_type": "red",
    "appellation": "Margaux AOC",
    "region": "bordeaux",
    "subregion": "Médoc",
    "country": "France",
    "grape_varieties": ["Cabernet Sauvignon", "Merlot"],
    "alcohol_content": 13.5,
    "color": "Ruby red",
    "nose": "Black currant, cedar, tobacco",
    "palate": "Full-bodied, elegant tannins",
    "body": "Full",
    "tannins": "High",
    "food_pairings": ["Filet mignon", "Agneau rôti"],
    "serving_temperature": "16-18°C",
    "decanting_time": 60,
    "aging_potential": "20-30 years",
    "description": "One of the most prestigious wines from Bordeaux",
    "price_range": "500-800€",
    "saq_code": "12345678",
    "custom": false
  }
]
```

### CSV pour vins

```csv
name,winery,vintage,type,region,country,grapes,alcohol,price,saq_code,description
Château Margaux,Château Margaux,2015,red,bordeaux,France,"Cabernet Sauvignon,Merlot",13.5,500-800€,12345678,Prestigious Bordeaux wine
Chablis Grand Cru,William Fèvre,2020,white,bourgogne,France,Chardonnay,13.0,60-80€,87654321,Classic Chablis with minerality
```

### JSON pour spiritueux

```json
[
  {
    "name": "Hennessy X.O",
    "brand": "Hennessy",
    "liquor_type": "cognac",
    "origin": "france",
    "region": "Cognac",
    "distillery": "Hennessy",
    "alcohol_content": 40.0,
    "age_statement": "X.O (Extra Old)",
    "color": "Deep amber",
    "aroma": "Oak, vanilla, dried fruits",
    "taste": "Rich, complex, spicy",
    "finish": "Long, smooth",
    "base_ingredient": "grape",
    "distillation_type": "pot still",
    "cask_type": "oak",
    "flavor_notes": ["vanilla", "oak", "dried fruit", "spice"],
    "serving_suggestions": "Neat or on rocks",
    "cocktail_suggestions": ["French Connection", "Sidecar"],
    "food_pairings": ["Chocolat noir", "Fromages affinés"],
    "description": "A prestigious Cognac with exceptional aging",
    "price_range": "150-200€",
    "saq_code": "11111111",
    "custom": false
  }
]
```

### CSV pour spiritueux

```csv
name,brand,type,origin,distillery,alcohol,age,flavors,price,saq_code,description
Hennessy X.O,Hennessy,cognac,france,Hennessy,40.0,X.O,"vanilla,oak,dried fruit",150-200€,11111111,Prestigious Cognac
Glenfiddich 18,Glenfiddich,scotch,scotland,Glenfiddich,40.0,18 years,"apple,oak,vanilla",80-100€,22222222,Smooth single malt Scotch
```

## Variables d'environnement

Les scripts utilisent ces variables d'environnement (définies dans `.env`) :

```bash
MONGODB_URL=mongodb://legrimoire:grimoire_mongo_password@localhost:27017/legrimoire?authSource=admin
MONGODB_DB_NAME=legrimoire
```

Vous pouvez aussi les passer en arguments :

```bash
python import_wines.py \
  --file wines.json \
  --mongodb-url "mongodb://user:pass@host:27017/db?authSource=admin" \
  --db-name legrimoire
```

## Gestion des doublons

Les scripts gèrent automatiquement les doublons :

1. **Par code SAQ/LCBO** : Si un code existe déjà, le vin/spiritueux est mis à jour
2. **Par nom + producteur** : Si aucun code n'est fourni, la correspondance se fait par nom et producteur

### Comportement :
- **Insertion** : Si l'entrée n'existe pas
- **Mise à jour** : Si l'entrée existe déjà (basé sur code ou nom)
- **Erreur** : Rapportée dans le résumé final

## Index créés

### Pour les vins :
- `name`, `winery` (recherche texte)
- `wine_type` (type de vin)
- `region` (région)
- `country` (pays)
- `saq_code` (unique, sparse)
- `lcbo_code` (unique, sparse)
- `custom` (personnalisé)

### Pour les spiritueux :
- `name`, `brand` (recherche texte)
- `liquor_type` (type de spiritueux)
- `origin` (origine)
- `distillery` (distillerie)
- `saq_code` (unique, sparse)
- `lcbo_code` (unique, sparse)
- `custom` (personnalisé)

## Exemples de sortie

```
======================================================================
🍷 Wine Database Import
======================================================================

📦 Connecting to MongoDB...

🔧 Creating indexes...
   ✅ Indexes created

📥 Importing 5 wines...
   Progress: 5 wines processed...

======================================================================
📊 Import Summary
======================================================================
   ✅ Inserted: 5
   🔄 Updated:  0
   📦 Total:    5 wines in database
======================================================================
```

## Exécution automatique (Cron)

Pour importer automatiquement de nouvelles données :

```bash
# Ajoutez au crontab
crontab -e

# Import quotidien à 2h du matin
0 2 * * * cd /path/to/backend && python scripts/import_wines.py --file /path/to/wines.json
```

## Développement futur

Ces scripts sont conçus pour être étendus avec :

- [ ] Import depuis API SAQ (Québec)
- [ ] Import depuis API LCBO (Ontario)
- [ ] Web scraping de sites de vins
- [ ] Import depuis bases de données publiques
- [ ] Validation avancée des données
- [ ] Enrichissement automatique (images, notes, etc.)

## Dépannage

### Erreur de connexion MongoDB
```
pymongo.errors.ServerSelectionTimeoutError
```
**Solution** : Vérifiez que MongoDB est en cours d'exécution et que l'URL est correcte.

### Erreur de duplication
```
DuplicateKeyError
```
**Solution** : Un vin/spiritueux avec le même code SAQ/LCBO existe déjà. Utilisez `--drop` pour recréer la collection.

### Erreur de format de fichier
```
json.decoder.JSONDecodeError
```
**Solution** : Vérifiez que votre fichier JSON est valide (utilisez un validateur JSON en ligne).

## Support

Pour plus d'informations :
- Documentation complète : `/docs/features/WINE_LIQUOR_DATABASE.md`
- API Reference : `/docs/architecture/API_REFERENCE.md`
- Issues GitHub : https://github.com/sparck75/le-grimoire/issues
