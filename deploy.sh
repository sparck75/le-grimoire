#!/bin/bash

# Le Grimoire Production Deployment Script
# This script helps deploy Le Grimoire to production

set -e  # Exit on any error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env.production exists
check_env_file() {
    if [ ! -f .env.production ]; then
        log_error ".env.production file not found!"
        log_info "Please create .env.production from .env.production.example"
        log_info "Run: cp .env.production.example .env.production"
        exit 1
    fi
    log_success ".env.production file found"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed!"
        log_info "Please install Docker first"
        exit 1
    fi
    log_success "Docker is installed"
}

# Check if Docker Compose is installed
check_docker_compose() {
    if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed!"
        log_info "Please install Docker Compose first"
        exit 1
    fi
    log_success "Docker Compose is installed"
}

# Check if SSL certificates exist
check_ssl_certs() {
    if [ ! -f nginx/ssl/fullchain.pem ] || [ ! -f nginx/ssl/privkey.pem ]; then
        log_warning "SSL certificates not found in nginx/ssl/"
        log_info "Make sure to obtain SSL certificates with Let's Encrypt"
        log_info "See docs/deployment/VULTR_DEPLOYMENT.md for instructions"
        return 1
    fi
    log_success "SSL certificates found"
    return 0
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    mkdir -p nginx/ssl
    mkdir -p data/mongodb
    mkdir -p backups
    log_success "Directories created"
}

# Pull latest code from git
pull_latest_code() {
    log_info "Pulling latest code from git..."
    git pull origin main || {
        log_warning "Failed to pull latest code. Continuing with current version..."
    }
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    docker compose -f docker-compose.prod.yml build --no-cache
    log_success "Docker images built"
}

# Start services
start_services() {
    log_info "Starting services..."
    docker compose -f docker-compose.prod.yml up -d
    log_success "Services started"
}

# Stop services
stop_services() {
    log_info "Stopping services..."
    docker compose -f docker-compose.prod.yml down
    log_success "Services stopped"
}

# Restart services
restart_services() {
    log_info "Restarting services..."
    docker compose -f docker-compose.prod.yml restart
    log_success "Services restarted"
}

# Show logs
show_logs() {
    log_info "Showing logs (Ctrl+C to exit)..."
    docker compose -f docker-compose.prod.yml logs -f
}

# Show status
show_status() {
    log_info "Showing service status..."
    docker compose -f docker-compose.prod.yml ps
}

# Backup MongoDB
backup_mongodb() {
    log_info "Creating MongoDB backup..."
    BACKUP_DIR="backups"
    DATE=$(date +%Y%m%d_%H%M%S)
    CONTAINER="le-grimoire-mongodb-prod"
    
    mkdir -p "$BACKUP_DIR"
    
    docker exec $CONTAINER mongodump \
        --out /tmp/backup_$DATE \
        --authenticationDatabase admin \
        -u legrimoire || {
            log_error "MongoDB backup failed!"
            return 1
        }
    
    docker cp $CONTAINER:/tmp/backup_$DATE "$BACKUP_DIR/mongodb_backup_$DATE"
    
    cd "$BACKUP_DIR"
    tar -czf "mongodb_backup_$DATE.tar.gz" "mongodb_backup_$DATE"
    rm -rf "mongodb_backup_$DATE"
    
    log_success "Backup saved to: $BACKUP_DIR/mongodb_backup_$DATE.tar.gz"
}

# Import ingredients
import_ingredients() {
    log_info "Importing OpenFoodFacts ingredients..."
    docker compose -f docker-compose.prod.yml exec backend python scripts/import_openfoodfacts.py
    log_success "Ingredients imported"
}

# Main menu
show_menu() {
    echo ""
    echo "========================================="
    echo "  Le Grimoire - Production Deployment"
    echo "========================================="
    echo ""
    echo "1) Deploy (first time setup)"
    echo "2) Update (pull latest code and rebuild)"
    echo "3) Start services"
    echo "4) Stop services"
    echo "5) Restart services"
    echo "6) Show logs"
    echo "7) Show status"
    echo "8) Backup MongoDB"
    echo "9) Import ingredients"
    echo "0) Exit"
    echo ""
    read -p "Select an option: " choice
    
    case $choice in
        1)
            deploy_first_time
            ;;
        2)
            update_deployment
            ;;
        3)
            start_services
            ;;
        4)
            stop_services
            ;;
        5)
            restart_services
            ;;
        6)
            show_logs
            ;;
        7)
            show_status
            ;;
        8)
            backup_mongodb
            ;;
        9)
            import_ingredients
            ;;
        0)
            log_info "Exiting..."
            exit 0
            ;;
        *)
            log_error "Invalid option"
            show_menu
            ;;
    esac
}

# First time deployment
deploy_first_time() {
    log_info "Starting first-time deployment..."
    
    check_docker
    check_docker_compose
    check_env_file
    create_directories
    
    if ! check_ssl_certs; then
        log_error "Cannot proceed without SSL certificates"
        log_info "Please follow the SSL certificate setup instructions in:"
        log_info "docs/deployment/VULTR_DEPLOYMENT.md"
        exit 1
    fi
    
    build_images
    start_services
    
    log_info "Waiting for services to start (30 seconds)..."
    sleep 30
    
    log_info "Checking if MongoDB needs ingredients..."
    docker compose -f docker-compose.prod.yml exec mongodb mongosh legrimoire --eval "db.ingredients.countDocuments()" || {
        log_info "Importing ingredients..."
        import_ingredients
    }
    
    show_status
    
    log_success "Deployment completed!"
    log_info "Your application should now be accessible at https://legrimoireonline.ca"
}

# Update existing deployment
update_deployment() {
    log_info "Updating deployment..."
    
    check_docker
    check_docker_compose
    check_env_file
    
    log_info "Creating backup before update..."
    backup_mongodb
    
    pull_latest_code
    build_images
    
    log_info "Restarting services with new images..."
    docker compose -f docker-compose.prod.yml up -d
    
    log_info "Waiting for services to restart (30 seconds)..."
    sleep 30
    
    show_status
    
    log_success "Update completed!"
}

# Run the menu
if [ $# -eq 0 ]; then
    show_menu
else
    case $1 in
        deploy)
            deploy_first_time
            ;;
        update)
            update_deployment
            ;;
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        backup)
            backup_mongodb
            ;;
        import-ingredients)
            import_ingredients
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Usage: $0 [deploy|update|start|stop|restart|logs|status|backup|import-ingredients]"
            exit 1
            ;;
    esac
fi
