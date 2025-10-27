# Test Data Seeding for CI/CD

This document describes the test data seeding system used in the CI/CD pipeline.

## Overview

The `seed_test_data.py` script creates a consistent, reproducible dataset for E2E testing. It's automatically run during CI/CD builds to ensure tests run against clean, known data.

## What Gets Seeded

### 1. Test Users (PostgreSQL)

| Email | Username | Password | Role | Active | Purpose |
|-------|----------|----------|------|--------|---------|
| admin@test.com | admin_test | Test123!@# | admin | ✅ | Full admin access testing |
| collab@test.com | collab_test | Test123!@# | collaborator | ✅ | Recipe creation/editing |
| reader@test.com | reader_test | Test123!@# | reader | ✅ | Read-only access |
| inactive@test.com | inactive_test | Test123!@# | reader | ❌ | Inactive user testing |

**⚠️ WARNING**: These credentials are for **TESTING ONLY**. Never use in production!

### 2. Test Recipes (PostgreSQL)

The script creates 8 diverse recipes with various properties:

1. **Tomates Vertes Frites** (Public, Admin)
   - Category: Accompaniment
   - Cuisine: American South
   - Difficulty: Easy
   - Equipment: Deep pan, bowls
   - Tests: Equipment field, multilingual ingredients

2. **Pâtes à l'Ail et aux Crevettes** (Public, Collaborator)
   - Category: Main Course
   - Cuisine: Italian
   - Difficulty: Easy
   - Tests: Seafood recipes, collaborator-created content

3. **Soupe Minestrone Classique** (Public, Admin)
   - Category: Soup
   - Cuisine: Italian
   - Difficulty: Easy
   - Tests: Vegetarian recipes, long ingredient lists

4. **Poulet au Beurre** (Public, Collaborator)
   - Category: Main Course
   - Cuisine: Indian
   - Difficulty: Medium
   - Tests: Complex recipes, multiple steps

5. **Saumon Grillé au Sirop d'Érable** (Public, Admin)
   - Category: Main Course
   - Cuisine: Canadian
   - Difficulty: Easy
   - Tests: Seafood, temperature settings

6. **Brownies au Chocolat Fondant** (Public, Collaborator)
   - Category: Dessert
   - Cuisine: American
   - Difficulty: Easy
   - Tests: Baking recipes, precise measurements

7. **Recette Privée - Test** (Private, Admin)
   - Category: Test
   - Cuisine: Test
   - Tests: Private recipe filtering

8. **Salade César Classique** (Public, Admin)
   - Category: Salad
   - Cuisine: American
   - Difficulty: Medium
   - Tests: No-cook recipes, dressings

**Coverage:**
- ✅ Public vs Private recipes
- ✅ Multiple cuisines (Italian, Indian, Canadian, American)
- ✅ Various difficulties (Easy, Medium)
- ✅ Different categories (Main, Soup, Dessert, Salad)
- ✅ Admin and Collaborator authorship
- ✅ With/without equipment
- ✅ Various cooking times and temperatures

### 3. Test Ingredients (MongoDB - Optional)

If MongoDB is configured, seeds 5 sample ingredients:

| OFF ID | English | French | Vegan | Vegetarian |
|--------|---------|--------|-------|------------|
| en:tomato | Tomato | Tomate | ✅ | ✅ |
| en:garlic | Garlic | Ail | ✅ | ✅ |
| en:olive-oil | Olive oil | Huile d'olive | ✅ | ✅ |
| en:chicken | Chicken | Poulet | ❌ | ❌ |
| en:shrimp | Shrimp | Crevette | ❌ | ❌ |

**Note**: MongoDB seeding is gracefully skipped if dependencies aren't available or if ingredients already exist.

## Usage

### In CI/CD (Automatic)

The GitHub Actions workflow automatically runs this script after database migrations:

```yaml
- name: Run database migrations
  run: |
    docker compose exec -T backend alembic upgrade head

- name: Seed test data
  run: |
    docker compose exec -T backend python -m scripts.seed_test_data
```

⚠️ **Important**: Migrations must run BEFORE seeding to ensure all required database columns exist.

### Local Testing

```bash
# From project root with Docker running
docker-compose exec backend python -m scripts.seed_test_data

# Or directly if you have Python environment set up
cd backend
python -m scripts.seed_test_data
```

### Resetting Data

The script automatically clears existing data before seeding:

```bash
# Just run it again to reset
docker-compose exec backend python -m scripts.seed_test_data
```

## Script Behavior

### 1. Data Clearing
- Deletes ALL recipes and users from PostgreSQL
- Respects foreign key constraints (deletes in correct order)
- Does NOT clear MongoDB (checks for existing data instead)

### 2. Error Handling
- PostgreSQL failures: Script fails, rolls back transaction
- MongoDB failures: Warnings logged, script continues
- Graceful degradation if MongoDB unavailable

### 3. Output
The script provides detailed progress output:

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
   Password for all users: Test123!@#

🍳 Creating test recipes...
   ✓ Tomates Vertes Frites - 🌍 Publique
   ✓ Pâtes à l'Ail et aux Crevettes - 🌍 Publique
   ...
✅ Created 8 test recipes

🥕 Seeding MongoDB ingredients...
   ✓ Tomato
   ✓ Garlic
   ...
✅ Created 5 test ingredients in MongoDB

============================================================
✅ POSTGRESQL DATA SEEDED SUCCESSFULLY
============================================================

📊 Summary:
   • Users: 4
   • Recipes: 8

🔑 Test Credentials:
   • Admin: admin@test.com / Test123!@#
   • Collaborator: collab@test.com / Test123!@#
   • Reader: reader@test.com / Test123!@#

============================================================
🎉 ALL TEST DATA SEEDED
============================================================
```

## Testing with This Data

### Playwright Tests

The E2E tests can now rely on this data:

```typescript
// Test recipe search
test('should find "Tomates Vertes Frites"', async ({ page }) => {
  await page.goto('/recipes');
  await page.getByPlaceholder(/recherch/i).fill('tomates');
  await expect(page.getByText('Tomates Vertes Frites')).toBeVisible();
});

// Test authentication
test('should login as admin', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="email"]', 'admin@test.com');
  await page.fill('[name="password"]', 'Test123!@#');
  await page.click('[type="submit"]');
  await expect(page.getByText('admin_test')).toBeVisible();
});

// Test private recipes
test('should not show private recipes to unauthenticated users', async ({ page }) => {
  await page.goto('/recipes');
  await expect(page.getByText('Recette Privée - Test')).not.toBeVisible();
});
```

### API Tests

```typescript
// Test recipes endpoint
test('should return 7 public recipes', async ({ request }) => {
  const response = await request.get('http://localhost:8000/api/v2/recipes/');
  expect(response.ok()).toBeTruthy();
  const recipes = await response.json();
  expect(recipes).toHaveLength(7); // Excludes 1 private recipe
});
```

## CI/CD Integration

### Workflow Steps

1. **Start Services**: Docker Compose brings up all containers
2. **Wait for Health**: Services must be healthy (MongoDB, PostgreSQL, Backend, Frontend)
3. **Seed Data**: ← This script runs here
4. **Run Tests**: Playwright tests execute against seeded data
5. **Cleanup**: Docker Compose tears down with `-v` flag (removes volumes)

### Why Seed After Services Start?

- Database schemas must exist (migrations run on startup)
- Backend must be running (uses app models and database session)
- Ensures fresh data for every test run
- Prevents test pollution from previous runs

### Volume Cleanup

The CI workflow uses `docker compose down -v` to remove volumes, ensuring:
- Each test run starts with empty databases
- No leftover data from previous runs
- Consistent testing environment

## Maintenance

### Adding New Test Data

To add more recipes/users/ingredients:

1. Edit `backend/scripts/seed_test_data.py`
2. Add entries to the relevant lists (`users`, `recipes`, `test_ingredients`)
3. Test locally: `docker-compose exec backend python -m scripts.seed_test_data`
4. Update this README if adding new patterns or use cases

### Best Practices

- ✅ Keep recipes diverse (cuisines, difficulties, categories)
- ✅ Include edge cases (private recipes, inactive users)
- ✅ Use realistic data (actual recipe names, plausible ingredients)
- ✅ Document test credentials prominently
- ✅ Keep passwords simple for testing (but never use in production!)
- ❌ Don't add too much data (slows down tests)
- ❌ Don't use real user credentials
- ❌ Don't hardcode production secrets

## Troubleshooting

### Script Fails in CI

**Symptom**: `python -m scripts.seed_test_data` fails in GitHub Actions

**Checks**:
1. Backend container is running: `docker compose ps`
2. PostgreSQL is healthy: `docker compose logs db`
3. Migrations ran successfully: `docker compose logs backend | grep migration`
4. Environment variables set: Check `.env` creation step

**Solution**:
```bash
# Check backend can reach database
docker compose exec backend python -c "from app.core.database import SessionLocal; db = SessionLocal(); print('Connected!')"
```

### MongoDB Seeding Fails

**Symptom**: Warning about MongoDB, but script continues

**This is normal if**:
- MongoDB dependencies not installed
- Ingredients already exist in database
- MongoDB connection fails (non-critical)

**To fix if needed**:
```bash
# Check MongoDB connection
docker compose exec backend python -c "from motor.motor_asyncio import AsyncIOMotorClient; import os; client = AsyncIOMotorClient(os.getenv('MONGODB_URL')); print(client.server_info())"
```

### Users Not Created

**Symptom**: Login fails with seeded credentials

**Causes**:
1. Password hashing failed (bcrypt not installed)
2. Database transaction rolled back
3. User table doesn't exist (migration not run)

**Solution**:
```bash
# Check if users exist
docker compose exec db psql -U grimoire -d le_grimoire -c "SELECT username, email, role, is_active FROM users;"

# Check password hash format
docker compose exec db psql -U grimoire -d le_grimoire -c "SELECT username, length(password_hash) FROM users;"
```

### Recipes Not Visible

**Symptom**: API returns empty array even after seeding

**Causes**:
1. All recipes marked as private
2. Wrong database connection
3. Transaction not committed

**Solution**:
```bash
# Check if recipes exist
docker compose exec db psql -U grimoire -d le_grimoire -c "SELECT title, is_public, user_id FROM recipes;"

# Test API directly
curl http://localhost:8000/api/v2/recipes/
```

## Related Files

- `backend/scripts/seed_test_data.py` - Main seeding script
- `.github/workflows/playwright.yml` - CI/CD workflow
- `frontend/tests/e2e/` - Playwright tests that use this data
- `backend/app/models/` - Database models
- `docker-compose.ci.yml` - CI-specific Docker configuration

## Security Notes

⚠️ **NEVER use this data in production**:
- Test passwords are publicly documented
- User emails follow predictable patterns
- Data is designed for testing, not security

✅ **Safe for CI/CD**:
- Fresh environment for each run
- No persistent data
- Containers destroyed after tests
- No external network access during tests
