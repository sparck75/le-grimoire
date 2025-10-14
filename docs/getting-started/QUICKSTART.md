# Guide de démarrage rapide - Le Grimoire

## 🚀 Installation rapide

### Prérequis

- [Docker](https://www.docker.com/) et Docker Compose
- Git

### Installation en 3 étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/sparck75/le-grimoire.git
cd le-grimoire

# 2. Configurer l'environnement
cp .env.example .env

# 3. Démarrer l'application
docker-compose up -d
```

L'application sera disponible sur :
- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **API Documentation** : http://localhost:8000/docs

## 📍 Services et ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend (Next.js) | 3000 | Interface utilisateur |
| Backend (FastAPI) | 8000 | API REST |
| MongoDB | 27017 | Base de données |
| Nginx | 80 | Reverse proxy |

## 🔧 Commandes Docker utiles

```bash
# Voir les logs
docker-compose logs -f

# Voir les logs d'un service spécifique
docker-compose logs -f frontend
docker-compose logs -f backend

# Arrêter l'application
docker-compose down

# Redémarrer un service
docker-compose restart frontend
docker-compose restart backend

# Reconstruire les images
docker-compose build --no-cache

# Supprimer tout (⚠️ efface les données)
docker-compose down -v
```

## 🗄️ Configuration MongoDB

### Initialiser la base de données d'ingrédients

Les ingrédients OpenFoodFacts sont déjà inclus dans le conteneur MongoDB. Pour les réimporter :

```bash
# Télécharger et importer les ingrédients
docker-compose exec backend python -c "from app.models.mongodb import init_database; import asyncio; asyncio.run(init_database())"
```

### Vérifier la base de données

```bash
# Se connecter à MongoDB
docker-compose exec mongodb mongosh

# Dans le shell MongoDB
use le_grimoire
db.ingredients.countDocuments()  // Devrait retourner 5942
db.recipes.countDocuments()      // Nombre de recettes
```

## 👤 Premiers pas

### 1. Accéder à l'application

Ouvrez http://localhost:3000 dans votre navigateur.

### 2. Créer une recette

1. Allez sur http://localhost:3000/admin/recipes/new
2. Remplissez les informations de la recette
3. Ajoutez des ingrédients (avec recherche autocomplete)
4. Sauvegardez

### 3. Voir les recettes publiques

Accédez à http://localhost:3000/recipes pour voir toutes les recettes publiques.

## 🔍 Explorer l'API

L'API FastAPI fournit une documentation interactive :

1. Ouvrez http://localhost:8000/docs
2. Explorez les endpoints disponibles
3. Testez les requêtes directement depuis l'interface

### Endpoints principaux

- `GET /api/v2/recipes/` - Liste des recettes
- `GET /api/v2/ingredients/` - Recherche d'ingrédients
- `POST /api/v2/recipes/` - Créer une recette
- `GET /api/stats/dashboard` - Statistiques

## 🐛 Résolution de problèmes

### Le frontend ne démarre pas

```bash
# Vérifier les logs
docker-compose logs frontend

# Reconstruire le conteneur
docker-compose build frontend
docker-compose up -d frontend
```

### Le backend ne démarre pas

```bash
# Vérifier les logs
docker-compose logs backend

# Vérifier que MongoDB est démarré
docker-compose ps

# Redémarrer le backend
docker-compose restart backend
```

### MongoDB n'a pas d'ingrédients

```bash
# Vérifier le nombre d'ingrédients
docker-compose exec mongodb mongosh --eval "use le_grimoire; db.ingredients.countDocuments()"

# Si 0, réimporter les ingrédients
docker-compose exec backend python scripts/import_openfoodfacts.py
```

### Réinitialiser complètement l'application

```bash
# Arrêter et supprimer tous les conteneurs et volumes
docker-compose down -v

# Supprimer les images
docker-compose rm -f

# Reconstruire tout
docker-compose build --no-cache
docker-compose up -d
```

## 📚 Prochaines étapes

- Consultez le [Guide de développement](../development/DEVELOPMENT.md)
- Lisez l'[Architecture](../architecture/OVERVIEW.md)
- Explorez la [Gestion des ingrédients](../development/INGREDIENTS.md)
- Consultez le [Guide de contribution](CONTRIBUTING.md)

## 🆘 Besoin d'aide ?

- Consultez la [documentation complète](../README.md)
- Ouvrez une [issue sur GitHub](https://github.com/sparck75/le-grimoire/issues)
