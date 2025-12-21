/**
 * Authentication setup for Playwright tests
 *
 * This file creates an authenticated session that can be reused across tests.
 * Run: npx playwright test --project=setup
 */

import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../../.auth/user.json');

setup('authenticate', async ({ page }) => {
  const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

  // Go to login page
  await page.goto(`${BASE_URL}/login`);

  // Fill in test name (simple name-based auth, no password needed)
  await page.fill('#name', 'Test User');

  // Click login button
  await page.click('button[type="submit"]');

  // Wait for redirect to home or onboarding page (indicating successful login)
  // The app might redirect to /onboarding for first-time users or / for returning users
  await page.waitForURL(new RegExp(`${BASE_URL}/(onboarding)?`), { timeout: 10000 });

  // If redirected to onboarding, skip it
  const url = page.url();
  if (url.includes('/onboarding')) {
    // Look for a skip or continue button
    const skipButton = page.locator('button:has-text("Skip")');
    const continueButton = page.locator('button:has-text("Continue")');
    const getStartedButton = page.locator('button:has-text("Get Started")');

    if (await skipButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await skipButton.click();
    } else if (await continueButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await continueButton.click();
    } else if (await getStartedButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await getStartedButton.click();
    }

    // Wait for redirect to home
    await page.waitForURL(`${BASE_URL}/`, { timeout: 5000 }).catch(() => {
      // Might already be on home, that's ok
    });
  }

  // Verify we're logged in - should be on home page or have navigation visible
  await expect(page.locator('nav, header')).toBeVisible({ timeout: 5000 });

  // Save authentication state
  await page.context().storageState({ path: authFile });
});
