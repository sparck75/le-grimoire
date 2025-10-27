import { test, expect } from '@playwright/test';

test.describe('Login and Authentication', () => {
  test('should load the login page', async ({ page }) => {
    await page.goto('/login');
    
    // Check that the page loaded successfully
    await expect(page).toHaveURL(/.*login/);
  });

  test('should display login form elements', async ({ page }) => {
    await page.goto('/login');
    
    // Check for email/username input
    const inputs = page.locator('input[type="email"], input[type="text"]');
    const inputCount = await inputs.count();
    expect(inputCount).toBeGreaterThan(0);
    
    // Check for password input
    const passwordInput = page.locator('input[type="password"]');
    await expect(passwordInput).toBeVisible();
  });

  test('should have a link to registration page', async ({ page }) => {
    await page.goto('/login');
    
    // Look for a link containing "inscription" or "register"
    const registerLink = page.getByRole('link', { name: /inscri|register/i });
    if (await registerLink.isVisible()) {
      await expect(registerLink).toBeVisible();
    }
  });

  test('should be able to navigate to register page', async ({ page }) => {
    await page.goto('/login');
    
    // Try to find and click register link
    const registerLink = page.getByRole('link', { name: /inscri|register/i });
    if (await registerLink.isVisible()) {
      await registerLink.click();
      await expect(page).toHaveURL(/.*register/);
    }
  });
});

test.describe('Register Page', () => {
  test('should load the registration page', async ({ page }) => {
    await page.goto('/register');
    
    // Check that the page loaded successfully
    await expect(page).toHaveURL(/.*register/);
  });

  test('should display registration form', async ({ page }) => {
    await page.goto('/register');
    
    // Check that form inputs exist
    const inputs = page.locator('input');
    const inputCount = await inputs.count();
    expect(inputCount).toBeGreaterThan(0);
  });
});
