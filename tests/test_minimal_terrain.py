import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.course_file import CourseFile
from config import copy_to_game

print("Testing if terrain data needs to be in a special format...")

# Load blank course
sample_file = Path(__file__).parent.parent / "reference" / "samples" / "vr1p6c0wqeyf.course"
course = CourseFile.load(sample_file)

# Try just ONE terrain point with MORE data
# Maybe the game expects additional fields?
terrain_point = {
    "position": [0.0, 0.0],  # Center
    "value": 10.0  # 10 meters high
}

course.course_data['terrainHeight'].append(terrain_point)
course.course_data['height'].append(terrain_point)

# Maybe we need to set a flag to enable custom terrain?
# Let's enable the height field flags
course.course_data['useV4Height'] = True  # Try enabling height system
course.course_data['useV46HeightFieldDiscretization'] = True  # 2K25 terrain flag

course.set_name("TERRAIN TEST - Single Point v2")
output_file = Path(__file__).parent.parent / "output" / "terrain_test_v2.course"
course.save(output_file)

print(f"✓ Saved with terrain flags enabled")
copy_to_game(output_file, game_version='2K25', custom_name='terraintest2')

print("\n✅ Try loading 'TERRAIN TEST - Single Point v2' in the game")