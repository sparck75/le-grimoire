# Architecture de Le Grimoire

## Vue d'ensemble

Le Grimoire est une application web full-stack pour la gestion de recettes avec reconnaissance optique de caractères (OCR) et intégration des spéciaux d'épiceries.

## Diagramme d'architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          UTILISATEUR                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NGINX (Reverse Proxy)                         │
│                         Port 80/443                              │
└────────────┬──────────────────────────────┬─────────────────────┘
             │                              │
             ▼                              ▼
┌────────────────────────┐      ┌─────────────────────────────────┐
│   FRONTEND (Next.js)   │      │    BACKEND (FastAPI)            │
│      Port 3000         │      │       Port 8000                 │
│                        │      │                                 │
│  ├── App Router        │      │  ├── API Routes                │
│  ├── Pages             │◄─────┤  │   ├── /auth                 │
│  │   ├── Home          │      │  │   ├── /recipes              │
│  │   ├── Recipes       │      │  │   ├── /ocr                  │
│  │   └── Upload        │      │  │   ├── /grocery              │
│  ├── Components        │      │  │   └── /shopping-lists       │
│  └── Styles            │      │  ├── Services                  │
│                        │      │  │   ├── OCR Service           │
│                        │      │  │   └── Scraper Service       │
│                        │      │  ├── Models (SQLAlchemy)       │
│                        │      │  └── Core                       │
│                        │      │      ├── Config                │
│                        │      │      ├── Database              │
│                        │      │      └── Security              │
└────────────────────────┘      └────────┬────────────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
         ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐
         │   PostgreSQL    │  │      Redis       │  │   Tesseract    │
         │   Database      │  │     Cache        │  │   OCR Engine   │
         │   Port 5432     │  │   Port 6379      │  │   (in backend) │
         │                 │  │                  │  │                │
         │ ├── users       │  │ ├── Sessions    │  │ ├── French     │
         │ ├── recipes     │  │ ├── Cache       │  │ └── English    │
         │ ├── grocery_*   │  │ └── Task Queue  │  │                │
         │ ├── shopping_*  │  │                  │  │                │
         │ └── ocr_jobs    │  │                  │  │                │
         └─────────────────┘  └──────────────────┘  └────────────────┘
                    │
                    ▼
         ┌─────────────────┐
         │  External APIs  │
         │                 │
         │ ├── Google OAuth│
         │ ├── Apple OAuth │
         │ ├── IGA.net     │
         │ └── Metro.ca    │
         └─────────────────┘
```

## Composants principaux

### 1. Frontend (Next.js 14)

**Responsabilités:**
- Affichage de l'interface utilisateur
- Gestion de l'état côté client
- Communication avec l'API backend
- Routage et navigation
- Rendu côté serveur (SSR) pour SEO

**Technologies:**
- Next.js 14 avec App Router
- TypeScript
- React 18
- CSS Modules
- SWR pour la gestion des données

**Structure:**
```
src/app/
├── layout.tsx          # Layout principal
├── page.tsx            # Page d'accueil
├── globals.css         # Styles globaux
├── recipes/
│   └── page.tsx        # Liste des recettes
└── upload/
    └── page.tsx        # Upload de recettes
```

### 2. Backend (FastAPI)

**Responsabilités:**
- API REST pour toutes les opérations
- Authentification OAuth
- Traitement OCR des images
- Scraping des spéciaux d'épiceries
- Gestion de la base de données
- Logique métier

**Technologies:**
- FastAPI
- SQLAlchemy (ORM)
- Pydantic (validation)
- Python-Jose (JWT)
- Pytesseract (OCR)
- BeautifulSoup4 & Selenium (scraping)

**Structure:**
```
app/
├── main.py             # Point d'entrée
├── api/                # Routes API
│   ├── auth.py
│   ├── recipes.py
│   ├── ocr.py
│   ├── grocery.py
│   └── shopping_lists.py
├── models/             # Modèles de données
│   ├── user.py
│   ├── recipe.py
│   ├── grocery.py
│   ├── shopping_list.py
│   └── ocr_job.py
├── services/           # Services métier
│   ├── ocr_service.py
│   └── scraper_service.py
└── core/               # Configuration
    ├── config.py
    ├── database.py
    └── security.py
```

### 3. Base de données (PostgreSQL)

**Responsabilités:**
- Stockage persistant des données
- Gestion des relations
- Transactions ACID
- Performance via indexes

**Schéma:**
```
users                   # Utilisateurs OAuth
├── id (UUID)
├── email
├── name
├── oauth_provider
└── oauth_provider_id

recipes                 # Recettes
├── id (UUID)
├── title
├── ingredients[]
├── instructions
├── user_id (FK)
└── is_public

grocery_stores          # Magasins
├── id (UUID)
├── name
└── code

grocery_specials        # Spéciaux
├── id (UUID)
├── store_id (FK)
├── product_name
├── special_price
└── valid_from/until

shopping_lists          # Listes d'achats
├── id (UUID)
├── user_id (FK)
└── name

shopping_list_items     # Articles
├── id (UUID)
├── shopping_list_id (FK)
├── ingredient_name
└── matched_special_id (FK)

ocr_jobs                # Jobs OCR
├── id (UUID)
├── user_id (FK)
├── image_path
├── status
└── extracted_text
```

### 4. Redis

**Responsabilités:**
- Cache des données fréquentes
- Sessions utilisateurs
- File d'attente pour les tâches asynchrones
- Rate limiting pour le scraping

### 5. Services externes

**OAuth Providers:**
- Google OAuth 2.0
- Apple Sign In

**Sites web scrapés:**
- IGA.net (spéciaux d'épicerie)
- Metro.ca (spéciaux d'épicerie)

## Flux de données

### 1. Consultation de recettes (public)

```
Utilisateur → Frontend → Backend API → PostgreSQL → Backend → Frontend → Utilisateur
```

### 2. Soumission de recette avec OCR (authentifié)

```
Utilisateur → OAuth Login → Backend (JWT) → Frontend
     ↓
Upload Image → Backend → Tesseract OCR
     ↓
Extracted Text → Parse Recipe → PostgreSQL
     ↓
Recipe Created → Frontend → Utilisateur
```

### 3. Génération de liste d'achats

```
Utilisateur → Select Recipes → Backend
     ↓
Extract Ingredients → Match with Specials (PostgreSQL)
     ↓
Scraper Service → IGA/Metro (if needed)
     ↓
Generate Shopping List → PostgreSQL → Frontend → Utilisateur
```

### 4. Scraping automatique

```
Cron Job → Backend Script
     ↓
Scraper Service → IGA/Metro Websites
     ↓
Parse HTML → Extract Specials
     ↓
Save to PostgreSQL (grocery_specials)
```

## Sécurité

### Authentification
- OAuth 2.0 pour Google et Apple
- JWT tokens pour les sessions
- Tokens avec expiration (7 jours par défaut)

### API
- CORS configuré pour les origines autorisées
- Rate limiting sur les endpoints sensibles
- Validation des données avec Pydantic

### Base de données
- Connexions sécurisées (credentials dans .env)
- SQL injection prévenue par SQLAlchemy ORM
- Foreign keys avec contraintes

### Uploads
- Validation du type de fichier
- Limite de taille (10MB)
- Scan antivirus recommandé en production

## Scalabilité

### Horizontal Scaling
- Frontend: Multiples instances Next.js derrière Nginx
- Backend: Multiples workers FastAPI
- Database: Read replicas PostgreSQL

### Caching
- Redis pour cache applicatif
- Nginx pour cache des assets statiques
- Browser caching pour frontend

### Task Queue
- Redis comme message broker
- Celery ou RQ pour tâches asynchrones
- OCR et scraping en arrière-plan

## Monitoring et Logs

### Logs
- Backend: Structured logging avec Python logging
- Frontend: Console logs en dev, service en prod
- Nginx: Access et error logs

### Metrics (à implémenter)
- Prometheus pour métriques
- Grafana pour visualisation
- Alerting sur erreurs critiques

### Health Checks
- `/health` endpoint sur backend
- `/api/health` avec status des services
- Docker health checks

## Déploiement

### Développement
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### CI/CD (à implémenter)
- GitHub Actions pour tests automatiques
- Build et push des images Docker
- Déploiement automatique sur staging/prod

## Performance

### Optimisations frontend
- Server-Side Rendering (SSR)
- Static Site Generation (SSG) pour pages statiques
- Image optimization avec Next.js
- Code splitting automatique

### Optimisations backend
- Database indexes sur colonnes fréquentes
- Connection pooling pour PostgreSQL
- Compression des réponses (gzip)
- Pagination des résultats

### Optimisations base de données
- Indexes sur foreign keys
- Indexes sur colonnes de recherche
- Query optimization
- Vacuuming régulier

## Évolutions futures

### Court terme
- Tests unitaires et d'intégration
- Authentication middleware complet
- OCR avec AI/ML pour meilleure précision
- Scraping réel des sites IGA et Metro

### Moyen terme
- Application mobile (React Native)
- Export PDF des listes d'achats
- Partage de recettes par lien
- Notifications push

### Long terme
- Recommandations de recettes par AI
- Planification de repas
- Calcul nutritionnel
- Intégration avec services de livraison

## Support

Pour plus d'informations, consultez:
- [README.md](README.md) - Installation et utilisation
- [DEVELOPMENT.md](DEVELOPMENT.md) - Guide de développement
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution au projet
