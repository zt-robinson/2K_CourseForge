# Getting Started - Phase 1 Investigation

## Quick Start Guide

### What You'll Need

**Software:**
- Python 3.12 (https://www.python.org/downloads/)
- Git (https://git-scm.com/downloads)
- A code editor (VS Code recommended: https://code.visualstudio.com/)
- TGC 2019 game (for testing)

**Optional but Helpful:**
- Hex editor (HxD: https://mh-nexus.de/en/hxd/)
- PyCharm Community Edition (better Python debugging)

---

## Step 1: Clone the Repository

Open a terminal/command prompt:

```bash
# Navigate to where you want the project
cd C:\Users\YourName\Documents\Projects

# Clone the repository
git clone https://github.com/HiCamino/TGC-Designer-Tools.git

# Enter the directory
cd TGC-Designer-Tools
```

---

## Step 2: Set Up Python Environment

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 3: Test Run the Existing Tool

```bash
# Run the GUI
python tgc_gui.py
```

This should launch the existing TGC Designer Tools interface. Don't worry if it looks confusing - that's what we're improving!

**Take screenshots and notes:**
- What options are available?
- What's unclear or confusing?
- What errors do you encounter?

---

## Step 4: Explore the Code

Open the project in your code editor and start reading:

### Priority Files to Understand:

**1. tgc_tools.py**
- Look for functions like `unpack_course_file()`, `pack_course_file()`
- These handle reading/writing .course files
- Add comments as you understand what each function does

**2. tgc_gui.py**
- This is the main GUI
- Understand the user workflow
- Note where things could be simplified

**3. lidar_map_api.py**
- How LiDAR data is fetched
- Look for NOAA/USGS API calls
- Could this be automated better?

**4. tgc_image_terrain.py**
- How heightmaps are generated
- Look for resolution settings
- This likely relates to 2K25 issues

---

## Step 5: Create a Test Course

**In TGC 2019:**
1. Open the game
2. Go to Course Designer
3. Create a new course
4. Choose any theme
5. Don't add anything - keep it blank
6. Delete the clubhouse if present
7. Save and exit

**Find the course file:**
1. Open File Explorer
2. Enable "Show hidden files" in View options
3. Navigate to: `C:\Users\YourName\AppData\LocalLow\2K\The Golf Club 2019\Courses`
4. Find your course (random name like XYHGHEOKJP.course)
5. Copy it to your project folder for testing

---

## Step 6: Analyze the Course File

### Basic Inspection:

```bash
# See file size
ls -lh your_course_name.course

# Look at first few bytes (shows file type/header)
head -c 100 your_course_name.course | xxd
```

### With Hex Editor:
1. Open .course file in HxD or similar
2. Look for patterns:
   - Text strings (course name, metadata)
   - Repeating structures (arrays)
   - Magic numbers (file format identifiers)
3. Take notes on what you find

---

## Step 7: Test the Processing Pipeline

**Get sample LiDAR data:**
1. Pick a small golf course for testing
2. Go to https://apps.nationalmap.gov/downloader/
3. Search for your test course
4. Download 1-2 LiDAR tiles (keep it small for testing)
5. Extract .las or .laz files

**Process through existing tool:**
1. Run `python tgc_gui.py`
2. Import your test course
3. Process the LiDAR data
4. Watch what happens - take notes on:
   - How long does it take?
   - What messages appear?
   - Where do output files go?
   - Any errors?

---

## Step 8: Document Your Findings

Create a new file: `investigation_notes.md`

```markdown
# My Investigation Notes

## Date: [Today's Date]

### Course File Analysis
- File size: 
- Apparent structure:
- Questions:

### LiDAR Processing
- Time taken:
- Memory used:
- Issues encountered:

### Code Questions
- What does [function_name] actually do?
- Why is [this step] necessary?
- Could [this process] be simplified?
```

---

## Common Issues & Solutions

### "Can't find AppData folder"
- Enable "Show hidden files" in Windows Explorer
- View > Show > Hidden items

### "Python not found"
- Make sure Python is added to PATH during installation
- Restart terminal after installing Python

### "Module not found" errors
- Make sure you activated the virtual environment
- Run `pip install -r requirements.txt` again

### "Permission denied" on course file
- Close TGC 2019 completely
- Make sure you're not trying to edit a file in use

---

## What to Focus On

### Week 1 Goals:
1. Get everything running
2. Understand the current workflow
3. Identify the biggest pain points
4. Start documenting code

### Week 2 Goals:
1. Analyze .course file format
2. Test LiDAR processing
3. Document findings
4. Identify improvement opportunities

---

## Questions to Answer as You Go

1. **File Format:**
   - Is the .course file compressed?
   - Where is the heightmap data stored?
   - How is metadata encoded?

2. **Processing:**
   - What's the slowest step?
   - Where do errors usually happen?
   - What could be parallelized?

3. **User Experience:**
   - What confuses users most?
   - What steps could be automated?
   - What feedback is missing?

---

## Getting Help

**Stuck?** Here's what to try:

1. Check existing GitHub issues
2. Search Golf Simulator Forum
3. Read the tutorial again with fresh eyes
4. Try a simpler test case
5. Ask in the community forums

**Document everything** - even failed attempts teach us something!

---

## Next Steps

Once you've completed these getting-started steps:

1. Share your findings
2. Identify the most critical issue to tackle first
3. Create a proof-of-concept improvement
4. Test with real users

Remember: The goal isn't to understand everything perfectly, but to understand enough to start improving things!

---

Good luck! 🏌️
