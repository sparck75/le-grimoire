#!/bin/bash

# Le Grimoire - Quick Start Script
# This script helps you quickly start the application with Docker Compose

echo "🧙 Le Grimoire - Quick Start"
echo "=============================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker Desktop."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé."
    exit 1
fi

echo "✅ Docker et Docker Compose sont installés"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Le fichier .env n'existe pas. Création à partir de .env.example..."
    cp .env.example .env
    echo "✅ Fichier .env créé. Veuillez le configurer avec vos valeurs OAuth."
    echo ""
fi

# Start services
echo "🚀 Démarrage des services Docker..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "⏳ Attente du démarrage des services..."
sleep 10

# Check service health
echo ""
echo "🔍 Vérification de l'état des services..."
docker-compose ps

echo ""
echo "✨ L'application est prête!"
echo ""
echo "📍 Accès aux services:"
echo "   - Frontend:     http://localhost:3000"
echo "   - Backend API:  http://localhost:8000"
echo "   - API Docs:     http://localhost:8000/docs"
echo "   - PostgreSQL:   localhost:5432"
echo "   - Redis:        localhost:6379"
echo ""
echo "📖 Pour voir les logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Pour arrêter l'application:"
echo "   docker-compose down"
echo ""
echo "📚 Consultez README.md et DEVELOPMENT.md pour plus d'informations"
