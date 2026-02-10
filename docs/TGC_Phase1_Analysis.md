# TGC Designer Tools - Phase 1 Analysis & Investigation Plan

**Date:** February 8, 2026  
**Project:** User-Friendly LiDAR Course Creation Tool  
**Current Phase:** Understanding & Documentation

---

## Executive Summary

The goal is to create a modern, user-friendly application for importing real-world golf courses into PGA 2K games using LiDAR elevation data. The current process involves multiple manual steps, several software tools, and is prone to errors. This document outlines our Phase 1 investigation plan.

---

## Current Workflow (The Problem)

### Step-by-Step Process
1. Create blank course in TGC 2019
2. Manually download LiDAR files from NOAA
3. Export course file from game
4. Run TGC Designer Tools
5. Process LiDAR data
6. Create mask images manually
7. Re-import to game
8. Manual decoration and cleanup

### Major Pain Points
- Must use TGC 2019 even for 2K25 courses
- Manual file management across multiple directories
- Complex LiDAR data acquisition
- No visual feedback during processing
- Cryptic error messages
- Steep learning curve

---

## Technical Investigation Areas

### 1. Course File Format (.course)

**What we know:**
- Binary/JSON hybrid structure
- Contains heightmap, metadata, object placements
- Different between game versions

**What we need to learn:**
- Exact file structure for each version (2019, 2K23, 2K25)
- Terrain data encoding format
- Coordinate system used
- What changed causing 2K25 compatibility issues

**Investigation approach:**
- Hex dump analysis of .course files
- Compare files before/after TGC Designer Tools processing
- Test minimal changes to understand structure
- Examine tgc_tools.py code for file parsing logic

### 2. LiDAR Processing Pipeline

**What we know:**
- Uses .las/.laz files from NOAA/USGS
- Generates heightmaps from point cloud data
- 2K25 requires higher quality (QL1, 8+ points/meter)
- High-res causes "striation" artifacts in 2K25

**What we need to learn:**
- Why does high-res cause striations?
- What filtering/smoothing is currently applied?
- Optimal processing settings for each game version
- Memory optimization opportunities

**Investigation approach:**
- Read tgc_image_terrain.py and tgc_kd_terrain.py
- Trace LiDAR data flow through processing
- Test different resolution/quality settings
- Research anti-aliasing techniques for heightmaps

### 3. Coordinate System Transformations

**What we know:**
- LiDAR uses geographic coordinates (lat/lon)
- Game uses internal coordinate system
- Scale and projection must be handled

**What we need to learn:**
- Exact transformation formulas
- Game coordinate system details
- How elevation is scaled
- Why alignment issues occur

**Investigation approach:**
- Examine GeoPointCloud.py
- Test known coordinates in/out
- Review coordinate system documentation in code

---

## Immediate Action Items

### Week 1-2: Environment Setup & Code Reading

**Task 1: Setup Development Environment**
```bash
# Clone repository
git clone https://github.com/HiCamino/TGC-Designer-Tools.git
cd TGC-Designer-Tools

# Install dependencies
python -m pip install -r requirements.txt

# Test run the GUI
python tgc_gui.py
```

**Task 2: Map Code Structure**
- Create call graph of key functions
- Identify entry points and data flow
- Document each module's purpose
- Find error-prone sections

**Task 3: File Format Investigation**
- Create test course in TGC 2019
- Export and examine .course file
- Make small changes and observe differences
- Document file structure findings

### Week 3-4: Deep Dive into Key Systems

**Task 4: Reverse Engineer .course Format**
- Use hex editor to analyze file structure
- Write Python script to parse/read .course files
- Document all sections and data types
- Test compatibility across game versions

**Task 5: Understand LiDAR Pipeline**
- Trace code from LiDAR input to heightmap output
- Document processing steps
- Identify performance bottlenecks
- Test with various LiDAR datasets

**Task 6: Identify 2K25 Issues**
- Research what changed in 2K25
- Test same LiDAR data across game versions
- Reproduce striation problem
- Propose solutions

---

## Key Questions to Answer

### Critical Questions
1. Can we write directly to 2K25 format, or is TGC 2019 required?
2. What causes the striation artifacts in 2K25?
3. Can we automate LiDAR data acquisition?
4. Is there a documented API for the .course format?

### Secondary Questions
1. What resolution limits exist per game version?
2. Can we improve processing speed?
3. How to better handle coordinate transformations?
4. What causes the most common user errors?

---

## Documentation Deliverables

By end of Phase 1, we should have:

1. **Code Documentation**
   - Annotated source code with explanations
   - Function-level documentation
   - Data flow diagrams

2. **File Format Specification**
   - Complete .course file format docs
   - Differences between game versions
   - Example files with annotations

3. **Processing Pipeline Documentation**
   - Step-by-step LiDAR processing explanation
   - Parameter effects and tuning guide
   - Performance optimization notes

4. **Issue Analysis Report**
   - Common error scenarios and fixes
   - 2K25 compatibility problems and solutions
   - User experience pain points ranked

5. **Improvement Roadmap**
   - Prioritized list of enhancements
   - Estimated complexity for each
   - Dependencies between improvements

---

## Success Criteria for Phase 1

We'll know Phase 1 is complete when:

- [ ] We can read and parse .course files programmatically
- [ ] We understand the LiDAR processing pipeline completely
- [ ] We've identified root cause of 2K25 issues
- [ ] We have a clear roadmap for Phase 2
- [ ] All code is documented and understandable
- [ ] We can create test .course files from scratch

---

## Resources

**Code Repository:**
https://github.com/HiCamino/TGC-Designer-Tools

**Community Forums:**
- Golf Simulator Forum (golfsimulatorforum.com)
- TGC Tours (tgctours.proboards.com)

**Data Sources:**
- NOAA Elevation Inventory
- The National Map (USGS)

**Tools Needed:**
- Python 3.12+
- Hex editor (HxD, 010 Editor)
- 3D visualization tools
- TGC 2019 game

---

## Next Steps

**Immediate:**
1. Clone repository and set up environment
2. Run existing tools to understand current state
3. Start documenting code as we read it

**This Week:**
- Map out all Python modules
- Create simple test course
- Begin .course file analysis

**Next Week:**
- Deep dive into file format
- Test LiDAR processing
- Start documenting findings

---

*This is a living document - update as we learn more*
