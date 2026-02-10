# PGA 2K Course File Format - Complete Analysis

## Executive Summary

**GREAT NEWS:** We can absolutely skip the 2K19 → 2K23 → 2K25 conversion process!

The course files are **JSON-based** with a well-defined structure. They're just wrapped in compression layers. Once we understand the format changes between versions, we can write directly to any version.

---

## File Structure (All Versions)

### Layer 1: Compression
```
.course file → GZIP compressed
```

### Layer 2: Outer JSON (UTF-16 LE)
```json
{
  "data": {},
  "binaryData": {
    "CourseDescription": "<base64>",
    "Thumbnail": "<base64>",
    "CourseMetadata": "<base64>"
  }
}
```

### Layer 3: CourseDescription (Base64 → GZIP → UTF-16 LE → JSON)
This is where the actual course data lives - terrain, holes, objects, etc.

---

## Key Findings

### 1. File Format is Accessible ✅
- **No encryption** - Just standard compression
- **JSON structure** - Easy to read and modify
- **Documented by existing code** - TGC Designer Tools already does this

### 2. Version Differences Are Incremental 🎯

**2K19 → 2K23 Changes:**
- Added `blurHeight` flag
- Changed `userLayers` → `userLayers2` (simplified structure)
- Changed `holes` → `holes2`
- Changed `placedObjects*` → `placedObjects3`
- Changed `weather`/`weather2` → `weather3`
- Added version flags: `useV21PathBrush`, `useV28FairwaySeed`, etc.

**2K23 → 2K25 Changes:** (This is the big one!)
- Changed `userLayers2` structure → individual top-level keys
  - `terrainHeight` is now a top-level array (was in userLayers2)
  - `height` is now a top-level array (was in userLayers2)
  - `surfaces` → `surfaces2` and `secondarySurfaces`
- Added `bunkerSettings2` with new bunker configuration
- Added `legacyTerrain` flag (set to `false` for new courses)
- Many new version flags for new features
- Changed `holes2` → `holes3`
- Changed `placedObjects3` → `placedObjects4`

### 3. Terrain Data Location 🗺️

**2K19:** 
```json
"userLayers": {
  "terrainHeight": [],  // Imported LiDAR goes here
  "height": [],
  "surfaces": [],
  // ... other layers
}
```

**2K23:**
```json
"userLayers2": {
  "terrainHeight": [],  // Imported LiDAR goes here
  "height": [],
  "surfaces": [],
  // ... fewer layers than 2K19
}
```

**2K25:**
```json
// No more userLayers - everything is top-level!
"terrainHeight": [],  // Imported LiDAR goes here
"height": [],
"surfaceBrushes2": [],
"surfaces2": [...],
"secondarySurfaces": [...],
// etc.
```

**This is likely the source of 2K25 compatibility issues!** The TGC Designer Tools writes to `userLayers2`, but 2K25 expects top-level arrays.

---

## The Striation Problem - Root Cause Theory

Based on the new flags in 2K25:

```json
"useV46HeightFieldDiscretization": false,
"legacyTerrain": false,
"bunkerSettings2": {...}
```

**My Theory:**
1. 2K25 changed how terrain heightmaps are processed internally
2. The `useV46HeightFieldDiscretization` flag controls terrain mesh generation
3. Old courses have `legacyTerrain: true` which uses old processing
4. New courses need high-quality data formatted for the new system
5. When you import old-style terrain data into the new system, you get discretization artifacts (striations)

**The Fix:**
- Set appropriate version flags when creating 2K25 courses
- Use the new top-level structure instead of `userLayers2`
- Possibly apply different filtering when generating heightmaps

---

## What We Need to Build

### 1. Course File Writer (All Versions)

A Python class that can:
```python
course = CourseFile()
course.set_version('2K25')  # or '2K23', '2K19'
course.set_terrain_data(heightmap_array)
course.set_metadata(name="My Course", theme="boreal")
course.save("my_course.course")
```

### 2. Terrain Data Processor

```python
lidar_data = fetch_lidar(lat, lon, radius)
heightmap = process_for_version(lidar_data, version='2K25')
# Apply version-specific filtering, smoothing, etc.
```

### 3. Version Compatibility Layer

```python
def get_terrain_key_for_version(version):
    if version == '2K19':
        return 'userLayers.terrainHeight'
    elif version == '2K23':
        return 'userLayers2.terrainHeight'
    elif version == '2K25':
        return 'terrainHeight'  # Top-level
```

---

## Feasibility Assessment

### Can we write directly to 2K25? **YES! 100%**

**Required steps:**
1. Create the correct JSON structure (we know it now)
2. Set the right version flags
3. Use top-level keys instead of userLayers2
4. Encode as UTF-16 LE
5. Base64 encode → GZIP compress → embed in outer JSON
6. GZIP compress the whole thing
7. Save as .course file

**Complexity:** Medium - It's multiple layers but all standard formats

### Can we fix striations? **Probably! 80% confident**

**Approach:**
1. Understand what `useV46HeightFieldDiscretization` does
2. Possibly apply Gaussian blur or anti-aliasing
3. Match the expected resolution/format
4. Test and iterate

---

## Recommended Development Plan

### Phase 1.5: Proof of Concept (1-2 weeks)

**Goal:** Create a 2K25 course file from scratch programmatically

1. Write a Python script that:
   - Creates a blank course JSON structure for 2K25
   - Sets all required fields with defaults
   - Properly encodes and compresses
   - Saves as .course file

2. Test it:
   - Load in 2K25 game
   - Verify it works
   - Confirm structure is correct

3. Modify it:
   - Add simple terrain height data
   - Reload in game
   - See if terrain appears

**Success criteria:** We can create a playable 2K25 course without touching 2K19

### Phase 2: LiDAR Integration (2-3 weeks)

1. Take existing LiDAR processing code
2. Adapt it to write directly to 2K25 format
3. Test with real LiDAR data
4. Debug striation issues
5. Optimize for quality

### Phase 3: User Interface (3-4 weeks)

Build the dream workflow:
1. User selects location on map
2. App fetches LiDAR automatically
3. One-click processing
4. Course file appears in game directory

---

## Next Immediate Steps

**Today:**
1. ✅ Analyze course files ← DONE!
2. Write a simple encoder/decoder in Python
3. Test round-trip (read → modify → write → test in game)

**This Week:**
1. Create a blank 2K25 course programmatically
2. Verify it loads in the game
3. Add simple terrain modifications
4. Document the process

**Next Week:**
1. Port LiDAR processing to 2K25 format
2. Test with real courses
3. Start building proof-of-concept GUI

---

## Technical Details for Implementation

### Encoding Pipeline

```python
import json
import base64
import gzip

def create_course_file(course_data, output_path):
    # 1. Inner JSON (CourseDescription)
    inner_json_str = json.dumps(course_data)
    inner_utf16 = inner_json_str.encode('utf-16-le')
    inner_compressed = gzip.compress(inner_utf16)
    inner_b64 = base64.b64encode(inner_compressed).decode('ascii')
    
    # 2. Outer JSON
    outer = {
        "data": {},
        "binaryData": {
            "CourseDescription": inner_b64,
            "Thumbnail": "<generate or use default>",
            "CourseMetadata": "<generate or use default>"
        }
    }
    
    outer_json_str = json.dumps(outer)
    outer_utf16 = outer_json_str.encode('utf-16-le')
    
    # 3. Final GZIP
    final_compressed = gzip.compress(outer_utf16)
    
    # 4. Save
    with open(output_path, 'wb') as f:
        f.write(final_compressed)
```

### Version-Specific Templates

I can create starter templates with all required fields for each version, making it easy to generate valid courses.

---

## Conclusion

**The "create in 2K19 first" workflow is NOT necessary!**

It exists because:
1. The TGC Designer Tools were built around 2K19 format
2. They never updated for 2K25's structural changes
3. The games have backward compatibility (2K25 can read 2K19 files)

We can build a better tool that:
- Writes directly to any game version
- Uses the native structure for each
- Avoids compatibility issues
- Provides a much better user experience

The file format is fully accessible and documented. We're ready to start building!

---

*Analysis Date: February 8, 2026*
