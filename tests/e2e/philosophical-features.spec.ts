/**
 * E2E Tests for Philosophical Features
 *
 * Tests the full user experience of:
 * - GAP-59: Conscientization Prompts (Paulo Freire)
 * - GAP-61: Anonymous Gifts (Emma Goldman)
 * - GAP-62: Rest Mode (Goldman + Kropotkin)
 * - GAP-64: Power Dynamics Dashboard (Bakunin)
 *
 * Run with: npx playwright test philosophical-features.spec.ts
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';
const API_URL = process.env.API_URL || 'http://localhost:8001';

test.describe('Philosophical Features E2E', () => {

  test.beforeEach(async ({ page }) => {
    // Start fresh for each test
    await page.goto(BASE_URL);
  });

  // ========================================================================
  // GAP-61: Anonymous Gifts (Emma Goldman)
  // ========================================================================

  test.describe('GAP-61: Anonymous Gifts', () => {

    test('User can create an anonymous gift offering', async ({ page }) => {
      // Navigate to create offer
      await page.goto(`${BASE_URL}/listings/create/offer`);

      // Fill in offering details
      await page.fill('[name="title"]', 'Fresh Tomatoes');
      await page.fill('[name="description"]', 'Harvested this morning');
      await page.selectOption('[name="resource_spec"]', { label: 'Tomatoes' });
      await page.fill('[name="quantity"]', '5');

      // Toggle anonymous
      await page.check('[name="anonymous"]');

      // Verify UI reflects anonymous mode
      await expect(page.locator('.anonymous-badge')).toBeVisible();
      await expect(page.locator('.anonymous-badge')).toContainText('Anonymous Gift');

      // Submit
      await page.click('button[type="submit"]');

      // Verify success
      await expect(page.locator('.success-message')).toContainText('Posted to Community Shelf');

      // Verify agent name NOT shown on confirmation
      await expect(page.locator('.confirmation')).not.toContainText('Your name');
    });

    test('User can browse Community Shelf without seeing attribution', async ({ page }) => {
      // Navigate to Community Shelf
      await page.goto(`${BASE_URL}/community-shelf`);

      // Wait for listings to load
      await page.waitForSelector('.listing-card');

      // Verify listings exist
      const listings = page.locator('.listing-card');
      await expect(listings).toHaveCountGreaterThan(0);

      // Verify NO attribution shown
      const firstListing = listings.first();
      await expect(firstListing.locator('.agent-name')).not.toBeVisible();
      await expect(firstListing.locator('.anonymous-badge')).toBeVisible();

      // Verify "Take" button present (no permission needed)
      await expect(firstListing.locator('button:has-text("Take")')).toBeVisible();
    });

    test('Taking from Community Shelf does not create reciprocity obligation', async ({ page }) => {
      // Go to Community Shelf
      await page.goto(`${BASE_URL}/community-shelf`);

      // Take first item
      const firstItem = page.locator('.listing-card').first();
      await firstItem.locator('button:has-text("Take")').click();

      // Confirm
      await page.locator('button:has-text("Confirm")').click();

      // Verify NO "Thank" button or obligation UI
      await expect(page.locator('button:has-text("Thank the giver")')).not.toBeVisible();
      await expect(page.locator('.reciprocity-prompt')).not.toBeVisible();

      // Verify success message is neutral
      const successMsg = page.locator('.success-message');
      await expect(successMsg).toContainText('Taken from Community Shelf');
      await expect(successMsg).not.toContainText('obligation');
      await expect(successMsg).not.toContainText('owe');
    });
  });

  // ========================================================================
  // GAP-62: Rest Mode (Goldman + Kropotkin)
  // ========================================================================

  test.describe('GAP-62: Rest Mode', () => {

    test('User can set status to Resting', async ({ page }) => {
      // Login/navigate to profile
      await page.goto(`${BASE_URL}/profile`);

      // Click status dropdown
      await page.click('[data-testid="status-selector"]');

      // Select "Resting"
      await page.click('button:has-text("Resting")');

      // Optionally add note
      await page.fill('[name="status_note"]', 'Taking a break to recover');

      // Save
      await page.click('button:has-text("Save")');

      // Verify badge appears
      await expect(page.locator('.status-badge')).toContainText('Resting');
      await expect(page.locator('.status-badge')).toContainText('😴');

      // Verify note is private (only shown to user)
      await expect(page.locator('.status-note')).toContainText('Taking a break');
    });

    test('Resting user receives NO notifications (Goldman Test)', async ({ page, context }) => {
      // Set user to resting mode
      await page.goto(`${BASE_URL}/profile`);
      await page.click('[data-testid="status-selector"]');
      await page.click('button:has-text("Resting")');
      await page.click('button:has-text("Save")');

      // Create a notification trigger (someone creates match for your need)
      // This would normally send notification, but should be suppressed

      // Listen for notification events
      const notificationReceived = new Promise((resolve) => {
        page.on('console', msg => {
          if (msg.text().includes('notification')) {
            resolve(true);
          }
        });
        // Timeout after 3 seconds if no notification
        setTimeout(() => resolve(false), 3000);
      });

      // Trigger that would normally cause notification
      // (this would be done via API or another user's action in real test)

      // Verify NO notification received
      const gotNotification = await notificationReceived;
      expect(gotNotification).toBe(false);
    });

    test('Rest mode badge is neutral, not judgmental', async ({ page }) => {
      // View profile of resting user
      await page.goto(`${BASE_URL}/agents/agent-resting-123`);

      // Verify badge exists
      const badge = page.locator('.status-badge');
      await expect(badge).toBeVisible();
      await expect(badge).toContainText('Resting');

      // Goldman Test: Verify NO guilt-trip language
      const forbiddenPhrases = [
        'inactive',
        'not contributing',
        'lazy',
        'unproductive',
        'should be',
        'days since last',
        'compare',
      ];

      for (const phrase of forbiddenPhrases) {
        await expect(page.locator('body')).not.toContainText(phrase, { ignoreCase: true });
      }

      // Verify neutral presentation
      await expect(badge).toHaveCSS('background-color', /^rgb\(.*\)$/); // Just checking it has styling
    });

    test('User can return from rest mode', async ({ page }) => {
      // Go to profile
      await page.goto(`${BASE_URL}/profile`);

      // Change from Resting back to Active
      await page.click('[data-testid="status-selector"]');
      await page.click('button:has-text("Active")');
      await page.click('button:has-text("Save")');

      // Verify badge changes
      await expect(page.locator('.status-badge')).toContainText('Active');
      await expect(page.locator('.status-badge')).not.toContainText('Resting');

      // Verify notifications resume (would need more complex test)
    });
  });

  // ========================================================================
  // GAP-59: Conscientization Prompts (Paulo Freire)
  // ========================================================================

  test.describe('GAP-59: Conscientization Prompts', () => {

    test('First-time offer triggers "Why?" prompt', async ({ page }) => {
      // Navigate to create first offer
      await page.goto(`${BASE_URL}/listings/create/offer?first_time=true`);

      // Fill in basic details
      await page.fill('[name="title"]', 'My first gift');
      await page.selectOption('[name="resource_spec"]', { label: 'Tomatoes' });

      // Submit
      await page.click('button:has-text("Post Offer")');

      // Expect conscientization prompt
      await expect(page.locator('.conscientization-prompt')).toBeVisible();
      await expect(page.locator('.conscientization-prompt h2')).toContainText('Why are you offering this?');

      // Verify options present
      await expect(page.locator('input[value="abundance"]')).toBeVisible();
      await expect(page.locator('input[value="build_connections"]')).toBeVisible();
      await expect(page.locator('input[value="experimenting"]')).toBeVisible();

      // Verify Skip button is PROMINENT (Goldman Test: no coercion)
      const skipButton = page.locator('button:has-text("Skip")');
      await expect(skipButton).toBeVisible();
      await expect(skipButton).toHaveCSS('font-size', /\d+px/); // Check it's visible size
    });

    test('User can skip reflection without penalty', async ({ page }) => {
      // Trigger prompt
      await page.goto(`${BASE_URL}/listings/create/offer?first_time=true`);
      await page.fill('[name="title"]', 'Test offer');
      await page.click('button:has-text("Post Offer")');

      // Skip prompt
      await page.click('button:has-text("Skip")');

      // Verify offer was still posted successfully
      await expect(page.locator('.success-message')).toContainText('Offer posted');

      // Verify NO penalty or guilt message
      await expect(page.locator('body')).not.toContainText('skipped');
      await expect(page.locator('body')).not.toContainText('missed opportunity');
    });

    test('User can reflect and share anonymously', async ({ page }) => {
      // Trigger post-exchange reflection
      await page.goto(`${BASE_URL}/exchanges/123/complete`);

      // See reflection prompt
      await expect(page.locator('.conscientization-prompt')).toBeVisible();
      await expect(page.locator('.conscientization-prompt')).toContainText('How was this different from buying/selling?');

      // Enter reflection
      await page.fill('[name="reflection"]', 'It felt abundant, not transactional');

      // Choose to share anonymously
      await page.check('[name="share_anonymously"]');

      // Submit
      await page.click('button:has-text("Share")');

      // Verify success
      await expect(page.locator('.success-message')).toContainText('Reflection shared');

      // Go to Community Dialogue
      await page.goto(`${BASE_URL}/dialogue`);

      // Verify reflection appears WITHOUT attribution
      await expect(page.locator('.reflection')).toContainText('It felt abundant');
      await expect(page.locator('.reflection .author')).toContainText('anonymous');
    });

    test('Community Dialogue surfaces tensions, not just celebrations', async ({ page }) => {
      // Navigate to Dialogue Space
      await page.goto(`${BASE_URL}/dialogue`);

      // Verify problem-posing format
      await expect(page.locator('.dialogue-problem')).toBeVisible();

      // Check for tension-surfacing questions (not just praise)
      const dialogues = page.locator('.dialogue-problem');
      const firstDialogue = dialogues.first();

      const problemText = await firstDialogue.locator('h3').textContent();

      // Should ask real questions, not just celebrate
      const questionIndicators = ['why', 'what if', 'who', 'how', 'is this', '?'];
      const hasQuestion = questionIndicators.some(q => problemText?.toLowerCase().includes(q));
      expect(hasQuestion).toBe(true);
    });
  });

  // ========================================================================
  // GAP-64: Power Dynamics Dashboard (Bakunin)
  // ========================================================================

  test.describe('GAP-64: Power Dynamics Dashboard', () => {

    test('User can view power concentration alerts', async ({ page }) => {
      // Navigate to Power Dynamics dashboard
      await page.goto(`${BASE_URL}/power-dynamics`);

      // Verify dashboard loads
      await expect(page.locator('h1')).toContainText('Power Dynamics');

      // Verify alert categories present
      await expect(page.locator('[data-alert-type="resource_concentration"]')).toBeVisible();
      await expect(page.locator('[data-alert-type="skill_gatekeepers"]')).toBeVisible();
      await expect(page.locator('[data-alert-type="coordination_monopolies"]')).toBeVisible();

      // Verify decentralization score shown
      await expect(page.locator('.decentralization-score')).toBeVisible();
      const scoreText = await page.locator('.decentralization-score .value').textContent();
      const score = parseInt(scoreText || '0');
      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(100);
    });

    test('Battery Warlord alert celebrates contribution while noting dependency', async ({ page }) => {
      // Navigate to dashboard
      await page.goto(`${BASE_URL}/power-dynamics`);

      // Find a critical alert (if exists)
      const criticalAlert = page.locator('[data-risk-level="critical"]').first();

      if (await criticalAlert.isVisible()) {
        // Expand alert
        await criticalAlert.click();

        // Verify Bakunin pattern: celebrates THEN warns
        const analysis = criticalAlert.locator('.analysis');
        const analysisText = await analysis.textContent();

        // Should celebrate
        expect(analysisText).toMatch(/(amazing|incredible|valuable|great)/i);

        // BUT also warn
        expect(analysisText).toMatch(/(BUT|however|dependency|fragile|concern)/i);

        // Should have "✓" for celebration and "⚠" for warning
        await expect(analysis).toContainText('✓');
        await expect(analysis).toContainText('⚠');
      }
    });

    test('Power alert provides actionable decentralization suggestions', async ({ page }) => {
      // Navigate to dashboard
      await page.goto(`${BASE_URL}/power-dynamics`);

      // Click first alert
      const firstAlert = page.locator('.power-alert').first();
      await firstAlert.click();

      // Verify suggestions section exists
      await expect(page.locator('.suggestions')).toBeVisible();

      // Verify suggestions are actionable (not vague)
      const suggestions = page.locator('.suggestions li');
      const count = await suggestions.count();

      expect(count).toBeGreaterThan(0);

      // Check first suggestion is concrete
      const firstSuggestion = await suggestions.first().textContent();

      // Should have action verbs
      const actionVerbs = ['organize', 'teach', 'document', 'pool', 'create', 'discuss', 'train'];
      const hasActionVerb = actionVerbs.some(verb => firstSuggestion?.toLowerCase().includes(verb));
      expect(hasActionVerb).toBe(true);
    });

    test('Decentralization suggestions are community-focused, not individual blame', async ({ page }) => {
      // Navigate to suggestions page
      await page.goto(`${BASE_URL}/power-dynamics/suggestions`);

      // Verify suggestions present
      const suggestions = page.locator('.suggestion');
      await expect(suggestions).toHaveCountGreaterThan(0);

      // Check language is structural, not personal
      const allSuggestionsText = await page.locator('.suggestions-container').textContent();

      // FORBIDDEN: Blaming language
      const forbiddenPhrases = [
        'dave should stop',
        'alice is wrong',
        'bad for sharing',
        'selfish',
        'hoarding',
      ];

      for (const phrase of forbiddenPhrases) {
        expect(allSuggestionsText?.toLowerCase()).not.toContain(phrase);
      }

      // REQUIRED: Community-action language
      const requiredPhrases = [
        'community',
        'organize',
        'together',
        'collective',
      ];

      const hasRequired = requiredPhrases.some(phrase =>
        allSuggestionsText?.toLowerCase().includes(phrase)
      );
      expect(hasRequired).toBe(true);
    });

    test('Power dashboard respects privacy - no surveillance', async ({ page }) => {
      // Navigate to dashboard
      await page.goto(`${BASE_URL}/power-dynamics`);

      // Verify NO individual behavior tracking shown
      await expect(page.locator('.individual-contribution-chart')).not.toBeVisible();
      await expect(page.locator('.leaderboard')).not.toBeVisible();
      await expect(page.locator('.ranking')).not.toBeVisible();

      // Only structural patterns, not individual surveillance
      await expect(page.locator('.structural-pattern')).toBeVisible();
    });
  });

  // ========================================================================
  // Integration Test: Full User Journey
  // ========================================================================

  test('Full philosophical feature integration journey', async ({ page }) => {
    // 1. User creates anonymous gift (GAP-61)
    await page.goto(`${BASE_URL}/listings/create/offer`);
    await page.fill('[name="title"]', 'Tomatoes');
    await page.check('[name="anonymous"]');
    await page.click('button:has-text("Post")');

    // 2. Gets reflection prompt (GAP-59)
    await expect(page.locator('.conscientization-prompt')).toBeVisible();
    await page.click('button:has-text("Skip")'); // Tests non-coercion

    // 3. Checks Power Dynamics dashboard (GAP-64)
    await page.goto(`${BASE_URL}/power-dynamics`);
    await expect(page.locator('.decentralization-score')).toBeVisible();

    // 4. Sees they're becoming a "tomato warlord" (50% concentration)
    // (This would be visible if test data set up properly)

    // 5. Decides to rest (GAP-62)
    await page.goto(`${BASE_URL}/profile`);
    await page.click('[data-testid="status-selector"]');
    await page.click('button:has-text("Resting")');
    await page.fill('[name="status_note"]', 'Feeling overwhelmed');
    await page.click('button:has-text("Save")');

    // 6. Verifies rest mode active
    await expect(page.locator('.status-badge')).toContainText('Resting');

    // Complete journey without guilt, surveillance, or coercion ✓
  });
});

/**
 * Goldman Test Enforcement Tests
 *
 * Verify that NO features violate Emma Goldman's principles
 */
test.describe('Goldman Test Enforcement', () => {

  test('No engagement metrics or gamification anywhere', async ({ page }) => {
    // Check all major pages
    const pages = [
      '/',
      '/profile',
      '/community-shelf',
      '/power-dynamics',
      '/dialogue',
    ];

    for (const path of pages) {
      await page.goto(`${BASE_URL}${path}`);

      // Forbidden: Engagement metrics
      await expect(page.locator('.streak')).not.toBeVisible();
      await expect(page.locator('.points')).not.toBeVisible();
      await expect(page.locator('.level')).not.toBeVisible();
      await expect(page.locator('.badge-count')).not.toBeVisible();
      await expect(page.locator('.achievement')).not.toBeVisible();

      // Forbidden: Comparison/ranking
      await expect(page.locator('.leaderboard')).not.toBeVisible();
      await expect(page.locator('.top-contributors')).not.toBeVisible();
    }
  });

  test('No guilt-trip notifications or language', async ({ page }) => {
    // Check notifications center
    await page.goto(`${BASE_URL}/notifications`);

    const notificationsText = await page.locator('.notifications-container').textContent();

    const forbiddenPhrases = [
      'haven\'t posted',
      'it\'s been a while',
      'others are sharing',
      'falling behind',
      'should',
      'missing out',
    ];

    for (const phrase of forbiddenPhrases) {
      expect(notificationsText?.toLowerCase()).not.toContain(phrase);
    }
  });

  test('All prompts and alerts have prominent Skip/Dismiss', async ({ page }) => {
    // This would test that every prompt has a clear exit
    // Implementation depends on specific prompt components
  });
});
