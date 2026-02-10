import sys
sys.path.insert(0, '.')
from src.course_file import CourseFile
from pathlib import Path
import json

c = CourseFile.load(Path('reference/samples/gyreqqsrqbat.course'))
edits = c.course_data.get('AllMapEdits', [])
print(f'AllMapEdits length: {len(edits)}')
for i, edit in enumerate(edits):
    brushes = len(edit.get('brushes', []))
    splines = len(edit.get('splines', []))
    print(f'  Edit[{i}]: brushes={brushes}, splines={splines}')
    if brushes > 0:
        print(f'    Brushes sample: {json.dumps(edit["brushes"][:1], indent=2)[:600]}')
    if splines > 0:
        print(f'    Splines sample: {json.dumps(edit["splines"][:1], indent=2)[:600]}')

# Also export the full structure for inspection
with open('output/gyreqqsrqbat_decoded.json', 'w') as f:
    json.dump(c.course_data, f, indent=2)
print("\nDecoded JSON exported to output/gyreqqsrqbat_decoded.json")
