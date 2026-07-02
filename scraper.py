"""
Scrapes the SHL Individual Test Solutions catalog.
Run: python scraper.py
Output: catalog.json

Requirements: pip install requests beautifulsoup4
"""
import requests
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: beautifulsoup4 is not installed. Run: pip install beautifulsoup4")
    exit(1)
import json
import re
import time

CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"

def scrape_shl_catalog():
    print(f"Fetching {CATALOG_URL} ...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    resp = requests.get(CATALOG_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    products = []

    # SHL's catalog typically lists products as cards/links.
    # We look for links that point to /solutions/products/<product-slug>/
    seen_urls = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/solutions/products/" in href and href not in seen_urls:
            # Skip the catalog page itself and pre-packaged job solutions
            if href.rstrip("/").endswith("product-catalog"):
                continue
            if "job-solutions" in href or "pre-packaged" in href:
                continue
            seen_urls.add(href)

            # Build absolute URL
            if href.startswith("/"):
                href = "https://www.shl.com" + href

            # Get the visible text as a provisional name
            name = a.get_text(strip=True) or href.split("/")[-2].replace("-", " ").title()

            products.append({
                "name": name,
                "url": href,
                "test_type": "",
                "description": "",
                "tags": []
            })

    print(f"Found {len(products)} product links. Now fetching details...")

    # For each product, fetch its page and extract description + test_type
    enriched = []
    for i, p in enumerate(products):
        try:
            print(f"  [{i+1}/{len(products)}] {p['name']}")
            r = requests.get(p["url"], headers=headers, timeout=20)
            if r.status_code != 200:
                continue
            psoup = BeautifulSoup(r.text, "html.parser")

            # Extract description: first <p> or <meta description>
            meta = psoup.find("meta", attrs={"name": "description"})
            desc = meta["content"] if meta and meta.get("content") else ""
            if not desc:
                first_p = psoup.find("p")
                desc = first_p.get_text(strip=True) if first_p else ""

            # Determine test_type from keywords
            text_lower = (p["name"] + " " + desc).lower()
            if any(k in text_lower for k in ["personality", "opq", "behavioral"]):
                test_type = "P"
            elif any(k in text_lower for k in ["cognitive", "ability", "reasoning", "verbal", "numerical", "logical", "gma", "gsa"]):
                test_type = "A"
            elif any(k in text_lower for k in ["java", "python", "sql", "coding", "skill", "knowledge"]):
                test_type = "K"
            elif any(k in text_lower for k in ["simulation", "situational", "sjt"]):
                test_type = "S"
            else:
                test_type = "O"

            # Generate tags from keywords
            tags = []
            tag_map = {
                "personality": ["personality", "behavioral"],
                "cognitive": ["cognitive", "reasoning"],
                "verbal": ["verbal", "reasoning"],
                "numerical": ["numerical", "reasoning"],
                "leadership": ["leadership"],
                "graduate": ["graduate", "entry-level"],
                "senior": ["senior", "leadership"],
                "developer": ["technical", "developer"],
                "manager": ["management", "leadership"],
                "sales": ["sales"],
                "customer": ["customer service"],
            }
            for kw, tlist in tag_map.items():
                if kw in text_lower:
                    tags.extend(tlist)
            tags = list(set(tags))

            enriched.append({
                "name": p["name"],
                "url": p["url"],
                "test_type": test_type,
                "description": desc[:500],
                "tags": tags
            })
            time.sleep(0.3)  # be polite
        except Exception as e:
            print(f"    ! skipped: {e}")

    # Deduplicate by URL
    seen = set()
    final = []
    for p in enriched:
        if p["url"] not in seen:
            seen.add(p["url"])
            final.append(p)

    with open("catalog.json", "w") as f:
        json.dump(final, f, indent=2)
    print(f"\n✅ Saved {len(final)} products to catalog.json")

if __name__ == "__main__":
    scrape_shl_catalog()