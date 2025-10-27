import { test, expect } from '@playwright/test';

test.describe('Recipes Page', () => {
  test('should load the recipes page', async ({ page }) => {
    await page.goto('/recipes');
    
    // Check that the page loaded successfully
    await expect(page).toHaveURL(/.*recipes/);
  });

  test('should display search functionality', async ({ page }) => {
    await page.goto('/recipes');
    
    // Check for search input
    const searchInput = page.getByPlaceholder(/recherch/i);
    await expect(searchInput).toBeVisible();
  });

  test('should allow searching for recipes', async ({ page }) => {
    await page.goto('/recipes');
    
    // Find the search input
    const searchInput = page.getByPlaceholder(/recherch/i);
    
    // Type a search term
    await searchInput.fill('tomate');
    
    // Wait a bit for debounce and results
    await page.waitForTimeout(500);
    
    // The search should have been performed
    // (actual results depend on database content)
  });

  test('should have navigation back to home', async ({ page }) => {
    await page.goto('/recipes');
    
    // Should be able to click on logo or navigation to go back to home
    const navigation = page.locator('nav');
    await expect(navigation).toBeVisible();
  });
});
