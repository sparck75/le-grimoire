import { test as base, Page } from '@playwright/test';

/**
 * Example test fixtures for Le Grimoire
 * 
 * Fixtures allow you to set up test state and helper functions
 * that can be reused across multiple tests.
 */

// Define custom fixture types
type CustomFixtures = {
  // Example: A fixture that navigates to recipes page
  recipesPage: Page;
  // Example: A fixture for authenticated user
  authenticatedPage: Page;
};

/**
 * Extend base test with custom fixtures
 */
export const test = base.extend<CustomFixtures>({
  /**
   * Fixture that automatically navigates to recipes page
   */
  recipesPage: async ({ page }, use) => {
    await page.goto('/recipes');
    await use(page);
  },

  /**
   * Fixture for authenticated user (example - needs actual auth implementation)
   */
  authenticatedPage: async ({ page }, use) => {
    // This is a placeholder - actual implementation would:
    // 1. Navigate to login
    // 2. Fill in credentials
    // 3. Submit form
    // 4. Wait for authentication
    
    // For now, just use the page as-is
    await use(page);
  },
});

export { expect } from '@playwright/test';

/**
 * Example usage:
 * 
 * import { test, expect } from './fixtures';
 * 
 * test('should use recipes page fixture', async ({ recipesPage }) => {
 *   // recipesPage is already navigated to /recipes
 *   await expect(recipesPage).toHaveURL(/.*recipes/);
 * });
 */
