import sys
sys.path.insert(0, '.')
from src.course_file import CourseFile
from pathlib import Path
import json

c = CourseFile.load(Path('reference/samples/yb5jyp44qmsa.course'))
height = c.course_data.get('height', [])
print(f'Found {len(height)} entries in height array\n')
for i, entry in enumerate(height):
    print(f'Brush {i}:')
    print(f'  Position: ({entry["position"]["x"]}, {entry["position"]["z"]})')
    print(f'  Scale: {entry["scale"]["x"]}')
    print(f'  Value (height): {entry["value"]}')
    print(f'  Type: {entry["type"]}')
    print()
