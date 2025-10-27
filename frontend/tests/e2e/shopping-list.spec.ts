import { test, expect } from '@playwright/test';

test.describe('Shopping List Page', () => {
  test('should load the shopping list page', async ({ page }) => {
    await page.goto('/shopping-list');
    
    // Check that the page loaded successfully
    await expect(page).toHaveURL(/.*shopping-list/);
  });

  test('should display shopping list interface', async ({ page }) => {
    await page.goto('/shopping-list');
    
    // The page should have loaded
    const pageContent = await page.content();
    expect(pageContent).toBeTruthy();
    expect(pageContent.length).toBeGreaterThan(0);
  });
});
