# FunnelFunction Schema Models & Plugins

> **"Each schema is a universe unto itself."**

## Philosophy

This repository contains **self-contained, copy-paste-ready** data collection schemas for [FunnelFunction](https://funnelfunction.com). Every file in this repo is designed to work independently—no imports, no dependencies on other files here.

### The Golden Rule

```
✅ CORRECT: One file = One complete schema
   Copy google_maps_scraper.py → Paste anywhere → It runs

❌ WRONG: Files that import from each other
   scraper.ts imports from utils.ts imports from config.ts
```

### Why Self-Contained?

1. **Portability** - Copy one file to any project, it works
2. **Clarity** - Everything you need is visible in one place
3. **Testability** - Run/debug one file in isolation
4. **Shareability** - Users can grab exactly what they need

---

## Repository Structure

```
src_0.0_Schema_Models_Plugins/
│
├── 0.0_Core_Lead_Ontology/           ← THE canonical lead definition
│   ├── lead_schema_definition.ts     ← What IS a lead?
│   └── README.md
│
├── 1.0_Keyless_Scrapers/             ← No API key required
│   ├── 1.0.a_Google_Maps_Playwright/
│   ├── 1.0.b_DuckDuckGo_Places/
│   ├── 1.0.c_Yelp_Business/
│   ├── 1.0.d_YellowPages/
│   └── 1.0.e_BBB_Directory/
│
├── 2.0_API_Schemas/                  ← Requires API key
│   ├── 2.0.a_HunterIO/
│   ├── 2.0.b_Clearbit/
│   └── 2.0.c_Apollo/
│
├── 3.0_Data_Transformers/            ← Format converters
│   ├── csv_to_lead_transformer.ts
│   └── json_to_lead_transformer.ts
│
└── 4.0_Handshake_Templates/          ← Protocol-OS templates
    ├── curl_templates/
    └── oauth_templates/
```

---

## How to Use a Schema

### For FunnelFunction App Users

1. Browse to the schema you want
2. Copy the entire file
3. Paste into Librarian's Sync tab (or your engine config)
4. Done—the schema connects to your existing Playwright/ScraperBee infrastructure

### For External Users

1. Copy the schema file
2. Install listed dependencies (in file header)
3. Run directly—it's self-contained

---

## Schema File Anatomy

Every schema follows this structure:

```python
# -*- coding: utf-8 -*-
"""
SCHEMA: Google Maps Business Scraper
VERSION: 1.0.0
AUTHOR: FunnelFunction
DEPENDENCIES: playwright, beautifulsoup4, fake-useragent
OUTPUT: BusinessEntitySearchResult[]

This schema scrapes Google Maps for business listings.
It extracts: name, address, phone, website, email, rating, reviews.
"""

# ============================================
# CONSTANTS (no external imports)
# ============================================
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
SELECTORS = {
    'search_input': '#searchboxinput',
    'result_card': '.hfpxzc',
    # ... all selectors defined here
}

# ============================================
# HELPER FUNCTIONS (self-contained)
# ============================================
def extract_emails(text): ...
def crawl_website(url): ...

# ============================================
# MAIN SCRAPER LOGIC
# ============================================
async def run(playwright, category, city, state): ...

# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    asyncio.run(main())
```

---

## Output Contract

All scrapers output data matching the **FunnelFunction Lead Ontology**:

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `business_name` | string | YES | For {{business_name}} template replacement |
| `business_address` | string | NO | Full street address |
| `business_city` | string | NO | City name |
| `business_state` | string | NO | State/Province |
| `business_zip` | string | NO | ZIP/Postal code |
| `business_phone` | string | NO | Primary phone number |
| `business_website` | string | YES* | Domain for email discovery |
| `business_email` | string | YES* | Primary outreach email |
| `business_category` | string | NO | Industry/niche |
| `rating` | string | NO | Star rating if available |
| `review_count` | string | NO | Number of reviews |

*At least one of `business_website` or `business_email` required for outreach.

---

## Contributing

1. Fork this repo
2. Create your schema as a **single self-contained file**
3. Follow the naming convention: `{number}_{source}_scraper.{ext}`
4. Include a header comment with VERSION, DEPENDENCIES, OUTPUT
5. Test in isolation before submitting
6. Submit PR

---

## Related Repositories

- [0.0_funnelfunction_app](https://github.com/FunnelFunction/0.0_funnelfunction_app) - Main application (private)
- [0.0_git_funnelfunction_marketing_Principals](https://github.com/FunnelFunction/0.0_git_funnelfunction_marketing_Principals) - Marketing mathematics
- [Intent Tensor Theory](https://github.com/intent-tensor-theory/0.0_Coding_Principals_Intent_Tensor_Theory) - Coding principles

---

## License

MIT License - See [LICENSE](LICENSE)

---

*Built by Armstrong Knight & Abdullah Khan at [Funnel Function LLC](https://funnelfunction.com)*
