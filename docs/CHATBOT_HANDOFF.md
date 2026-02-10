# CourseForge Handoff

## Project Goal
Build a modern pipeline to create PGA 2K course files directly from LiDAR or elevation data without going through TGC 2019. The course format is JSON wrapped by gzip/base64 layers, and version differences are structural rather than encrypted.

## Repo Layout (Key Files)
- src/course_file.py: CourseFile class for reading/writing .course files, handles compression and encoding.
- config.py: paths, constants, and copy_to_game helper.
- docs/Course_File_Analysis.md: format analysis and version differences.
- tests/test_process_laz.py: LAZ to terrain grid experiment for 2K25.
- tests/test_process_elevation.py: raster elevation to terrain experiment for 2K25.

## Key Findings
- .course files are gzip compressed UTF-16 JSON.
- CourseDescription is base64 + gzip + UTF-16 JSON.
- 2K25 uses top-level terrain arrays (terrainHeight, height, surfaces2, secondarySurfaces). Older tooling writes to userLayers2, which 2K25 does not expect.

## Current Focus
1. Generate 2K25-compatible terrain data using top-level arrays.
2. Reduce grid artifacts (blocky or voxel-like terrain) by adjusting grid density and smoothing.
3. Investigate striation and discretization behavior using 2K25 flags.

## Recent Work (High Level)
- Working on grid artifacts in LAZ-derived terrain.
- Increased GRID_SIZE and added smoothing (box blur + gaussian) to reduce blockiness.
- Encountered issues: terrain still looks grid-like, sometimes flat with a single bump, and occasional "black hole" chunks.
- Experiments are in tests/test_process_laz.py.

## Suggested Next Steps
- Revisit grid binning logic and height normalization in tests/test_process_laz.py.
- Ensure NaN handling is not creating holes; consider fill or interpolation before smoothing.
- Confirm 2K25 uses height vs terrainHeight for terrain tool entries.
- Build a minimal, validated 2K25 course schema and test it in-game.
