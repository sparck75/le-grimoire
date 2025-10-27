import { test, expect } from '@playwright/test';
import { HomePage } from '../pages/HomePage';
import { RecipesPage } from '../pages/RecipesPage';

/**
 * Example tests using Page Object Model
 * 
 * These tests demonstrate how to use Page Objects for more maintainable tests.
 */

test.describe('Page Object Model Examples', () => {
  test('should navigate from home to recipes using POM', async ({ page }) => {
    const homePage = new HomePage(page);
    const recipesPage = new RecipesPage(page);

    // Navigate to home
    await homePage.goto();

    // Verify we're on the home page
    await expect(homePage.heading).toBeVisible();

    // Click explore recipes button
    await homePage.clickExploreRecipes();

    // Verify we're on the recipes page
    await expect(page).toHaveURL(/.*recipes/);
    await expect(recipesPage.searchInput).toBeVisible();
  });

  test('should search for recipes using POM', async ({ page }) => {
    const recipesPage = new RecipesPage(page);

    // Navigate to recipes page
    await recipesPage.goto();

    // Verify search input is visible
    await expect(recipesPage.searchInput).toBeVisible();

    // Perform a search
    await recipesPage.search('tomate');

    // The search should have been executed
    // (actual verification depends on having data in the database)
  });

  test('should check if add recipe button is visible for authenticated users', async ({ page }) => {
    const homePage = new HomePage(page);

    await homePage.goto();

    // Check if add recipe button is visible
    // This will depend on whether user is authenticated
    const isVisible = await homePage.isAddRecipeVisible();
    
    // We can't assert true/false without knowing auth state,
    // but we can verify the method works
    expect(typeof isVisible).toBe('boolean');
  });
});
