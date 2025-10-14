"""
Analyze Open Food Facts Taxonomy Structure

This script analyzes the downloaded taxonomy JSON files to understand:
- Data structure and format
- Available languages
- Hierarchical relationships
- Sample entries
"""

import json
from pathlib import Path
from collections import Counter
from typing import Dict, Any


def analyze_taxonomy(taxonomy_path: Path):
    """Analyze a single taxonomy file"""
    print(f"\n{'='*70}")
    print(f"📊 Analyzing: {taxonomy_path.name}")
    print(f"{'='*70}")
    
    # Load taxonomy
    with open(taxonomy_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n📈 Total entries: {len(data):,}")
    
    # Sample entry
    if data:
        sample_key = list(data.keys())[0]
        sample_entry = data[sample_key]
        
        print(f"\n🔍 Sample Entry: {sample_key}")
        print(f"   Structure:")
        for key, value in list(sample_entry.items())[:10]:  # First 10 fields
            value_preview = str(value)[:100]
            print(f"   • {key}: {value_preview}")
        
        # Check for translations
        if 'name' in sample_entry and isinstance(sample_entry['name'], dict):
            languages = list(sample_entry['name'].keys())
            print(f"\n🌍 Available languages: {len(languages)}")
            print(f"   Sample languages: {', '.join(languages[:10])}")
            
            # Show bilingual example
            if 'fr' in sample_entry['name'] and 'en' in sample_entry['name']:
                print(f"\n💬 Bilingual Example:")
                print(f"   EN: {sample_entry['name']['en']}")
                print(f"   FR: {sample_entry['name']['fr']}")
        
        # Check for hierarchy
        if 'parents' in sample_entry or 'children' in sample_entry:
            print(f"\n🌳 Hierarchical:")
            if 'parents' in sample_entry:
                parents = sample_entry.get('parents', [])
                print(f"   Parents: {parents}")
            if 'children' in sample_entry:
                children = sample_entry.get('children', [])
                print(f"   Children: {len(children)} entries")
    
    # Count entries with images (if image field exists)
    entries_with_images = sum(
        1 for entry in data.values()
        if isinstance(entry, dict) and 'image' in entry
    )
    if entries_with_images > 0:
        print(f"\n🖼️ Entries with images: {entries_with_images} ({entries_with_images/len(data)*100:.1f}%)")
    
    # Find common fields
    all_fields = Counter()
    for entry in data.values():
        if isinstance(entry, dict):
            all_fields.update(entry.keys())
    
    print(f"\n📋 Common fields:")
    for field, count in all_fields.most_common(15):
        percentage = count / len(data) * 100
        print(f"   • {field}: {count:,} ({percentage:.1f}%)")


def main():
    """Analyze all taxonomies"""
    script_dir = Path(__file__).parent
    taxonomy_dir = script_dir.parent.parent / "data" / "taxonomies"
    
    print("="*70)
    print("🔬 Open Food Facts Taxonomy Structure Analysis")
    print("="*70)
    
    if not taxonomy_dir.exists():
        print(f"\n❌ Error: Taxonomy directory not found: {taxonomy_dir}")
        return 1
    
    # Priority taxonomies
    priority = ['ingredients', 'categories']
    
    for taxonomy_name in priority:
        taxonomy_file = taxonomy_dir / f"{taxonomy_name}.json"
        if taxonomy_file.exists():
            analyze_taxonomy(taxonomy_file)
    
    print(f"\n{'='*70}")
    print("✅ Analysis complete!")
    print(f"{'='*70}\n")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
