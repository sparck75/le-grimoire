#!/bin/bash

# Le Grimoire - Production Deployment Script
# This script sets up the production environment on the Vultr server

set -e  # Exit on error

echo "=========================================="
echo "Le Grimoire - Production Deployment"
echo "=========================================="
echo ""

# Check if running in the correct directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: docker-compose.prod.yml not found!"
    echo "Please run this script from the le-grimoire directory."
    exit 1
fi

# Step 1: Fetch and checkout the branch with fixes
echo "📥 Step 1: Fetching latest code..."
git fetch origin copilot/implement-ui-testing-playwright
git checkout copilot/implement-ui-testing-playwright
git pull origin copilot/implement-ui-testing-playwright
echo "✅ Code updated successfully"
echo ""

# Step 2: Check if .env.production already exists
if [ -f ".env.production" ]; then
    echo "⚠️  .env.production already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing .env.production file"
        ENV_EXISTS=true
    else
        ENV_EXISTS=false
    fi
else
    ENV_EXISTS=false
fi

# Step 3: Generate .env.production with secure values
if [ "$ENV_EXISTS" = false ]; then
    echo "🔐 Step 2: Generating .env.production with secure values..."
    
    # Generate secure random keys
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    MONGODB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")
    POSTGRES_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")
    
    echo "Generated secure keys ✓"
    
    # Create .env.production
    cat > .env.production << EOF
# Le Grimoire - Production Environment Configuration
# Generated on $(date)

# ===== Database Configuration =====

# MongoDB (Primary Database)
MONGODB_USER=legrimoire
MONGODB_PASSWORD=${MONGODB_PASSWORD}
MONGODB_URL=mongodb://legrimoire:${MONGODB_PASSWORD}@mongodb:27017/legrimoire?authSource=admin
MONGODB_DB_NAME=legrimoire

# PostgreSQL (Legacy/Optional - for backward compatibility)
POSTGRES_USER=grimoire
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=le_grimoire
DATABASE_URL=postgresql://grimoire:${POSTGRES_PASSWORD}@db:5432/le_grimoire

# ===== Application Secrets =====

# Backend secret key for session encryption
SECRET_KEY=${SECRET_KEY}

# JWT token encryption key
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# ===== Frontend Configuration =====

# Public API URL (accessible from browser)
NEXT_PUBLIC_API_URL=https://legrimoireonline.ca

# Backend URL for server-side requests (internal Docker network)
BACKEND_URL=http://backend:8000

# ===== Redis Configuration =====

REDIS_URL=redis://redis:6379

# ===== OAuth Configuration (Optional) =====

# Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Apple OAuth
APPLE_CLIENT_ID=
APPLE_CLIENT_SECRET=

# ===== Email Configuration (Optional) =====

SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=noreply@legrimoireonline.ca

# ===== Environment =====

ENVIRONMENT=production
DEBUG=false
EOF

    chmod 600 .env.production  # Secure permissions
    
    echo "✅ .env.production created with secure credentials"
    echo ""
    echo "📝 Important: The following passwords have been generated:"
    echo "   - MongoDB Password: ${MONGODB_PASSWORD}"
    echo "   - PostgreSQL Password: ${POSTGRES_PASSWORD}"
    echo ""
    echo "⚠️  Please save these passwords securely!"
    echo "   They are stored in .env.production (chmod 600)"
    echo ""
    read -p "Press Enter to continue..."
fi

# Step 4: Create necessary directories
echo "📁 Step 3: Creating necessary directories..."
mkdir -p nginx/ssl
mkdir -p data/mongodb
mkdir -p backups
mkdir -p backend/uploads
echo "✅ Directories created"
echo ""

# Step 5: Build Docker images
echo "🐳 Step 4: Building Docker images..."
echo "This may take several minutes..."
docker compose -f docker-compose.prod.yml build
echo "✅ Docker images built successfully"
echo ""

# Step 6: Display next steps
echo "=========================================="
echo "✅ Deployment preparation complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. 📜 Configure SSL certificates (if not done yet):"
echo "   sudo certbot certonly --standalone -d legrimoireonline.ca -d www.legrimoireonline.ca"
echo "   sudo cp /etc/letsencrypt/live/legrimoireonline.ca/*.pem ~/apps/le-grimoire/nginx/ssl/"
echo "   sudo chown legrimoire:legrimoire ~/apps/le-grimoire/nginx/ssl/*"
echo ""
echo "2. 🚀 Start the application:"
echo "   docker compose -f docker-compose.prod.yml up -d"
echo ""
echo "3. 📊 Monitor the logs:"
echo "   docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo "4. ✅ Verify deployment:"
echo "   curl http://localhost/api/health"
echo "   Visit https://legrimoireonline.ca"
echo ""
echo "5. 🗄️  Import ingredients (optional):"
echo "   docker compose -f docker-compose.prod.yml exec backend python scripts/import_off_ingredients.py"
echo ""
echo "=========================================="
