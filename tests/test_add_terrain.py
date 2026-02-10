import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.course_file import CourseFile
from config import copy_to_game

print("=" * 60)
print("ADDING SIMPLE TERRAIN DATA")
print("=" * 60)

# Load blank course
sample_file = Path(__file__).parent.parent / "reference" / "samples" / "vr1p6c0wqeyf.course"
course = CourseFile.load(sample_file)

print(f"Original terrain points: {len(course.course_data['terrainHeight'])}")

# Add a simple 5x5 grid of elevated terrain in the center
print("\nAdding 5x5 grid of elevated points...")

for x in range(-2, 3):  # -2, -1, 0, 1, 2
    for z in range(-2, 3):
        terrain_point = {
            "position": [x * 10.0, z * 10.0],  # Space them 10 meters apart
            "value": 5.0  # Raise by 5 meters
        }
        course.course_data['terrainHeight'].append(terrain_point)
        course.course_data['height'].append(terrain_point)

print(f"New terrain points: {len(course.course_data['terrainHeight'])}")
print(f"Added {5*5} = 25 points")

# Save it
course.set_name("TERRAIN TEST - 5x5 Grid")
output_file = Path(__file__).parent.parent / "output" / "terrain_test_grid.course"
course.save(output_file)

print(f"\n✓ Saved to: {output_file}")

# Automatically copy to game!
print("\n" + "=" * 60)
print("COPYING TO GAME")
print("=" * 60)
copy_to_game(output_file, game_version='2K25', custom_name='terraintest')

print("\n✅ Done! Open PGA 2K25 and look for 'TERRAIN TEST - 5x5 Grid'")