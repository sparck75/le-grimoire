# Le Grimoire 📚

Un outil pour extraire, sauvegarder et partager des recettes de cuisine à partir d'images grâce à l'OCR (Reconnaissance Optique de Caractères).

## Stack Technologique

- **Frontend**: Next.js 14 avec TypeScript
- **Backend**: FastAPI (Python)
- **Base de données**: PostgreSQL 15
- **Cache/Queue**: Redis
- **Conteneurisation**: Docker & Docker Compose
- **Authentification**: OAuth 2.0 (Google et Apple)
- **OCR**: Tesseract OCR
- **Web Scraping**: BeautifulSoup4, Selenium

## Fonctionnalités

### ✨ Fonctionnalités principales

- **Extraction OCR de recettes** : Téléchargez des images de recettes et extrayez automatiquement le texte
- **Bibliothèque de recettes** : Consultez et recherchez des recettes publiques sans authentification
- **Listes d'achats intelligentes** : Générez des listes d'achats avec les spéciaux actuels d'IGA et Metro
- **Authentification OAuth** : Connexion sécurisée avec Google ou Apple pour soumettre des recettes
- **Scraping automatique** : Récupération quotidienne des spéciaux d'épiceries

## Architecture

```
le-grimoire/
├── frontend/           # Application Next.js
│   ├── src/
│   │   ├── app/       # Pages et routes
│   │   ├── components/# Composants réutilisables
│   │   └── lib/       # Utilitaires et configuration
│   └── Dockerfile
├── backend/            # API FastAPI
│   ├── app/
│   │   ├── api/       # Routes API
│   │   ├── models/    # Modèles SQLAlchemy
│   │   ├── services/  # Services (OCR, scraper)
│   │   └── core/      # Configuration et sécurité
│   ├── scripts/       # Scripts utilitaires
│   └── Dockerfile
├── database/          # Scripts SQL d'initialisation
└── docker-compose.yml # Configuration Docker

```

## Installation et Configuration

### Prérequis

- Docker et Docker Compose
- Git

### Étapes d'installation

1. **Cloner le dépôt**

```bash
git clone https://github.com/sparck75/le-grimoire.git
cd le-grimoire
```

2. **Configurer les variables d'environnement**

Copiez le fichier `.env.example` et configurez vos valeurs :

```bash
cp .env.example .env
```

Modifiez le fichier `.env` avec vos propres valeurs, notamment :
- Les clés OAuth Google et Apple
- Le secret JWT pour la sécurité
- Les URLs de connexion

3. **Démarrer les services avec Docker Compose**

```bash
docker-compose up -d
```

Cela démarrera :
- PostgreSQL sur le port 5432
- Redis sur le port 6379
- Backend FastAPI sur le port 8000
- Frontend Next.js sur le port 3000

4. **Accéder à l'application**

- Frontend : http://localhost:3000
- API Backend : http://localhost:8000
- Documentation API : http://localhost:8000/docs

## Configuration OAuth

### Google OAuth

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet
3. Activez l'API Google+ 
4. Créez des identifiants OAuth 2.0
5. Ajoutez `http://localhost:3000` comme origine autorisée
6. Ajoutez `http://localhost:3000/api/auth/callback/google` comme URI de redirection
7. Copiez le Client ID et Client Secret dans votre `.env`

### Apple OAuth

1. Allez sur [Apple Developer](https://developer.apple.com/)
2. Configurez Sign in with Apple
3. Créez un Service ID
4. Configurez les domaines et URLs de redirection
5. Copiez les identifiants dans votre `.env`

## Développement

### Backend (FastAPI)

```bash
# Installer les dépendances
cd backend
pip install -r requirements.txt

# Lancer le serveur de développement
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Next.js)

```bash
# Installer les dépendances
cd frontend
npm install

# Lancer le serveur de développement
npm run dev
```

### Exécuter le scraper manuellement

```bash
cd backend
python scripts/scrape_specials.py
```

## Structure de la Base de Données

### Tables principales

- **users** : Utilisateurs authentifiés via OAuth
- **recipes** : Recettes avec ingrédients et instructions
- **recipe_tags** : Tags pour catégoriser les recettes
- **grocery_stores** : Magasins d'épiceries (IGA, Metro)
- **grocery_specials** : Spéciaux actuels des épiceries
- **shopping_lists** : Listes d'achats des utilisateurs
- **shopping_list_items** : Articles individuels avec correspondance aux spéciaux
- **ocr_jobs** : Suivi des tâches OCR
- **favorites** : Recettes favorites des utilisateurs

## API Endpoints

### Authentification
- `POST /api/auth/oauth/login` - Connexion OAuth
- `GET /api/auth/me` - Informations utilisateur actuel

### Recettes
- `GET /api/recipes/` - Liste des recettes publiques
- `GET /api/recipes/{id}` - Détails d'une recette

### OCR
- `POST /api/ocr/upload` - Télécharger une image de recette
- `GET /api/ocr/jobs/{id}` - Statut d'une tâche OCR

### Épiceries
- `GET /api/grocery/stores` - Liste des magasins
- `GET /api/grocery/specials` - Spéciaux actuels

### Listes d'achats
- `GET /api/shopping-lists/` - Listes de l'utilisateur
- `POST /api/shopping-lists/generate` - Générer une liste

Documentation complète disponible sur : http://localhost:8000/docs

## Scripts utilitaires

### Scraper de spéciaux d'épiceries

Le script `backend/scripts/scrape_specials.py` peut être exécuté manuellement ou configuré comme tâche cron :

```bash
# Exécution manuelle
cd backend
python scripts/scrape_specials.py

# Ajouter au crontab pour exécution quotidienne à 6h
0 6 * * * cd /path/to/le-grimoire/backend && python scripts/scrape_specials.py
```

## Licence

MIT

## Contribution

Les contributions sont les bienvenues ! Veuillez ouvrir une issue ou soumettre une pull request.

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.
