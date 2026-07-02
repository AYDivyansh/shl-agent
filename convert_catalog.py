import json
from collections import Counter

# Map the catalog 'keys' to our test types.
# We exclude "Development & 360" because the assignment says "Individual Test Solutions only".
KEY_TO_TYPE = {
    "Ability & Aptitude": "A",
    "Assessment Exercises": "K",
    "Biodata & Situational Judgment": "S",
    "Competencies": "P",
    "Personality & Behavior": "P",
    "Development & 360": None  # Exclude this category
}

def get_test_type(keys_list):
    """Determine test_type from the list of keys."""
    for k in keys_list:
        if k in KEY_TO_TYPE and KEY_TO_TYPE[k] is not None:
            return KEY_TO_TYPE[k]
    return "O"

def is_individual_test(item):
    """Filter out Development & 360 and Job Solutions."""
    keys = item.get('keys', [])
    name = item.get('name', '').lower()
    
    # If the ONLY key is Development & 360, exclude it
    if keys == ["Development & 360"]:
        return False
        
    # Exclude obvious job solutions or reports
    if "job solution" in name or "pre-packaged" in name:
        return False
        
    # If it has at least one valid Individual Test key, keep it
    valid_keys = [k for k in keys if k in KEY_TO_TYPE and KEY_TO_TYPE[k] is not None]
    if not valid_keys:
        return False
        
    return True

def convert():
    print("Reading catalog_raw.json...")
    with open('catalog_raw.json', 'r', encoding='utf-8') as f:
        raw = json.load(f)
    
    print(f"Total raw items: {len(raw)}")
    
    catalog = []
    skipped = 0
    for item in raw:
        if not isinstance(item, dict):
            skipped += 1
            continue
            
        if not is_individual_test(item):
            skipped += 1
            continue
            
        name = item.get('name', '').strip()
        url = item.get('link', '').strip()
        desc = item.get('description', '').strip()
        job_levels = item.get('job_levels', [])
        keys = item.get('keys', [])
        
        if not name or not url:
            skipped += 1
            continue
            
        test_type = get_test_type(keys)
        
        # Build tags from job levels and keys (great for retrieval!)
        tags = [t.lower().replace(' ', '-') for t in job_levels if t]
        tags.extend([k.lower() for k in keys if k])
        
        catalog.append({
            "name": name,
            "url": url,
            "test_type": test_type,
            "description": desc[:500],
            "tags": list(set(tags))
        })
        
    # Deduplicate by URL so we don't have the same test twice
    seen = set()
    final = []
    for p in catalog:
        if p['url'] not in seen:
            seen.add(p['url'])
            final.append(p)
            
    # Save the final catalog
    with open('catalog.json', 'w', encoding='utf-8') as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ Saved {len(final)} products to catalog.json ({skipped} skipped)")
    
    # Show a summary
    counts = Counter(p['test_type'] for p in final)
    print("\n📊 Test type breakdown:")
    for t, c in sorted(counts.items()):
        print(f"  {t}: {c}")
        
    print("\n🔍 First 3 items (check these to make sure they look right!):")
    for p in final[:3]:
        print(f"  - {p['name']} (Type: {p['test_type']})")
        print(f"    URL: {p['url']}")

if __name__ == "__main__":
    convert()