# CourseForge

CourseForge is a reverse-engineering and tooling project for reading, modifying, and writing PGA TOUR 2K `.course` files, with a current focus on PGA TOUR 2K25 terrain workflows and LiDAR-driven terrain generation.

The project provides:
- A Python reader/writer for `.course` files
- Script-based experiments for terrain brush behavior
- Iterative pipelines for converting LiDAR (`.laz`) data into game terrain stamps

## Current Status

This repository is actively experimental. Core file decode/encode is working, and terrain brush data can be written and loaded by the game. The exact behavior of full-surface terrain reconstruction from dense LiDAR stamps is still being tuned.

## Key Findings So Far (2K25)

These findings are based on practical tests in-game and sample file comparison:

- `height` is the active landscaping brush container for relevant terrain edits.
- `terrainHeight` should generally remain empty for this workflow (can trigger undesirable behavior in some tests).
- For tested files, `tool: 1` behaves as raise/lower delta mode.
- `type: 54` matches a soft circular brush profile in known sample files.
- Brush `value` acts in meter-like units (calibrated against known 150 ft ~ 45.72 behavior).
- Stamp overlap and density strongly affect net accumulation and can create ceiling-lock behavior if not managed.

## Repository Layout

```text
CourseForge/
|- src/
|  `- course_file.py              # Core .course load/save implementation
|- tests/
|  |- test_process_laz.py         # Main LiDAR -> brush stamping pipeline
|  |- make_single_stamp.py        # Minimal single-brush semantics test
|  |- dump_brush_tests.py         # Compare FLAT/RAISE/LOWER sample files
|  `- test_reader.py              # Basic reader sanity check
|- reference/
|  `- samples/                    # Known sample .course files used as templates
|- elevation_data/                # Input .laz files
|- output/                        # Generated courses + debug dumps
|- config.py                      # Local game paths and constants
`- README.md                      # Project guide and status
```

## How `.course` Handling Works

`src/course_file.py` performs two-layer decode/encode:

1. Outer file is gzip-compressed UTF-16 JSON
2. `binaryData.CourseDescription` is base64-encoded gzip data
3. Inner data (CourseDescription JSON) is decoded, modified, then re-encoded
4. Entire outer structure is written back to a valid `.course` file

Version detection is currently heuristic-based (`terrainHeight`, `userLayers2`, `userLayers` keys).

## Prerequisites

- Python 3.10+
- pip
- Windows environment with access to local PGA TOUR 2K folders

Install dependencies:

```powershell
python -m pip install numpy scipy laspy lazrs
```

## Configuration

Edit `config.py` to match your local install paths.

Important key:
- `GAME_PATHS['2K25']` should point to your 2K25 `Courses` folder

`copy_to_game(...)` uses this path to place generated `.course` files directly in-game.

## Quick Start

### 1. Verify Reader/Writer

```powershell
python tests/test_reader.py
```

### 2. Run Single Stamp Semantics Test

```powershell
python tests/make_single_stamp.py
```

This validates whether a known brush entry in `height` is applied by the game.

### 3. Run LiDAR Pipeline

```powershell
python tests/test_process_laz.py
```

This script:
- Loads first `.laz` file from `elevation_data/` (sorted order)
- Filters to ground classification (class 2) when available
- Bins points into a grid
- Fills gaps, smooths field, maps to plot coordinates
- Converts to landscaping brush stamps and writes to `height`
- Saves to `output/test_laz_grid.course`
- Copies output to the game folder

## LiDAR Pipeline Notes

`tests/test_process_laz.py` includes:
- Gap filling using nearest-neighbor distance transform
- Unit heuristic for feet->meters conversion
- Configurable smoothing and brush density
- Auto-gain based on percentile amplitude to reduce manual tuning
- Stamp clipping diagnostics (`Clipped stamps: ...`) to detect saturation

Useful console outputs:
- `Height range (meters)`
- `Brush value range written (meters)`
- `Mean |stamp|`
- `Auto-gain`
- `Clipped stamps`

These metrics help distinguish:
- under-driven stamps (no visible effect)
- over-clipped stamps (loss of detail)
- bias/accumulation risk

## Recommended Test Workflow

1. Generate a course with `test_process_laz.py`
2. Load the generated course in 2K25
3. Check:
   - Ceiling lock (yes/no)
   - Relief visibility (none/mild/clear)
   - Sculpt editability (raise/lower works?)
4. Use script diagnostics + in-game observations to retune knobs
5. Repeat quickly with new output name/version suffixes

## Important Caveats

- This is reverse-engineered and behavior may differ by template/course seed.
- Some templates appear to react poorly when procedural terrain/noise is force-disabled.
- Dense overlapping stamps can flatten detail or push terrain limits unexpectedly.
- File schema details not yet fully documented by official sources.

## Safety and Backups

- Keep backups of known-good `.course` files.
- Use unique output names when testing to avoid cache/stale-load confusion.
- Avoid editing live courses without versioned copies.

## Roadmap

Planned/likely next steps:
- Multi-tile LiDAR merge support
- Better normalization for preserving micro-relief
- Controlled calibration presets (land-first vs full terrain)
- More robust template selection and compatibility matrix
- Cleaner CLI entry points (instead of test-script driven workflow)

## Contributing

Contributions are welcome, especially around:
- Terrain semantics validation
- Additional sample diffing
- 2K25-specific structure mapping
- Safer/faster LiDAR conversion strategies

When contributing, include:
- exact input file(s)
- script parameters
- console diagnostics
- in-game observed outcome

## Disclaimer

This project is unofficial and not affiliated with HB Studios, 2K, or Take-Two. Use at your own risk.
