import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.course_file import CourseFile

print("=" * 80)
print("COMPARING FLAT vs TERRAIN COURSE - THE BREAKTHROUGH!")
print("=" * 80)

# Load both courses
flat_file = Path(__file__).parent.parent / "reference" / "samples" / "dh5s31bwqzbp.course"
terrain_file = Path(__file__).parent.parent / "reference" / "samples" / "5ehhve1aqsi6.course"

flat_course = CourseFile.load(flat_file)
terrain_course = CourseFile.load(terrain_file)

print(f"\nFlat course: {flat_course.get_name()}")
print(f"Terrain course: {terrain_course.get_name()}")

# Export both for detailed comparison
flat_course.export_json(Path(__file__).parent.parent / "output" / "flat_decoded.json")
terrain_course.export_json(Path(__file__).parent.parent / "output" / "terrain_decoded.json")
print("\n✓ Exported both to output folder")

# Compare key terrain fields
print("\n" + "=" * 80)
print("KEY TERRAIN FIELD COMPARISON")
print("=" * 80)

terrain_keys = ['terrainHeight', 'height', 'legacyTerrain', 'useV46HeightFieldDiscretization',
                'surfaceBrushes2', 'AllMapEdits']

for key in terrain_keys:
    flat_val = flat_course.course_data.get(key, "MISSING")
    terrain_val = terrain_course.course_data.get(key, "MISSING")
    
    if isinstance(flat_val, list) and isinstance(terrain_val, list):
        print(f"\n{key}:")
        print(f"  Flat:    {len(flat_val)} items")
        print(f"  Terrain: {len(terrain_val)} items")
        
        if len(terrain_val) > 0:
            print(f"  First terrain item: {terrain_val[0]}")
            if len(terrain_val) > 1:
                print(f"  Second terrain item: {terrain_val[1]}")
    elif flat_val != terrain_val:
        print(f"\n{key}:")
        print(f"  Flat:    {flat_val}")
        print(f"  Terrain: {terrain_val}")
    else:
        print(f"\n{key}: (same in both)")

# Find ALL differences
print("\n" + "=" * 80)
print("ALL FIELDS THAT DIFFER")
print("=" * 80)

all_keys = set(flat_course.course_data.keys()) | set(terrain_course.course_data.keys())

differences = []
for key in all_keys:
    flat_val = flat_course.course_data.get(key)
    terrain_val = terrain_course.course_data.get(key)
    
    if flat_val != terrain_val:
        differences.append(key)

print(f"\nFound {len(differences)} different fields:")
for key in sorted(differences):
    flat_val = flat_course.course_data.get(key)
    terrain_val = terrain_course.course_data.get(key)
    
    # Show type and basic info
    if isinstance(terrain_val, list):
        print(f"\n{key}: (list - {len(flat_course.course_data.get(key, []))} → {len(terrain_val)} items)")
    elif isinstance(terrain_val, dict):
        print(f"\n{key}: (dict)")
    else:
        print(f"\n{key}: {flat_val} → {terrain_val}")

print("\n" + "=" * 80)
print("🎯 NOW CHECK output/terrain_decoded.json FOR THE TERRAIN FORMAT!")
print("=" * 80)