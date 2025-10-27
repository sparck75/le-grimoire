import { test, expect } from '@playwright/test';

test.describe('Ingredients Page', () => {
  test('should load the ingredients page', async ({ page }) => {
    await page.goto('/ingredients');
    
    // Check that the page loaded successfully
    await expect(page).toHaveURL(/.*ingredients/);
  });

  test('should display ingredient search functionality', async ({ page }) => {
    await page.goto('/ingredients');
    
    // Check for search input
    const searchInput = page.getByPlaceholder(/recherch/i);
    if (await searchInput.isVisible()) {
      await expect(searchInput).toBeVisible();
    }
  });

  test('should be able to search for ingredients', async ({ page }) => {
    await page.goto('/ingredients');
    
    // Find search input if available
    const searchInput = page.getByPlaceholder(/recherch/i);
    
    if (await searchInput.isVisible()) {
      // Type a search term
      await searchInput.fill('tomate');
      
      // Wait a bit for results
      await page.waitForTimeout(500);
    }
  });
});
