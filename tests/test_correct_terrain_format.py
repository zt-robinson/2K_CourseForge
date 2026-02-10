import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.course_file import CourseFile
from config import copy_to_game

print("=" * 60)
print("USING THE CORRECT 2K25 TERRAIN FORMAT!")
print("=" * 60)

# Load flat course as template
sample_file = Path(__file__).parent.parent / "reference" / "samples" / "dh5s31bwqzbp.course"
course = CourseFile.load(sample_file)

print(f"Original height entries: {len(course.course_data['height'])}")

# Add terrain using the CORRECT format!
terrain_entry = {
    'tool': 0,
    'position': {'x': 0.0, 'y': '-Infinity', 'z': 0.0},  # Center of map
    'rotation': {'x': 0.0, 'y': 0.0, 'z': 0.0},
    'scale': {'x': 100.0, 'y': 1.0, 'z': 100.0},  # 100m radius
    'type': 72,  # Type 72 seems to be terrain modification
    'value': 20.0,  # 20 meters high!
    'holeId': -1
}

course.course_data['height'].append(terrain_entry)

print(f"New height entries: {len(course.course_data['height'])}")

# Save it
course.set_name("CORRECT FORMAT - Big Hill Test")
output_file = Path(__file__).parent.parent / "output" / "correct_terrain.course"
course.save(output_file)

print(f"\n✓ Saved to: {output_file}")

# Copy to game
copy_to_game(output_file, game_version='2K25', custom_name='correctterrain')

print("\n" + "=" * 60)
print("✅ TRY IT IN THE GAME!")
print("Look for: 'CORRECT FORMAT - Big Hill Test'")
print("There should be a BIG hill in the center!")
print("=" * 60)