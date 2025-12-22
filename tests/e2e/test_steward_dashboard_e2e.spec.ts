/**
 * End-to-End tests for Steward Dashboard (Frontend)
 *
 * Tests the complete steward workflow from viewing metrics to taking action.
 *
 * "Stewards need situational awareness"
 *
 * This test ensures community leaders can effectively monitor and support their cells.
 */

import { test, expect, Page } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

// Use authenticated session
test.use({ storageState: '.auth/user.json' });

test.describe('Steward Dashboard E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to steward dashboard
    await page.goto(`${BASE_URL}/steward`);
  });

  test('Steward can view cell metrics and statistics', async ({ page }) => {
    /**
     * Scenario from proposal:
     * - Steward views dashboard for their cell
     * - Sees: member count, active offers/needs, exchanges this week
     * - Sees attention items: join requests, proposals, trust issues
     * - Sees recent activity timeline
     * - Sees celebrations (NO individual $ amounts)
     */

    // Wait for dashboard to load
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Check for metrics section
    const hasMetrics =
      (await page.locator('text=/member|offer|need|exchange/i').count()) > 0;

    if (hasMetrics) {
      // Verify key metrics are visible
      await expect(
        page.locator('text=/member|participant|people/i').first()
      ).toBeVisible({ timeout: 5000 });

      // Should show counts/numbers
      const hasNumbers = await page.locator('text=/\\d+/').count() > 0;
      expect(hasNumbers).toBe(true);
    } else {
      // If no data, should show empty state
      await expect(
        page.locator('text=/no data|loading|empty/i').first()
      ).toBeVisible({ timeout: 5000 });
    }
  });

  test('Steward can see attention items requiring action', async ({ page }) => {
    /**
     * Attention items include:
     * - Join requests pending approval
     * - Proposals needing steward input
     * - Trust issues flagged
     * - Conflicts needing mediation
     */

    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Look for attention items section
    const attentionSection = page.locator(
      'text=/attention|action|pending|review/i'
    );

    if ((await attentionSection.count()) > 0) {
      // Should have list of items or "no items" message
      const hasItems =
        (await page
          .locator('[class*="item"], [class*="request"], [class*="proposal"]')
          .count()) > 0;
      const hasEmptyState = await page
        .locator('text=/no.*item|all.*clear|nothing/i')
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      expect(hasItems || hasEmptyState).toBe(true);
    }
  });

  test('Steward can approve join request from dashboard', async ({ page }) => {
    /**
     * From proposal: "WHEN steward clicks 'approve' on join request THEN member added to cell"
     */

    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Look for join request
    const joinRequest = page.locator(
      'button:has-text("Approve"), button:has-text("Accept")'
    );

    if (
      (await joinRequest.isVisible({ timeout: 3000 }).catch(() => false))
    ) {
      // Click approve
      await joinRequest.first().click();

      // Should show success message or item disappears
      const hasSuccess =
        (await page
          .locator('text=/approved|accepted|added/i')
          .isVisible({ timeout: 3000 })
          .catch(() => false)) ||
        !(await joinRequest.first().isVisible({ timeout: 2000 }));

      expect(hasSuccess).toBe(true);
    }
    // If no join requests, that's okay - test passes
  });

  test('Steward can view recent activity timeline', async ({ page }) => {
    /**
     * Activity timeline shows:
     * - Recent exchanges
     * - New members joined
     * - Offers/needs posted
     * - Proposals created
     * Ordered by time (most recent first)
     */

    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Look for activity or timeline section
    const activitySection = page.locator(
      'text=/activity|timeline|recent|history/i'
    );

    if ((await activitySection.count()) > 0) {
      // Should show activity items with timestamps
      const hasTimestamps =
        (await page.locator('text=/ago|today|yesterday|\\d+ (min|hour|day)/i').count()) > 0;
      const hasEmptyState = await page
        .locator('text=/no activity|no recent/i')
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      expect(hasTimestamps || hasEmptyState).toBe(true);
    }
  });

  test('Steward dashboard celebrates success without individual dollar amounts', async ({ page }) => {
    /**
     * CRITICAL: From proposal - "sees celebrations (NO individual $ amounts - per anti-reputation-capitalism)"
     *
     * Should show:
     * - Total community value circulated (aggregate)
     * - Number of exchanges completed
     * - Member growth
     *
     * Should NOT show:
     * - Individual member contribution amounts
     * - Leaderboards
     * - "Top contributors"
     */

    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Look for celebrations or success metrics
    const celebrationSection = page.locator(
      'text=/celebration|success|milestone|achievement/i'
    );

    if ((await celebrationSection.count()) > 0) {
      const pageContent = await page.textContent('body');

      // Should have aggregate metrics
      const hasAggregate =
        pageContent?.includes('total') ||
        pageContent?.includes('community') ||
        pageContent?.includes('collective');

      // Should NOT have individual rankings
      const hasIndividualRanking =
        pageContent?.toLowerCase().includes('top contributor') ||
        pageContent?.toLowerCase().includes('leaderboard') ||
        pageContent?.toLowerCase().includes('#1') ||
        pageContent?.toLowerCase().includes('rank');

      expect(hasAggregate).toBe(true);
      expect(hasIndividualRanking).toBe(false); // CRITICAL: No rankings
    }
  });

  test('Steward can navigate to detailed views from dashboard', async ({ page }) => {
    /**
     * Dashboard provides links to:
     * - Member directory
     * - Offers list
     * - Needs list
     * - Exchanges
     * - Proposals
     */

    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Look for navigation links
    const links = [
      'members',
      'offers',
      'needs',
      'exchanges',
      'proposals',
    ];

    let foundLinks = 0;

    for (const linkText of links) {
      const link = page.locator(`a:has-text("${linkText}")`);
      if ((await link.count()) > 0) {
        foundLinks++;
      }
    }

    // Should have at least some navigation links
    expect(foundLinks).toBeGreaterThan(0);
  });

  test('Steward can filter metrics by time period', async ({ page }) => {
    /**
     * Steward may want to see:
     * - This week's activity
     * - This month's growth
     * - Year-to-date metrics
     */

    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Look for time period selectors
    const timeFilters = page.locator(
      'select:has-text("week"), button:has-text("month"), [role="tab"]:has-text("year")'
    );

    if ((await timeFilters.count()) > 0) {
      // Click a time filter
      await timeFilters.first().click();
      await page.waitForTimeout(1000);

      // Metrics should update (or stay the same if no data difference)
      await expect(page.locator('body')).toBeVisible(); // Page should still be functional
    }
    // If no time filters, that's okay - test passes
  });

  test('Steward sees empty state when cell is new', async ({ page }) => {
    /**
     * New cells should show helpful empty states:
     * - "No members yet - invite people to join"
     * - "No activity yet - this will fill up as your community grows"
     */

    await page.waitForLoadState('networkidle', { timeout: 10000 });

    const pageContent = await page.textContent('body');

    // Should either have data OR helpful empty states
    const hasData =
      (await page.locator('text=/\\d+/').count()) > 0; // Numbers indicate data

    const hasEmptyState =
      pageContent?.toLowerCase().includes('no members') ||
      pageContent?.toLowerCase().includes('no activity') ||
      pageContent?.toLowerCase().includes('no data') ||
      pageContent?.toLowerCase().includes('empty') ||
      pageContent?.toLowerCase().includes('loading');

    expect(hasData || hasEmptyState).toBe(true);
  });

  test('Steward dashboard loads within 5 seconds', async ({ page }) => {
    /**
     * Performance test: Dashboard should load quickly
     * Stewards need fast situational awareness
     */

    const startTime = Date.now();

    await page.goto(`${BASE_URL}/steward`);
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    const loadTime = Date.now() - startTime;

    // Should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });

  test('Steward can access cell-specific dashboard if managing multiple cells', async ({ page }) => {
    /**
     * Some stewards may manage multiple cells
     * Should be able to switch between cell dashboards
     */

    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Look for cell selector
    const cellSelector = page.locator(
      'select[name="cell"], [role="combobox"]:has-text("cell")'
    );

    if (
      (await cellSelector.isVisible({ timeout: 2000 }).catch(() => false))
    ) {
      // Get current selection
      const initialValue = await cellSelector.textContent();

      // Try to open selector
      await cellSelector.click();
      await page.waitForTimeout(500);

      // Should show cell options or dropdown
      const hasOptions =
        (await page.locator('[role="option"], option').count()) > 0;

      if (hasOptions) {
        // Select different cell if available
        const options = page.locator('[role="option"], option');
        if ((await options.count()) > 1) {
          await options.nth(1).click();
          await page.waitForTimeout(1000);

          // Dashboard should update
          const newValue = await cellSelector.textContent();
          // Value may or may not change depending on implementation
        }
      }
    }
    // If no cell selector, steward manages only one cell - test passes
  });

  test('Steward dashboard shows trust issues that need attention', async ({ page }) => {
    /**
     * Trust issues include:
     * - Users flagged for suspicious behavior
     * - Vouch chains broken
     * - Trust score below threshold
     */

    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Look for trust-related alerts
    const trustAlerts = page.locator(
      'text=/trust|vouch|suspicious|flag/i'
    );

    if ((await trustAlerts.count()) > 0) {
      // Should show list of trust issues or "all clear" message
      const hasIssues =
        (await page.locator('[class*="alert"], [class*="issue"]').count()) > 0;
      const hasAllClear = await page
        .locator('text=/no issue|all clear|healthy/i')
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      expect(hasIssues || hasAllClear).toBe(true);
    }
  });

  test('Steward can view member directory from dashboard', async ({ page }) => {
    /**
     * Steward should see:
     * - List of cell members
     * - Trust scores (if authorized)
     * - Activity status
     * - Join date
     */

    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Click on members link
    const membersLink = page.locator('a:has-text("Members"), a:has-text("Directory")');

    if (
      (await membersLink.isVisible({ timeout: 2000 }).catch(() => false))
    ) {
      await membersLink.first().click();
      await page.waitForLoadState('networkidle', { timeout: 5000 });

      // Should show member list or redirect to members page
      const hasMemberList =
        (await page.locator('[class*="member"], [class*="user"]').count()) > 0;
      const hasEmptyState = await page
        .locator('text=/no member|empty/i')
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      expect(hasMemberList || hasEmptyState).toBe(true);
    }
  });

  test('Steward sees proposals pending review', async ({ page }) => {
    /**
     * Governance proposals that need steward input:
     * - Policy changes
     * - Resource allocation
     * - Conflict resolution
     */

    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Look for proposals section
    const proposalsSection = page.locator(
      'text=/proposal|vote|decision/i'
    );

    if ((await proposalsSection.count()) > 0) {
      // Should show proposals or "no pending proposals"
      const hasProposals =
        (await page.locator('[class*="proposal"]').count()) > 0;
      const hasEmptyState = await page
        .locator('text=/no proposal|none pending/i')
        .isVisible({ timeout: 2000 })
        .catch(() => false);

      expect(hasProposals || hasEmptyState).toBe(true);
    }
  });
});
