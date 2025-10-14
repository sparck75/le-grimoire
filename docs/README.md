# Le Grimoire - Documentation

Bienvenue dans la documentation de Le Grimoire, une application web de gestion de recettes avec reconnaissance optique (OCR) et intégration des ingrédients OpenFoodFacts.

## 📚 Table des matières

### Pour commencer
- [Guide de démarrage rapide](./getting-started/QUICKSTART.md)
- [Installation et configuration](./getting-started/INSTALLATION.md)
- [Guide de contribution](./getting-started/CONTRIBUTING.md)

### Architecture
- [Vue d'ensemble de l'architecture](./architecture/OVERVIEW.md)
- [Architecture MongoDB](./architecture/MONGODB.md)
- [API Reference](./architecture/API_REFERENCE.md)

### Guides de développement
- [Guide de développement](./development/DEVELOPMENT.md)
- [Gestion des ingrédients](./development/INGREDIENTS.md)
- [Système de recettes](./development/RECIPES.md)
- [Frontend Admin](./development/ADMIN.md)

### Fonctionnalités
- [Système d'ingrédients OpenFoodFacts](./features/OPENFOODFACTS.md)
- [Traduction française](./features/FRENCH_LOCALIZATION.md)
- [Listes de courses](./features/SHOPPING_LISTS.md)

### Historique des migrations
- [Migration vers MongoDB](./migrations/MONGODB_MIGRATION.md)
- [Migration des ingrédients](./migrations/INGREDIENTS_MIGRATION.md)
- [Migration des recettes](./migrations/RECIPES_MIGRATION.md)

## 🚀 Démarrage rapide

```bash
# Cloner le projet
git clone https://github.com/sparck75/le-grimoire.git
cd le-grimoire

# Configurer l'environnement
cp .env.example .env

# Démarrer avec Docker
docker-compose up -d

# Accéder à l'application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

## 🏗️ Stack technologique

- **Frontend**: Next.js 14 (TypeScript)
- **Backend**: FastAPI (Python)
- **Base de données**: MongoDB (Beanie ODM)
- **Ingrédients**: OpenFoodFacts (5,942 ingrédients)
- **OCR**: Tesseract
- **Conteneurisation**: Docker & Docker Compose

## 📝 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](../LICENSE) pour plus de détails.
