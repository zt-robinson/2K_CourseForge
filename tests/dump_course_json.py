from pathlib import Path
import sys

# make repo imports work
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.course_file import CourseFile  # noqa: E402


def main():
    course_path = REPO_ROOT / "reference" / "samples" / "FLAT_BRUSH.course"
    out_path = REPO_ROOT / "output" / "flatten_test_dump.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    course = CourseFile.load(course_path)
    course.export_json(out_path)

    print("Dumped to:", out_path)


if __name__ == "__main__":
    main()