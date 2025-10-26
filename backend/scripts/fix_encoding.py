"""
Fix encoding issues in JSON export files
This script fixes double-encoded UTF-8 characters
"""
import json
import sys

def fix_encoding(text):
    """Fix double-encoded UTF-8 text"""
    if text is None:
        return None
    if isinstance(text, str):
        # Fix common double-encoding patterns
        # These are the actual byte sequences that appear
        text = text.replace('\xc3\xa9', 'é')  # é
        text = text.replace('\xc3\xa8', 'è')  # è
        text = text.replace('\xc3\xaa', 'ê')  # ê
        text = text.replace('\xc3\xa0', 'à')  # à
        text = text.replace('\xc3\xa2', 'â')  # â
        text = text.replace('\xc3\xb4', 'ô')  # ô
        text = text.replace('\xc3\xae', 'î')  # î
        text = text.replace('\xc3\xb9', 'ù')  # ù
        text = text.replace('\xc3\xbb', 'û')  # û
        text = text.replace('\xc3\xa7', 'ç')  # ç
        text = text.replace('\xc3\x89', 'É')  # É
        text = text.replace('\xc3\x88', 'È')  # È
        text = text.replace('\xc3\x8a', 'Ê')  # Ê
        text = text.replace('\xc3\x80', 'À')  # À
        text = text.replace('\xc3\x82', 'Â')  # Â
        text = text.replace('\xc3\x94', 'Ô')  # Ô
        text = text.replace('\xc3\x8e', 'Î')  # Î
        text = text.replace('\xc3\x99', 'Ù')  # Ù
        text = text.replace('\xc3\x9b', 'Û')  # Û
        text = text.replace('\xc3\x87', 'Ç')  # Ç
        return text
    return text

def fix_recipe(recipe):
    """Fix encoding in a recipe dict"""
    fixed = {}
    for key, value in recipe.items():
        if isinstance(value, str):
            fixed[key] = fix_encoding(value)
        elif isinstance(value, list):
            fixed[key] = [fix_encoding(item) if isinstance(item, str) else item for item in value]
        else:
            fixed[key] = value
    return fixed

def main():
    if len(sys.argv) < 3:
        print("Usage: python fix_encoding.py input.json output.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print(f"📖 Reading {input_file}...")
    
    # Read with UTF-8-sig to handle BOM
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    print(f"🔧 Fixing encoding for {len(data)} recipes...")
    
    # Fix encoding for each recipe
    fixed_data = [fix_recipe(recipe) for recipe in data]
    
    # Write fixed JSON
    print(f"💾 Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Done!")
    
    # Show some examples
    print("\n📝 Sample fixes:")
    for i, (original, fixed) in enumerate(zip(data[:3], fixed_data[:3])):
        print(f"\n{i+1}. {original['title']} → {fixed['title']}")
        if original.get('description'):
            print(f"   {original['description'][:50]}... → {fixed['description'][:50]}...")

if __name__ == '__main__':
    main()
