# Cellier (Cave à Vin) - Wine & Liquor Management

## Vue d'ensemble

Le Cellier est un système complet de gestion de vins et spiritueux pour Le Grimoire, intégrant des recommandations d'accords mets-vins alimentées par IA.

## Objectifs

1. **Gestion de cave à vin** - Suivre votre collection de vins et spiritueux
2. **Accords mets-vins IA** - Suggestions intelligentes basées sur vos recettes
3. **Base de données complète** - Import de sources externes (Open Wine Database, etc.)
4. **Suivi d'inventaire** - Gestion des bouteilles, localisation, fenêtres de consommation

## Architecture

### Collections MongoDB

#### Collection `wines`
```javascript
{
  _id: ObjectId,
  
  // Informations de base
  name: String,                    // Nom du vin
  producer: String,                // Producteur/Domaine
  vintage: Number,                 // Année (ex: 2019)
  country: String,                 // Pays d'origine
  region: String,                  // Région (ex: "Bordeaux", "Napa Valley")
  appellation: String,             // Appellation (ex: "Saint-Émilion", "AOC Bourgogne")
  
  // Classification
  wine_type: String,               // Type: "red", "white", "rosé", "sparkling", "dessert"
  classification: String,          // Grand Cru, Premier Cru, etc.
  
  // Composition
  grape_varieties: [               // Cépages
    {
      name: String,                // Nom du cépage (ex: "Cabernet Sauvignon")
      percentage: Number           // Pourcentage (optionnel)
    }
  ],
  
  // Caractéristiques
  alcohol_content: Number,         // % d'alcool
  body: String,                    // "light", "medium", "full"
  sweetness: String,               // "dry", "off-dry", "sweet", "very-sweet"
  acidity: String,                 // "low", "medium", "high"
  tannins: String,                 // "low", "medium", "high" (vins rouges)
  
  // Dégustation
  color: String,                   // Description de la couleur
  nose: [String],                  // Arômes au nez
  palate: [String],                // Arômes en bouche
  tasting_notes: String,           // Notes de dégustation complètes
  
  // Accords
  food_pairings: [String],         // Suggestions d'accords
  suggested_recipes: [ObjectId],   // Références vers recettes
  
  // Informations cave
  purchase_date: Date,             // Date d'achat
  purchase_price: Number,          // Prix d'achat
  purchase_location: String,       // Lieu d'achat
  current_quantity: Number,        // Nombre de bouteilles
  cellar_location: String,         // Emplacement dans la cave
  
  // Fenêtre de consommation
  drink_from: Number,              // Année minimum pour boire
  drink_until: Number,             // Année maximum pour boire
  peak_drinking: String,           // Période optimale
  
  // Métadonnées
  rating: Number,                  // Note personnelle (0-5)
  professional_ratings: [          // Notes professionnelles
    {
      source: String,              // "Wine Spectator", "Robert Parker", etc.
      score: Number,               // Note
      year: Number                 // Année de la note
    }
  ],
  image_url: String,               // URL de l'image
  qr_code: String,                 // Code QR pour identification rapide
  barcode: String,                 // Code-barres EAN
  
  // Sources externes
  vivino_id: String,               // ID Vivino
  wine_searcher_id: String,        // ID Wine-Searcher
  external_data: Object,           // Données externes brutes
  
  // Gestion
  is_public: Boolean,              // Visible publiquement
  user_id: String,                 // Propriétaire
  created_at: Date,
  updated_at: Date
}
```

#### Collection `liquors`
```javascript
{
  _id: ObjectId,
  
  // Informations de base
  name: String,                    // Nom du spiritueux
  brand: String,                   // Marque
  distillery: String,              // Distillerie
  country: String,                 // Pays d'origine
  region: String,                  // Région
  
  // Classification
  spirit_type: String,             // "whiskey", "vodka", "rum", "gin", "tequila", "brandy", "liqueur", "other"
  subtype: String,                 // "bourbon", "scotch", "cognac", etc.
  
  // Caractéristiques
  alcohol_content: Number,         // % d'alcool (proof)
  age_statement: String,           // "12 ans", "XO", etc.
  cask_type: String,               // Type de fût
  finish: String,                  // Finition spéciale
  
  // Dégustation
  color: String,                   // Description de la couleur
  nose: [String],                  // Arômes au nez
  palate: [String],                // Arômes en bouche
  finish_notes: String,            // Notes de finale
  tasting_notes: String,           // Notes complètes
  
  // Usage
  cocktail_uses: [String],         // Suggestions de cocktails
  food_pairings: [String],         // Accords mets-spiritueux
  
  // Informations cave
  purchase_date: Date,
  purchase_price: Number,
  purchase_location: String,
  current_quantity: Number,        // Niveau de la bouteille (0-100%)
  cellar_location: String,
  
  // Métadonnées
  rating: Number,                  // Note personnelle
  professional_ratings: [
    {
      source: String,
      score: Number,
      year: Number
    }
  ],
  image_url: String,
  qr_code: String,
  barcode: String,
  
  // Sources externes
  external_id: String,
  external_data: Object,
  
  // Gestion
  is_public: Boolean,
  user_id: String,
  created_at: Date,
  updated_at: Date
}
```

## API Endpoints

### Vins

#### Lister et rechercher
```
GET /api/v2/wines/
```

**Paramètres:**
- `search`: Recherche textuelle
- `wine_type`: Filtrer par type (red, white, rosé, etc.)
- `region`: Filtrer par région
- `country`: Filtrer par pays
- `grape_variety`: Filtrer par cépage
- `vintage_min`, `vintage_max`: Filtrer par millésime
- `price_min`, `price_max`: Filtrer par prix
- `in_stock`: Uniquement les vins en stock
- `limit`, `skip`: Pagination

**Example:**
```bash
curl "http://localhost:8000/api/v2/wines/?wine_type=red&region=Bordeaux&limit=20"
```

#### Obtenir un vin spécifique
```
GET /api/v2/wines/{id}
```

#### Créer un vin
```
POST /api/v2/wines/
```

**Body:**
```json
{
  "name": "Château Margaux",
  "producer": "Château Margaux",
  "vintage": 2015,
  "country": "France",
  "region": "Bordeaux",
  "appellation": "Margaux",
  "wine_type": "red",
  "grape_varieties": [
    {"name": "Cabernet Sauvignon", "percentage": 87},
    {"name": "Merlot", "percentage": 13}
  ],
  "alcohol_content": 13.5,
  "current_quantity": 6,
  "cellar_location": "Rangée 3, Étagère 2"
}
```

#### Mettre à jour un vin
```
PUT /api/v2/wines/{id}
```

#### Supprimer un vin
```
DELETE /api/v2/wines/{id}
```

#### Obtenir des accords mets-vins (IA)
```
POST /api/v2/wines/pairing-suggestions
```

**Body:**
```json
{
  "recipe_id": "507f1f77bcf86cd799439011",
  "preferences": {
    "price_range": "medium",
    "from_collection": true
  }
}
```

**Response:**
```json
{
  "recipe": {
    "id": "507f1f77bcf86cd799439011",
    "title": "Boeuf Bourguignon"
  },
  "suggestions": [
    {
      "wine_id": "507f1f77bcf86cd799439012",
      "name": "Gevrey-Chambertin 2018",
      "wine_type": "red",
      "region": "Bourgogne",
      "confidence": 0.95,
      "reasoning": "Ce vin de Bourgogne s'accorde parfaitement avec le boeuf bourguignon grâce à ses tanins structurés et ses notes de fruits rouges qui complètent la richesse du plat.",
      "in_collection": true,
      "alternative_suggestions": [
        "Côtes du Rhône Villages",
        "Bordeaux Médoc"
      ]
    }
  ]
}
```

### Spiritueux

Mêmes endpoints que les vins, sous `/api/v2/liquors/`

#### Suggestions de cocktails
```
GET /api/v2/liquors/{id}/cocktail-suggestions
```

### Statistiques

```
GET /api/v2/cellier/stats
```

**Response:**
```json
{
  "wines": {
    "total": 145,
    "by_type": {
      "red": 89,
      "white": 42,
      "rosé": 8,
      "sparkling": 6
    },
    "by_country": {
      "France": 102,
      "Italy": 25,
      "USA": 18
    },
    "total_value": 12450.00,
    "average_price": 85.86
  },
  "liquors": {
    "total": 38,
    "by_type": {
      "whiskey": 15,
      "rum": 8,
      "gin": 7,
      "vodka": 5,
      "other": 3
    },
    "total_value": 2890.00
  }
}
```

## Service IA pour Accords Mets-Vins

### Fichier: `backend/app/services/ai_wine_pairing.py`

Le service utilise l'infrastructure IA existante (OpenAI/Gemini) pour générer des suggestions d'accords mets-vins intelligentes.

**Fonctionnalités:**
1. Analyse de la recette (ingrédients, cuisine, préparation)
2. Génération de suggestions de vins appropriés
3. Recherche dans la collection personnelle de l'utilisateur
4. Alternatives si le vin suggéré n'est pas disponible
5. Explications détaillées des accords

**Prompt Template:**
```
Tu es un sommelier expert. Analyse cette recette et suggère des accords mets-vins.

Recette:
- Titre: {title}
- Ingrédients principaux: {main_ingredients}
- Type de cuisine: {cuisine}
- Préparation: {cooking_method}

Collection de vins disponible:
{user_wine_collection}

Fournis:
1. 3 suggestions de vins de la collection (si disponibles)
2. 3 suggestions alternatives (types de vins génériques)
3. Une explication détaillée pour chaque accord
4. Des notes sur la température de service

Format de réponse en JSON.
```

## Import de Données Externes

### Sources de données potentielles

1. **Open Wine Database**
   - Similar to OpenFoodFacts
   - Données ouvertes, multilingues
   - Format structuré, facile à importer

2. **Vivino API** (si disponible)
   - Données communautaires
   - Notes et avis
   - Prix du marché

3. **Wine.com API** (commercial)
   - Base de données complète
   - Informations de vente

4. **LCBO API** (Ontario, Canada)
   - API publique
   - Bon pour marché canadien

### Script d'import

Fichier: `backend/scripts/import_wine_data.py`

Pattern similaire à `import_off_ingredients.py`:
- Téléchargement des données
- Parsing et transformation
- Import dans MongoDB
- Création d'indexes
- Logging et statistiques

## Frontend - Pages et Composants

### Pages

#### `/cellier/page.tsx` - Page principale
- Liste des vins et spiritueux
- Filtres multiples (type, région, année, etc.)
- Recherche textuelle
- Vue grille/liste
- Statistiques rapides

#### `/cellier/wines/new/page.tsx` - Ajouter un vin
- Formulaire structuré
- Recherche externe (si API disponible)
- Scan code-barres (optionnel)
- Upload d'image

#### `/cellier/wines/[id]/page.tsx` - Détail du vin
- Informations complètes
- Suggestions d'accords (IA)
- Historique de consommation
- Modifier/Supprimer

#### `/cellier/liquors/...` - Pages spiritueux
- Structure similaire aux vins
- Suggestions de cocktails

#### `/cellier/pairing/page.tsx` - Accords IA
- Sélection de recette
- Génération de suggestions
- Comparaison de vins

### Composants

#### `WineCard.tsx`
- Affichage compact d'un vin
- Image, nom, région, millésime
- Actions rapides (voir, modifier, supprimer)

#### `WineFilters.tsx`
- Filtres multiples
- Recherche autocomplete
- Reset rapide

#### `WinePairingResults.tsx`
- Affichage des suggestions IA
- Explications détaillées
- Liens vers vins de la collection

#### `CellierStats.tsx`
- Statistiques visuelles
- Graphiques (types, régions, valeur)
- Métriques clés

## Taxonomie et Classification

### Types de vins
- Rouge (Red)
- Blanc (White)
- Rosé
- Mousseux (Sparkling)
- Dessert (Sweet/Fortified)

### Régions principales (France)
- Bordeaux
- Bourgogne
- Champagne
- Vallée du Rhône
- Vallée de la Loire
- Alsace
- Languedoc-Roussillon

### Cépages principaux

**Rouges:**
- Cabernet Sauvignon
- Merlot
- Pinot Noir
- Syrah/Shiraz
- Grenache
- Cabernet Franc
- Malbec
- Tempranillo

**Blancs:**
- Chardonnay
- Sauvignon Blanc
- Riesling
- Pinot Grigio/Gris
- Viognier
- Gewurztraminer

### Types de spiritueux
- Whiskey (Scotch, Bourbon, Irish, Japanese, Canadian)
- Vodka
- Rum (Light, Dark, Spiced)
- Gin
- Tequila (Blanco, Reposado, Añejo)
- Brandy/Cognac
- Liqueurs

## Intégration avec Recettes

### Liens bidirectionnels
- Recette → Vins suggérés (automatique via IA)
- Vin → Recettes compatibles

### Filtres avancés
- Rechercher recettes par vin disponible
- Rechercher vins pour recette planifiée

### Liste de courses intelligente
Extension de la fonctionnalité existante:
- Suggérer vins à acheter pour repas planifié
- Intégration avec SAQ/LCBO pour prix

## Sécurité et Permissions

### Visibilité
- Vins privés (par défaut) - Uniquement propriétaire
- Vins publics - Suggestions communautaires

### Données sensibles
- Prix d'achat (privé)
- Localisation cave (privé)
- Notes de dégustation (optionnel public)

## Phases d'implémentation

### Phase 1: MVP (Minimal Viable Product)
1. ✅ Modèles de base (Wine, Liquor)
2. ✅ CRUD endpoints
3. ✅ Pages frontend basiques
4. ✅ Import manuel de données

### Phase 2: IA et Accords
1. Service d'accords mets-vins IA
2. Interface de suggestions
3. Intégration avec recettes existantes

### Phase 3: Sources Externes
1. Recherche et évaluation d'APIs
2. Scripts d'import automatique
3. Synchronisation des données

### Phase 4: Fonctionnalités Avancées
1. Scan code-barres
2. Génération QR codes
3. Application mobile
4. Notifications fenêtres de consommation
5. Historique de consommation
6. Recommandations ML basées sur l'historique

## Ressources et Références

### APIs et bases de données
- [OpenWineDatabase](https://github.com/OpenWineDatabase)
- [Vivino](https://www.vivino.com/)
- [LCBO API](https://lcboapi.com/)
- [SAQ](https://www.saq.com/)

### Documentation de référence
- [Wine Folly](https://winefolly.com/) - Éducation vin
- [The Wine Bible](https://www.amazon.com/Wine-Bible-Karen-MacNeil/dp/1607747464)

### Exemples de projets similaires
- [Cellar Tracker](https://www.cellartracker.com/)
- [Vivino App](https://www.vivino.com/app)
- [Wine-Searcher](https://www.wine-searcher.com/)

## Questions Ouvertes

1. **Quelle API externe utiliser?**
   - Évaluer disponibilité, coût, qualité des données
   - Commencer avec Open Wine Database?

2. **Scan de code-barres?**
   - Bibliothèque: ZXing, QuaggaJS
   - Intégration mobile vs web

3. **Gestion multi-utilisateurs?**
   - Collections partagées (famille, cave partagée)?
   - Permissions granulaires?

4. **Monétisation future?**
   - Fonctionnalités premium?
   - Partenariats avec cavistes?

## Prochaines Étapes

1. ✅ Créer ce document de planification
2. Rechercher et évaluer APIs de vins disponibles
3. Créer modèles MongoDB (Wine, Liquor)
4. Implémenter endpoints API de base
5. Créer pages frontend MVP
6. Développer service IA d'accords
7. Tester et itérer

---

**Auteur:** Le Grimoire Development Team  
**Date:** 2025-10-29  
**Version:** 1.0 (Plan initial)
