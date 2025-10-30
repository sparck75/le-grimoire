# Le Grimoire 📚

Application web moderne de gestion de recettes avec reconnaissance OCR, intégration d'ingrédients OpenFoodFacts (5,942 ingrédients), et génération de listes de courses intelligentes.

## ✨ Fonctionnalités principales

- 🔍 **Bibliothèque de recettes** - Parcourez, recherchez et filtrez des recettes avec interface moderne
- 🥕 **Ingrédients OpenFoodFacts** - 5,942 ingrédients multilingues (50+ langues) avec autocomplete
- 🍷 **Cave à vin LWIN** - Intégration base de données LWIN (200,000+ vins) avec identification universelle
- 📸 **AI Wine Extraction** - Scan d'étiquettes de vin avec GPT-4 Vision et enrichissement automatique
- 📝 **Éditeur avancé** - Créez et modifiez des recettes avec liaison optionnelle aux ingrédients
- 📊 **Tableau de bord admin** - Statistiques, filtres multiples, sélection et suppression en masse
- 🛒 **Listes de courses** - Génération automatique avec intégration des spéciaux IGA/Metro
- 📷 **OCR** - Extraction automatique de recettes à partir d'images
- 🌍 **Multilingue** - Interface en français, ingrédients en 50+ langues

## 🚀 Démarrage rapide

```bash
git clone https://github.com/sparck75/le-grimoire.git
cd le-grimoire
docker-compose up -d
```

**Accès** :
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

📖 **[Guide complet de démarrage](docs/getting-started/QUICKSTART.md)**

## 🏗️ Stack technologique

- **Frontend**: Next.js 14 (TypeScript, React 18)
- **Backend**: FastAPI (Python 3.11)
- **Base de données**: MongoDB avec Beanie ODM
- **Ingrédients**: OpenFoodFacts Taxonomy (5,942 items)
- **Vins**: LWIN Database (200,000+ vins avec codes universels)
- **OCR**: Tesseract
- **Conteneurisation**: Docker & Docker Compose
- **Web Scraping**: BeautifulSoup4, Selenium

## 📁 Structure du projet

```
le-grimoire/
├── backend/              # API FastAPI
│   ├── app/
│   │   ├── api/         # Endpoints REST
│   │   ├── models/      # Modèles MongoDB (Beanie)
│   │   ├── services/    # OCR, Scraper
│   │   └── core/        # Config, Database, Security
│   └── scripts/         # Import OpenFoodFacts, etc.
├── frontend/            # Application Next.js
│   └── src/app/         # Pages et composants
├── docs/                # Documentation complète
│   ├── getting-started/ # Guides de démarrage
│   ├── architecture/    # Architecture et API
│   ├── development/     # Guides dev
│   ├── features/        # Documentation fonctionnalités
│   └── migrations/      # Historique migrations
├── docker-compose.yml   # Configuration Docker
└── .env.example         # Variables d'environnement

```

## 📚 Documentation

### Pour commencer
- 📖 [Guide de démarrage rapide](docs/getting-started/QUICKSTART.md)
- 🏗️ [Architecture du système](docs/architecture/OVERVIEW.md)
- 👨‍💻 [Guide de développement](docs/development/DEVELOPMENT.md)
- 🤝 [Guide de contribution](docs/getting-started/CONTRIBUTING.md)

### Déploiement et Opérations
- 🚀 [Guide de déploiement](docs/deployment/README.md)
- 🌐 [Déploiement sur Vultr](docs/deployment/VULTR_DEPLOYMENT.md)
- 🔧 [Configuration DNS GoDaddy](docs/deployment/GODADDY_DNS.md)
- 🔒 [Guide de sécurité](docs/deployment/SECURITY.md)
- 💾 [Sauvegarde et Restauration](docs/operations/BACKUP_RESTORE.md)
- ⚙️ [Opérations quotidiennes](docs/operations/README.md)

### Fonctionnalités
- 🥕 [Système d'ingrédients](docs/development/INGREDIENTS.md)
- 🍷 [Intégration LWIN (Cave à vin)](docs/features/LWIN_INTEGRATION.md)
- 📸 [AI Wine Extraction (Scan d'étiquettes)](docs/features/AI_WINE_EXTRACTION.md)
- 📊 [API Reference](docs/architecture/API_REFERENCE.md)
- 🌍 [Localisation française](docs/features/FRENCH_LOCALIZATION.md)
- 📈 [Statut du projet](docs/PROJECT_STATUS.md)

## 🛠️ Commandes utiles

```bash
# Démarrer l'application
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter l'application
docker-compose down

# Redémarrer un service
docker-compose restart backend

# Accéder à MongoDB
docker-compose exec mongodb mongosh le_grimoire

# Compter les ingrédients
docker-compose exec mongodb mongosh --eval "use le_grimoire; db.ingredients.countDocuments()"

# Exécuter les tests E2E
cd frontend && npm test
```

## 🧪 Tests

Le projet inclut des tests E2E automatisés avec Playwright :

```bash
cd frontend

# Exécuter tous les tests
npm test

# Mode visuel (voir le navigateur)
npm run test:headed

# Mode UI interactif
npm run test:ui
```

Les tests s'exécutent automatiquement dans la CI/CD sur chaque push et pull request.

📖 **[Documentation complète des tests](frontend/tests/README.md)**

## � Développement local

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

**Voir le [Guide de développement](docs/development/DEVELOPMENT.md) pour plus de détails.**

## 📊 Collections MongoDB

- **ingredients** (5,942) - Taxonomie OpenFoodFacts avec noms multilingues
- **wines** - Cave à vin avec codes LWIN et données détaillées
- **liquors** - Cave à spiritueux
- **recipes** - Recettes avec ingrédients et instructions
- **users** - Utilisateurs authentifiés (OAuth)
- **shopping_lists** - Listes de courses
- **ocr_jobs** - Tâches OCR

## 🔌 API Endpoints principaux

**v2 API**:
- `GET /api/v2/recipes/` - Liste et recherche de recettes
- `GET /api/v2/ingredients/?search={term}&language={lang}` - Recherche d'ingrédients
- `GET /api/v2/lwin/search` - Recherche de vins LWIN
- `GET /api/v2/lwin/code/{lwin}` - Recherche par code LWIN
- `POST /api/v2/recipes/` - Créer une recette
- `GET /api/stats/dashboard` - Statistiques

**Documentation interactive** : http://localhost:8000/docs

## 🤝 Contribution

Les contributions sont les bienvenues! Consultez le [Guide de contribution](docs/getting-started/CONTRIBUTING.md).

### Processus de contribution
1. Fork le projet
2. Créez une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout de ma fonctionnalité'`)
4. Push vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrez une Pull Request

## 📄 License

Ce projet est sous license MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [OpenFoodFacts](https://world.openfoodfacts.org/) pour la taxonomie d'ingrédients
- [Next.js](https://nextjs.org/) et [FastAPI](https://fastapi.tiangolo.com/) pour les frameworks
- Tous les contributeurs du projet

## 📞 Support

- 📖 [Documentation complète](docs/README.md)
- 🐛 [Signaler un bug](https://github.com/sparck75/le-grimoire/issues)
- 💡 [Proposer une fonctionnalité](https://github.com/sparck75/le-grimoire/issues)

---

**Le Grimoire** - Votre compagnon culinaire numérique 👨‍🍳

## Contribution

Les contributions sont les bienvenues ! Veuillez ouvrir une issue ou soumettre une pull request.

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.
