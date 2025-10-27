#!/bin/bash

# Le Grimoire - Production Update Script
# Use this to update an existing deployment with the latest code

set -e  # Exit on error

echo "=========================================="
echo "Le Grimoire - Production Update"
echo "=========================================="
echo ""

# Check if running in the correct directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: docker-compose.prod.yml not found!"
    echo "Please run this script from the le-grimoire directory."
    exit 1
fi

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production not found!"
    echo "Please run deploy-production.sh first to set up the environment."
    exit 1
fi

# Step 1: Backup current data
echo "💾 Step 1: Creating backup..."
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
MONGODB_CONTAINER="le-grimoire-mongodb-prod"

mkdir -p "$BACKUP_DIR"

# Get MongoDB password from .env.production
MONGODB_PASSWORD=$(grep MONGODB_PASSWORD .env.production | cut -d '=' -f2)

# Check if MongoDB container is running
if docker ps --format '{{.Names}}' | grep -q "^${MONGODB_CONTAINER}$"; then
    echo "Creating MongoDB backup..."
    
    # Try to create backup inside container
    if docker exec $MONGODB_CONTAINER mongodump \
        --out /tmp/backup_$DATE \
        --authenticationDatabase admin \
        -u legrimoire \
        -p "$MONGODB_PASSWORD" 2>/dev/null; then
        
        # Copy backup out of container
        docker cp $MONGODB_CONTAINER:/tmp/backup_$DATE "$BACKUP_DIR/mongodb_backup_$DATE"
        
        # Compress backup
        cd "$BACKUP_DIR"
        tar -czf "mongodb_backup_$DATE.tar.gz" "mongodb_backup_$DATE"
        rm -rf "mongodb_backup_$DATE"
        cd ..
        
        # Clean up inside container
        docker exec $MONGODB_CONTAINER rm -rf /tmp/backup_$DATE 2>/dev/null || true
        
        echo "✅ Backup saved to: $BACKUP_DIR/mongodb_backup_$DATE.tar.gz"
    else
        echo "⚠️  Backup failed - mongodump error (check credentials or database status)"
    fi
else
    echo "⚠️  MongoDB container not running - skipping backup"
fi
echo ""

# Step 2: Pull latest code
echo "📥 Step 2: Pulling latest code..."
git pull origin main
echo "✅ Code updated"
echo ""

# Step 3: Check for environment changes
echo "🔍 Step 3: Checking environment configuration..."
if ! grep -q "ALLOWED_ORIGINS=" .env.production; then
    echo "⚠️  Adding missing ALLOWED_ORIGINS to .env.production..."
    echo "" >> .env.production
    echo "# CORS Configuration" >> .env.production
    echo "ALLOWED_ORIGINS=https://legrimoireonline.ca,https://www.legrimoireonline.ca" >> .env.production
    echo "✅ ALLOWED_ORIGINS added"
fi

if ! grep -q "NEXT_PUBLIC_API_URL=https://" .env.production; then
    echo "⚠️  WARNING: NEXT_PUBLIC_API_URL should use HTTPS!"
    echo "   Current value: $(grep NEXT_PUBLIC_API_URL .env.production)"
    echo "   Recommended: NEXT_PUBLIC_API_URL=https://legrimoireonline.ca"
    echo ""
    read -p "Do you want to update it to HTTPS? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sed -i 's|NEXT_PUBLIC_API_URL=http://|NEXT_PUBLIC_API_URL=https://|g' .env.production
        echo "✅ Updated to HTTPS"
    fi
fi
echo ""

# Step 4: Rebuild images
echo "🐳 Step 4: Rebuilding Docker images..."
echo "This will rebuild both frontend and backend with latest code and environment variables"
echo ""

# Ask which services to rebuild
echo "Which services do you want to rebuild?"
echo "1) All services (recommended after code changes)"
echo "2) Frontend only (for NEXT_PUBLIC_API_URL or UI changes)"
echo "3) Backend only (for API or database changes)"
read -p "Select option (1-3): " rebuild_option

case $rebuild_option in
    1)
        echo "Rebuilding all services..."
        docker compose -f docker-compose.prod.yml build --no-cache
        RESTART_SERVICES="all"
        ;;
    2)
        echo "Rebuilding frontend only..."
        docker compose -f docker-compose.prod.yml build --no-cache frontend
        RESTART_SERVICES="frontend"
        ;;
    3)
        echo "Rebuilding backend only..."
        docker compose -f docker-compose.prod.yml build --no-cache backend
        RESTART_SERVICES="backend"
        ;;
    *)
        echo "Invalid option, rebuilding all services..."
        docker compose -f docker-compose.prod.yml build --no-cache
        RESTART_SERVICES="all"
        ;;
esac

echo "✅ Images rebuilt"
echo ""

# Step 5: Restart services
echo "🔄 Step 5: Restarting services..."
if [ "$RESTART_SERVICES" = "all" ]; then
    docker compose -f docker-compose.prod.yml up -d
else
    docker compose -f docker-compose.prod.yml up -d $RESTART_SERVICES
fi

echo "✅ Services restarted"
echo ""

# Step 6: Wait and check status
echo "⏳ Waiting for services to stabilize (10 seconds)..."
sleep 10

echo "📊 Current service status:"
docker compose -f docker-compose.prod.yml ps
echo ""

# Step 7: Show logs
echo "=========================================="
echo "✅ Update complete!"
echo "=========================================="
echo ""
echo "📋 Recent logs (Ctrl+C to exit):"
echo ""
sleep 2
docker compose -f docker-compose.prod.yml logs --tail=50 -f
