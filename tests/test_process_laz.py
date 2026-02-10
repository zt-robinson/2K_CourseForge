import sys
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt

def box_blur(grid, radius=2):
    pad = radius
    padded = np.pad(grid, pad, mode="edge")
    out = np.empty_like(grid)
    for y in range(grid.shape[0]):
        for x in range(grid.shape[1]):
            window = padded[y:y + 2 * radius + 1, x:x + 2 * radius + 1]
            out[y, x] = np.nanmean(window)
    return out


def fill_nan_nearest(grid):
    mask = np.isnan(grid)
    if not np.any(mask):
        return grid
    _, indices = distance_transform_edt(mask, return_indices=True)
    filled = grid[tuple(indices)]
    return filled.astype(grid.dtype)

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.course_file import CourseFile
from config import copy_to_game

try:
    import laspy
except ImportError:
    print("ERROR: laspy not installed. Run: python -m pip install laspy lazrs")
    sys.exit(1)

try:
    import lazrs  # noqa: F401
except ImportError:
    print("ERROR: lazrs not installed. Run: python -m pip install lazrs")
    sys.exit(1)

GRID_SIZE = 1024
HEIGHT_SCALE = 1.0  # 1.0 = true elevations, >1.0 would exaggerate
CELL_SCALE_MIN = 2.0

lidar_dir = Path(__file__).parent.parent / "elevation_data"
laz_files = sorted(lidar_dir.glob("*.laz"))

if not laz_files:
    print(f"ERROR: No .laz files found in {lidar_dir}")
    sys.exit(1)

laz_file = laz_files[0]
print(f"Loading LAZ: {laz_file.name}")

las = laspy.read(laz_file)
x = las.x.copy()
y = las.y.copy()
z = las.z.copy()

# Use ground points if classification is available
if hasattr(las, "classification"):
    ground_mask = las.classification == 2
    if np.any(ground_mask):
        x = x[ground_mask]
        y = y[ground_mask]
        z = z[ground_mask]
        print(f"Using ground points: {len(z)}")
    else:
        print("No ground classification found; using all points.")
else:
    print("No classification field; using all points.")

min_x, max_x = np.min(x), np.max(x)
min_y, max_y = np.min(y), np.max(y)

if max_x == min_x or max_y == min_y:
    print("ERROR: Invalid bounds in LAZ file.")
    sys.exit(1)

# Bin to grid using average elevation per cell
sum_grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
count_grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.int32)

xi = np.floor((x - min_x) / (max_x - min_x) * (GRID_SIZE - 1)).astype(np.int32)
yi = np.floor((y - min_y) / (max_y - min_y) * (GRID_SIZE - 1)).astype(np.int32)

xi = np.clip(xi, 0, GRID_SIZE - 1)
yi = np.clip(yi, 0, GRID_SIZE - 1)

np.add.at(sum_grid, (yi, xi), z)
np.add.at(count_grid, (yi, xi), 1)

grid = np.full((GRID_SIZE, GRID_SIZE), np.nan, dtype=np.float32)
mask = count_grid > 0
grid[mask] = (sum_grid[mask] / count_grid[mask]).astype(np.float32)

grid = fill_nan_nearest(grid)
base_elev = np.min(grid)
height_grid = (grid - base_elev) * HEIGHT_SCALE
height_grid = np.clip(height_grid, 0.0, np.percentile(height_grid, 99.7))
height_grid = box_blur(height_grid, radius=2)
height_grid = gaussian_filter(height_grid, sigma=5.0, mode="nearest")
height_grid = box_blur(height_grid, radius=2)
height_grid = gaussian_filter(height_grid, sigma=4.0, mode="nearest")
height_grid = gaussian_filter(height_grid, sigma=3.0, mode="nearest")
height_grid = gaussian_filter(height_grid, sigma=2.0, mode="nearest")

# Convert heightmap to landscaping brush strokes with fixed sizing
# Game map is 2000x2000, create brushes on a regular grid
brush_spacing = 20.0
brush_scale = 50.0  # Fixed size for consistent blending

terrain_entries = []
x_pos = -1000.0
while x_pos <= 1000.0:
    z_pos = -1000.0
    while z_pos <= 1000.0:
        # Map game coordinates (-1000 to 1000) to grid indices (0 to 1023)
        grid_x = ((x_pos + 1000.0) / 2000.0) * (GRID_SIZE - 1)
        grid_z = ((z_pos + 1000.0) / 2000.0) * (GRID_SIZE - 1)
        
        # Bilinear interpolation to sample height at this position
        gx, gz = int(grid_x), int(grid_z)
        fx, fz = grid_x - gx, grid_z - gz
        
        gx = max(0, min(GRID_SIZE - 2, gx))
        gz = max(0, min(GRID_SIZE - 2, gz))
        
        h00 = height_grid[gz, gx]
        h10 = height_grid[gz, gx + 1]
        h01 = height_grid[gz + 1, gx]
        h11 = height_grid[gz + 1, gx + 1]
        
        h0 = h00 * (1 - fx) + h10 * fx
        h1 = h01 * (1 - fx) + h11 * fx
        height_val = h0 * (1 - fz) + h1 * fz
        
        if height_val > 0.01:  # Only create brushes for non-zero heights
            terrain_entries.append({
                "tool": 1,
                "position": {"x": float(x_pos), "y": "-Infinity", "z": float(z_pos)},
                "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
                "scale": {"x": float(brush_scale), "y": 1.0, "z": float(brush_scale)},
                "type": 54,  # Soft feathered brush
                "value": float(height_val),
                "holeId": -1
            })
        
        z_pos += brush_spacing
    x_pos += brush_spacing

print(f"Created {len(terrain_entries)} landscaping brush strokes")
print(f"Height range: {np.nanmin(height_grid):.2f} to {np.nanmax(height_grid):.2f}")
print(f"Brush size: {brush_scale} (fixed)")

template_file = Path(__file__).parent.parent / "reference" / "samples" / "3owvjyf3q5fv.course"
course = CourseFile.load(template_file)
course.course_data["height"] = terrain_entries
course.set_name("TEST - LAZ LANDSCAPING BRUSHES")

output_file = Path(__file__).parent.parent / "output" / "test_laz_grid.course"
course.save(output_file)
copy_to_game(output_file, game_version="2K25", custom_name="testlazgrid")

print("Done. Load 'TEST - LAZ GRID' in 2K25.")