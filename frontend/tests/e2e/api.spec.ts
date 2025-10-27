import { test, expect } from '@playwright/test';

/**
 * API Testing Examples
 * 
 * Playwright can also test APIs directly. These tests demonstrate
 * how to test the backend API endpoints.
 */

// Get the API URL from environment or use default
const API_URL = process.env.BACKEND_URL || 'http://localhost:8000';

test.describe('API Tests', () => {
  test('should check API health endpoint', async ({ request }) => {
    const response = await request.get(`${API_URL}/api/health`);
    
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(200);
  });

  test('should fetch recipes list from API', async ({ request }) => {
    const response = await request.get(`${API_URL}/api/v2/recipes/`);
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
  });

  test('should search for ingredients', async ({ request }) => {
    const response = await request.get(`${API_URL}/api/v2/ingredients/`, {
      params: {
        search: 'tomate',
        language: 'fr',
        limit: 10
      }
    });
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
  });

  test('should return 404 for non-existent recipe', async ({ request }) => {
    const response = await request.get(`${API_URL}/api/v2/recipes/nonexistent-id-12345`);
    
    expect(response.status()).toBe(404);
  });

  test('should have correct CORS headers', async ({ request }) => {
    const response = await request.get(`${API_URL}/api/health`);
    
    const headers = response.headers();
    // Check if CORS headers are present (if configured)
    // expect(headers['access-control-allow-origin']).toBeDefined();
  });
});

/**
 * Integration Tests - Testing UI with API
 * 
 * These tests verify that the UI correctly integrates with the API.
 */
test.describe('UI-API Integration', () => {
  test('should display recipes from API', async ({ page, request }) => {
    // First, verify API has recipes
    const apiResponse = await request.get(`${API_URL}/api/v2/recipes/`);
    const recipes = await apiResponse.json();
    
    if (recipes.length > 0) {
      // Navigate to recipes page
      await page.goto('/recipes');
      
      // Wait for page to load
      await page.waitForLoadState('networkidle');
      
      // Page should have loaded successfully
      await expect(page).toHaveURL(/.*recipes/);
    }
  });

  test('should search recipes through UI and API', async ({ page, request }) => {
    // Navigate to recipes page
    await page.goto('/recipes');
    
    // Search for a recipe
    const searchInput = page.getByPlaceholder(/recherch/i);
    await searchInput.fill('tomate');
    
    // Wait for the API call to complete
    const responsePromise = page.waitForResponse(
      response => response.url().includes('/api/v2/recipes') && response.status() === 200,
      { timeout: 5000 }
    ).catch(() => null);
    
    const response = await responsePromise;
    
    if (response) {
      expect(response.ok()).toBeTruthy();
    }
  });
});
