# Playwright Quick Reference

## Common Commands

```bash
# Run all tests
npm test

# Run tests in headed mode (see browser)
npm run test:headed

# Run tests in UI mode (interactive)
npm run test:ui

# Run specific test file
npx playwright test home.spec.ts

# Run tests matching a pattern
npx playwright test -g "should login"

# Debug mode (step through tests)
npx playwright test --debug

# Generate tests interactively
npm run test:codegen

# View last test report
npm run test:report

# Update snapshots
npx playwright test --update-snapshots
```

## Common Test Patterns

### Navigation
```typescript
await page.goto('/');
await page.goBack();
await page.reload();
```

### Locators
```typescript
// By role (preferred)
page.getByRole('button', { name: 'Submit' })
page.getByRole('link', { name: /login/i })
page.getByRole('textbox', { name: 'Email' })

// By text
page.getByText('Welcome')
page.getByText(/hello/i)

// By label
page.getByLabel('Email')

// By placeholder
page.getByPlaceholder('Search...')

// By test ID
page.getByTestId('submit-btn')
```

### Actions
```typescript
// Click
await page.getByRole('button').click();

// Fill input
await page.getByLabel('Email').fill('user@example.com');

// Check checkbox
await page.getByRole('checkbox').check();

// Select dropdown
await page.getByRole('combobox').selectOption('option-value');

// Upload file
await page.getByLabel('Upload').setInputFiles('file.jpg');

// Press key
await page.keyboard.press('Enter');
await page.keyboard.type('Hello');
```

### Assertions
```typescript
// Visibility
await expect(element).toBeVisible();
await expect(element).toBeHidden();

// Content
await expect(element).toHaveText('Hello');
await expect(element).toContainText('Hello');

// Attributes
await expect(element).toHaveAttribute('href', '/page');
await expect(element).toHaveClass('active');

// State
await expect(checkbox).toBeChecked();
await expect(button).toBeDisabled();
await expect(input).toBeFocused();

// URL
await expect(page).toHaveURL(/.*success/);
await expect(page).toHaveTitle('Le Grimoire');

// Count
await expect(items).toHaveCount(5);
```

### Waits
```typescript
// Wait for element
await page.waitForSelector('text=Success');

// Wait for URL
await page.waitForURL('**/dashboard');

// Wait for load state
await page.waitForLoadState('networkidle');

// Wait for response
await page.waitForResponse('**/api/recipes');

// Wait for function
await page.waitForFunction(() => window.innerWidth < 768);
```

### API Testing
```typescript
test('API test', async ({ request }) => {
  const response = await request.get('http://localhost:8000/api/health');
  expect(response.ok()).toBeTruthy();
  
  const data = await response.json();
  expect(data).toHaveProperty('status', 'ok');
});
```

## Debugging

```bash
# Run with browser visible
npx playwright test --headed

# Run with slow motion
npx playwright test --headed --slow-mo=1000

# Debug specific test
npx playwright test --debug -g "login"

# Generate trace
npx playwright test --trace on

# View trace
npx playwright show-trace trace.zip
```

## Configuration

```typescript
// playwright.config.ts
export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  retries: 2,
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
});
```

## CI/CD

Tests run automatically on:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

Artifacts uploaded:
- Test reports (HTML)
- Screenshots (on failure)
- Videos (on failure)
- Traces (on retry)

## Tips

1. **Use semantic locators** - `getByRole()`, `getByLabel()`, not CSS
2. **Wait for conditions** - `expect(el).toBeVisible()`, not `waitForTimeout()`
3. **Keep tests independent** - Each test should work standalone
4. **Test user flows** - Focus on what users do, not implementation
5. **Use Page Objects** - For complex pages, encapsulate structure
6. **Descriptive test names** - "should show error when email is invalid"

## Resources

- 📖 [Full Test Documentation](./README.md)
- 🤝 [Contributing Guide](./CONTRIBUTING.md)
- 🐳 [Docker Guide](./DOCKER.md)
- 🌐 [Playwright Docs](https://playwright.dev/)
