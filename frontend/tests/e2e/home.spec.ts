import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('should load the home page successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check that the page title contains "Le Grimoire"
    await expect(page).toHaveTitle(/Le Grimoire/);
  });

  test('should display the logo and main heading', async ({ page }) => {
    await page.goto('/');
    
    // Check for logo
    const logo = page.locator('img[alt="Le Grimoire"]');
    await expect(logo).toBeVisible();
    
    // Check for main heading
    const heading = page.getByRole('heading', { name: /Votre Bibliothèque de/ });
    await expect(heading).toBeVisible();
  });

  test('should have a link to explore recipes', async ({ page }) => {
    await page.goto('/');
    
    // Check for "Explorer les Recettes" link
    const exploreLink = page.getByRole('link', { name: /Explorer les Recettes/ });
    await expect(exploreLink).toBeVisible();
    await expect(exploreLink).toHaveAttribute('href', '/recipes');
  });

  test('should navigate to recipes page when clicking explore button', async ({ page }) => {
    await page.goto('/');
    
    // Click on "Explorer les Recettes"
    await page.getByRole('link', { name: /Explorer les Recettes/ }).click();
    
    // Should navigate to recipes page
    await expect(page).toHaveURL(/.*recipes/);
  });
});
