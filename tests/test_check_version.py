import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.course_file import CourseFile

sample_file = Path(__file__).parent.parent / "reference" / "samples" / "vr1p6c0wqeyf.course"
course = CourseFile.load(sample_file)

print("Course internal version number:")
print(f"  version: {course.course_data.get('version', 'NOT FOUND')}")
print(f"  type: {course.course_data.get('type', 'NOT FOUND')}")

# Check for any version-related fields
print("\nAll fields with 'version' or 'use' in the name:")
for key in course.course_data.keys():
    if 'version' in key.lower() or key.startswith('use'):
        print(f"  {key}: {course.course_data[key]}")