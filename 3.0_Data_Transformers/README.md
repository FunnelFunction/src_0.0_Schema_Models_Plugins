# 3.0 Data Transformers

> **"Raw data in, clean leads out."**

Utilities for converting various data formats into the `BusinessLeadRecord` schema.

## Available Transformers

| File | Purpose | Status |
|------|---------|--------|
| `csv_to_lead_transformer.ts` | Convert CSV rows to leads | 📋 Planned |
| `json_to_lead_transformer.ts` | Convert JSON objects to leads | 📋 Planned |
| `normalize_address.ts` | Standardize US addresses | 📋 Planned |

## Usage

Each transformer is self-contained. Import and use directly:

```typescript
import { csvToLead } from './csv_to_lead_transformer';

const lead = csvToLead(csvRow);
```

