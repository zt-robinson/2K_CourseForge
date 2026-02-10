import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.course_file import CourseFile
from config import copy_to_game

try:
    import rasterio
    from rasterio.windows import Window
except ImportError:
    print("ERROR: rasterio not installed!")
    sys.exit(1)

print("="*80)
print("LOADING ELEVATION DATA")
print("="*80)

tif_file = Path(__file__).parent.parent / "elevation_data" / "USGS_13_n43w071_20230117.tif"

with rasterio.open(tif_file) as src:
    window = Window(2603, 2603, 200, 200)
    elevation_data = src.read(1, window=window)

print(f"Data range: {np.min(elevation_data):.2f} to {np.max(elevation_data):.2f}")

# Load template
template_file = Path(__file__).parent.parent / "reference" / "samples" / "2k25_flat.course"
course = CourseFile.load(template_file)

print("\nCreating terrain...")
terrain_entries = []

# SAMPLE EVERY PIXEL - don't skip any!
for y in range(0, 200, 1):  # Changed from 5 to 1
    for x in range(0, 200, 1):  # Changed from 5 to 1
        elev = float(elevation_data[y, x])
        
        if elev < -1000:
            continue
        
        game_x = (x / 200.0) * 2000 - 1000
        game_z = (y / 200.0) * 2000 - 1000
        
        # AMPLIFY BY 100X
        height_value = elev * 100.0
        
        terrain_entry = {
            'tool': 0,
            'position': {'x': float(game_x), 'y': '-Infinity', 'z': float(game_z)},
            'rotation': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'scale': {'x': 25.0, 'y': 1.0, 'z': 25.0},  # Smaller scale since more points
            'type': 10,
            'value': float(height_value),
            'holeId': -1
        }
        
        terrain_entries.append(terrain_entry)

heights = [t['value'] for t in terrain_entries]
print(f"Created {len(terrain_entries)} points")
print(f"Height range: {min(heights):.2f} to {max(heights):.2f}")

course.course_data['height'].extend(terrain_entries)
course.set_name("TEST - Amplified Terrain")

output_file = Path(__file__).parent.parent / "output" / "test_amplified.course"
course.save(output_file)
copy_to_game(output_file, game_version='2K25', custom_name='testamp')

print(f"\n✅ DONE - Check 'TEST - Amplified Terrain' in game")