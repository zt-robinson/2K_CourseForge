import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.course_file import CourseFile

# Compare our modified course to the original
original = Path(__file__).parent.parent / "reference" / "samples" / "vr1p6c0wqeyf.course"
modified = Path(__file__).parent.parent / "output" / "terrain_test_grid.course"

print("Comparing original vs modified course...")
print("=" * 60)

course_orig = CourseFile.load(original)
course_mod = CourseFile.load(modified)

# Check structure differences
print("\nOriginal terrainHeight:", course_orig.course_data.get('terrainHeight'))
print("\nModified terrainHeight (first 3):")
if len(course_mod.course_data['terrainHeight']) > 0:
    for i in range(min(3, len(course_mod.course_data['terrainHeight']))):
        print(f"  {i}: {course_mod.course_data['terrainHeight'][i]}")

print("\n" + "=" * 60)
print("Let's check what keys changed between files:")
print("=" * 60)

# Export both for comparison
course_orig.export_json(Path(__file__).parent.parent / "output" / "original_structure.json")
course_mod.export_json(Path(__file__).parent.parent / "output" / "modified_structure.json")

print("✓ Exported both to output folder")
print("\nNext: Look at the TGC Designer Tools code to see")
print("how they handle 2K25 specifically...")