# Guide de développement - Le Grimoire

## Démarrage rapide

### Avec Docker (Recommandé)

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down

# Reconstruire les images
docker-compose build
```

### Sans Docker

#### Backend

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Démarrer le serveur
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Démarrer le serveur de développement
npm run dev
```

#### Base de données

```bash
# Démarrer PostgreSQL avec Docker
docker run -d \
  --name le-grimoire-db \
  -e POSTGRES_USER=grimoire \
  -e POSTGRES_PASSWORD=grimoire_password \
  -e POSTGRES_DB=le_grimoire \
  -p 5432:5432 \
  -v ./database/init.sql:/docker-entrypoint-initdb.d/init.sql \
  postgres:15-alpine
```

## Tests

### Tester l'API Backend

```bash
# Vérifier que l'API fonctionne
curl http://localhost:8000/

# Voir la documentation interactive
open http://localhost:8000/docs
```

### Tester les endpoints

```bash
# Lister les recettes
curl http://localhost:8000/api/recipes/

# Lister les magasins
curl http://localhost:8000/api/grocery/stores

# Health check
curl http://localhost:8000/api/health
```

### Tester le scraper

```bash
cd backend
python scripts/scrape_specials.py
```

## Structure du code

### Backend (FastAPI)

```
backend/
├── app/
│   ├── main.py              # Point d'entrée de l'application
│   ├── core/
│   │   ├── config.py        # Configuration de l'app
│   │   ├── database.py      # Connexion à la DB
│   │   └── security.py      # Utilitaires de sécurité
│   ├── models/              # Modèles SQLAlchemy
│   │   ├── user.py
│   │   ├── recipe.py
│   │   ├── grocery.py
│   │   ├── shopping_list.py
│   │   └── ocr_job.py
│   ├── api/                 # Routes API
│   │   ├── auth.py          # Authentification OAuth
│   │   ├── recipes.py       # CRUD recettes
│   │   ├── ocr.py           # Upload et OCR
│   │   ├── grocery.py       # Spéciaux d'épiceries
│   │   └── shopping_lists.py
│   └── services/            # Services métier
│       ├── ocr_service.py   # Service OCR
│       └── scraper_service.py
└── scripts/
    └── scrape_specials.py   # Script de scraping
```

### Frontend (Next.js)

```
frontend/
├── src/
│   └── app/
│       ├── layout.tsx       # Layout principal
│       ├── page.tsx         # Page d'accueil
│       ├── globals.css      # Styles globaux
│       ├── recipes/
│       │   └── page.tsx     # Liste des recettes
│       └── upload/
│           └── page.tsx     # Upload de recettes
└── public/                  # Fichiers statiques
```

## Dépannage

### Le backend ne démarre pas

1. Vérifier que PostgreSQL est démarré
2. Vérifier les variables d'environnement dans `.env`
3. Vérifier les logs : `docker-compose logs backend`

### Le frontend ne se connecte pas au backend

1. Vérifier que `NEXT_PUBLIC_API_URL` est défini dans `.env`
2. Vérifier que le backend est accessible sur le port 8000
3. Vérifier la configuration CORS dans `backend/app/main.py`

### Problèmes de base de données

```bash
# Recréer la base de données
docker-compose down -v
docker-compose up -d db

# Se connecter à la DB
docker exec -it le-grimoire-db psql -U grimoire -d le_grimoire
```

### Problèmes d'OCR

1. Vérifier que Tesseract est installé dans le conteneur backend
2. Vérifier les logs du backend lors de l'upload
3. Tester avec une image claire et bien contrastée

## Prochaines étapes

### Fonctionnalités à implémenter

1. **Authentification complète**
   - Intégrer Google OAuth réel
   - Intégrer Apple Sign In
   - Middleware d'authentification pour les routes protégées

2. **OCR avancé**
   - Améliorer le parsing des recettes
   - Ajouter la correction automatique
   - Support multi-langues

3. **Scraper de production**
   - Implémenter le scraping réel d'IGA
   - Implémenter le scraping réel de Metro
   - Gérer la pagination et les catégories
   - Ajouter le cache Redis

4. **Liste d'achats intelligente**
   - Algorithme de matching ingrédients/spéciaux
   - Calcul du meilleur magasin
   - Export PDF/email

5. **Interface utilisateur**
   - Page de détail de recette
   - Édition de recettes
   - Recherche avancée
   - Favoris et collections

6. **Tests**
   - Tests unitaires backend (pytest)
   - Tests d'intégration API
   - Tests frontend (Jest, React Testing Library)
   - Tests E2E (Playwright)

## Contributions

Avant de soumettre une PR :

1. Tester localement avec Docker
2. Vérifier que tous les endpoints fonctionnent
3. S'assurer que le code respecte les conventions
4. Mettre à jour la documentation si nécessaire

## Support

Pour toute question, ouvrir une issue sur GitHub.
