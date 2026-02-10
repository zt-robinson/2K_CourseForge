import sys
sys.path.insert(0, '.')
from src.course_file import CourseFile
from pathlib import Path

c = CourseFile.load(Path('reference/samples/ji55lvo7qm18.course'))

print('Non-empty arrays/objects in course:')
for k in sorted(c.course_data.keys()):
    v = c.course_data[k]
    if isinstance(v, list):
        if len(v) > 0:
            print(f'{k}: list len={len(v)}')
    elif isinstance(v, dict):
        if len(v) > 0:
            print(f'{k}: dict len={len(v)}')
