# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════════
SCHEMA: Google Maps Business Scraper with Email Discovery
═══════════════════════════════════════════════════════════════════════════════════
VERSION: 1.0.0
AUTHOR: FunnelFunction (Armstrong Knight & Abdullah Khan)
LICENSE: MIT
ORIGINAL: https://colab.research.google.com/drive/1-EjSA62m5QuD8-t32OLa65F0m7oC7tMP

DEPENDENCIES:
  pip install gspread google-auth pandas requests beautifulsoup4 lxml 
  pip install openpyxl fake-useragent tldextract playwright nest-asyncio
  playwright install chromium

OUTPUT: BusinessLeadRecord[]
  - business_name (Title)
  - business_address (Address)
  - business_city (City)
  - business_state (State)
  - business_phone (Phone)
  - business_website (Website)
  - business_email (Email - scraped from website)
  - business_category (Category)
  - rating (Rating)
  - review_count (Total Reviews)

DESCRIPTION:
  This scraper navigates Google Maps, searches for businesses by keyword + location,
  scrolls through all results, extracts business details, then visits each website
  to discover email addresses via contact page crawling and mailto: link extraction.

ANTI-BOT MEASURES HANDLED:
  - Rotating User-Agent via fake_useragent
  - ScraperAPI fallback for blocked requests
  - Human-like typing delays
  - Consent dialog handling ("Accept all")
  - Rate limiting via semaphores

SELF-CONTAINED: Yes - Copy this file anywhere and it runs independently.
═══════════════════════════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════════════

# !pip install gspread google-auth pandas requests beautifulsoup4 lxml openpyxl fake-useragent tldextract playwright nest-asyncio
# !playwright install chromium

import re
import time
import random
import asyncio
import warnings
import requests
import traceback
import tldextract
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
from playwright.async_api import async_playwright

warnings.simplefilter(action='ignore', category=FutureWarning)

# ═══════════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════════

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# ScraperAPI fallback key (replace with your own or remove if not needed)
SCRAPERAPI_KEY = "69ceba7bcab653d66d03843b47bada72"

# Google Sheets document ID (replace with your own)
GOOGLE_SHEET_ID = "1eZOOd90NPJdC9_CrI_KQJTkyk4PuB0AFJbMo7GZQYUU"

# DOM Selectors for Google Maps
SELECTORS = {
    'search_input': '#searchboxinput',
    'result_cards': '.hfpxzc',
    'title_xpath': '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]/h1',
    'category_xpath': '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/span[1]/span/button',
    'rating_xpath': '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]',
    'reviews_xpath': '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[2]/span/span',
    'website_link': 'a.CsEnBe',
}

# US State Abbreviation Map
US_STATES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming'
}

# Email domains to exclude (placeholders, platforms, etc.)
EMAIL_EXCLUSIONS = ['example.com', 'domain.com', 'wixpress.com', 'squarespace.com']

# File extensions that are NOT emails (false positive prevention)
FILE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'pdf', 'js', 'html', 'css', 'svg', 'webp', 'gif']

# ═══════════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS - DOMAIN & URL
# ═══════════════════════════════════════════════════════════════════════════════════

def extract_domain(url):
    """Extract clean domain from URL, removing www prefix."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def clean_url(url):
    """Extract just domain.tld from a URL using tldextract."""
    try:
        extracted = tldextract.extract(url)
        if not extracted.domain or not extracted.suffix:
            return None
        return f"{extracted.domain}.{extracted.suffix}"
    except Exception:
        return None


def validate_domain(domain):
    """Try different URL formats until one works, return valid URL or None."""
    if not domain or ".." in domain:
        return None

    prefixes = ["https://", "http://"]
    subdomains = ["www.", ""]

    for prefix in prefixes:
        for subdomain in subdomains:
            url = f"{prefix}{subdomain}{domain}"
            try:
                ua = UserAgent()
                headers = {'User-Agent': ua.random}
                response = requests.get(url=url, headers=headers, timeout=20)
                
                # If blocked, try ScraperAPI
                if '4' in str(response.status_code):
                    url_ = f'http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}'
                    response = requests.get(url_, timeout=20)

                if response.status_code == 200:
                    return url
            except requests.RequestException:
                pass
    return None

# ═══════════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS - EMAIL EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════════

def is_valid_email(email):
    """Check if email passes our validation rules."""
    if not email or not re.match(EMAIL_REGEX, email):
        return False
    
    # Reject if starts with digit
    if email[0].isdigit():
        return False
    
    # Reject excluded domains
    for exclusion in EMAIL_EXCLUSIONS:
        if exclusion in email.lower():
            return False
    
    # Reject file extensions masquerading as emails
    extension = email.split('.')[-1].lower()
    if extension in FILE_EXTENSIONS:
        return False
    
    return True


def extract_emails(text):
    """Extract all valid emails from HTML text."""
    emails = set()
    soup = BeautifulSoup(text, 'lxml')

    # Extract from mailto: links
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith("mailto:"):
            email = href[7:]
            email = email.split('?')[0].split('#')[0]
            email = unquote(email).strip()
            if is_valid_email(email):
                emails.add(email)

    # Extract via regex from full text
    regex_emails = re.findall(EMAIL_REGEX, text)
    for email in regex_emails:
        email = unquote(email).strip()
        if is_valid_email(email):
            emails.add(email)

    return emails


def crawl_contact_page(url):
    """Fetch a single contact page and extract emails."""
    emails = set()
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        ua = UserAgent()
        headers = {"User-Agent": ua.random}
        response = requests.get(url, headers=headers, timeout=20)

        # Fallback to ScraperAPI if blocked
        if response.status_code not in [200, '200']:
            response = requests.get(
                f"https://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}",
                timeout=20
            )
        
        emails.update(extract_emails(response.text))
    except (requests.RequestException, ValueError):
        pass
    return emails


def crawl_footer_links(domain, url):
    """Crawl a website's footer and contact pages for emails."""
    emails = set()
    
    try:
        ua = UserAgent()
        headers = {"User-Agent": ua.random}
        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code not in [200, '200']:
            response = requests.get(
                f"https://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}",
                timeout=20
            )

    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching {url}: {e}")
        return list(emails)

    soup = BeautifulSoup(response.text, "lxml")
    emails.update(extract_emails(response.text))

    # Crawl footer links
    footer = soup.find("footer")
    if footer:
        for link in footer.find_all("a", href=True):
            if domain not in link['href']:
                next_url = urljoin(url, link["href"])
            else:
                next_url = link["href"]
            
            if next_url.startswith(url) and next_url != url:
                try:
                    linked_response = requests.get(next_url, timeout=20)
                    linked_response.raise_for_status()
                    emails.update(extract_emails(linked_response.text))
                except (requests.RequestException, ValueError):
                    pass

    # Find and crawl contact pages
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "contact" in href.lower():
            if domain not in href:
                contact_url = urljoin(url, href)
            else:
                contact_url = href
            emails.update(crawl_contact_page(contact_url))

    return list(emails)


def process_website(website):
    """Process a website URL to extract emails."""
    if pd.notna(website) and 'google' not in website and 'facebook' not in website:
        start_url = website.strip()
        domain = extract_domain(start_url)

        if not start_url.startswith(("http://", "https://")):
            start_url = "https://" + domain

        try:
            emails = crawl_footer_links(domain, start_url)
            return '\n'.join(emails)
        except Exception as e:
            print(f"Error processing {start_url}: {e}")
            return None
    return None

# ═══════════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS - GOOGLE MAPS PARSING
# ═══════════════════════════════════════════════════════════════════════════════════

def aria_label(buttons):
    """Extract aria-label text from button elements, filtering out irrelevant ones."""
    for button in buttons:
        if 'aria-label' in button.attrs:
            text = button['aria-label']
            if 'Send to phone' not in text and 'Copy website' not in text:
                return text
    return ""

# ═══════════════════════════════════════════════════════════════════════════════════
# GOOGLE SHEETS INTEGRATION (Optional - Replace with your own storage)
# ═══════════════════════════════════════════════════════════════════════════════════

def setup_google_sheets():
    """Authenticate with Google Sheets. For Colab use."""
    try:
        from google.colab import auth
        auth.authenticate_user()
        
        import gspread
        from google.auth import default
        
        creds, _ = default()
        client = gspread.authorize(creds)
        return client
    except ImportError:
        print("Not running in Colab - Google Sheets disabled")
        return None


def google_sheets_get_record(client, sheet_name='States and Cities'):
    """Read records from a Google Sheet."""
    if not client:
        return pd.DataFrame()
    sh = client.open_by_key(GOOGLE_SHEET_ID)
    worksheet = sh.worksheet(sheet_name)
    return pd.DataFrame(worksheet.get_all_records())


def write_in_row(client, batch_data):
    """Write batch data to the scrapedResults sheet."""
    if not client:
        print("Google Sheets not configured - data not saved")
        return
    
    sh = client.open_by_key(GOOGLE_SHEET_ID)
    worksheet = sh.worksheet('scrapedResults')

    last_row = len(worksheet.get_all_values())
    row_start = last_row + 1

    num_rows = len(batch_data)
    cell_range = f'A{row_start}:M{row_start + num_rows - 1}'

    worksheet.update(range_name=cell_range, values=batch_data)
    print('Written to Google Sheets')


def write_in_cell(client, row, value):
    """Update a single cell in States and Cities sheet."""
    if not client:
        return
    sh = client.open_by_key(GOOGLE_SHEET_ID)
    worksheet = sh.worksheet('States and Cities')
    worksheet.update_cell(row, 4, value)

# ═══════════════════════════════════════════════════════════════════════════════════
# MAIN SCRAPER LOGIC
# ═══════════════════════════════════════════════════════════════════════════════════

async def run(playwright, state, city, country, keywords=None, client=None):
    """
    Main scraping function. Navigates Google Maps, extracts business data,
    and crawls websites for emails.
    
    Args:
        playwright: Playwright instance
        state: US state name or abbreviation
        city: City name
        country: Country (usually "USA")
        keywords: List of search keywords (default: ["Venture Capital Company"])
        client: Google Sheets client (optional)
    
    Returns:
        List of business records
    """
    if keywords is None:
        keywords = ["Venture Capital Company"]
    
    df = pd.DataFrame(columns=[
        'Keyword', 'Category', 'Title', 'State', 'City', 
        'Address', 'Website', 'Email', 'Phone', 'Rating', 
        'Total Reviews', 'Domain', 'Valid URL'
    ])
    
    data = []

    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    page.set_default_timeout(30000)

    for keyword in keywords:
        try:
            print(f'{keyword} - {city} - {state}', end=' - ')

            # Navigate to Google Maps
            await page.goto("https://www.google.com/maps?hl=en")
            await asyncio.sleep(2)

            # Handle consent dialog
            try:
                page.set_default_timeout(3000)
                await page.get_by_role("button", name="Accept all").click()
            except:
                pass

            page.set_default_timeout(15000)

            content = await page.content()
            if 'Search Google Maps' not in content:
                continue
            print('Browser launched', end=' - ')

            await asyncio.sleep(2)

            # Type search query with human-like delay
            await page.locator(SELECTORS['search_input']).type(
                f"{keyword} near {city} {state} {country}", 
                delay=200
            )
            await asyncio.sleep(3)
            await page.locator(SELECTORS['search_input']).press("Enter")
            await asyncio.sleep(3)
            print('Search made', end=' - ')

            # Scroll through results until end
            errors = 0
            while True:
                query = await page.query_selector_all(SELECTORS['result_cards'])

                if len(query) <= 1:
                    break

                try:
                    await query[-1].click()
                except Exception:
                    errors += 1
                    pass
                await asyncio.sleep(1)

                if errors > 5:
                    break

                soup = BeautifulSoup(await page.content(), 'lxml')
                if "end of the list" in soup.text:
                    break

            if errors > 5:
                continue
            
            query = await page.query_selector_all(SELECTORS['result_cards'])
            print(f'Results: {len(query)}')
            page.set_default_timeout(3000)

            # Process each result
            for i, q in enumerate(query):
                try:
                    await q.click()
                    await asyncio.sleep(1)
                    soup = BeautifulSoup(await page.content(), 'lxml')
                    
                    # Extract title
                    title = await page.locator(SELECTORS['title_xpath']).inner_text()

                    # Extract category
                    try:
                        category = await page.locator(SELECTORS['category_xpath']).inner_text()
                    except:
                        category = ''

                    # Extract rating
                    try:
                        rating = await page.locator(SELECTORS['rating_xpath']).inner_text()
                    except Exception:
                        rating = ""
                    
                    # Extract review count
                    try:
                        total_reviews = await page.locator(SELECTORS['reviews_xpath']).inner_text()
                        total_reviews = total_reviews.replace('(', '').replace(')', '')
                    except Exception:
                        total_reviews = ""

                    # Extract website
                    try:
                        website = await page.locator(SELECTORS['website_link']).first.get_attribute('href')
                    except Exception:
                        website = ""

                    # Extract address and phone from aria-labels
                    address_elements = soup.find_all('button', {'aria-label': re.compile('^Address:', re.IGNORECASE)})
                    phone_elements = soup.find_all('button', {'aria-label': re.compile('^Phone:*', re.IGNORECASE)})

                    address = aria_label(address_elements).replace('Address:', '').strip()
                    
                    # Parse city and state from address
                    try:
                        city_ = address.split(',')[-2].strip()
                        state_abbrev = address.split(',')[-1].split()[0].strip()
                        state_ = US_STATES.get(state_abbrev, state_abbrev)
                    except:
                        city_ = city
                        state_ = state

                    # Extract phone
                    try:
                        phone = aria_label(phone_elements).replace('Phone:', '').strip()
                    except Exception:
                        phone = ""

                    # Crawl website for email
                    email = process_website(website) if website else ''
                    if not email:
                        email = ''

                    # Add to dataframe
                    row = len(df)
                    df.at[row, 'Keyword'] = keyword
                    df.at[row, 'Category'] = category
                    df.at[row, 'Title'] = title
                    df.at[row, 'State'] = state_
                    df.at[row, 'City'] = city_
                    df.at[row, 'Address'] = address
                    df.at[row, 'Website'] = website
                    df.at[row, 'Email'] = email
                    df.at[row, 'Phone'] = phone
                    df.at[row, 'Rating'] = rating
                    df.at[row, 'Total Reviews'] = total_reviews
                    
                    print(f'{i+1}', end=', ')
                except Exception:
                    pass
        except:
            pass

    # Validate domains
    for r in range(len(df)):
        website = df.at[r, 'Website']
        domain = clean_url(website) if pd.notna(website) else None
        valid_url = validate_domain(domain) if domain else None
        
        df.at[r, 'Domain'] = domain if domain else ''
        df.at[r, 'Valid URL'] = valid_url if valid_url else ''
        data.append(df.iloc[r].tolist())

    print(f"\nTotal records: {len(data)}")
    
    if client:
        write_in_row(client, data)

    await context.close()
    await browser.close()
    
    return data

# ═══════════════════════════════════════════════════════════════════════════════════
# PARALLEL PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════════

async def process_record(sc, states_cities, semaphore, client=None):
    """Process a single city/state record with semaphore rate limiting."""
    if states_cities.at[sc, 'Status'] in ['Done']:
        return

    async with semaphore:
        try:
            state = states_cities.at[sc, 'State']
            city = states_cities.at[sc, 'City']
            country = states_cities.at[sc, 'Country']

            async with async_playwright() as playwright:
                await run(playwright, state, city, country, client=client)
            
            if client:
                write_in_cell(client, sc + 2, 'Done')
        except Exception as e:
            if client:
                write_in_cell(client, sc + 2, 'Error')
            print(f"Error processing {city}, {state}: {e}")


async def main():
    """Main entry point - process all cities from Google Sheets."""
    client = setup_google_sheets()
    states_cities = google_sheets_get_record(client)
    
    if states_cities.empty:
        print("No data found. Running demo mode...")
        async with async_playwright() as playwright:
            results = await run(
                playwright, 
                state="California",
                city="San Francisco",
                country="USA",
                keywords=["Venture Capital Company"]
            )
            print(f"Demo results: {results}")
        return
    
    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent browsers

    tasks = [
        asyncio.create_task(process_record(i, states_cities, semaphore, client))
        for i in range(len(states_cities))
    ]

    await asyncio.gather(*tasks)


# ═══════════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # For Jupyter/Colab, use nest_asyncio
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass
    
    asyncio.run(main())
