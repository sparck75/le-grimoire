# Contributing to Playwright Tests

This guide helps contributors understand how to write and maintain Playwright tests for Le Grimoire.

## Getting Started

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Install Playwright browsers**
   ```bash
   npx playwright install chromium
   ```

3. **Start the application**
   ```bash
   # From project root
   docker-compose up -d
   ```

4. **Run existing tests**
   ```bash
   npm test
   ```

## Test Organization

### Directory Structure

```
tests/
├── e2e/              # End-to-end test specs
│   ├── home.spec.ts
│   ├── recipes.spec.ts
│   ├── auth.spec.ts
│   └── ...
├── pages/            # Page Object Models
│   ├── HomePage.ts
│   └── RecipesPage.ts
├── helpers.ts        # Utility functions
└── fixtures.ts       # Custom test fixtures
```

### Naming Conventions

- **Test files**: `feature.spec.ts` (e.g., `recipes.spec.ts`)
- **Page objects**: `FeaturePage.ts` (e.g., `RecipesPage.ts`)
- **Test descriptions**: Clear, descriptive, user-focused
  - ✅ "should display search results when typing in search box"
  - ❌ "test search functionality"

## Writing Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test('should do something specific', async ({ page }) => {
    // Arrange: Navigate and set up
    await page.goto('/some-page');
    
    // Act: Perform user actions
    await page.getByRole('button', { name: 'Submit' }).click();
    
    // Assert: Verify outcomes
    await expect(page).toHaveURL(/.*success/);
  });
});
```

### Best Practices

#### 1. Use Semantic Locators

```typescript
// ✅ Good - semantic and resilient
page.getByRole('button', { name: 'Submit' })
page.getByLabel('Email')
page.getByPlaceholder('Search...')
page.getByText('Welcome')

// ❌ Bad - brittle and implementation-dependent
page.locator('#submit-btn')
page.locator('.form-input')
page.locator('div > button:nth-child(2)')
```

#### 2. Wait for Conditions, Not Time

```typescript
// ✅ Good - wait for actual condition
await expect(page.getByText('Success')).toBeVisible();
await page.waitForLoadState('networkidle');

// ❌ Bad - arbitrary timeout
await page.waitForTimeout(3000);
```

#### 3. Keep Tests Independent

```typescript
// ✅ Good - each test sets up its own state
test('test 1', async ({ page }) => {
  await page.goto('/recipes');
  // ... test logic
});

test('test 2', async ({ page }) => {
  await page.goto('/recipes');
  // ... different test logic
});

// ❌ Bad - tests depend on each other
let sharedState;
test('test 1', async ({ page }) => {
  sharedState = await page.locator('.data').textContent();
});
test('test 2', async ({ page }) => {
  expect(sharedState).toBe('something'); // Depends on test 1
});
```

#### 4. Test User Flows, Not Implementation

```typescript
// ✅ Good - focuses on user behavior
test('user can find and view a recipe', async ({ page }) => {
  await page.goto('/recipes');
  await page.getByPlaceholder('Rechercher').fill('tomate');
  await page.getByRole('link', { name: /tomate/i }).first().click();
  await expect(page.getByRole('heading')).toBeVisible();
});

// ❌ Bad - tests implementation details
test('search sets query parameter', async ({ page }) => {
  await page.goto('/recipes');
  await page.locator('#search').fill('tomate');
  expect(page.url()).toContain('?q=tomate');
});
```

## Using Page Objects

For complex pages, create Page Object Models to encapsulate page structure:

### Creating a Page Object

```typescript
// tests/pages/LoginPage.ts
import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Login' });
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
```

### Using Page Objects in Tests

```typescript
import { LoginPage } from '../pages/LoginPage';

test('should login successfully', async ({ page }) => {
  const loginPage = new LoginPage(page);
  
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password');
  
  await expect(page).toHaveURL('/dashboard');
});
```

## Testing APIs

Use Playwright's request fixture for API testing:

```typescript
test('should fetch recipes from API', async ({ request }) => {
  const response = await request.get('http://localhost:8000/api/v2/recipes/');
  
  expect(response.ok()).toBeTruthy();
  
  const data = await response.json();
  expect(Array.isArray(data)).toBeTruthy();
});
```

## Handling Authentication

For tests that require authentication, create a fixture:

```typescript
// tests/fixtures.ts
export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    // Login
    await page.goto('/login');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('password');
    await page.getByRole('button', { name: 'Login' }).click();
    
    // Wait for login to complete
    await page.waitForURL('/dashboard');
    
    await use(page);
  },
});

// In your test
import { test, expect } from './fixtures';

test('authenticated user can create recipe', async ({ authenticatedPage }) => {
  await authenticatedPage.goto('/recipes/new');
  // ... test logic
});
```

## Debugging Tests

### Run in Headed Mode

```bash
npm run test:headed
```

### Use UI Mode

```bash
npm run test:ui
```

### Debug Specific Test

```bash
npx playwright test --debug -g "test name"
```

### Generate Tests Interactively

```bash
npm run test:codegen
```

## Testing Checklist

Before submitting tests:

- [ ] Tests follow naming conventions
- [ ] Tests use semantic locators
- [ ] Tests are independent and can run in any order
- [ ] No arbitrary `waitForTimeout()` calls
- [ ] Tests focus on user behavior, not implementation
- [ ] Page Objects are used for complex pages
- [ ] Tests pass locally
- [ ] Tests pass in CI
- [ ] Documentation is updated if needed

## Common Patterns

### Handling Dropdowns

```typescript
await page.getByRole('combobox', { name: 'Country' }).click();
await page.getByRole('option', { name: 'France' }).click();
```

### Handling Forms

```typescript
await page.getByLabel('Name').fill('John Doe');
await page.getByLabel('Email').fill('john@example.com');
await page.getByRole('checkbox', { name: 'Subscribe' }).check();
await page.getByRole('button', { name: 'Submit' }).click();
```

### Handling Modals

```typescript
// Open modal
await page.getByRole('button', { name: 'Delete' }).click();

// Interact with modal
await expect(page.getByRole('dialog')).toBeVisible();
await page.getByRole('button', { name: 'Confirm' }).click();

// Wait for modal to close
await expect(page.getByRole('dialog')).not.toBeVisible();
```

### Handling File Uploads

```typescript
await page.getByLabel('Upload file').setInputFiles('path/to/file.jpg');
```

## CI/CD

Tests run automatically in GitHub Actions:

- On push to `main` or `develop`
- On pull requests to `main` or `develop`

The workflow:
1. Starts all services with Docker Compose
2. Waits for health checks
3. Runs all tests
4. Uploads test reports as artifacts

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [API Reference](https://playwright.dev/docs/api/class-playwright)
- [Debugging Guide](https://playwright.dev/docs/debug)

## Getting Help

If you need help with tests:

1. Check existing tests for examples
2. Review Playwright documentation
3. Ask in pull request comments
4. Open a discussion on GitHub
