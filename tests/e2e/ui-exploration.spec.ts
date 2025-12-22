/**
 * UI Exploration Test - Systematically tests all pages and reports bugs/usability issues
 */

import { test, expect, Page } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3004';

// Helper to capture page state for reporting
async function capturePageState(page: Page, pageName: string) {
  const issues: string[] = [];

  // Check for console errors
  const consoleErrors: string[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  // Check for failed network requests
  page.on('requestfailed', request => {
    issues.push(`NETWORK_ERROR: ${request.url()} - ${request.failure()?.errorText}`);
  });

  // Wait for page to settle
  await page.waitForLoadState('networkidle').catch(() => {});

  // Check for visible error messages
  const errorElements = await page.locator('[class*="error"], [class*="Error"], .text-red-500, .text-red-600, .text-red-700').all();
  for (const el of errorElements) {
    const text = await el.textContent().catch(() => '');
    if (text && text.trim()) {
      issues.push(`UI_ERROR: ${text.trim()}`);
    }
  }

  // Check for loading spinners that never resolve (stuck loading)
  const loadingElements = await page.locator('[class*="loading"], [class*="Loading"], [class*="spinner"]').count();

  return {
    pageName,
    issues,
    consoleErrors,
    hasStuckLoading: loadingElements > 0,
    url: page.url(),
  };
}

test.describe('UI Exploration', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto(`${BASE_URL}/login`);
    await page.fill('#name', 'UI Tester');
    await page.click('button[type="submit"]');

    // Wait for navigation
    await page.waitForURL(/\/(onboarding)?/, { timeout: 10000 });

    // If on onboarding, complete it
    if (page.url().includes('/onboarding')) {
      // Click through all onboarding steps
      for (let i = 0; i < 6; i++) {
        const nextButton = page.locator('button').filter({ hasText: /next|get started|continue|finish|start exploring/i }).first();
        if (await nextButton.isVisible({ timeout: 2000 }).catch(() => false)) {
          await nextButton.click();
          await page.waitForTimeout(500);
        }
      }
    }

    // Should now be on homepage with nav
    await page.waitForURL(`${BASE_URL}/`, { timeout: 10000 }).catch(() => {});
  });

  test('HomePage', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('networkidle').catch(() => {});

    // Check nav is visible
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: 'test-results/homepage.png', fullPage: true });

    // Log page title
    console.log('HomePage title:', await page.title());
  });

  test('Offers Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/offers`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/offers-page.png', fullPage: true });

    // Check for expected elements
    const heading = page.locator('h1, h2').first();
    console.log('Offers page heading:', await heading.textContent().catch(() => 'No heading'));
  });

  test('Create Offer Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/offers/create`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/create-offer-page.png', fullPage: true });

    // Check form exists
    const form = page.locator('form');
    const formVisible = await form.isVisible().catch(() => false);
    console.log('Create Offer form visible:', formVisible);
  });

  test('Needs Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/needs`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/needs-page.png', fullPage: true });
  });

  test('Create Need Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/needs/create`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/create-need-page.png', fullPage: true });
  });

  test('Exchanges Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/exchanges`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/exchanges-page.png', fullPage: true });
  });

  test('Discovery Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/discovery`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/discovery-page.png', fullPage: true });
  });

  test('Network Resources Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/network-resources`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/network-resources-page.png', fullPage: true });
  });

  test('Knowledge Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/knowledge`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/knowledge-page.png', fullPage: true });
  });

  test('Network Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/network`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/network-page.png', fullPage: true });
  });

  test('Agents Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/agents`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/agents-page.png', fullPage: true });
  });

  test('Cells Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/cells`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/cells-page.png', fullPage: true });
  });

  test('Create Cell Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/cells/create`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/create-cell-page.png', fullPage: true });
  });

  test('Messages Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/messages`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/messages-page.png', fullPage: true });
  });

  test('New Message Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/messages/new`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/new-message-page.png', fullPage: true });
  });

  test('Steward Dashboard Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/steward`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/steward-dashboard-page.png', fullPage: true });
  });

  test('Rapid Response Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/rapid-response`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/rapid-response-page.png', fullPage: true });
  });

  test('Communities Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/communities`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/communities-page.png', fullPage: true });
  });

  test('Community Shelf Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/community-shelf`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/community-shelf-page.png', fullPage: true });
  });

  test('Profile Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/profile`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/profile-page.png', fullPage: true });
  });

  test('Power Dynamics Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/power-dynamics`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/power-dynamics-page.png', fullPage: true });
  });

  test('Event Create Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/events/create`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/event-create-page.png', fullPage: true });
  });

  test('Event Join Page', async ({ page }) => {
    await page.goto(`${BASE_URL}/join/event`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/event-join-page.png', fullPage: true });
  });
});
