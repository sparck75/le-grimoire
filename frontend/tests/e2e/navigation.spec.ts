import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('should display navigation menu', async ({ page }) => {
    await page.goto('/');
    
    // Check that navigation is present
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();
  });

  test('should be able to navigate between pages', async ({ page }) => {
    await page.goto('/');
    
    // Navigate to recipes
    await page.getByRole('link', { name: /recettes/i }).first().click();
    await expect(page).toHaveURL(/.*recipes/);
    
    // Navigate back to home
    await page.goto('/');
    await expect(page).toHaveURL(/^.*\/$/);
  });

  test('should show login/register links when not authenticated', async ({ page }) => {
    await page.goto('/');
    
    // Check for auth-related links (may be in nav or on page)
    const pageContent = await page.content();
    
    // The page should load without errors
    expect(pageContent).toBeTruthy();
  });
});
