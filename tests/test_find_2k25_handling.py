"""
Search the TGC Designer Tools code for 2K25-specific handling
"""
import os
from pathlib import Path

tgc_tools_path = Path(r"C:\Users\ztrob\Documents\dev\python\TGC-Designer-Tools")

print("Searching for version 25 or 2K25 handling...")
print("=" * 60)

# Search for version checks in tgc_tools.py
tools_file = tgc_tools_path / "tgc_tools.py"

if tools_file.exists():
    with open(tools_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("\nSearching tgc_tools.py for version checks...")
    for i, line in enumerate(lines, 1):
        if 'version' in line.lower() and ('25' in line or '2k25' in line.lower()):
            print(f"Line {i}: {line.strip()}")
        
        # Also look for where they decide to use userLayers vs top-level
        if 'terrainHeight' in line and ('version' in line.lower() or 'if' in line.lower()):
            print(f"Line {i}: {line.strip()}")

# Check tgc_definitions.py for version constants
defs_file = tgc_tools_path / "tgc_definitions.py"
if defs_file.exists():
    print("\n" + "=" * 60)
    print("Checking tgc_definitions.py for version tags...")
    print("=" * 60)
    with open(defs_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Find version_tags definition
        if 'version_tags' in content:
            start = content.find('version_tags')
            end = content.find('}', start) + 1
            print(content[start:end])