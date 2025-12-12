# Core Lead Ontology

> **"What IS a lead?"**

This folder contains the **single source of truth** for what constitutes a lead in FunnelFunction.

## Files

| File | Purpose |
|------|---------|
| `lead_schema_definition.ts` | The complete TypeScript interface and validators |

## The BusinessLeadRecord Interface

Every scraper, API integration, and data transformer in this repo must output data conforming to this interface:

```typescript
interface BusinessLeadRecord {
  // Required
  business_name: string;           // For {{business_name}} in emails
  
  // Location
  business_address?: string;
  business_city?: string;
  business_state?: string;         // Use "CO" not "Colorado"
  business_zip?: string;
  
  // Contact (at least one required for outreach)
  business_phone?: string;
  business_website?: string;       // For email discovery
  business_email?: string;         // The target
  
  // Classification
  business_category?: string;
  
  // Social proof
  rating?: string;
  review_count?: string;
}
```

## Why This Matters

When a scraper outputs:
```json
{
  "business_name": "Bob's Plumbing",
  "business_email": "bob@bobsplumbing.com"
}
```

The email engine can confidently do:
```
Subject: Partnership opportunity for {{business_name}}
→ Subject: Partnership opportunity for Bob's Plumbing
```

**No guessing. No auto-detection. Deterministic.**

## Field Mapping for Different Sources

| Source | Their Field | Maps To |
|--------|-------------|---------|
| Google Maps | `title` | `business_name` |
| Google Maps | `formatted_address` | `business_address` |
| Yelp | `name` | `business_name` |
| Yelp | `display_phone` | `business_phone` |
| Hunter.io | `value` | `business_email` |
| Hunter.io | `domain` | `business_website` |

Each scraper handles its own mapping. The output is always `BusinessLeadRecord`.
