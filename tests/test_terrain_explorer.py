import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from course_file import CourseFile

print("=" * 60)
print("TERRAIN DATA EXPLORER")
print("=" * 60)

# Load your 2K25 course
print("\nLoading 2K25 course...")
sample_file = Path(__file__).parent.parent / "reference" / "samples" / "vr1p6c0wqeyf.course"
course = CourseFile.load(sample_file)

print(f"Course: {course.get_name()}")
print(f"Version: {course.version.value}")

# Look at terrain-related keys
print("\n" + "=" * 60)
print("TERRAIN-RELATED KEYS IN COURSE DATA")
print("=" * 60)

terrain_keys = ['terrainHeight', 'height', 'userLayers', 'userLayers2', 
                'surfaceBrushes2', 'surfaces2', 'secondarySurfaces',
                'legacyTerrain', 'useV46HeightFieldDiscretization']

for key in terrain_keys:
    if key in course.course_data:
        value = course.course_data[key]
        
        if isinstance(value, list):
            print(f"\n{key}: (list)")
            print(f"  Length: {len(value)}")
            if len(value) > 0:
                print(f"  First item type: {type(value[0])}")
                print(f"  First item: {value[0]}")
        elif isinstance(value, dict):
            print(f"\n{key}: (dict)")
            print(f"  Keys: {list(value.keys())}")
        else:
            print(f"\n{key}: {value}")

# Export full course data to JSON for inspection
print("\n" + "=" * 60)
print("EXPORTING FULL COURSE DATA")
print("=" * 60)

output_file = Path(__file__).parent.parent / "output" / "terrain_analysis.json"
course.export_json(output_file)
print(f"✓ Exported to: {output_file}")

# Look specifically at terrainHeight structure
print("\n" + "=" * 60)
print("DETAILED terrainHeight ANALYSIS")
print("=" * 60)

if 'terrainHeight' in course.course_data:
    terrain_height = course.course_data['terrainHeight']
    print(f"Type: {type(terrain_height)}")
    print(f"Length: {len(terrain_height)}")
    
    if len(terrain_height) > 0:
        print(f"\nFirst element:")
        print(f"  Type: {type(terrain_height[0])}")
        print(f"  Value: {terrain_height[0]}")
        
        if isinstance(terrain_height[0], dict):
            print(f"  Keys: {list(terrain_height[0].keys())}")
        elif isinstance(terrain_height[0], str):
            print(f"  String length: {len(terrain_height[0])}")
            print(f"  First 100 chars: {terrain_height[0][:100]}")

# Look at height structure
print("\n" + "=" * 60)
print("DETAILED height ANALYSIS")
print("=" * 60)

if 'height' in course.course_data:
    height = course.course_data['height']
    print(f"Type: {type(height)}")
    print(f"Length: {len(height)}")
    
    if len(height) > 0:
        print(f"\nFirst element:")
        print(f"  Type: {type(height[0])}")
        print(f"  Value: {height[0]}")
        
        if isinstance(height[0], dict):
            print(f"  Keys: {list(height[0].keys())}")
        elif isinstance(height[0], str):
            print(f"  String length: {len(height[0])}")
            print(f"  First 100 chars: {height[0][:100]}")

print("\n" + "=" * 60)
print("✓ Analysis complete!")
print("=" * 60)