# Playwright MCP Guide

## Installation Complete ✅

Playwright MCP server has been installed and configured in this project.

### Configuration

**Location**: `.mcp.json`

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"],
      "env": {
        "PLAYWRIGHT_BROWSERS_PATH": "/Users/annhoward/.cache/ms-playwright"
      }
    }
  }
}
```

---

## How to Use After Restart

### 1. Restart Claude Code

After restarting Claude Code, the Playwright MCP tools will be automatically available.

### 2. Available Playwright Tools

Once loaded, you'll have access to Playwright MCP tools for:

**Browser Automation:**
- `playwright_navigate` - Navigate to URLs
- `playwright_screenshot` - Take screenshots
- `playwright_click` - Click elements
- `playwright_fill` - Fill form fields
- `playwright_select` - Select dropdown options
- `playwright_evaluate` - Execute JavaScript

**Testing:**
- `playwright_expect` - Assertions for testing
- `playwright_waitFor` - Wait for elements/conditions
- `playwright_getElement` - Find elements by selector

### 3. Example UI Testing Commands

After restart, you can ask Claude to:

```
"Navigate to http://localhost:3000 and take a screenshot"
"Click the login button and fill in the username field"
"Test the registration flow and verify success message"
"Navigate through the app and document all pages with screenshots"
```

---

## Testing Your Frontend

### Start Your Frontend Server

```bash
cd /Users/annhoward/src/solarpunk_utopia/frontend
npm run dev
```

### Example Test Scenarios

1. **User Registration Flow**
   ```
   Navigate to http://localhost:3000/register
   Fill in username: "test_user"
   Fill in email: "test@example.com"
   Click submit button
   Verify success message appears
   Take screenshot
   ```

2. **Agent Dashboard**
   ```
   Navigate to http://localhost:3000/agents
   Wait for agents to load
   Take screenshot of each agent card
   Click on first agent
   Verify agent details display
   ```

3. **Offer/Need Creation**
   ```
   Navigate to http://localhost:3000/offers/create
   Fill in offer details
   Click submit
   Verify offer appears in list
   Take screenshot of confirmation
   ```

---

## Advanced Usage

### Multi-Step Flows

After restart, you can ask Claude to:

```
"Test the complete user journey:
1. Register new user
2. Create an offer
3. Browse community offers
4. Match with a need
5. Complete exchange
6. Take screenshots at each step"
```

### Visual Regression Testing

```
"Take screenshots of all main pages:
- Homepage
- Login
- Dashboard
- Agents page
- Offers page
- Needs page
- Settings

Save them to /screenshots/ folder for comparison"
```

### Accessibility Testing

```
"Navigate through the app and check:
- All buttons have aria-labels
- Forms have proper labels
- Color contrast ratios
- Keyboard navigation works
- Screen reader friendly markup"
```

---

## Configuration Options

### Browser Selection

To use Firefox or WebKit instead of Chromium, update `.mcp.json`:

```json
{
  "env": {
    "PLAYWRIGHT_BROWSER": "firefox"  // or "webkit"
  }
}
```

### Headless Mode

By default, Playwright runs in headless mode. To see the browser:

```json
{
  "env": {
    "PLAYWRIGHT_HEADLESS": "false"
  }
}
```

---

## Troubleshooting

### If Playwright Tools Don't Load

1. **Restart Claude Code** - MCP servers only load on startup
2. **Check .mcp.json syntax** - Ensure valid JSON
3. **Verify npx works**: `npx -y @executeautomation/playwright-mcp-server`
4. **Check browser installation**: `npx playwright install chromium`

### Permission Issues

If you get permission errors:
```bash
chmod +x node_modules/.bin/playwright
```

### Browser Not Found

Reinstall browsers:
```bash
npx playwright install --force
```

---

## Benefits for Workshop Testing

### Pre-Workshop Checklist

Use Playwright MCP to verify:
- ✅ All pages load without errors
- ✅ Forms submit successfully
- ✅ Navigation works across app
- ✅ Responsive design on mobile/tablet/desktop
- ✅ Error messages display correctly
- ✅ Loading states work
- ✅ Authentication flow complete

### Demo Preparation

1. **Screenshot Tour**: Generate screenshots of every feature for documentation
2. **Flow Validation**: Test each user journey end-to-end
3. **Visual Consistency**: Check design system across all pages
4. **Cross-Browser**: Test on Chromium, Firefox, WebKit
5. **Performance**: Measure page load times

---

## Integration with Existing Tests

### Complement Pytest Tests

Your existing Pytest tests cover:
- Backend API endpoints
- Database operations
- Business logic
- Integration flows

Playwright MCP adds:
- Frontend UI interactions
- Visual regression
- User experience flows
- Cross-browser compatibility
- Accessibility compliance

### E2E Testing Strategy

**Backend (Pytest):**
```python
# tests/test_governance_silence_weight.py
def test_create_vote_session():
    # Test API directly
    pass
```

**Frontend (Playwright MCP):**
```
Navigate to governance page
Create new vote via UI
Verify vote appears in list
Check silence weight displays
```

---

## Next Steps

1. **Restart Claude Code** to load Playwright MCP
2. **Start your frontend**: `cd frontend && npm run dev`
3. **Ask Claude to test**: "Navigate to localhost:3000 and test the login flow"
4. **Generate screenshots**: "Take screenshots of all pages for documentation"
5. **Test user flows**: "Test the complete offer creation and matching flow"

---

## Resources

- **Playwright Docs**: https://playwright.dev
- **MCP Server**: https://github.com/executeautomation/mcp-playwright
- **This Project's Frontend**: `/Users/annhoward/src/solarpunk_utopia/frontend/`

---

**Ready for comprehensive UI testing after restart!** 🎭
