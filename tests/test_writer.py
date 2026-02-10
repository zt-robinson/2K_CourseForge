import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from course_file import CourseFile

print("=" * 60)
print("COURSE FILE WRITER TEST")
print("=" * 60)

# Load your existing 2K25 course as a template
print("\n1. Loading your 2K25 course as template...")
sample_file = Path(__file__).parent.parent / "reference" / "samples" / "vr1p6c0wqeyf.course"
course = CourseFile.load(sample_file)
print(f"   ✓ Loaded: {course.get_name()}")

# Modify the course name
print("\n2. Modifying course name...")
new_name = "GENERATED - Test Course from Python"
course.set_name(new_name)
print(f"   ✓ New name: {course.get_name()}")

# Save to output folder
print("\n3. Saving modified course...")
output_file = Path(__file__).parent.parent / "output" / "test_generated.course"
course.save(output_file)
print(f"   ✓ Saved to: {output_file}")

# Verify we can read it back
print("\n4. Verifying saved file...")
verify_course = CourseFile.load(output_file)
print(f"   ✓ Course name: {verify_course.get_name()}")
print(f"   ✓ Theme: {verify_course.get_theme()}")
print(f"   ✓ Version: {verify_course.version.value}")

print("\n" + "=" * 60)
print("✅ SUCCESS! Course file created and verified!")
print("=" * 60)
print(f"\nNext step: Copy this file to your game:")
print(f"From: {output_file}")
print(f"To:   C:\\Users\\ztrob\\OneDrive\\Documents\\My Games\\PGA TOUR 2K25\\")
print(f"\nThen open PGA 2K25 and look for '{new_name}'")