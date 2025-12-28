/**
 * E2E tests for Offer Creation Flow
 *
 * Tests the complete user flow for creating offers, including:
 * - Form validation
 * - Successful creation
 * - Appearance in offers list
 * - Edit functionality
 * - Delete functionality
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

test.describe('Offer Creation Flow', () => {
  test('should create an offer with all fields', async ({ page }) => {
    // Navigate to create offer page
    await page.goto(`${BASE_URL}/offers/create`);

    // Wait for form to load
    await expect(page.locator('h1:has-text("Create an Offer")')).toBeVisible();

    // Fill in all form fields
    await page.fill('input[name="title"]', 'Fresh Tomatoes from Garden');
    await page.selectOption('select', { label: 'Tomatoes' });
    await page.fill('textarea[name="description"]', 'Organic heirloom tomatoes, freshly picked this morning');
    await page.fill('input[name="quantity"]', '5');
    await page.selectOption('select[name="unit"], select:has-option("kg")', 'kg');

    // Select location if available
    const locationSelect = page.locator('select:has-option("Community Garden"), select[name="location"]');
    if (await locationSelect.isVisible({ timeout: 1000 }).catch(() => false)) {
      await locationSelect.selectOption({ label: 'Community Garden' });
    }

    // Submit form
    await page.click('button[type="submit"]:has-text("Create Offer")');

    // Should redirect to offers page
    await page.waitForURL(`${BASE_URL}/offers`, { timeout: 10000 });

    // Should see success toast
    await expect(page.locator('text=/offer.*success|created/i')).toBeVisible({ timeout: 5000 });

    // Should see new offer in list
    await expect(page.locator('text=Fresh Tomatoes from Garden')).toBeVisible({ timeout: 5000 });
  });

  test('should create offer with minimal fields (title and quantity)', async ({ page }) => {
    await page.goto(`${BASE_URL}/offers/create`);

    // Fill only required fields
    await page.fill('input[name="title"]', 'Quick Offer Test');
    await page.fill('input[name="quantity"]', '1');

    // Submit
    await page.click('button[type="submit"]:has-text("Create Offer")');

    // Should succeed
    await page.waitForURL(`${BASE_URL}/offers`);
    await expect(page.locator('text=Quick Offer Test')).toBeVisible({ timeout: 5000 });
  });

  test('should show validation error if quantity is missing', async ({ page }) => {
    await page.goto(`${BASE_URL}/offers/create`);

    await page.fill('input[name="title"]', 'No Quantity Offer');
    // Don't fill quantity

    await page.click('button[type="submit"]');

    // Should show validation error
    await expect(page.locator('text=/quantity.*required|must.*greater/i')).toBeVisible({ timeout: 3000 });

    // Should NOT redirect
    await expect(page).toHaveURL(/\/offers\/create/);
  });

  test('should create anonymous gift when checkbox is checked', async ({ page }) => {
    await page.goto(`${BASE_URL}/offers/create`);

    await page.fill('input[name="title"]', 'Anonymous Community Gift');
    await page.fill('input[name="quantity"]', '3');

    // Check anonymous gift checkbox
    await page.check('input[name="anonymous"]');

    // Should show anonymous badge/indicator
    await expect(page.locator('text=/anonymous gift|🎁/i')).toBeVisible();

    await page.click('button[type="submit"]');

    // Should redirect to community shelf (not offers)
    await page.waitForURL(`${BASE_URL}/community-shelf`, { timeout: 10000 });
  });

  test('should set available dates correctly', async ({ page }) => {
    await page.goto(`${BASE_URL}/offers/create`);

    await page.fill('input[name="title"]', 'Seasonal Offer');
    await page.fill('input[name="quantity"]', '2');

    // Set available dates
    const today = new Date().toISOString().split('T')[0];
    const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];

    const availableFromInput = page.locator('input[type="date"]').first();
    const availableUntilInput = page.locator('input[type="date"]').last();

    await availableFromInput.fill(today);
    await availableUntilInput.fill(tomorrow);

    await page.click('button[type="submit"]');

    await page.waitForURL(`${BASE_URL}/offers`);
    await expect(page.locator('text=Seasonal Offer')).toBeVisible();
  });
});

test.describe('Offer Edit/Delete Flow', () => {
  test('should edit an existing offer', async ({ page }) => {
    // First create an offer to edit
    await page.goto(`${BASE_URL}/offers/create`);
    await page.fill('input[name="title"]', 'Original Offer Title');
    await page.fill('input[name="quantity"]', '10');
    await page.click('button[type="submit"]');
    await page.waitForURL(`${BASE_URL}/offers`);

    // Find and click edit button
    const editButton = page.locator('button:has-text("Edit")').first();
    await editButton.click();

    // Should navigate to edit page
    await expect(page).toHaveURL(/\/offers\/.*\/edit/);

    // Update title
    await page.fill('input[name="title"]', 'Updated Offer Title');

    // Save changes
    await page.click('button[type="submit"]:has-text("Save")');

    // Should redirect back to offers
    await page.waitForURL(`${BASE_URL}/offers`);

    // Should see updated title
    await expect(page.locator('text=Updated Offer Title')).toBeVisible();
    await expect(page.locator('text=Original Offer Title')).not.toBeVisible();
  });

  test('should delete an offer after confirmation', async ({ page }) => {
    // Create an offer to delete
    await page.goto(`${BASE_URL}/offers/create`);
    await page.fill('input[name="title"]', 'Offer To Delete');
    await page.fill('input[name="quantity"]', '1');
    await page.click('button[type="submit"]');
    await page.waitForURL(`${BASE_URL}/offers`);

    // Confirm offer exists
    await expect(page.locator('text=Offer To Delete')).toBeVisible();

    // Click delete button
    const deleteButton = page.locator('button:has-text("Delete")').first();

    // Handle confirmation dialog
    page.on('dialog', async dialog => {
      expect(dialog.type()).toBe('confirm');
      await dialog.accept();
    });

    await deleteButton.click();

    // Should see success toast
    await expect(page.locator('text=/deleted.*success/i')).toBeVisible({ timeout: 5000 });

    // Offer should be removed from list
    await expect(page.locator('text=Offer To Delete')).not.toBeVisible();
  });
});
