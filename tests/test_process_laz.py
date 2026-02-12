import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt

# ---- helpers ----
def fill_nan_nearest(grid: np.ndarray) -> np.ndarray:
    """
    Fill NaNs by nearest-neighbor (distance transform).
    Keeps edges sane without introducing new extrema.
    """
    mask = np.isnan(grid)
    if not np.any(mask):
        return grid
    _, indices = distance_transform_edt(mask, return_indices=True)
    filled = grid[tuple(indices)]
    return filled.astype(grid.dtype)


def safe_unit_convert_to_meters(z: np.ndarray) -> tuple[np.ndarray, str]:
    """
    Calibration: 150 ft ~= 45.72 value => brush VALUE IS METERS.

    Heuristic:
      - If vertical range > ~800 units in one tile, likely feet -> convert to meters.
    """
    z_min = float(np.nanmin(z))
    z_max = float(np.nanmax(z))
    z_range = z_max - z_min

    if z_range > 800.0:
        return z * 0.3048, "feet->meters (heuristic)"
    return z, "meters (heuristic)"


# ---- repo imports ----
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.course_file import CourseFile  # noqa: E402
from config import copy_to_game  # noqa: E402

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

# ---- knobs you can tweak safely ----
GRID_SIZE = 1024

# how dense the stamps are on the 2000x2000 plot
BRUSH_SPACING = 60.0
BRUSH_SCALE = 85.0            # tighter brush to preserve local relief

# smoothing applied to height field (in grid-cell units)
SIGMA_LAND = 0.8              # overall smoothing
SIGMA_WATER = 3.0             # extra smoothing for "missing" areas (likely water)

# near-zero cutoff (meters) for stamping
STAMP_EPS = 0.01              # don’t stamp tiny values (noise)

# how much to compress the real-world relief into the game (unitless)
RELIEF_MULT = 0.35

# auto-gain and stamp safety clamp (meters)
OVERLAP_GAIN = 1.0            # tune empirically; higher = less accumulation
TARGET_ABS_PERCENTILE = 95.0  # percentile used to normalize stamp amplitudes
TARGET_STAMP_AT_PERCENTILE = 8.0
MAX_STAMP_ABS = 20.0          # hard cap per stamp to avoid spikes

# If you want to “pin” the map so that the lowest point is exactly 0m in-game:
PIN_MIN_TO_ZERO = False

# Keep stamp distribution centered around zero to avoid whole-map vertical drift.
FORCE_ZERO_MEAN_STAMPS = True

# Some templates appear to collapse to a flat plateau when procedural terrain is forced to zero.
# Leave this off by default and only disable if you've confirmed your template handles it.
DISABLE_PROCEDURAL_TERRAIN = False


# ---- load LAZ ----
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

# Prefer ground points (class 2)
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

# Convert units so that brush "value" is meters
z_m, units_note = safe_unit_convert_to_meters(z)
print(f"Z units: {units_note}")

min_x, max_x = float(np.min(x)), float(np.max(x))
min_y, max_y = float(np.min(y)), float(np.max(y))
if max_x == min_x or max_y == min_y:
    print("ERROR: Invalid bounds in LAZ file.")
    sys.exit(1)

# ---- bin to grid (average elevation per cell) ----
sum_grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
count_grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.int32)

xi = np.floor((x - min_x) / (max_x - min_x) * (GRID_SIZE - 1)).astype(np.int32)
yi = np.floor((y - min_y) / (max_y - min_y) * (GRID_SIZE - 1)).astype(np.int32)
xi = np.clip(xi, 0, GRID_SIZE - 1)
yi = np.clip(yi, 0, GRID_SIZE - 1)

np.add.at(sum_grid, (yi, xi), z_m)
np.add.at(count_grid, (yi, xi), 1)

grid = np.full((GRID_SIZE, GRID_SIZE), np.nan, dtype=np.float32)
mask = count_grid > 0
grid[mask] = (sum_grid[mask] / count_grid[mask]).astype(np.float32)

missing = np.isnan(grid)  # sparse/no returns (often water)

# fill gaps for continuity, then shift to relative heights
grid = fill_nan_nearest(grid)

if PIN_MIN_TO_ZERO:
    base_elev = float(np.min(grid))
else:
    # Centering around median yields signed cut/fill stamps and reduces net upward bias.
    base_elev = float(np.median(grid))

height_grid = (grid - base_elev) * RELIEF_MULT  # meters

# smooth: global + extra on missing zones
height_grid = gaussian_filter(height_grid, sigma=SIGMA_LAND, mode="nearest")
if np.any(missing):
    height_smooth_more = gaussian_filter(height_grid, sigma=SIGMA_WATER, mode="nearest")
    height_grid[missing] = height_smooth_more[missing]

if FORCE_ZERO_MEAN_STAMPS:
    height_grid = height_grid - float(np.median(height_grid))

print(f"Height range (meters): {float(np.nanmin(height_grid)):.2f} to {float(np.nanmax(height_grid)):.2f}")

# ---- sample onto plot and generate landscaping stamps ("height") ----
sampled = []

x_pos = -1000.0
while x_pos <= 1000.0:
    z_pos = -1000.0
    while z_pos <= 1000.0:
        # map plot coords [-1000,1000] to [0, GRID_SIZE-1]
        grid_x = ((x_pos + 1000.0) / 2000.0) * (GRID_SIZE - 1)
        grid_z = ((z_pos + 1000.0) / 2000.0) * (GRID_SIZE - 1)

        gx, gz = int(grid_x), int(grid_z)
        fx, fz = grid_x - gx, grid_z - gz

        gx = max(0, min(GRID_SIZE - 2, gx))
        gz = max(0, min(GRID_SIZE - 2, gz))

        # bilinear sample (grid is [row=z][col=x])
        h00 = float(height_grid[gz, gx])
        h10 = float(height_grid[gz, gx + 1])
        h01 = float(height_grid[gz + 1, gx])
        h11 = float(height_grid[gz + 1, gx + 1])

        h0 = h00 * (1 - fx) + h10 * fx
        h1 = h01 * (1 - fx) + h11 * fx
        height_val_m = h0 * (1 - fz) + h1 * fz  # meters

        sampled.append((float(x_pos), float(z_pos), height_val_m))

        z_pos += BRUSH_SPACING
    x_pos += BRUSH_SPACING

raw_vals = np.array([h for _, _, h in sampled], dtype=np.float64)
pctl_abs = float(np.percentile(np.abs(raw_vals), TARGET_ABS_PERCENTILE))
auto_gain = TARGET_STAMP_AT_PERCENTILE / max(pctl_abs, 1e-6)

landscape_entries = []
clip_count = 0
for x_pos, z_pos, height_val_m in sampled:
    raw_stamp = (height_val_m * auto_gain) / OVERLAP_GAIN
    stamp_value = float(np.clip(raw_stamp, -MAX_STAMP_ABS, MAX_STAMP_ABS))
    if abs(raw_stamp) > MAX_STAMP_ABS:
        clip_count += 1
    if abs(stamp_value) > STAMP_EPS:
        landscape_entries.append(
            {
                "tool": 1,  # raise/lower delta mode
                "position": {"x": x_pos, "y": "-Infinity", "z": z_pos},
                "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
                "scale": {"x": float(BRUSH_SCALE), "y": 1.0, "z": float(BRUSH_SCALE)},
                "type": 54,                 # your soft circular brush
                "value": stamp_value,
                "holeId": -1,
            }
        )

if not landscape_entries:
    print("WARNING: No terrain entries were created. Check STAMP_EPS / RELIEF_MULT.")
    sys.exit(0)

vals = [e["value"] for e in landscape_entries]
pos_count = sum(1 for v in vals if v > 0.0)
neg_count = sum(1 for v in vals if v < 0.0)
print(f"Created {len(landscape_entries)} landscaping brush strokes")
print(f"Brush value range written (meters): {min(vals):.4f} to {max(vals):.4f}")
print(f"Mean |stamp| (meters): {float(np.mean(np.abs(vals))):.4f}")
print(f"Stamp sign counts: +{pos_count} / -{neg_count} (mean {float(np.mean(vals)):.6f})")
print(f"Auto-gain: {auto_gain:.5f} (p{TARGET_ABS_PERCENTILE:.0f} |h| = {pctl_abs:.5f} m)")
print(f"Clipped stamps: {clip_count}/{len(sampled)} ({(100.0 * clip_count / max(1, len(sampled))):.1f}%)")
print(f"Brush spacing: {BRUSH_SPACING}, brush scale: {BRUSH_SCALE}")
print(f"Overlap gain: {OVERLAP_GAIN}, max abs stamp: {MAX_STAMP_ABS}")
print(f"Pin min to zero: {PIN_MIN_TO_ZERO}, force zero mean: {FORCE_ZERO_MEAN_STAMPS}")

# ---- write course ----
template_file = Path(__file__).parent.parent / "reference" / "samples" / "2k25_flat.course"
course = CourseFile.load(template_file)

# OPTIONAL debug dump
dump_path = Path(__file__).parent.parent / "output" / "template_dump.json"
course.export_json(dump_path)
print(f"Dumped template JSON to: {dump_path}")

# IMPORTANT: Use LANDSCAPING stamps
course.course_data["height"] = landscape_entries
course.course_data["terrainHeight"] = []  # keep empty

if DISABLE_PROCEDURAL_TERRAIN:
    # Turn off procedural hills/noise so only LiDAR stamps shape the plot.
    course.course_data["hillsAmount"] = 0.0
    course.course_data["hillsHeight"] = 0.0
    if "terrainNoise" in course.course_data and isinstance(course.course_data["terrainNoise"], dict):
        course.course_data["terrainNoise"]["scale"] = 0.0
    if "perturbationNoise" in course.course_data and isinstance(course.course_data["perturbationNoise"], dict):
        course.course_data["perturbationNoise"]["scale"] = 0.0

course.set_name("TEST - LAZ LANDSCAPING (METERS) V3")

output_file = Path(__file__).parent.parent / "output" / "test_laz_grid.course"
course.save(output_file)
copy_to_game(output_file, game_version="2K25", custom_name="testlazgrid_v3")

print("Done. Load 'TEST - LAZ LANDSCAPING (METERS) V3' in 2K25.")
