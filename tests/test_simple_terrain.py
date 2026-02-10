import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from course_file import CourseFile

print("Creating course with simple terrain modification...")

# Load blank course
sample_file = Path(__file__).parent.parent / "reference" / "samples" / "vr1p6c0wqeyf.course"
course = CourseFile.load(sample_file)

# Let's try adding a simple terrain entry
# Based on the structure, terrain data might be stored as dictionaries or encoded strings
# Let's try a simple test structure

print("Original terrainHeight length:", len(course.course_data['terrainHeight']))

# Try adding a simple entry (we're guessing the structure here)
# This might not work, but it's a starting point
test_terrain = {
    "x": 0,
    "y": 0,
    "radius": 10.0,
    "height": 5.0
}

course.course_data['terrainHeight'].append(test_terrain)

print("Modified terrainHeight length:", len(course.course_data['terrainHeight']))

# Save it
course.set_name("TERRAIN TEST - Simple Bump")
output_file = Path(__file__).parent.parent / "output" / "terrain_test.course"
course.save(output_file)

print(f"Saved to: {output_file}")
print("\nCopy this to your game and see what happens!")
print("copy output\\terrain_test.course \"C:\\Users\\ztrob\\OneDrive\\Documents\\My Games\\PGA TOUR 2K25\\terraintest.course\"")