"""Add image_sources to all AdminWineResponse in list endpoints"""
import re

with open('app/api/admin_wines.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for list endpoints with lwin7 after bottle_image
pattern = r'(bottle_image=wine\.bottle_image,)\n(\s+)(lwin7=wine\.lwin7,)'
replacement = r'\1\n\2image_sources=wine.image_sources or {},\n\2\3'

content = re.sub(pattern, replacement, content)

with open('app/api/admin_wines.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed image_sources in list endpoints")
