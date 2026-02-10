"""
Research terrain data format by examining what we know:
1. terrainHeight is an empty list in blank courses
2. When LiDAR is imported, it populates this list
3. We need to figure out what format the data uses

Let's check the decoded JSON files for any clues about terrain structure
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

print("=" * 60)
print("RESEARCHING TERRAIN DATA FORMAT")
print("=" * 60)

# Load the decoded 2K25 JSON to see all fields
decoded_file = Path(__file__).parent.parent / "reference" / "decoded" / "2k25_full_decoded.json"

with open(decoded_file, 'r') as f:
    data = json.load(f)

# Look for any fields that might give us clues about terrain format
print("\nSearching for terrain-related documentation in the data...")

# Check if there are any sample terrain entries in other fields
print("\n--- Checking 'holes3' structure (might have terrain info) ---")
if 'holes3' in data and len(data['holes3']) > 0:
    print(f"Number of holes: {len(data['holes3'])}")
    print(f"First hole keys: {list(data['holes3'][0].keys())}")
else:
    print("No holes data")

# Check surfaces2 - this might tell us about texture/material painting
print("\n--- Checking 'surfaces2' structure ---")
if 'surfaces2' in data:
    print(f"Number of surface definitions: {len(data['surfaces2'])}")
    if len(data['surfaces2']) > 0:
        print(f"First surface: {json.dumps(data['surfaces2'][0], indent=2)}")

# Check surfaceBrushes2 - this is how you paint surfaces
print("\n--- Checking 'surfaceBrushes2' structure ---")
if 'surfaceBrushes2' in data:
    print(f"Number of brush strokes: {len(data['surfaceBrushes2'])}")
    print("(Empty in blank course, but this is where painted surfaces go)")

# Look for any example data structures
print("\n--- Looking for data structure hints ---")
interesting_keys = ['userLayers', 'userLayers2', 'AllMapEdits']
for key in interesting_keys:
    if key in data:
        value = data[key]
        print(f"\n{key}:")
        if isinstance(value, dict):
            print(f"  Type: dict")
            print(f"  Keys: {list(value.keys())}")
        else:
            print(f"  Type: {type(value)}")

print("\n" + "=" * 60)
print("NEXT STEP: Check TGC Designer Tools source code")
print("=" * 60)
print("\nThe Python files in the original repo should show us:")
print("1. How they write to terrainHeight")
print("2. What format the heightmap data uses")
print("3. How coordinates are mapped")
print("\nLet's look at the TGC Designer Tools GitHub repo...")