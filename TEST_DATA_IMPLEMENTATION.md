# Test Data Seeding - CI/CD Integration

## Summary

I've created a comprehensive test data seeding system for CI/CD that will:

1. **Clear existing data** before each test run
2. **Create test users** with different roles (admin, collaborator, reader)
3. **Create diverse test recipes** covering various cuisines, difficulties, and categories
4. **Seed MongoDB ingredients** (optional, gracefully skipped if unavailable)

## Files Created

### 1. `backend/scripts/seed_test_data.py`
Main seeding script that creates:
- **4 test users**: admin, collaborator, reader, and inactive user
- **8 test recipes**: French, Italian, Indian, Canadian, American cuisines
- **5 test ingredients**: Common ingredients in MongoDB

**Password for all test users**: `Test123!@#`

### 2. `backend/scripts/README_TEST_DATA.md`
Comprehensive documentation including:
- What data gets seeded
- How to use the script locally and in CI
- Troubleshooting guide
- Security notes

### 3. `.github/workflows/playwright.yml` (Updated)
Added seeding step after services are healthy:
```yaml
- name: Seed test data
  run: |
    echo "Seeding test data..."
    docker compose -f docker-compose.yml -f docker-compose.ci.yml exec -T backend python -m scripts.seed_test_data
    echo "Test data seeded successfully!"
```

## Test Credentials

| User | Email | Password | Role | Purpose |
|------|-------|----------|------|---------|
| Admin | admin@test.com | Test123!@# | admin | Full access testing |
| Collaborator | collab@test.com | Test123!@# | collaborator | Recipe creation/editing |
| Reader | reader@test.com | Test123!@# | reader | Read-only access |
| Inactive | inactive@test.com | Test123!@# | reader (inactive) | Inactive user testing |

## Test Recipes

8 diverse recipes have been created:

1. **Tomates Vertes Frites** - American South, Easy, with equipment
2. **Pâtes à l'Ail et aux Crevettes** - Italian, Easy, seafood
3. **Soupe Minestrone Classique** - Italian, Easy, vegetarian
4. **Poulet au Beurre** - Indian, Medium, complex steps
5. **Saumon Grillé au Sirop d'Érable** - Canadian, Easy, with temperature
6. **Brownies au Chocolat Fondant** - American, Easy, dessert/baking
7. **Recette Privée - Test** - Private recipe (won't appear in public lists)
8. **Salade César Classique** - American, Medium, no-cook

**Coverage**:
- ✅ Public (7) vs Private (1) recipes
- ✅ Multiple cuisines and difficulties
- ✅ Various categories (Main, Soup, Dessert, Salad, Side)
- ✅ Admin and Collaborator authorship
- ✅ Recipes with/without equipment, temperatures, notes

## How It Works in CI/CD

### Workflow Steps

1. **Start Services**: Docker Compose brings up all containers
2. **Wait for Health**: All services must be healthy (MongoDB, PostgreSQL, Backend, Frontend)
3. **Seed Data**: `python -m scripts.seed_test_data` runs inside backend container
4. **Run Tests**: Playwright tests execute against the seeded data
5. **Cleanup**: `docker compose down -v` removes all data (fresh start next run)

### Why This Approach?

- **Consistent Testing Environment**: Every test run starts with identical data
- **No Test Pollution**: Fresh data prevents tests from affecting each other
- **Realistic Scenarios**: Diverse data covers edge cases
- **Fast & Reliable**: Seeding takes ~2 seconds, no external dependencies

## Database Schema Fixes

During implementation, I discovered and fixed missing database columns:

**Users table**: Added `username`, `password_hash`, `role`, `is_active`
**Recipes table**: Added `equipment`, `difficulty_level`, `temperature`, `temperature_unit`, `notes`

These columns were in the models but missing from the database. They're now added and the seed script works perfectly.

## Local Testing

To seed data locally:

```powershell
# With Docker running
docker-compose exec backend python -m scripts.seed_test_data
```

Output:
```
============================================================
🌱 SEEDING TEST DATA FOR CI/CD
============================================================
🗑️  Clearing existing data...
✅ Existing data cleared

👥 Creating test users...
   ✓ admin_test (admin)
   ✓ collab_test (collaborator)
   ✓ reader_test (reader)
   ✓ inactive_test (reader)
✅ Created 4 test users

🍳 Creating test recipes...
   ✓ Tomates Vertes Frites - 🌍 Publique
   ...
✅ Created 8 test recipes

🥕 Seeding MongoDB ingredients...
   ✓ Tomato
   ...
✅ Created 5 test ingredients

============================================================
🎉 ALL TEST DATA SEEDED
============================================================
```

## Next Steps

1. **Commit These Files**:
   - `backend/scripts/seed_test_data.py`
   - `backend/scripts/README_TEST_DATA.md`
   - `.github/workflows/playwright.yml` (updated)

2. **Push to PR Branch**: The CI/CD workflow will now:
   - Start all services
   - Seed fresh test data
   - Run Playwright tests against known data
   - Clean up completely

3. **Update Tests**: Tests can now rely on predictable data:
   ```typescript
   // Example: Test recipe search
   test('should find "Tomates Vertes Frites"', async ({ page }) => {
     await page.goto('/recipes');
     await page.getByPlaceholder(/recherch/i).fill('tomates');
     await expect(page.getByText('Tomates Vertes Frites')).toBeVisible();
   });
   
   // Example: Test authentication
   test('should login as admin', async ({ page }) => {
     await page.goto('/login');
     await page.fill('[name="email"]', 'admin@test.com');
     await page.fill('[name="password"]', 'Test123!@#');
     await page.click('[type="submit"]');
     await expect(page.getByText('admin_test')).toBeVisible();
   });
   ```

## Benefits

✅ **Reproducible Tests**: Same data every run
✅ **Fast**: Seeding takes ~2 seconds
✅ **Comprehensive**: Covers all major use cases
✅ **Clean**: No data pollution between runs
✅ **Documented**: Clear instructions for maintenance
✅ **Tested**: Successfully runs locally with Docker

## Security Note

⚠️ **NEVER use these credentials or this script in production!**

- Test passwords are publicly documented
- Script clears ALL data
- Designed for disposable test environments only
