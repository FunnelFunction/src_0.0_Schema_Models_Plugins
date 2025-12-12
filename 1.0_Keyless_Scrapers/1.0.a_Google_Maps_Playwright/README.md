# Google Maps Business Scraper with Email Discovery

## Overview

A complete, self-contained Playwright scraper that:
1. Searches Google Maps for businesses by keyword + location
2. Scrolls through all results
3. Extracts business details (name, address, phone, website, rating, reviews)
4. Visits each website to discover email addresses

## Dependencies

```bash
pip install gspread google-auth pandas requests beautifulsoup4 lxml 
pip install openpyxl fake-useragent tldextract playwright nest-asyncio
playwright install chromium
```

## Output Fields

| Field | Maps To | Example |
|-------|---------|---------|
| Title | `business_name` | "Bob's Plumbing LLC" |
| Address | `business_address` | "123 Main St, Denver, CO 80202" |
| City | `business_city` | "Denver" |
| State | `business_state` | "Colorado" |
| Phone | `business_phone` | "(303) 555-1234" |
| Website | `business_website` | "https://bobsplumbing.com" |
| Email | `business_email` | "bob@bobsplumbing.com" |
| Category | `business_category` | "Plumber" |
| Rating | `rating` | "4.5" |
| Total Reviews | `review_count` | "127" |

## Usage

### Standalone (Demo Mode)
```python
python google_maps_business_scraper.py
```

### With Google Sheets
1. Update `GOOGLE_SHEET_ID` in the script
2. Create sheets named "States and Cities" and "scrapedResults"
3. Run in Google Colab for authentication

### Programmatic
```python
from google_maps_business_scraper import run
from playwright.async_api import async_playwright

async with async_playwright() as playwright:
    results = await run(
        playwright,
        state="California",
        city="San Francisco", 
        country="USA",
        keywords=["Coffee Shop", "Bakery"]
    )
```

## Anti-Bot Measures

- ✅ Rotating User-Agent via `fake_useragent`
- ✅ ScraperAPI fallback for blocked requests
- ✅ Human-like typing delays (200ms)
- ✅ GDPR consent dialog handling
- ✅ Semaphore-based rate limiting

## Customization

### Change Keywords
Edit the `keywords` list in `main()` or pass as argument to `run()`.

### Change ScraperAPI Key
Update `SCRAPERAPI_KEY` constant.

### Disable Google Sheets
Comment out the `setup_google_sheets()` and related calls. Data will be returned directly from `run()`.
