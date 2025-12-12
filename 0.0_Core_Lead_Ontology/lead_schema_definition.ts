/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * FUNNELFUNCTION LEAD ONTOLOGY - THE CANONICAL DEFINITION
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * VERSION: 1.0.0
 * AUTHOR: FunnelFunction (Armstrong Knight & Abdullah Khan)
 * PURPOSE: Defines what a "Lead" IS across all FunnelFunction systems
 * 
 * This file is the SINGLE SOURCE OF TRUTH for lead data structure.
 * All scrapers, APIs, and transformers must output data conforming to this schema.
 * 
 * SELF-CONTAINED: This file has no dependencies. Copy and use anywhere.
 * ═══════════════════════════════════════════════════════════════════════════════
 */

// ═══════════════════════════════════════════════════════════════════════════════
// CORE LEAD INTERFACE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * BusinessLeadRecord: The atomic unit of the FunnelFunction system.
 * 
 * This is what flows through the entire pipeline:
 * Scraper → Verification → Email Sender → Analytics
 * 
 * REQUIRED FIELDS for email sending:
 * - business_name: Used in {{business_name}} template replacements
 * - business_email OR business_website: Need at least one to find/send email
 */
export interface BusinessLeadRecord {
  // ─────────────────────────────────────────────────────────────────────────────
  // IDENTITY (Position 1) - Required for email personalization
  // ─────────────────────────────────────────────────────────────────────────────
  business_name: string;           // "Bob's Plumbing LLC" - for {{business_name}}
  
  // ─────────────────────────────────────────────────────────────────────────────
  // LOCATION (Positions 2-5) - For geo-targeting and address personalization
  // ─────────────────────────────────────────────────────────────────────────────
  business_address?: string;       // "123 Main Street, Suite 400"
  business_city?: string;          // "Denver"
  business_state?: string;         // "CO" or "Colorado"
  business_zip?: string;           // "80202" or "80202-1234"
  business_country?: string;       // "US" or "United States"
  
  // ─────────────────────────────────────────────────────────────────────────────
  // CONTACT (Positions 6-8) - Critical for outreach
  // ─────────────────────────────────────────────────────────────────────────────
  business_phone?: string;         // "+1-303-555-1234" or "(303) 555-1234"
  business_website?: string;       // "https://bobsplumbing.com" - for email discovery
  business_email?: string;         // "contact@bobsplumbing.com" - primary target
  
  // ─────────────────────────────────────────────────────────────────────────────
  // CLASSIFICATION (Positions 9-10) - For filtering and segmentation
  // ─────────────────────────────────────────────────────────────────────────────
  business_category?: string;      // "Plumber", "HVAC", "Restaurant"
  business_subcategory?: string;   // "Commercial Plumbing", "Fine Dining"
  
  // ─────────────────────────────────────────────────────────────────────────────
  // SOCIAL PROOF (Positions 11-12) - For prioritization
  // ─────────────────────────────────────────────────────────────────────────────
  rating?: string;                 // "4.5" (keep as string for flexibility)
  review_count?: string;           // "127" (keep as string for flexibility)
  
  // ─────────────────────────────────────────────────────────────────────────────
  // CONTACT PERSON (Positions 13-14) - If individual contact known
  // ─────────────────────────────────────────────────────────────────────────────
  contact_name?: string;           // "Bob Smith"
  contact_title?: string;          // "Owner", "Marketing Director"
  contact_email?: string;          // Personal email if different from business
  
  // ─────────────────────────────────────────────────────────────────────────────
  // METADATA (System-managed, not from scrapers)
  // ─────────────────────────────────────────────────────────────────────────────
  source_engine?: string;          // "google_maps", "yelp", "hunterio"
  scraped_at?: string;             // ISO timestamp
  confidence_score?: number;       // 0-100 confidence in data accuracy
}

// ═══════════════════════════════════════════════════════════════════════════════
// FIELD VALIDATORS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Validation patterns for lead fields.
 * Use these to validate/clean data before inserting into the system.
 */
export const LeadFieldValidators = {
  
  // Email pattern - standard RFC 5322 simplified
  EMAIL: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  
  // Phone patterns (US)
  PHONE_US: /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/,
  
  // ZIP code (US)
  ZIP_US: /^\d{5}(-\d{4})?$/,
  
  // Website URL
  WEBSITE: /^(https?:\/\/)?(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(\/.*)?$/,
  
  // US State abbreviation
  STATE_ABBREV: /^[A-Z]{2}$/,
  
  // Rating (1-5 with decimals)
  RATING: /^[1-5](\.[0-9])?$/,
  
} as const;

// ═══════════════════════════════════════════════════════════════════════════════
// EMAIL EXCLUSION PATTERNS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Emails matching these patterns should be filtered out.
 * These are typically placeholder, example, or invalid addresses.
 */
export const EmailExclusionPatterns = [
  /example\.com$/i,
  /domain\.com$/i,
  /test\.com$/i,
  /placeholder\.com$/i,
  /wixpress\.com$/i,           // Wix placeholder
  /squarespace\.com$/i,        // Squarespace placeholder
  /sentry\.io$/i,              // Error tracking
  /cloudflare\.com$/i,         // CDN
  /noreply@/i,                 // No-reply addresses
  /donotreply@/i,
  /^admin@/i,                  // Generic admin
  /^info@/i,                   // Often unmonitored
  /^support@/i,                // Support queues
  /^webmaster@/i,
] as const;

// ═══════════════════════════════════════════════════════════════════════════════
// FILE EXTENSION EXCLUSIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * When regex-extracting emails from HTML, exclude these file extensions.
 * These are commonly false positives like "image@2x.png".
 */
export const FileExtensionExclusions = [
  'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'ico',  // Images
  'pdf', 'doc', 'docx', 'xls', 'xlsx',                 // Documents
  'js', 'css', 'html', 'htm', 'xml', 'json',           // Code
  'mp3', 'mp4', 'wav', 'avi', 'mov',                   // Media
  'zip', 'rar', 'tar', 'gz',                           // Archives
] as const;

// ═══════════════════════════════════════════════════════════════════════════════
// US STATE MAPPINGS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Two-way mapping between US state abbreviations and full names.
 * Scrapers should normalize to abbreviations (e.g., "CO" not "Colorado").
 */
export const USStateMap: Record<string, string> = {
  'AL': 'Alabama',
  'AK': 'Alaska',
  'AZ': 'Arizona',
  'AR': 'Arkansas',
  'CA': 'California',
  'CO': 'Colorado',
  'CT': 'Connecticut',
  'DE': 'Delaware',
  'FL': 'Florida',
  'GA': 'Georgia',
  'HI': 'Hawaii',
  'ID': 'Idaho',
  'IL': 'Illinois',
  'IN': 'Indiana',
  'IA': 'Iowa',
  'KS': 'Kansas',
  'KY': 'Kentucky',
  'LA': 'Louisiana',
  'ME': 'Maine',
  'MD': 'Maryland',
  'MA': 'Massachusetts',
  'MI': 'Michigan',
  'MN': 'Minnesota',
  'MS': 'Mississippi',
  'MO': 'Missouri',
  'MT': 'Montana',
  'NE': 'Nebraska',
  'NV': 'Nevada',
  'NH': 'New Hampshire',
  'NJ': 'New Jersey',
  'NM': 'New Mexico',
  'NY': 'New York',
  'NC': 'North Carolina',
  'ND': 'North Dakota',
  'OH': 'Ohio',
  'OK': 'Oklahoma',
  'OR': 'Oregon',
  'PA': 'Pennsylvania',
  'RI': 'Rhode Island',
  'SC': 'South Carolina',
  'SD': 'South Dakota',
  'TN': 'Tennessee',
  'TX': 'Texas',
  'UT': 'Utah',
  'VT': 'Vermont',
  'VA': 'Virginia',
  'WA': 'Washington',
  'WV': 'West Virginia',
  'WI': 'Wisconsin',
  'WY': 'Wyoming',
  'DC': 'District of Columbia',
};

// Reverse mapping: "California" → "CA"
export const USStateReverseMap: Record<string, string> = Object.fromEntries(
  Object.entries(USStateMap).map(([abbrev, full]) => [full, abbrev])
);

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Validate an email address against our patterns.
 * Returns true if email is valid and not excluded.
 */
export function isValidLeadEmail(email: string): boolean {
  if (!email || typeof email !== 'string') return false;
  
  // Check basic format
  if (!LeadFieldValidators.EMAIL.test(email)) return false;
  
  // Check against exclusion patterns
  for (const pattern of EmailExclusionPatterns) {
    if (pattern.test(email)) return false;
  }
  
  // Check for file extension false positives
  const extension = email.split('.').pop()?.toLowerCase();
  if (extension && FileExtensionExclusions.includes(extension as any)) {
    return false;
  }
  
  // Check doesn't start with number (common false positive)
  if (/^[0-9]/.test(email)) return false;
  
  return true;
}

/**
 * Normalize a US state to its two-letter abbreviation.
 * "California" → "CA", "ca" → "CA", "CA" → "CA"
 */
export function normalizeUSState(state: string): string | null {
  if (!state || typeof state !== 'string') return null;
  
  const cleaned = state.trim();
  
  // Already an abbreviation?
  const upper = cleaned.toUpperCase();
  if (USStateMap[upper]) return upper;
  
  // Full name?
  const titleCase = cleaned.charAt(0).toUpperCase() + cleaned.slice(1).toLowerCase();
  if (USStateReverseMap[titleCase]) return USStateReverseMap[titleCase];
  
  // Try matching full name case-insensitively
  for (const [abbrev, fullName] of Object.entries(USStateMap)) {
    if (fullName.toLowerCase() === cleaned.toLowerCase()) {
      return abbrev;
    }
  }
  
  return null;
}

/**
 * Extract domain from a URL.
 * "https://www.bobsplumbing.com/contact" → "bobsplumbing.com"
 */
export function extractDomain(url: string): string | null {
  if (!url || typeof url !== 'string') return null;
  
  try {
    // Add protocol if missing
    let fullUrl = url;
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      fullUrl = 'https://' + url;
    }
    
    const parsed = new URL(fullUrl);
    let domain = parsed.hostname;
    
    // Remove www prefix
    if (domain.startsWith('www.')) {
      domain = domain.slice(4);
    }
    
    return domain;
  } catch {
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// TYPE GUARDS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Check if an object is a valid BusinessLeadRecord with required fields.
 */
export function isValidLead(obj: unknown): obj is BusinessLeadRecord {
  if (!obj || typeof obj !== 'object') return false;
  
  const lead = obj as BusinessLeadRecord;
  
  // Must have business_name
  if (!lead.business_name || typeof lead.business_name !== 'string') {
    return false;
  }
  
  // Must have either email or website (for outreach capability)
  const hasEmail = lead.business_email && typeof lead.business_email === 'string';
  const hasWebsite = lead.business_website && typeof lead.business_website === 'string';
  
  if (!hasEmail && !hasWebsite) {
    return false;
  }
  
  return true;
}

/**
 * Check if a lead is ready for email sending.
 * Stricter than isValidLead—requires validated email.
 */
export function isEmailReady(lead: BusinessLeadRecord): boolean {
  if (!isValidLead(lead)) return false;
  if (!lead.business_email) return false;
  return isValidLeadEmail(lead.business_email);
}
