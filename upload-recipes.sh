#!/bin/bash
# Upload recipe export to production and import

echo "📤 Uploading recipe export to production server..."
scp -r recipe_export legrimoire@legrimoireonline.ca:~/apps/le-grimoire/

echo ""
echo "📥 Importing recipes to production MongoDB..."
ssh legrimoire@legrimoireonline.ca "cd ~/apps/le-grimoire && docker compose -f docker-compose.prod.yml exec -T backend python scripts/import_recipes.py recipe_export/recipes_export_*.json recipe_export/images"

echo ""
echo "✅ Recipe import complete!"
echo "🧹 Cleaning up export folder on server..."
ssh legrimoire@legrimoireonline.ca "cd ~/apps/le-grimoire && rm -rf recipe_export"

echo ""
echo "✨ All done! Your recipes are now in production."
