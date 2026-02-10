"""
Configuration file for CourseForge
Stores paths and constants
"""
import os
from pathlib import Path

# User-specific paths (you'll edit these)
GAME_PATHS = {
    '2K25': Path(r"C:\Users\ztrob\OneDrive\Documents\My Games\PGA TOUR 2K25\Courses"),
    '2K23': Path(r"C:\Users\ztrob\OneDrive\Documents\My Games\PGA TOUR 2K23\Courses"),
    '2K19': Path(r"C:\Users\ztrob\AppData\LocalLow\2K\The Golf Club 2019\Courses")
}

# Project paths
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
REFERENCE_DIR = PROJECT_ROOT / "reference"
OUTPUT_DIR = PROJECT_ROOT / "output"
DOCS_DIR = PROJECT_ROOT / "docs"

# Course dimensions (in yards)
COURSE_SIZE_YARDS = 2187.23
COURSE_SIZE_METERS = COURSE_SIZE_YARDS * 0.9144  # = ~2000 meters

# Course coordinate system
# The game uses a coordinate system where:
# - Center is (0, 0)
# - Range is approximately -1000 to +1000 meters in both X and Z
COURSE_MIN_COORD = -1000.0
COURSE_MAX_COORD = 1000.0
COURSE_SIZE_TOTAL = 2000.0  # meters

# Theme mappings (number to name)
THEMES = {
    0: "links",
    1: "parkland", 
    2: "desert",
    3: "tropics",
    4: "alpine",
    5: "boreal",
    6: "coast",
    7: "prairie",
    8: "wasteland",
    9: "autumn"
}

# Reverse mapping
THEME_NAMES = {v: k for k, v in THEMES.items()}

def get_game_courses_path(version='2K25'):
    """Get the courses directory for a specific game version"""
    path = GAME_PATHS.get(version)
    if path and path.exists():
        return path
    return None

def get_output_path(filename):
    """Get full path for output file"""
    return OUTPUT_DIR / filename

def copy_to_game(source_file, game_version='2K25', custom_name=None):
    """
    Copy a course file to the game directory
    
    Args:
        source_file: Path to the .course file to copy
        game_version: Which game ('2K25', '2K23', '2K19')
        custom_name: Optional custom filename (without .course extension)
    
    Returns:
        Path to the copied file
    """
    import shutil
    import random
    import string
    
    game_path = GAME_PATHS.get(game_version)
    
    if not game_path or not game_path.exists():
        print(f"❌ Game path not found: {game_path}")
        return None
    
    # Generate random filename like the game does if not provided
    if custom_name is None:
        custom_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    
    dest_file = game_path / f"{custom_name}.course"
    
    # Copy the file
    shutil.copy2(source_file, dest_file)
    
    print(f"✓ Copied to game:")
    print(f"  {dest_file}")
    
    return dest_file