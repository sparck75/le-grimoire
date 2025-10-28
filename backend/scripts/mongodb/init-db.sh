#!/bin/bash

# MongoDB Initialization Script for Le Grimoire
# This script runs on container startup to ensure database is properly initialized
# It checks if collections exist and creates indexes if needed

set -e

echo "========================================"
echo "Le Grimoire - MongoDB Initialization"
echo "========================================"

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
until mongosh --quiet --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    echo "   MongoDB is unavailable - sleeping"
    sleep 2
done

echo "✅ MongoDB is ready"
echo ""

# Get database credentials from environment
MONGO_USER="${MONGO_INITDB_ROOT_USERNAME:-legrimoire}"
MONGO_PASSWORD="${MONGO_INITDB_ROOT_PASSWORD}"
MONGO_DB="${MONGO_INITDB_DATABASE:-legrimoire}"

# Check if authentication is required
if [ -n "$MONGO_PASSWORD" ]; then
    AUTH_STRING="--username $MONGO_USER --password $MONGO_PASSWORD --authenticationDatabase admin"
else
    AUTH_STRING=""
fi

echo "📊 Checking database: $MONGO_DB"

# Function to check if collection exists
check_collection() {
    local collection=$1
    mongosh $AUTH_STRING --quiet --eval "
        use $MONGO_DB;
        db.getCollectionNames().includes('$collection')
    " | tail -1
}

# Function to create collection indexes
create_indexes() {
    echo "🔧 Creating indexes..."
    
    mongosh $AUTH_STRING --quiet --eval "
        use $MONGO_DB;
        
        // Ingredients collection indexes
        print('Creating ingredients indexes...');
        db.ingredients.createIndex({ 'off_id': 1 }, { unique: true, background: true });
        db.ingredients.createIndex({ 'names.fr': 1 }, { background: true });
        db.ingredients.createIndex({ 'names.en': 1 }, { background: true });
        db.ingredients.createIndex({ 'custom': 1 }, { background: true });
        
        // Categories collection indexes
        print('Creating categories indexes...');
        db.categories.createIndex({ 'off_id': 1 }, { unique: true, background: true });
        db.categories.createIndex({ 'names.fr': 1 }, { background: true });
        db.categories.createIndex({ 'names.en': 1 }, { background: true });
        
        // Recipes collection indexes
        print('Creating recipes indexes...');
        db.recipes.createIndex({ 'title': 1 }, { background: true });
        db.recipes.createIndex({ 'created_at': -1 }, { background: true });
        db.recipes.createIndex({ 'is_public': 1 }, { background: true });
        db.recipes.createIndex({ 'category': 1 }, { background: true });
        db.recipes.createIndex({ 'cuisine': 1 }, { background: true });
        
        print('✅ Indexes created successfully');
    " 2>&1 | grep -v "Warning:"
}

# Check collections
echo ""
echo "📋 Checking collections..."

INGREDIENTS_EXISTS=$(check_collection "ingredients")
CATEGORIES_EXISTS=$(check_collection "categories")
RECIPES_EXISTS=$(check_collection "recipes")

echo "   - ingredients: $INGREDIENTS_EXISTS"
echo "   - categories: $CATEGORIES_EXISTS"
echo "   - recipes: $RECIPES_EXISTS"

# Create indexes if collections exist or will be created
echo ""
if [ "$INGREDIENTS_EXISTS" = "true" ] || [ "$CATEGORIES_EXISTS" = "true" ] || [ "$RECIPES_EXISTS" = "true" ]; then
    echo "📊 Collections found, ensuring indexes are created..."
    create_indexes
else
    echo "📊 No collections found yet, they will be created when data is imported"
    echo "   Indexes will be created automatically when collections are populated"
fi

# Show database statistics
echo ""
echo "📊 Database statistics:"
mongosh $AUTH_STRING --quiet --eval "
    use $MONGO_DB;
    
    const stats = {
        database: '$MONGO_DB',
        collections: db.getCollectionNames().length,
        ingredients: db.ingredients.countDocuments(),
        categories: db.categories.countDocuments(),
        recipes: db.recipes.countDocuments()
    };
    
    print('   Database: ' + stats.database);
    print('   Collections: ' + stats.collections);
    print('   Ingredients: ' + stats.ingredients);
    print('   Categories: ' + stats.categories);
    print('   Recipes: ' + stats.recipes);
" 2>&1 | grep "   "

echo ""
echo "========================================"
echo "✅ MongoDB initialization complete"
echo "========================================"
