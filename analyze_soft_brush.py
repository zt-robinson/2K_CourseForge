import sys
sys.path.insert(0, '.')
from src.course_file import CourseFile
from pathlib import Path
import json

c = CourseFile.load(Path('reference/samples/7axpgok0qipw.course'))
height = c.course_data.get('height', [])
print(f'Found {len(height)} entries in height array')
print()
for i, entry in enumerate(height):
    print(f'Entry {i}:')
    print(json.dumps(entry, indent=2))
