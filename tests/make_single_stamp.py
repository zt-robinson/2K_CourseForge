import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.course_file import CourseFile  # noqa: E402
from config import copy_to_game  # noqa: E402


def main():
    repo = Path(__file__).parent.parent
    template_file = repo / "reference" / "samples" / "3owvjyf3q5fv.course"

    course = CourseFile.load(template_file)

    # hard reset all terrain/landscaping edits
    course.course_data["height"] = []
    course.course_data["terrainHeight"] = []

    # keep procedural noise ON for this test (don’t change hills/noise yet)
    # (we’re only validating stamp semantics)

    # ONE stamp in the dead center
    stamp = {
        "tool": 1,  # IMPORTANT: this is the same "raise/lower" tool family you’ve been using
        "position": {"x": 0.0, "y": "-Infinity", "z": 0.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
        "scale": {"x": 100.0, "y": 1.0, "z": 100.0},
        "type": 54,        # soft circle
        "value": 10.0,     # meters (~33 ft). Try 45.72 if you want the known 150 ft test.
        "holeId": -1
    }

    course.course_data["height"] = [stamp]
    course.set_name("TEST - SINGLE STAMP")

    out = repo / "output" / "single_stamp.course"
    course.save(out)
    copy_to_game(out, game_version="2K25", custom_name="single_stamp")

    print("Wrote single_stamp.course. Load 'TEST - SINGLE STAMP' in 2K25.")


if __name__ == "__main__":
    main()
