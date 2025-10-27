import { Page, Locator } from '@playwright/test';

/**
 * Page Object Model for the Home Page
 * 
 * This class encapsulates the structure and behavior of the home page,
 * making tests more maintainable and readable.
 */
export class HomePage {
  readonly page: Page;
  readonly logo: Locator;
  readonly heading: Locator;
  readonly exploreRecipesButton: Locator;
  readonly addRecipeButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.logo = page.locator('img[alt="Le Grimoire"]');
    this.heading = page.getByRole('heading', { name: /Votre Bibliothèque de/ });
    this.exploreRecipesButton = page.getByRole('link', { name: /Explorer les Recettes/ });
    this.addRecipeButton = page.getByRole('link', { name: /Ajouter une Recette/ });
  }

  /**
   * Navigate to the home page
   */
  async goto() {
    await this.page.goto('/');
  }

  /**
   * Click on "Explorer les Recettes" button
   */
  async clickExploreRecipes() {
    await this.exploreRecipesButton.click();
  }

  /**
   * Click on "Ajouter une Recette" button (if visible)
   */
  async clickAddRecipe() {
    await this.addRecipeButton.click();
  }

  /**
   * Check if the add recipe button is visible
   */
  async isAddRecipeVisible(): Promise<boolean> {
    try {
      return await this.addRecipeButton.isVisible({ timeout: 1000 });
    } catch {
      return false;
    }
  }
}
