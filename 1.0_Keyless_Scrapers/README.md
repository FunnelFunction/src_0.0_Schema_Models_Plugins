# 1.0 Keyless Scrapers

> **"No API key required. Just DOM negotiation."**

These scrapers work by navigating directly to websites and extracting data from the HTML/DOM. They don't require any API keys from the data sources themselves.

## Available Scrapers

| Folder | Source | Status |
|--------|--------|--------|
| `1.0.a_Google_Maps_Playwright/` | Google Maps | ✅ Complete |
| `1.0.b_DuckDuckGo_Places/` | DuckDuckGo Local | 📋 Planned |
| `1.0.c_Yelp_Business/` | Yelp | 📋 Planned |
| `1.0.d_YellowPages/` | YellowPages.com | 📋 Planned |
| `1.0.e_BBB_Directory/` | Better Business Bureau | 📋 Planned |

## Architecture

Each scraper is **self-contained**:
- All selectors, constants, and logic in ONE file
- No imports from other files in this repo
- Copy → Paste → Run

## Required Infrastructure

These scrapers typically need:
- `playwright` - Browser automation
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests
- `fake_useragent` - Anti-bot measure

Your app should have these installed. The scraper file just provides the navigation logic and selectors.

## Anti-Bot Patterns

All keyless scrapers implement:
1. **User-Agent Rotation** - Random browser fingerprints
2. **Human-like Delays** - Typing and click delays
3. **Fallback Proxies** - ScraperAPI or similar when blocked
4. **Consent Handling** - GDPR/cookie dialogs
5. **Rate Limiting** - Semaphores to prevent hammering
