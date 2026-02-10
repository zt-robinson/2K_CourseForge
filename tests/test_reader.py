import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from course_file import CourseFile

# Test it
print("Testing file reader...")
sample_file = Path(__file__).parent.parent / "reference" / "samples" / "vr1p6c0wqeyf.course"

print(f"Looking for file at: {sample_file}")

if not sample_file.exists():
    print(f"❌ File not found!")
    print(f"Make sure the file exists at:")
    print(f"   {sample_file}")
    sys.exit(1)

course = CourseFile.load(sample_file)
print(f"Course name: {course.get_name()}")
print(f"Theme ID: {course.get_theme()}")
print(f"Version: {course.version.value}")
print(f"Legacy terrain: {course.course_data.get('legacyTerrain', 'N/A')}")
print(f"Top-level keys count: {len(course.course_data.keys())}")
print("\n✅ Success! File decoded correctly.")