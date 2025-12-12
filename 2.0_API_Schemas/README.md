# 2.0 API Schemas

> **"When you have the key, use the front door."**

These schemas work with external APIs that require authentication (API keys, OAuth, etc.).

## Available Schemas

| Folder | Service | Status |
|--------|---------|--------|
| `2.0.a_HunterIO/` | Hunter.io Email Finder | 📋 Planned |
| `2.0.b_Clearbit/` | Clearbit Enrichment | 📋 Planned |
| `2.0.c_Apollo/` | Apollo.io | 📋 Planned |

## Architecture

Each schema defines:
- API endpoint configuration
- Authentication method (API key, OAuth, etc.)
- Request/Response mapping to `BusinessLeadRecord`
- Rate limiting parameters

