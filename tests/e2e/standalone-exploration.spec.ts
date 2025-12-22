/**
 * Standalone UI Exploration Test - No setup dependencies
 * Tests all pages and reports bugs/usability issues
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3004';

// Issues found during testing
const issues: { type: string; page: string; description: string; severity: 'bug' | 'usability' }[] = [];

function recordIssue(type: string, page: string, description: string, severity: 'bug' | 'usability') {
  issues.push({ type, page, description, severity });
  console.log(`[${severity.toUpperCase()}] ${page}: ${description}`);
}

// Increase timeout for this comprehensive test
test.setTimeout(120000);

test.describe.configure({ mode: 'serial' });

test.describe('Standalone UI Exploration', () => {
  test('Complete flow - Login through all pages', async ({ page }) => {
    // Listen for console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(`[CONSOLE ERROR] ${msg.text()}`);
      }
    });

    // Listen for network errors
    page.on('requestfailed', request => {
      console.log(`[NETWORK ERROR] ${request.url()} - ${request.failure()?.errorText}`);
    });

    // ====== LOGIN PAGE ======
    console.log('\n=== Testing Login Page ===');
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/01-login-page.png', fullPage: true });

    // Check login form exists
    const nameInput = page.locator('#name');
    const submitBtn = page.locator('button[type="submit"]');

    if (!await nameInput.isVisible({ timeout: 5000 })) {
      recordIssue('MISSING_ELEMENT', 'Login', 'Name input field not found', 'bug');
    }
    if (!await submitBtn.isVisible({ timeout: 2000 })) {
      recordIssue('MISSING_ELEMENT', 'Login', 'Submit button not found', 'bug');
    }

    // Fill and submit login
    await nameInput.fill('UI Tester');
    await submitBtn.click();

    // Wait for navigation
    await page.waitForTimeout(2000);
    console.log('After login, URL:', page.url());

    // ====== ONBOARDING PAGE ======
    if (page.url().includes('/onboarding')) {
      console.log('\n=== Testing Onboarding Page ===');
      await page.screenshot({ path: 'test-results/02-onboarding-step1.png', fullPage: true });

      // Specific onboarding button texts in order
      const onboardingButtons = [
        "Let's Get Started",  // WelcomeStep
        "I'm Ready to Share",  // GiftEconomyStep
        "Skip",               // CreateOfferStep (optional)
        "Next",               // BrowseOffersStep
        "Got It",             // AgentsHelpStep
        "Enter the Network"   // CompletionStep
      ];

      let stepCount = 0;
      while (page.url().includes('/onboarding') && stepCount < 10) {
        stepCount++;
        let clicked = false;

        // Try each button in order
        for (const text of onboardingButtons) {
          const btn = page.locator('button').filter({ hasText: new RegExp(text, 'i') }).first();
          if (await btn.isVisible({ timeout: 500 }).catch(() => false)) {
            await page.screenshot({ path: `test-results/02-onboarding-step${stepCount}.png`, fullPage: true });
            console.log(`Step ${stepCount}: Clicking "${text}"`);
            await btn.click();
            await page.waitForTimeout(500);
            clicked = true;
            break;
          }
        }

        if (!clicked) {
          // Try any button that looks like a "next" action
          const anyBtn = page.locator('button').filter({ hasText: /→|next|continue|skip|finish|start|done|got it|enter/i }).first();
          if (await anyBtn.isVisible({ timeout: 500 }).catch(() => false)) {
            const btnText = await anyBtn.textContent();
            console.log(`Step ${stepCount}: Clicking fallback button "${btnText}"`);
            await anyBtn.click();
            await page.waitForTimeout(500);
          } else {
            console.log(`Step ${stepCount}: No button found, breaking`);
            break;
          }
        }
      }

      console.log(`Onboarding completed after ${stepCount} steps, URL: ${page.url()}`);
    }

    // Should now be on homepage
    await page.waitForTimeout(1000);

    // ====== HOMEPAGE ======
    console.log('\n=== Testing HomePage ===');
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/03-homepage.png', fullPage: true });

    // Check navigation
    const nav = page.locator('nav');
    if (!await nav.isVisible({ timeout: 5000 })) {
      recordIssue('MISSING_ELEMENT', 'HomePage', 'Navigation bar not visible', 'bug');
    }

    // Check nav items are visible
    const navItems = ['Home', 'Offers', 'Needs', 'Exchanges', 'Cells', 'Messages'];
    for (const item of navItems) {
      const link = page.locator(`nav a`).filter({ hasText: item }).first();
      if (!await link.isVisible({ timeout: 1000 }).catch(() => false)) {
        recordIssue('MISSING_NAV_ITEM', 'Navigation', `Nav item "${item}" not visible on desktop (might be mobile)`, 'usability');
      }
    }

    // ====== OFFERS PAGE ======
    console.log('\n=== Testing Offers Page ===');
    await page.goto(`${BASE_URL}/offers`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/04-offers-page.png', fullPage: true });

    // Check for error messages
    const errorElements = await page.locator('.text-red-500, .text-red-600, .text-red-700, [class*="error"]').all();
    for (const el of errorElements) {
      const text = await el.textContent().catch(() => '');
      if (text && text.trim().length > 0 && !text.includes('No')) {
        recordIssue('ERROR_DISPLAYED', 'Offers', `Error message visible: ${text.trim().substring(0, 100)}`, 'bug');
      }
    }

    // ====== CREATE OFFER PAGE ======
    console.log('\n=== Testing Create Offer Page ===');
    await page.goto(`${BASE_URL}/offers/create`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/05-create-offer-page.png', fullPage: true });

    // Check form elements
    const offerForm = page.locator('form');
    if (!await offerForm.isVisible({ timeout: 3000 }).catch(() => false)) {
      recordIssue('MISSING_ELEMENT', 'Create Offer', 'Form not visible', 'bug');
    }

    // ====== NEEDS PAGE ======
    console.log('\n=== Testing Needs Page ===');
    await page.goto(`${BASE_URL}/needs`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/06-needs-page.png', fullPage: true });

    // ====== CREATE NEED PAGE ======
    console.log('\n=== Testing Create Need Page ===');
    await page.goto(`${BASE_URL}/needs/create`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/07-create-need-page.png', fullPage: true });

    // ====== EXCHANGES PAGE ======
    console.log('\n=== Testing Exchanges Page ===');
    await page.goto(`${BASE_URL}/exchanges`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/08-exchanges-page.png', fullPage: true });

    // ====== DISCOVERY PAGE ======
    console.log('\n=== Testing Discovery Page ===');
    await page.goto(`${BASE_URL}/discovery`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/09-discovery-page.png', fullPage: true });

    // Check search functionality
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], input[placeholder*="Search" i]').first();
    if (!await searchInput.isVisible({ timeout: 2000 }).catch(() => false)) {
      recordIssue('MISSING_ELEMENT', 'Discovery', 'Search input not found or not obvious', 'usability');
    }

    // ====== KNOWLEDGE PAGE ======
    console.log('\n=== Testing Knowledge Page ===');
    await page.goto(`${BASE_URL}/knowledge`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/10-knowledge-page.png', fullPage: true });

    // ====== NETWORK PAGE ======
    console.log('\n=== Testing Network Page ===');
    await page.goto(`${BASE_URL}/network`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/11-network-page.png', fullPage: true });

    // ====== AGENTS PAGE ======
    console.log('\n=== Testing Agents Page ===');
    await page.goto(`${BASE_URL}/agents`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/12-agents-page.png', fullPage: true });

    // ====== CELLS PAGE ======
    console.log('\n=== Testing Cells Page ===');
    await page.goto(`${BASE_URL}/cells`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/13-cells-page.png', fullPage: true });

    // ====== CREATE CELL PAGE ======
    console.log('\n=== Testing Create Cell Page ===');
    await page.goto(`${BASE_URL}/cells/create`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/14-create-cell-page.png', fullPage: true });

    // ====== MESSAGES PAGE ======
    console.log('\n=== Testing Messages Page ===');
    await page.goto(`${BASE_URL}/messages`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/15-messages-page.png', fullPage: true });

    // ====== NEW MESSAGE PAGE ======
    console.log('\n=== Testing New Message Page ===');
    await page.goto(`${BASE_URL}/messages/new`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/16-new-message-page.png', fullPage: true });

    // ====== STEWARD DASHBOARD ======
    console.log('\n=== Testing Steward Dashboard ===');
    await page.goto(`${BASE_URL}/steward`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/17-steward-dashboard.png', fullPage: true });

    // ====== RAPID RESPONSE PAGE ======
    console.log('\n=== Testing Rapid Response Page ===');
    await page.goto(`${BASE_URL}/rapid-response`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/18-rapid-response-page.png', fullPage: true });

    // ====== COMMUNITIES PAGE ======
    console.log('\n=== Testing Communities Page ===');
    await page.goto(`${BASE_URL}/communities`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/19-communities-page.png', fullPage: true });

    // ====== COMMUNITY SHELF PAGE ======
    console.log('\n=== Testing Community Shelf Page ===');
    await page.goto(`${BASE_URL}/community-shelf`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/20-community-shelf-page.png', fullPage: true });

    // ====== PROFILE PAGE ======
    console.log('\n=== Testing Profile Page ===');
    await page.goto(`${BASE_URL}/profile`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/21-profile-page.png', fullPage: true });

    // ====== POWER DYNAMICS PAGE ======
    console.log('\n=== Testing Power Dynamics Page ===');
    await page.goto(`${BASE_URL}/power-dynamics`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/22-power-dynamics-page.png', fullPage: true });

    // ====== EVENT CREATE PAGE ======
    console.log('\n=== Testing Event Create Page ===');
    await page.goto(`${BASE_URL}/events/create`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/23-event-create-page.png', fullPage: true });

    // ====== EVENT JOIN PAGE ======
    console.log('\n=== Testing Event Join Page ===');
    await page.goto(`${BASE_URL}/join/event`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/24-event-join-page.png', fullPage: true });

    // ====== NETWORK RESOURCES PAGE ======
    console.log('\n=== Testing Network Resources Page ===');
    await page.goto(`${BASE_URL}/network-resources`);
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: 'test-results/25-network-resources-page.png', fullPage: true });

    // ====== SUMMARY ======
    console.log('\n\n========================================');
    console.log('=== ISSUES SUMMARY ===');
    console.log('========================================');
    console.log('Total issues found:', issues.length);

    if (issues.filter(i => i.severity === 'bug').length > 0) {
      console.log('\n🐛 BUGS:');
      issues.filter(i => i.severity === 'bug').forEach(i => {
        console.log(`  - [${i.page}] ${i.description}`);
      });
    }

    if (issues.filter(i => i.severity === 'usability').length > 0) {
      console.log('\n⚠️ USABILITY ISSUES:');
      issues.filter(i => i.severity === 'usability').forEach(i => {
        console.log(`  - [${i.page}] ${i.description}`);
      });
    }
    console.log('========================================\n');
  });
});
