import sys
from pathlib import Path
from src.course_file import CourseFile

samples = list(Path('reference/samples').glob('*.course'))
print('Checking samples for terrain data:')
for s in samples:
    try:
        c = CourseFile.load(s)
        h_len = len(c.course_data.get('height', []))
        th_len = len(c.course_data.get('terrainHeight', []))
        print(f'{s.name}: height={h_len}, terrainHeight={th_len}')
    except Exception as e:
        print(f'{s.name}: Error - {e}')
