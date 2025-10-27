import { Page, Locator } from '@playwright/test';

/**
 * Page Object Model for the Recipes Page
 * 
 * This class encapsulates the structure and behavior of the recipes listing page.
 */
export class RecipesPage {
  readonly page: Page;
  readonly searchInput: Locator;
  readonly recipeCards: Locator;

  constructor(page: Page) {
    this.page = page;
    this.searchInput = page.getByPlaceholder(/recherch/i);
    this.recipeCards = page.locator('[class*="recipe"]'); // Adjust based on actual class names
  }

  /**
   * Navigate to the recipes page
   */
  async goto() {
    await this.page.goto('/recipes');
  }

  /**
   * Search for recipes
   */
  async search(query: string) {
    await this.searchInput.fill(query);
    // Wait a bit for debounce
    await this.page.waitForTimeout(500);
  }

  /**
   * Get the number of visible recipe cards
   */
  async getRecipeCount(): Promise<number> {
    try {
      return await this.recipeCards.count();
    } catch {
      return 0;
    }
  }

  /**
   * Click on a recipe by index
   */
  async clickRecipe(index: number = 0) {
    const recipes = this.recipeCards;
    const recipe = recipes.nth(index);
    await recipe.click();
  }
}
