"""
Download Open Food Facts Taxonomies

This script downloads the latest OFF taxonomies in JSON format.
These are much smaller than the full MongoDB dump and contain the
structured ingredient/category data we need.

Taxonomies: ingredients, categories, allergens, labels, etc.
"""

import requests
import json
from pathlib import Path
from typing import List
import sys

# Taxonomy URLs
BASE_URL = "https://static.openfoodfacts.org/data/taxonomies"

TAXONOMIES = [
    "ingredients",
    "categories", 
    "allergens",
    "labels",
    "nutrients",
    "additives",
    "origins",
    "packaging_shapes",
    "packaging_materials",
]


def download_taxonomy(name: str, output_dir: Path) -> bool:
    """Download a single taxonomy file"""
    url = f"{BASE_URL}/{name}.json"
    output_file = output_dir / f"{name}.json"
    
    print(f"\n📥 Downloading {name}...")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse to validate JSON
        data = response.json()
        
        # Save
        output_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        
        # Stats
        num_entries = len(data)
        size_mb = len(response.content) / 1024 / 1024
        
        print(f"   ✅ Saved: {output_file.name}")
        print(f"   📊 Entries: {num_entries:,}")
        print(f"   💾 Size: {size_mb:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Download all taxonomies"""
    # Setup output directory
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent.parent / "data" / "taxonomies"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*70)
    print("📦 Open Food Facts Taxonomy Downloader")
    print("="*70)
    print(f"\n📁 Output directory: {data_dir}")
    
    # Download each taxonomy
    success_count = 0
    failed = []
    
    for taxonomy_name in TAXONOMIES:
        if download_taxonomy(taxonomy_name, data_dir):
            success_count += 1
        else:
            failed.append(taxonomy_name)
    
    # Summary
    print("\n" + "="*70)
    print("📊 Download Summary")
    print("="*70)
    print(f"\n✅ Successfully downloaded: {success_count}/{len(TAXONOMIES)}")
    
    if failed:
        print(f"\n❌ Failed to download:")
        for name in failed:
            print(f"   • {name}")
    
    print(f"\n📁 Files saved to: {data_dir}")
    print("\n" + "="*70)
    
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
