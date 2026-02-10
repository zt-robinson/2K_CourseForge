import sys
sys.path.insert(0, '.')
from src.course_file import CourseFile
from pathlib import Path
import json

c = CourseFile.load(Path('reference/samples/ji55lvo7qm18.course'))

# Check what's in AllMapEdits
edits = c.course_data.get('AllMapEdits', [])
print(f'AllMapEdits length: {len(edits)}')
for i, edit in enumerate(edits):
    brushes = len(edit.get('brushes', []))
    splines = len(edit.get('splines', []))
    print(f'  Edit[{i}]: brushes={brushes}, splines={splines}')

# Find which layer has the brush
for i, edit in enumerate(edits):
    if len(edit.get('brushes', [])) > 0:
        print(f'\nFound brushes in Edit layer {i}!')
        print(f'Number of brushes: {len(edit["brushes"])}')
        print(f'\nFirst 2 brushes:')
        for j, brush in enumerate(edit['brushes'][:2]):
            print(f'\nBrush {j}:')
            print(json.dumps(brush, indent=2))

# Export full course for inspection
with open('output/ji55lvo7qm18_decoded.json', 'w') as f:
    json.dump(c.course_data, f, indent=2)
print("\n\nFull decoded JSON exported to output/ji55lvo7qm18_decoded.json")
