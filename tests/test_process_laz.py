import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import (
    gaussian_filter,
    distance_transform_edt,
    binary_closing,
    binary_fill_holes,
)

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
from config import copy_to_game, get_game_courses_path  # noqa: E402

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

# TGC compatibility profile (borrowed from TGC-Designer-Tools patterns).
# 2K25 currently behaves better with this disabled.
USE_TGC_COMPAT_PROFILE = False

# how dense the stamps are on the 2000x2000 plot
BRUSH_SPACING = 150.0
BRUSH_SCALE = 460.0           # heavier overlap for smoother blended surface
BRUSH_TYPE = 54
STAMP_TOOL = 1

# smoothing applied to height field (in grid-cell units)
SIGMA_LAND = 0.8              # overall smoothing
SIGMA_WATER = 3.0             # extra smoothing for "missing" areas (likely water)

# near-zero cutoff (meters) for stamping
STAMP_EPS = 0.01              # don’t stamp tiny values (noise)

# how much to compress the real-world relief into the game (unitless)
RELIEF_MULT = 0.35

# auto-gain and stamp safety clamp (meters)
OVERLAP_GAIN = 1.4            # tune empirically; higher = less accumulation
TARGET_ABS_PERCENTILE = 95.0  # percentile used to normalize stamp amplitudes
TARGET_STAMP_AT_PERCENTILE = 12.0
MAX_STAMP_ABS = 60.0          # hard cap per stamp to avoid spikes

# land/water shaping controls:
# - gamma < 1 boosts subtle relief
# - negatives are attenuated so water effects don't dominate
RELIEF_GAMMA = 1.00
POSITIVE_RELIEF_BOOST = 1.15
NEGATIVE_RELIEF_SCALE = 0.25

# If you want to “pin” the map so that the lowest point is exactly 0m in-game:
PIN_MIN_TO_ZERO = False

# Keep stamp distribution centered around zero to avoid whole-map vertical drift.
FORCE_ZERO_MEAN_STAMPS = True

# Some templates appear to collapse to a flat plateau when procedural terrain is forced to zero.
# Leave this off by default and only disable if you've confirmed your template handles it.
DISABLE_PROCEDURAL_TERRAIN = False

# Recognition mode: exaggerate broad landform so tile shape is obvious first.
RECOGNITION_MODE = True
MACRO_SIGMA = 24.0
MACRO_GAIN = 3.0
DETAIL_GAIN = 0.03
POST_SHAPE_SIGMA = 9.0

# Optional lowland flattening to convert speckled puddles into broader basins.
ENABLE_WATER_FLOOR = True
WATER_FLOOR_PERCENTILE = 12.0
WATER_FLOOR_BLEND = 0.85
WATER_SURFACE_BAND = 0.45     # tighter band so only true low basin stays water
WATER_MASK_CLOSE_ITERS = 4    # stronger cleanup to suppress tiny islands
WATER_FLAT_BLEND = 0.995      # near-hard flattening in detected water areas

# Extra water cleanup pass: apply explicit negative stamps only in water mask areas.
ENABLE_WATER_DRAIN_STAMPS = True
WATER_DRAIN_SPACING = 80.0
WATER_DRAIN_SCALE = 300.0
WATER_DRAIN_VALUE = -5.0
WATER_DRAIN_DOUBLE_PASS = True

# Calibration mode: ignore water shaping and focus only on land relief tuning.
LAND_ONLY_MODE = False

# Similar to tgc_tools.elevate_terrain defaults:
# push terrain up and clip extreme lows to avoid unstable/deep artifacts.
ELEVATE_BUFFER_HEIGHT = 10.0
CLIP_LOWEST_VALUE = -2.0

if USE_TGC_COMPAT_PROFILE:
    BRUSH_TYPE = 10           # "soft_circle" in TGC definitions
    STAMP_TOOL = 0            # TGC importer uses tool 0 for height stamps
    FORCE_ZERO_MEAN_STAMPS = False
    RECOGNITION_MODE = False

if LAND_ONLY_MODE:
    ENABLE_WATER_FLOOR = False
    ENABLE_WATER_DRAIN_STAMPS = False


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
src_min = float(np.nanmin(z_m))
src_max = float(np.nanmax(z_m))
src_p05 = float(np.nanpercentile(z_m, 5))
src_p95 = float(np.nanpercentile(z_m, 95))
print(
    f"Source LiDAR range: {src_min:.2f} to {src_max:.2f} m "
    f"(full {src_max - src_min:.2f} m, p95-p05 {src_p95 - src_p05:.2f} m)"
)

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

if RECOGNITION_MODE:
    # Boost broad contours and suppress micro undulation for easier visual matching.
    macro = gaussian_filter(height_grid, sigma=MACRO_SIGMA, mode="nearest")
    detail = height_grid - macro
    height_grid = macro * MACRO_GAIN + detail * DETAIL_GAIN
    height_grid = gaussian_filter(height_grid, sigma=POST_SHAPE_SIGMA, mode="nearest")

water_floor = None
water_coverage = None
water_mask = None
if ENABLE_WATER_FLOOR:
    water_floor = float(np.percentile(height_grid, WATER_FLOOR_PERCENTILE))
    water_mask = height_grid < (water_floor + WATER_SURFACE_BAND)
    water_mask = binary_closing(water_mask, iterations=WATER_MASK_CLOSE_ITERS)
    water_mask = binary_fill_holes(water_mask)
    water_coverage = float(np.mean(water_mask))
    if np.any(water_mask):
        height_grid[water_mask] = (
            (1.0 - WATER_FLAT_BLEND) * height_grid[water_mask] + WATER_FLAT_BLEND * water_floor
        )
        # Gentle blend after flattening to avoid hard shoreline edges.
        height_grid = gaussian_filter(height_grid, sigma=2.0, mode="nearest")

if USE_TGC_COMPAT_PROFILE:
    # Mimic tgc_tools.elevate_terrain behavior: shift to a positive buffer and clip very low values.
    elevate_shift = -float(np.min(height_grid)) + ELEVATE_BUFFER_HEIGHT
    height_grid = height_grid + elevate_shift
    height_grid = np.where(height_grid >= CLIP_LOWEST_VALUE, height_grid, np.nan)
    if np.any(np.isnan(height_grid)):
        height_grid = fill_nan_nearest(height_grid.astype(np.float32)).astype(np.float32)

print(f"Height range (meters): {float(np.nanmin(height_grid)):.2f} to {float(np.nanmax(height_grid)):.2f}")
hg_p05 = float(np.nanpercentile(height_grid, 5))
hg_p95 = float(np.nanpercentile(height_grid, 95))
print(f"Height p95-p05 (meters): {hg_p95 - hg_p05:.2f}")

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
    # Nonlinear contrast: make subtle land relief more visible while keeping lows restrained.
    mag = abs(height_val_m)
    shaped = (mag ** RELIEF_GAMMA)
    if height_val_m >= 0.0:
        shaped *= POSITIVE_RELIEF_BOOST
    else:
        shaped *= -NEGATIVE_RELIEF_SCALE

    raw_stamp = (shaped * auto_gain) / OVERLAP_GAIN
    stamp_value = float(np.clip(raw_stamp, -MAX_STAMP_ABS, MAX_STAMP_ABS))
    if abs(raw_stamp) > MAX_STAMP_ABS:
        clip_count += 1
    if abs(stamp_value) > STAMP_EPS:
        landscape_entries.append(
            {
                "tool": STAMP_TOOL,
                "position": {"x": x_pos, "y": "-Infinity", "z": z_pos},
                "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
                "scale": {"x": float(BRUSH_SCALE), "y": 1.0, "z": float(BRUSH_SCALE)},
                "type": BRUSH_TYPE,
                "value": stamp_value,
                "holeId": -1,
            }
        )

# Optional second pass to suppress residual islands inside detected water bodies.
water_drain_count = 0
if ENABLE_WATER_DRAIN_STAMPS and (water_mask is not None):
    pass_offsets = [(0.0, 0.0)]
    if WATER_DRAIN_DOUBLE_PASS:
        pass_offsets.append((WATER_DRAIN_SPACING * 0.5, WATER_DRAIN_SPACING * 0.5))

    for ox, oz in pass_offsets:
        xw = -1000.0 + ox
        while xw <= 1000.0:
            zw = -1000.0 + oz
            while zw <= 1000.0:
                mx = int(((xw + 1000.0) / 2000.0) * (GRID_SIZE - 1))
                mz = int(((zw + 1000.0) / 2000.0) * (GRID_SIZE - 1))
                mx = max(0, min(GRID_SIZE - 1, mx))
                mz = max(0, min(GRID_SIZE - 1, mz))
                if bool(water_mask[mz, mx]):
                    landscape_entries.append(
                        {
                            "tool": 1,
                            "position": {"x": float(xw), "y": "-Infinity", "z": float(zw)},
                            "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
                            "scale": {"x": float(WATER_DRAIN_SCALE), "y": 1.0, "z": float(WATER_DRAIN_SCALE)},
                            "type": 54,
                            "value": float(WATER_DRAIN_VALUE),
                            "holeId": -1,
                        }
                    )
                    water_drain_count += 1
                zw += WATER_DRAIN_SPACING
            xw += WATER_DRAIN_SPACING

if not landscape_entries:
    print("WARNING: No terrain entries were created. Check STAMP_EPS / RELIEF_MULT.")
    sys.exit(0)

vals = [e["value"] for e in landscape_entries]
pos_count = sum(1 for v in vals if v > 0.0)
neg_count = sum(1 for v in vals if v < 0.0)
vals_np = np.array(vals, dtype=np.float64)
v_p05 = float(np.percentile(vals_np, 5))
v_p95 = float(np.percentile(vals_np, 95))
print(f"Created {len(landscape_entries)} landscaping brush strokes")
print(f"Brush value range written (meters): {min(vals):.4f} to {max(vals):.4f}")
print(f"Brush value p95-p05 (meters): {v_p95 - v_p05:.4f}")
print(f"Mean |stamp| (meters): {float(np.mean(np.abs(vals))):.4f}")
print(f"Stamp sign counts: +{pos_count} / -{neg_count} (mean {float(np.mean(vals)):.6f})")
print(f"Auto-gain: {auto_gain:.5f} (p{TARGET_ABS_PERCENTILE:.0f} |h| = {pctl_abs:.5f} m)")
print(f"Clipped stamps: {clip_count}/{len(sampled)} ({(100.0 * clip_count / max(1, len(sampled))):.1f}%)")
print(f"Brush spacing: {BRUSH_SPACING}, brush scale: {BRUSH_SCALE}")
print(f"Overlap gain: {OVERLAP_GAIN}, max abs stamp: {MAX_STAMP_ABS}")
print(f"Stamp tool/type: {STAMP_TOOL}/{BRUSH_TYPE}")
print(
    f"Relief shaping: gamma={RELIEF_GAMMA}, +boost={POSITIVE_RELIEF_BOOST}, "
    f"-scale={NEGATIVE_RELIEF_SCALE}"
)
print(
    f"Recognition mode: {RECOGNITION_MODE} (macro_sigma={MACRO_SIGMA}, "
    f"macro_gain={MACRO_GAIN}, detail_gain={DETAIL_GAIN}, post_sigma={POST_SHAPE_SIGMA})"
)
print(
    f"Water floor: {ENABLE_WATER_FLOOR} (pct={WATER_FLOOR_PERCENTILE}, level={water_floor}, "
    f"band={WATER_SURFACE_BAND}, flat_blend={WATER_FLAT_BLEND}, coverage={water_coverage})"
)
print(
    f"Water drain pass: {ENABLE_WATER_DRAIN_STAMPS} "
    f"(count={water_drain_count}, spacing={WATER_DRAIN_SPACING}, "
    f"scale={WATER_DRAIN_SCALE}, value={WATER_DRAIN_VALUE}, double_pass={WATER_DRAIN_DOUBLE_PASS})"
)
if USE_TGC_COMPAT_PROFILE:
    print(
        f"TGC compat: True (buffer={ELEVATE_BUFFER_HEIGHT}, clip_low={CLIP_LOWEST_VALUE})"
    )
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

course.set_name("TEST - LAZ LANDSCAPING (METERS) V5")

output_file = Path(__file__).parent.parent / "output" / "test_laz_grid.course"
course.save(output_file)
target_course_name = "testlazgrid_v5"
game_courses_path = get_game_courses_path("2K25")
if game_courses_path is not None:
    existing_target = game_courses_path / f"{target_course_name}.course"
    if existing_target.exists():
        existing_target.unlink()
        print(f"Removed existing course file: {existing_target}")
copy_to_game(output_file, game_version="2K25", custom_name=target_course_name)

print("Done. Load 'TEST - LAZ LANDSCAPING (METERS) V5' in 2K25.")
