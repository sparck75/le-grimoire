# Architecture du Système Vins & Spiritueux

## Vue d'ensemble

Le système de gestion des vins et spiritueux est conçu pour fonctionner de manière autonome ou intégrée avec le reste de l'application Le Grimoire.

## Diagramme d'architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SOURCES DE DONNÉES                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ Fichiers │  │ API SAQ  │  │ API LCBO │  │    Manuel    │   │
│  │ JSON/CSV │  │ (futur)  │  │ (futur)  │  │   (CLI/UI)   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘   │
└───────┼─────────────┼─────────────┼────────────────┼───────────┘
        │             │             │                │
        └─────────────┴─────────────┴────────────────┘
                              │
                              ▼
        ┌────────────────────────────────────────────┐
        │      SCRIPTS D'IMPORTATION                  │
        ├────────────────────────────────────────────┤
        │                                             │
        │  ┌─────────────────────────────────────┐   │
        │  │  import_wines.py                    │   │
        │  │  - load_wines_from_json()           │   │
        │  │  - load_wines_from_csv()            │   │
        │  │  - add_manual_wine()                │   │
        │  │  - transform_wine()                 │   │
        │  │  - create_indexes()                 │   │
        │  └─────────────────────────────────────┘   │
        │                                             │
        │  ┌─────────────────────────────────────┐   │
        │  │  import_liquors.py                  │   │
        │  │  - load_liquors_from_json()         │   │
        │  │  - load_liquors_from_csv()          │   │
        │  │  - add_manual_liquor()              │   │
        │  │  - transform_liquor()               │   │
        │  │  - create_indexes()                 │   │
        │  └─────────────────────────────────────┘   │
        │                                             │
        └──────────────────┬──────────────────────────┘
                           │
                           ▼
        ┌────────────────────────────────────────────┐
        │         BASE DE DONNÉES MONGODB             │
        ├────────────────────────────────────────────┤
        │                                             │
        │  ┌─────────────────────────────────────┐   │
        │  │  Collection: wines                  │   │
        │  │  ├─ name, winery, vintage           │   │
        │  │  ├─ wine_type, region, country      │   │
        │  │  ├─ grape_varieties[]               │   │
        │  │  ├─ alcohol_content, tannins        │   │
        │  │  ├─ food_pairings[]                 │   │
        │  │  ├─ price_range, saq_code           │   │
        │  │  └─ Indexes: name, type, region     │   │
        │  └─────────────────────────────────────┘   │
        │                                             │
        │  ┌─────────────────────────────────────┐   │
        │  │  Collection: liquors                │   │
        │  │  ├─ name, brand, liquor_type        │   │
        │  │  ├─ origin, distillery              │   │
        │  │  ├─ alcohol_content, age            │   │
        │  │  ├─ flavor_notes[]                  │   │
        │  │  ├─ cocktail_suggestions[]          │   │
        │  │  ├─ price_range, saq_code           │   │
        │  │  └─ Indexes: name, brand, type      │   │
        │  └─────────────────────────────────────┘   │
        │                                             │
        └──────────────────┬──────────────────────────┘
                           │
                           ▼
        ┌────────────────────────────────────────────┐
        │         MODÈLES BEANIE ODM                  │
        ├────────────────────────────────────────────┤
        │                                             │
        │  ┌─────────────────────────────────────┐   │
        │  │  Wine (Document)                    │   │
        │  │  ├─ WineType (Enum)                 │   │
        │  │  ├─ WineRegion (Enum)               │   │
        │  │  ├─ search()                        │   │
        │  │  ├─ get_by_saq_code()               │   │
        │  │  ├─ get_by_type()                   │   │
        │  │  └─ get_by_region()                 │   │
        │  └─────────────────────────────────────┘   │
        │                                             │
        │  ┌─────────────────────────────────────┐   │
        │  │  Liquor (Document)                  │   │
        │  │  ├─ LiquorType (Enum)               │   │
        │  │  ├─ LiquorOrigin (Enum)             │   │
        │  │  ├─ search()                        │   │
        │  │  ├─ get_by_saq_code()               │   │
        │  │  ├─ get_by_type()                   │   │
        │  │  └─ get_by_origin()                 │   │
        │  └─────────────────────────────────────┘   │
        │                                             │
        └──────────────────┬──────────────────────────┘
                           │
                           ▼
        ┌────────────────────────────────────────────┐
        │            API FASTAPI                      │
        ├────────────────────────────────────────────┤
        │                                             │
        │  ┌─────────────────────────────────────┐   │
        │  │  /api/v2/wines                      │   │
        │  │  ├─ GET    / (search, filters)      │   │
        │  │  ├─ GET    /{id}                    │   │
        │  │  ├─ POST   / (create)               │   │
        │  │  ├─ PUT    /{id} (update)           │   │
        │  │  ├─ DELETE /{id}                    │   │
        │  │  ├─ GET    /saq/{code}              │   │
        │  │  ├─ GET    /types/{type}            │   │
        │  │  └─ GET    /regions/{region}        │   │
        │  └─────────────────────────────────────┘   │
        │                                             │
        │  ┌─────────────────────────────────────┐   │
        │  │  /api/v2/liquors                    │   │
        │  │  ├─ GET    / (search, filters)      │   │
        │  │  ├─ GET    /{id}                    │   │
        │  │  ├─ POST   / (create)               │   │
        │  │  ├─ PUT    /{id} (update)           │   │
        │  │  ├─ DELETE /{id}                    │   │
        │  │  ├─ GET    /saq/{code}              │   │
        │  │  ├─ GET    /types/{type}            │   │
        │  │  └─ GET    /origins/{origin}        │   │
        │  └─────────────────────────────────────┘   │
        │                                             │
        └──────────────────┬──────────────────────────┘
                           │
                           ▼
        ┌────────────────────────────────────────────┐
        │          APPLICATIONS CLIENTES              │
        ├────────────────────────────────────────────┤
        │                                             │
        │  ┌────────────┐  ┌────────────┐           │
        │  │  Frontend  │  │  Scripts   │           │
        │  │  Next.js   │  │  Python    │           │
        │  │  (futur)   │  │  CLI       │           │
        │  └────────────┘  └────────────┘           │
        │                                             │
        │  ┌────────────┐  ┌────────────┐           │
        │  │   Mobile   │  │  Cron Jobs │           │
        │  │   (futur)  │  │  Automated │           │
        │  └────────────┘  └────────────┘           │
        │                                             │
        └─────────────────────────────────────────────┘
```

## Flux de données

### 1. Import de données

```
Fichier JSON/CSV → Script d'import → Transformation → MongoDB
                                          │
                                          ├─ Validation des champs
                                          ├─ Détection des doublons
                                          ├─ Création des index
                                          └─ Rapport de progression
```

### 2. Requête API

```
Client HTTP → FastAPI → Beanie ODM → MongoDB → Résultat JSON
    │            │           │
    │            │           └─ Recherche avec filtres
    │            └─ Validation Pydantic
    └─ Authentication (futur)
```

### 3. Opération CRUD

```
POST /api/v2/wines/
    ↓
Validation des données (Pydantic)
    ↓
Vérification des doublons (SAQ code)
    ↓
Création du document (Beanie)
    ↓
Insertion MongoDB
    ↓
Retour de l'ID et confirmation
```

## Composants clés

### 1. Modèles de données

**Wine (45+ champs)**
- Identification: name, winery, vintage, wine_type
- Localisation: region, country, appellation
- Caractéristiques: grape_varieties, alcohol_content, color, nose, palate
- Dégustation: tannins, body, acidity
- Usage: food_pairings, serving_temperature, aging_potential
- Commercial: price_range, saq_code, lcbo_code

**Liquor (47+ champs)**
- Identification: name, brand, liquor_type
- Origine: origin, distillery, region
- Production: base_ingredient, distillation_type, age_statement
- Caractéristiques: alcohol_content, color, aroma, taste, finish
- Usage: cocktail_suggestions, serving_suggestions, food_pairings
- Certifications: organic, kosher, gluten_free

### 2. Endpoints API

Chaque ressource (wines/liquors) dispose de 8 endpoints:
1. **GET /** - Liste avec recherche et filtres
2. **GET /{id}** - Détails d'une entrée
3. **POST /** - Création
4. **PUT /{id}** - Mise à jour
5. **DELETE /{id}** - Suppression
6. **GET /saq/{code}** - Recherche par code SAQ
7. **GET /types/{type}** - Liste par type
8. **GET /regions|origins/{value}** - Liste par région/origine

### 3. Scripts d'import

**Fonctionnalités communes:**
- Import JSON (format structuré)
- Import CSV (format tabulaire)
- Entrée manuelle interactive (CLI)
- Transformation et validation
- Gestion des doublons
- Création automatique des index
- Rapports de progression détaillés

**Options de ligne de commande:**
```bash
--file PATH       # Fichier source
--format json|csv # Format du fichier
--manual          # Mode interactif
--drop            # Supprimer collection existante
--mongodb-url URL # URL personnalisée
--db-name NAME    # Nom de base personnalisé
```

## Intégration

### Avec les recettes

Les vins peuvent être associés aux recettes via:
- Champ `food_pairings` dans Wine
- Recherche de vins par ingrédient/plat
- Suggestions automatiques d'accords mets-vins

```python
# Trouver des vins pour une recette de boeuf
wines = await Wine.find({
    "food_pairings": {"$regex": "boeuf", "$options": "i"}
}).to_list()
```

### Avec les cocktails

Les spiritueux peuvent suggérer des cocktails:
- Champ `cocktail_suggestions` dans Liquor
- Recherche de spiritueux par cocktail
- Création future de recettes de cocktails

```python
# Spiritueux pour un Mojito
liquors = await Liquor.find({
    "cocktail_suggestions": {"$regex": "mojito", "$options": "i"}
}).to_list()
```

## Sécurité

### Niveau actuel
- Validation Pydantic des données entrantes
- Gestion des erreurs MongoDB
- Indexes unique sur codes SAQ/LCBO

### À implémenter
- [ ] Authentication OAuth pour les opérations d'écriture
- [ ] Rate limiting sur les endpoints de création
- [ ] Validation avancée des données (regex, ranges)
- [ ] Audit trail des modifications

## Performance

### Optimisations actuelles
- Index MongoDB sur tous les champs de recherche
- Index texte pour recherche full-text
- Index sparse sur SAQ/LCBO (optionnels)
- Pagination sur toutes les listes

### Métriques cibles
- Recherche: < 100ms
- GET par ID: < 50ms
- Import 1000 entrées: < 30s
- Création unique: < 100ms

## Extensibilité

### À court terme
- Frontend React pour gestion visuelle
- Import API SAQ/LCBO automatique
- OCR pour étiquettes de bouteilles

### À moyen terme
- Système de notation utilisateur
- Photos de bouteilles
- Historique des prix
- Alertes de disponibilité

### À long terme
- Recommandations par IA
- Cave à vin virtuelle
- Application mobile avec scanner
- Intégration e-commerce

## Monitoring

### Logs
- Import: nombre d'insertions/mises à jour/erreurs
- API: requêtes, temps de réponse, erreurs
- Base de données: croissance, performance des index

### Métriques à surveiller
- Nombre total de vins/spiritueux
- Taux de succès des imports
- Temps de réponse moyen des API
- Utilisation de l'espace disque MongoDB

## Maintenance

### Tâches régulières
- Import automatique (cron jobs)
- Sauvegarde MongoDB
- Nettoyage des doublons
- Mise à jour des prix

### Commandes utiles
```bash
# Compter les entrées
docker-compose exec mongodb mongosh --eval "use legrimoire; db.wines.countDocuments()"

# Sauvegarder la collection
mongodump --collection=wines --db=legrimoire --out=/backup

# Restaurer la collection
mongorestore --collection=wines --db=legrimoire /backup/legrimoire/wines.bson
```

## Documentation

- **Guide utilisateur**: `docs/features/WINE_LIQUOR_DATABASE.md`
- **Guide scripts**: `backend/scripts/README_WINE_LIQUOR.md`
- **API Reference**: `docs/architecture/API_REFERENCE.md`
- **Résumé implémentation**: `WINE_LIQUOR_SYSTEM_SUMMARY.md`
