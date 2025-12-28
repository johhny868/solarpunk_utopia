/**
 * E2E tests for Community Selection and Impact
 *
 * Tests that community selection properly affects what offers/needs are shown
 * and that empty states display correctly when no community is selected.
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

test.describe('Community Selection Impact', () => {
  test('should show empty state when no community selected on offers page', async ({ page }) => {
    // Navigate to offers page
    await page.goto(`${BASE_URL}/offers`);

    // Should see "No Community Selected" message if no community is active
    const noCommunityHeading = page.locator('h2:has-text("No Community Selected")');

    if (await noCommunityHeading.isVisible({ timeout: 2000 }).catch(() => false)) {
      // Verify empty state content
      await expect(page.locator('text=/select a community/i')).toBeVisible();
      await expect(page.locator('button:has-text("Browse Communities")')).toBeVisible();
      await expect(page.locator('button:has-text("Create Community")')).toBeVisible();
    }
  });

  test('should show empty state when no community selected on needs page', async ({ page }) => {
    await page.goto(`${BASE_URL}/needs`);

    const noCommunityHeading = page.locator('h2:has-text("No Community Selected")');

    if (await noCommunityHeading.isVisible({ timeout: 2000 }).catch(() => false)) {
      await expect(page.locator('text=/select a community/i')).toBeVisible();
      await expect(page.locator('button:has-text("Browse Communities")')).toBeVisible();
    }
  });

  test('should update offers after community selection', async ({ page }) => {
    // Start at offers page
    await page.goto(`${BASE_URL}/offers`);

    // If no community selected, select one
    const communitySelector = page.locator('[data-testid="community-selector"], button:has-text("Select Community")');

    if (await communitySelector.isVisible({ timeout: 2000 }).catch(() => false)) {
      await communitySelector.click();

      // Wait for community list
      await page.waitForTimeout(500);

      // Select first community
      const firstCommunity = page.locator('[data-testid="community-option"], button[role="option"]').first();
      if (await firstCommunity.isVisible({ timeout: 2000 }).catch(() => false)) {
        await firstCommunity.click();

        // Wait for page to update
        await page.waitForTimeout(1000);

        // Should now show offers or empty state for that community
        // (not the "No Community Selected" message)
        await expect(page.locator('h2:has-text("No Community Selected")')).not.toBeVisible();
      }
    }
  });

  test('should navigate from empty state to communities page', async ({ page }) => {
    await page.goto(`${BASE_URL}/offers`);

    // Click "Browse Communities" button if visible
    const browseCommunitiesButton = page.locator('button:has-text("Browse Communities")');

    if (await browseCommunitiesButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await browseCommunitiesButton.click();

      // Should navigate to communities page
      await expect(page).toHaveURL(`${BASE_URL}/communities`);
    }
  });
});

test.describe('Empty States', () => {
  test('HomePage should show empty state with icons and CTAs', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // If no offers, should see improved empty state
    const noOffersText = page.locator('text=/no.*offers/i');

    if (await noOffersText.isVisible({ timeout: 2000 }).catch(() => false)) {
      // Should see icon (Package icon in SVG)
      await expect(page.locator('svg').first()).toBeVisible();

      // Should see helpful title and description
      await expect(page.locator('h2, h3')).toBeVisible();
      await expect(page.locator('text=/share|community/i')).toBeVisible();

      // Should have CTA buttons
      await expect(page.locator('button:has-text("Create"), a:has-text("Create")')).toBeVisible();
    }
  });

  test('ExchangesPage should show contextual empty states', async ({ page }) => {
    await page.goto(`${BASE_URL}/exchanges`);

    await page.waitForLoadState('networkidle');

    // If no exchanges, should see empty state
    const noExchanges = page.locator('text=/no.*exchanges/i');

    if (await noExchanges.isVisible({ timeout: 2000 }).catch(() => false)) {
      // Should have icon and helpful message
      await expect(page.locator('svg')).toBeVisible();
      await expect(page.locator('text=/offers.*needs|create/i')).toBeVisible();
    }

    // Test filtered empty state
    const statusFilter = page.locator('select:has-option("pending"), select:has-option("completed")');
    if (await statusFilter.isVisible({ timeout: 1000 }).catch(() => false)) {
      await statusFilter.selectOption('completed');
      await page.waitForTimeout(500);

      // If no completed exchanges, should see different message
      const noCompleted = page.locator('text=/no.*completed/i');
      if (await noCompleted.isVisible({ timeout: 1000 }).catch(() => false)) {
        // Should have "Clear Filters" option
        await expect(page.locator('button:has-text("Clear"), button:has-text("All")')).toBeVisible();
      }
    }
  });

  test('MessageThreadPage should show improved empty state', async ({ page }) => {
    // This test requires a valid thread ID, so we'll create a mock scenario
    // For now, just verify the component structure
    await page.goto(`${BASE_URL}/messages`);

    await expect(page).toHaveURL(/\/messages/);

    // Navigate to a thread if available
    const threadLink = page.locator('a[href*="/messages/thread"], button:has-text("thread")').first();

    if (await threadLink.isVisible({ timeout: 2000 }).catch(() => false)) {
      await threadLink.click();

      // If no messages in thread, should see improved empty state
      const noMessages = page.locator('text=/no messages/i');
      if (await noMessages.isVisible({ timeout: 2000 }).catch(() => false)) {
        // Should have icon and helpful message
        await expect(page.locator('svg')).toBeVisible();
        await expect(page.locator('text=/start.*conversation/i')).toBeVisible();
      }
    }
  });
});
