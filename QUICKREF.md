# Le Grimoire - Quick Reference

## 🚀 Quick Start

```bash
# Clone and start
git clone https://github.com/sparck75/le-grimoire.git
cd le-grimoire
./quick-start.sh

# Or manually:
cp .env.example .env
docker-compose up -d
```

## 📍 URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js application |
| Backend API | http://localhost:8000 | FastAPI REST API |
| API Docs | http://localhost:8000/docs | Interactive Swagger UI |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache & Queue |

## 🔑 Default Credentials

```
Database:
- User: grimoire
- Password: grimoire_password
- Database: le_grimoire
```

⚠️ **Change in production!**

## 📂 Project Structure

```
le-grimoire/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # REST endpoints
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic
│   │   └── core/     # Config & utils
│   └── scripts/      # Utility scripts
├── frontend/         # Next.js application
│   └── src/app/      # Pages & components
├── database/         # SQL schemas
└── nginx/           # Reverse proxy config
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [service]

# Rebuild images
docker-compose build

# Restart a service
docker-compose restart [service]

# Remove volumes (⚠️ deletes data)
docker-compose down -v
```

## 🔧 Development Commands

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run dev server
uvicorn app.main:app --reload

# Run scraper
python scripts/scrape_specials.py

# Database migrations (when implemented)
alembic revision --autogenerate -m "message"
alembic upgrade head
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint
npm run lint
```

### Database

```bash
# Connect to database
docker exec -it le-grimoire-db psql -U grimoire -d le_grimoire

# View tables
\dt

# View table schema
\d table_name

# Exit
\q
```

## 📝 API Endpoints

### Authentication
```
POST /api/auth/oauth/login      # OAuth login
GET  /api/auth/me               # Current user
```

### Recipes
```
GET  /api/recipes/              # List recipes
GET  /api/recipes/{id}          # Get recipe
POST /api/recipes/              # Create recipe*
PUT  /api/recipes/{id}          # Update recipe*
DELETE /api/recipes/{id}        # Delete recipe*
```

### OCR
```
POST /api/ocr/upload            # Upload image*
GET  /api/ocr/jobs/{id}         # Job status
```

### Grocery
```
GET  /api/grocery/stores        # List stores
GET  /api/grocery/specials      # List specials
```

### Shopping Lists
```
GET  /api/shopping-lists/       # User's lists*
POST /api/shopping-lists/generate # Generate list*
```

**\* = Requires authentication**

## 🧪 Testing

```bash
# Test API health
curl http://localhost:8000/

# Test recipe listing
curl http://localhost:8000/api/recipes/

# Test with authentication (replace TOKEN)
curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8000/api/ocr/upload
```

## 🐛 Common Issues

### Port already in use
```bash
# Find process using port
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Kill process
kill -9 PID
```

### Database connection error
```bash
# Check DB is running
docker ps | grep postgres

# Restart database
docker-compose restart db

# Check logs
docker-compose logs db
```

### Frontend can't reach backend
```bash
# Check NEXT_PUBLIC_API_URL in .env
# Default should be: http://localhost:8000

# Check CORS settings in backend/app/main.py
```

## 📊 Database Schema

### Main Tables
- `users` - OAuth authenticated users
- `recipes` - Recipe data with ingredients
- `grocery_stores` - IGA, Metro, etc.
- `grocery_specials` - Current deals
- `shopping_lists` - User shopping lists
- `shopping_list_items` - Items with special matching
- `ocr_jobs` - OCR processing status

## 🔐 Environment Variables

### Required
```env
DATABASE_URL=postgresql://...
SECRET_KEY=...
JWT_SECRET_KEY=...
```

### OAuth (for recipe submission)
```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
APPLE_CLIENT_ID=...
APPLE_CLIENT_SECRET=...
```

### Frontend
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=...
NEXT_PUBLIC_APPLE_CLIENT_ID=...
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Installation & usage |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Dev guide |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Current status |

## 🆘 Getting Help

1. Check documentation above
2. Search [GitHub Issues](https://github.com/sparck75/le-grimoire/issues)
3. Create new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details

## 💡 Tips

- Use `docker-compose logs -f` to watch all logs
- API docs at `/docs` are interactive - try endpoints there
- Frontend hot-reloads on save
- Backend auto-reloads with uvicorn --reload
- Use Redis CLI: `docker exec -it le-grimoire-redis redis-cli`

## 🎯 Next Steps

1. Configure OAuth credentials
2. Implement real scraping logic
3. Add tests
4. Deploy to production

---

**Happy coding! 🧙‍♂️**
