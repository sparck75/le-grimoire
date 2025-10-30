# Wine and Liquor Database Management

## Vue d'ensemble

Le système de gestion des vins et spiritueux de Le Grimoire permet de créer, gérer et rechercher une base de données complète de vins et spiritueux (liquors). Ce système peut fonctionner en arrière-plan ou être géré manuellement pour alimenter l'application avec des informations détaillées sur les boissons alcoolisées.

## Architecture

### Modèles de données

#### Wine (Vin)
Le modèle `Wine` stocke des informations détaillées sur les vins :

```python
{
    "name": "Château Margaux",
    "winery": "Château Margaux",
    "vintage": 2015,
    "wine_type": "red",  # red, white, rosé, sparkling, dessert, fortified
    "appellation": "Margaux AOC",
    "region": "bordeaux",
    "country": "France",
    "grape_varieties": ["Cabernet Sauvignon", "Merlot"],
    "alcohol_content": 13.5,
    "food_pairings": ["Filet mignon", "Agneau"],
    "serving_temperature": "16-18°C",
    "aging_potential": "20-30 years",
    "price_range": "500-800€",
    "saq_code": "12345678",  # Code SAQ (Québec)
    "custom": false
}
```

**Types de vin disponibles:**
- `red` - Vin rouge
- `white` - Vin blanc
- `rosé` - Vin rosé
- `sparkling` - Vin effervescent (Champagne, etc.)
- `dessert` - Vin de dessert
- `fortified` - Vin fortifié (Porto, Sherry, etc.)

**Régions principales:**
- Bordeaux, Bourgogne, Champagne, Rhône, Loire, Alsace
- Languedoc-Roussillon, Provence, Sud-Ouest
- Italy, Spain, Portugal, USA, Australia, Chile, etc.

#### Liquor (Spiritueux)
Le modèle `Liquor` stocke des informations sur les spiritueux :

```python
{
    "name": "Hennessy X.O",
    "brand": "Hennessy",
    "liquor_type": "cognac",
    "origin": "france",
    "distillery": "Hennessy",
    "alcohol_content": 40.0,
    "age_statement": "X.O (Extra Old)",
    "base_ingredient": "grape",
    "flavor_notes": ["vanilla", "oak", "dried fruit"],
    "cocktail_suggestions": ["French Connection", "Sidecar"],
    "price_range": "150-200€",
    "saq_code": "87654321",
    "custom": false
}
```

**Types de spiritueux disponibles:**
- `vodka`, `gin`, `rum`, `whisky`, `bourbon`, `scotch`
- `tequila`, `mezcal`, `brandy`, `cognac`, `armagnac`
- `liqueur`, `apéritif`, `digestif`, `vermouth`
- `sake`, `absinthe`, `cachaça`, `grappa`, etc.

**Origines principales:**
- France, Scotland, Ireland, USA, Canada, Mexico
- Caribbean, Russia, Sweden, Japan, Italy, Spain, etc.

### Base de données MongoDB

Les collections sont stockées dans MongoDB avec des index optimisés :

**Collection `wines`:**
- Index sur `name`, `winery` (recherche texte)
- Index sur `wine_type`, `region`, `country`
- Index unique sur `saq_code`, `lcbo_code`

**Collection `liquors`:**
- Index sur `name`, `brand` (recherche texte)
- Index sur `liquor_type`, `origin`, `distillery`
- Index unique sur `saq_code`, `lcbo_code`

## API Endpoints

### Wines API (`/api/v2/wines`)

#### Rechercher des vins
```http
GET /api/v2/wines/?search=margaux&wine_type=red&region=bordeaux&limit=50
```

**Paramètres:**
- `search` - Recherche par nom, domaine, appellation
- `wine_type` - Filtrer par type de vin
- `region` - Filtrer par région
- `limit` - Nombre maximum de résultats (1-1000, défaut: 50)
- `skip` - Pagination
- `custom_only` - Seulement les vins personnalisés

#### Obtenir un vin par ID
```http
GET /api/v2/wines/{wine_id}
```

#### Créer un nouveau vin
```http
POST /api/v2/wines/
Content-Type: application/json

{
    "name": "Mon Vin",
    "winery": "Mon Domaine",
    "wine_type": "red",
    "vintage": 2020,
    "custom": true
}
```

#### Mettre à jour un vin
```http
PUT /api/v2/wines/{wine_id}
Content-Type: application/json

{
    "price_range": "25-35€",
    "tasting_notes": "Excellent millésime"
}
```

#### Supprimer un vin
```http
DELETE /api/v2/wines/{wine_id}
```

#### Rechercher par code SAQ
```http
GET /api/v2/wines/saq/{saq_code}
```

#### Lister par type
```http
GET /api/v2/wines/types/red?limit=100
```

#### Lister par région
```http
GET /api/v2/wines/regions/bordeaux?limit=100
```

### Liquors API (`/api/v2/liquors`)

Les endpoints sont similaires à ceux des vins :

- `GET /api/v2/liquors/` - Rechercher
- `GET /api/v2/liquors/{liquor_id}` - Obtenir par ID
- `POST /api/v2/liquors/` - Créer
- `PUT /api/v2/liquors/{liquor_id}` - Mettre à jour
- `DELETE /api/v2/liquors/{liquor_id}` - Supprimer
- `GET /api/v2/liquors/saq/{saq_code}` - Par code SAQ
- `GET /api/v2/liquors/types/{liquor_type}` - Par type
- `GET /api/v2/liquors/origins/{origin}` - Par origine

## Scripts d'importation

### Import de vins

#### Depuis un fichier JSON
```bash
cd backend
python scripts/import_wines.py --file scripts/sample_wines.json
```

#### Depuis un fichier CSV
```bash
python scripts/import_wines.py --file wines.csv --format csv
```

#### Ajout manuel interactif
```bash
python scripts/import_wines.py --manual
```

#### Avec suppression de la collection existante
```bash
python scripts/import_wines.py --file wines.json --drop
```

### Import de spiritueux

Les commandes sont similaires :

```bash
# JSON
python scripts/import_liquors.py --file scripts/sample_liquors.json

# CSV
python scripts/import_liquors.py --file liquors.csv --format csv

# Manuel
python scripts/import_liquors.py --manual

# Avec suppression
python scripts/import_liquors.py --file liquors.json --drop
```

### Format des fichiers

#### JSON pour vins
```json
[
  {
    "name": "Nom du vin",
    "winery": "Domaine",
    "vintage": 2020,
    "wine_type": "red",
    "region": "bordeaux",
    "grape_varieties": ["Cabernet Sauvignon"],
    "alcohol_content": 13.5,
    "price_range": "20-30€",
    "custom": false
  }
]
```

#### CSV pour vins
```csv
name,winery,vintage,type,region,country,grapes,alcohol,price,saq_code,description
Château Margaux,Château Margaux,2015,red,bordeaux,France,"Cabernet Sauvignon,Merlot",13.5,500-800€,12345678,Prestigious wine
```

## Utilisation en production

### Exécution en arrière-plan

Pour exécuter les imports en tant que tâche cron (automatique) :

```bash
# Crontab pour import quotidien depuis SAQ
0 2 * * * cd /app/backend && python scripts/import_wines.py --source saq
0 3 * * * cd /app/backend && python scripts/import_liquors.py --source saq
```

### Docker Compose

Pour exécuter les imports dans le conteneur :

```bash
# Import de vins
docker-compose exec backend python scripts/import_wines.py --file scripts/sample_wines.json

# Import de spiritueux
docker-compose exec backend python scripts/import_liquors.py --file scripts/sample_liquors.json
```

### Variables d'environnement

Les scripts utilisent ces variables d'environnement :

```bash
MONGODB_URL=mongodb://user:pass@host:27017/dbname?authSource=admin
MONGODB_DB_NAME=legrimoire
```

## Intégration avec les recettes

### Accorder vins et recettes

Les vins peuvent être associés aux recettes via le champ `food_pairings` :

```python
# Rechercher des vins pour une recette de boeuf
wines = await Wine.find({
    "food_pairings": {"$regex": "boeuf", "$options": "i"}
}).to_list()
```

### Suggérer des cocktails

Les spiritueux peuvent suggérer des cocktails :

```python
# Trouver des spiritueux pour un Mojito
liquors = await Liquor.find({
    "cocktail_suggestions": {"$regex": "mojito", "$options": "i"}
}).to_list()
```

## Fonctionnalités futures

### Court terme
- [ ] Intégration API SAQ automatique
- [ ] Intégration API LCBO (Ontario)
- [ ] Import automatique des nouveaux produits
- [ ] Système de notation utilisateur

### Moyen terme
- [ ] Reconnaissance d'étiquettes par OCR
- [ ] Suggestions d'accords mets-vins automatiques
- [ ] Cave à vin virtuelle pour les utilisateurs
- [ ] Alertes de disponibilité

### Long terme
- [ ] Intégration marketplace (achat direct)
- [ ] Historique des prix
- [ ] Recommandations par IA
- [ ] Application mobile pour scanner les bouteilles

## Exemples d'utilisation

### Recherche avancée de vins

```python
from app.models.mongodb import Wine, WineType, WineRegion

# Vins rouges de Bordeaux
wines = await Wine.find({
    "wine_type": WineType.RED,
    "region": WineRegion.BORDEAUX,
    "alcohol_content": {"$gte": 13.0, "$lte": 14.5}
}).to_list()

# Vins dans une gamme de prix
wines = await Wine.search(
    query="margaux",
    wine_type=WineType.RED,
    limit=20
)
```

### Recherche de spiritueux

```python
from app.models.mongodb import Liquor, LiquorType, LiquorOrigin

# Whiskies écossais vieillis
liquors = await Liquor.find({
    "liquor_type": LiquorType.SCOTCH,
    "origin": LiquorOrigin.SCOTLAND,
    "age_statement": {"$exists": True}
}).to_list()

# Spiritueux pour cocktails
liquors = await Liquor.search(
    query="vodka",
    origin=LiquorOrigin.FRANCE,
    limit=10
)
```

## Support

Pour plus d'informations :
- [Documentation API](../architecture/API_REFERENCE.md)
- [Guide de développement](../development/DEVELOPMENT.md)
- [Architecture](../architecture/OVERVIEW.md)

## Contribution

Les contributions sont les bienvenues pour :
- Ajouter des sources de données (API, scraping)
- Améliorer les modèles de données
- Créer des interfaces utilisateur
- Développer des fonctionnalités d'accord mets-vins
