# E2E Tests with Playwright

This directory contains end-to-end (E2E) tests for Le Grimoire using Playwright.

## Overview

Playwright is a modern testing framework that allows us to test the application in real browsers. These tests simulate actual user interactions to ensure the application works correctly from a user's perspective.

## Test Structure

```
tests/e2e/
├── home.spec.ts          # Tests for the home page
├── recipes.spec.ts       # Tests for recipe browsing and search
├── navigation.spec.ts    # Tests for navigation between pages
├── ingredients.spec.ts   # Tests for ingredients functionality
├── shopping-list.spec.ts # Tests for shopping list
├── auth.spec.ts          # Tests for authentication (login/register)
├── api.spec.ts           # API testing and UI-API integration
└── example-pom.spec.ts   # Examples using Page Object Model

tests/pages/              # Page Object Models
├── HomePage.ts           # Home page object
└── RecipesPage.ts        # Recipes page object

tests/
├── helpers.ts            # Test helper functions
└── fixtures.ts           # Custom test fixtures
```

## Running Tests

### Locally

First, make sure the application is running:

```bash
# From the project root
docker-compose up -d
```

Then run the tests:

```bash
# From the frontend directory
cd frontend

# Run all tests
npm test

# Run tests in headed mode (see browser)
npm run test:headed

# Run tests in UI mode (interactive)
npm run test:ui

# Generate tests interactively
npm run test:codegen

# View test report
npm run test:report
```

### In CI/CD

Tests automatically run on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

The GitHub Actions workflow:
1. Starts all services (frontend, backend, databases) with Docker Compose
2. Waits for services to be healthy
3. Runs Playwright tests
4. Uploads test reports and results as artifacts

## Writing Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test('should do something', async ({ page }) => {
    // Navigate to page
    await page.goto('/some-page');
    
    // Interact with elements
    await page.getByRole('button', { name: 'Click Me' }).click();
    
    // Assert expected behavior
    await expect(page).toHaveURL(/.*expected-url/);
  });
});
```

### Best Practices

1. **Use semantic locators**: Prefer `getByRole()`, `getByText()`, `getByLabel()` over CSS selectors
2. **Wait for elements**: Use `await expect(element).toBeVisible()` instead of arbitrary timeouts
3. **Test user flows**: Focus on what users actually do, not implementation details
4. **Keep tests independent**: Each test should work in isolation
5. **Use descriptive names**: Test names should clearly describe what they test
6. **Group related tests**: Use `test.describe()` to organize tests by feature

### Common Locators

```typescript
// By role (preferred)
page.getByRole('button', { name: 'Submit' })
page.getByRole('link', { name: /login/i })
page.getByRole('heading', { name: 'Welcome' })

// By text
page.getByText('Some text')
page.getByText(/pattern/i)

// By placeholder
page.getByPlaceholder('Search...')

// By label
page.getByLabel('Email')

// By test ID (use sparingly)
page.getByTestId('submit-button')
```

### Page Object Model

For complex pages, use the Page Object Model pattern:

```typescript
// pages/HomePage.ts
export class HomePage {
  readonly page: Page;
  readonly exploreButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.exploreButton = page.getByRole('link', { name: /Explorer/ });
  }

  async goto() {
    await this.page.goto('/');
  }

  async clickExplore() {
    await this.exploreButton.click();
  }
}

// In your test
import { HomePage } from '../pages/HomePage';

test('navigate to recipes', async ({ page }) => {
  const homePage = new HomePage(page);
  await homePage.goto();
  await homePage.clickExplore();
});
```

See `tests/pages/` for examples and `tests/e2e/example-pom.spec.ts` for usage.

### API Testing

Playwright can also test APIs directly:

```typescript
test('should fetch recipes from API', async ({ request }) => {
  const response = await request.get('http://localhost:8000/api/v2/recipes/');
  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(Array.isArray(data)).toBeTruthy();
});
```

See `tests/e2e/api.spec.ts` for complete examples.

## Test Coverage

Current test coverage includes:

- ✅ Home page loading and navigation
- ✅ Recipe browsing and search
- ✅ Navigation between pages
- ✅ Ingredients search
- ✅ Shopping list page
- ✅ Authentication pages (login/register)
- ✅ API endpoint testing
- ✅ UI-API integration tests
- ✅ Page Object Model examples
- 🔲 Recipe creation and editing (forms)
- 🔲 Admin functionality (full coverage)

## Debugging Tests

### Visual debugging

```bash
# Run with headed browser
npm run test:headed

# Run with UI mode
npm run test:ui
```

### Screenshots and videos

Playwright automatically captures:
- Screenshots on test failure
- Videos when tests fail (retention-on-failure)
- Traces on first retry

These are saved in `test-results/` and `playwright-report/`.

### Debug specific test

```bash
# Run single test file
npx playwright test home.spec.ts

# Run single test by name
npx playwright test -g "should load the home page"

# Debug mode (opens inspector)
npx playwright test --debug
```

## Configuration

Configuration is in `playwright.config.ts`:

- **testDir**: `./tests/e2e` - Test directory
- **baseURL**: `http://localhost:3000` - Application URL
- **timeout**: 30 seconds per test
- **retries**: 2 on CI, 0 locally
- **reporter**: HTML report + list + GitHub Actions annotations

## CI/CD Integration

The workflow file `.github/workflows/playwright.yml` handles:

1. **Environment setup**
   - Node.js 20
   - npm dependencies
   - Playwright browsers

2. **Service orchestration**
   - Starts Docker Compose stack
   - Waits for health checks
   - Runs tests against running services

3. **Artifact collection**
   - Test reports (30 days retention)
   - Test results (videos, screenshots)
   - Docker logs on failure

## Troubleshooting

### Tests fail locally but pass in CI

- Check that all services are running: `docker-compose ps`
- Check service logs: `docker-compose logs backend frontend`
- Ensure database has data if tests expect it

### Tests are flaky

- Add proper waits: `await expect(element).toBeVisible()`
- Avoid `page.waitForTimeout()` - use condition-based waits
- Check for race conditions in async operations

### Browser not found

```bash
# Install browsers
npx playwright install chromium
```

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Debugging Guide](https://playwright.dev/docs/debug)
- [API Reference](https://playwright.dev/docs/api/class-playwright)
