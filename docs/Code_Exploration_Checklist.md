# Code Exploration Checklist

Use this checklist to systematically explore the TGC Designer Tools codebase.

---

## Module Analysis

### ✅ tgc_tools.py - Course File Handling

**Key Functions to Understand:**
- [ ] `unpack_course_file()` - How it reads .course files
- [ ] `pack_course_file()` - How it writes .course files  
- [ ] `get_metadata_json()` - Metadata extraction
- [ ] `set_course_metadata_name()` - Metadata modification
- [ ] `get_heightmap()` - Terrain data extraction
- [ ] `set_heightmap()` - Terrain data writing

**Questions to Answer:**
- [ ] What format is the heightmap? (PNG, raw bytes, other?)
- [ ] How is it compressed/encoded?
- [ ] What's the resolution (pixels/meters)?
- [ ] Where in the file is each component?

**Notes:**
```
[Write your observations here]
```

---

### ✅ tgc_image_terrain.py - Heightmap Generation

**Key Functions:**
- [ ] `generate_heightmap()` - Main processing function
- [ ] `apply_mask()` - How masks work
- [ ] `smooth_terrain()` - Smoothing algorithm
- [ ] Resolution/scale parameters

**Questions:**
- [ ] What causes striations in 2K25?
- [ ] How does resolution affect output?
- [ ] What smoothing is applied?
- [ ] Can we add anti-aliasing?

**Notes:**
```
[Write your observations here]
```

---

### ✅ lidar_map_api.py - LiDAR Data Access

**Key Functions:**
- [ ] `fetch_lidar_data()` - How data is retrieved
- [ ] `parse_coordinates()` - Coordinate handling
- [ ] Bounding box logic

**Questions:**
- [ ] Can we automate NOAA downloads?
- [ ] Is there a better API to use?
- [ ] How to handle multiple tiles?
- [ ] Can we cache downloaded data?

**Notes:**
```
[Write your observations here]
```

---

### ✅ usgs_lidar_parser.py - LiDAR File Parsing

**Key Functions:**
- [ ] `read_las_file()` - LAS format reader
- [ ] `read_laz_file()` - LAZ decompression
- [ ] Point cloud processing

**Questions:**
- [ ] What LiDAR formats are supported?
- [ ] How is point cloud filtered?
- [ ] Memory optimization opportunities?
- [ ] Can we stream large files?

**Notes:**
```
[Write your observations here]
```

---

### ✅ GeoPointCloud.py - Coordinate Transforms

**Key Functions:**
- [ ] Coordinate system conversions
- [ ] Projection handling
- [ ] Elevation scaling

**Questions:**
- [ ] What projection is used?
- [ ] How are coordinates transformed?
- [ ] Why do alignment issues occur?
- [ ] Can we improve accuracy?

**Notes:**
```
[Write your observations here]
```

---

### ✅ tgc_gui.py - User Interface

**Key Functions:**
- [ ] `importCourseAction()` - Course import handler
- [ ] `exportCourseAction()` - Course export handler
- [ ] UI layout and widgets

**Questions:**
- [ ] What's most confusing to users?
- [ ] What feedback is missing?
- [ ] Can we simplify the workflow?
- [ ] What modern UI framework to use?

**Notes:**
```
[Write your observations here]
```

---

## Data Structure Analysis

### Course File Structure

```
.course file layout:
[Document your findings here]

Offset | Size | Description
-------|------|------------
0x0000 | 4    | [File signature?]
0x0004 | ?    | [Metadata?]
...    | ...  | ...
```

### Heightmap Format

```
Heightmap encoding:
[Document your findings]

- Resolution: 
- Encoding: 
- Range: 
- Special values:
```

---

## Error Analysis

### Common Errors Encountered

**Error 1: Unicode Encode Error**
- When: 
- Cause:
- Fix:

**Error 2: JSON Decode Error**
- When:
- Cause:
- Fix:

**Error 3: [Add more as you find them]**
- When:
- Cause:
- Fix:

---

## Performance Profiling

### Processing Times

| Step | Time | Memory | Notes |
|------|------|--------|-------|
| Course import | | | |
| LiDAR parsing | | | |
| Heightmap gen | | | |
| Mask application | | | |
| Course export | | | |

### Bottlenecks Identified:
1. 
2. 
3. 

### Optimization Opportunities:
1.
2.
3.

---

## Compatibility Matrix

Test the same course across versions:

| Feature | 2019 | 2K23 | 2K25 | Notes |
|---------|------|------|------|-------|
| Import | | | | |
| Heightmap | | | | |
| High-res | | | | |
| Bunkers | | | | |
| Objects | | | | |

---

## Improvement Ideas

As you explore, jot down improvement ideas:

### Quick Wins (Easy, High Impact)
1. 
2. 
3. 

### Medium Complexity
1.
2.
3.

### Major Refactoring
1.
2.
3.

---

## Questions for Community/Forums

Things to ask other developers:

1. 
2. 
3. 

---

## Testing Checklist

### Unit Tests to Create
- [ ] Course file parsing
- [ ] Heightmap generation
- [ ] Coordinate transformation
- [ ] Mask application
- [ ] File I/O operations

### Integration Tests
- [ ] Full pipeline (LiDAR → Course)
- [ ] Cross-version compatibility
- [ ] Error handling
- [ ] Edge cases

---

## Documentation Progress

- [ ] All functions have docstrings
- [ ] Data structures documented
- [ ] File format spec written
- [ ] User guide updated
- [ ] Developer guide created

---

## Completion Criteria

Phase 1 is done when:

- [ ] All modules understood
- [ ] File format documented
- [ ] Issues identified and categorized
- [ ] Improvement roadmap created
- [ ] Test cases defined
- [ ] Can create .course file from scratch programmatically

---

**Last Updated:** [Date]
**Completed By:** [Your Name]
