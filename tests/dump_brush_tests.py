from pathlib import Path
import json
import sys

# Make repo imports work
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.course_file import CourseFile  # noqa: E402


def export_course_json(course_path: Path, out_dir: Path) -> Path:
    course = CourseFile.load(course_path)
    out_path = out_dir / f"{course_path.stem}.json"
    course.export_json(out_path)
    return out_path


def first_entry(d, key):
    """Return the first dict entry in a list field, or None."""
    v = d.get(key)
    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
        return v[0]
    return None


def summarize(d, label):
    height = d.get("height", [])
    terrain_height = d.get("terrainHeight", [])

    height_len = len(height) if isinstance(height, list) else None
    terrain_height_len = len(terrain_height) if isinstance(terrain_height, list) else None

    s = {
        "label": label,
        "name": d.get("name"),
        "version": d.get("version"),
        "legacyTerrain": d.get("legacyTerrain"),
        "height_len": height_len,
        "terrainHeight_len": terrain_height_len,
        "height_first": first_entry(d, "height"),
        "terrainHeight_first": first_entry(d, "terrainHeight"),
    }
    return s


def deep_diff(a, b, path=""):
    """
    Lightweight deep diff: returns list of changed paths.
    Does NOT print huge arrays; scans first ~200 list entries only.
    """
    changes = []

    if type(a) != type(b):
        changes.append(path or "<root>")
        return changes

    if isinstance(a, dict):
        keys = set(a.keys()) | set(b.keys())
        for k in sorted(keys):
            pa = a.get(k, "<MISSING>")
            pb = b.get(k, "<MISSING>")
            new_path = f"{path}.{k}" if path else k
            if pa == "<MISSING>" or pb == "<MISSING>":
                changes.append(new_path)
            else:
                changes.extend(deep_diff(pa, pb, new_path))
        return changes

    if isinstance(a, list):
        if len(a) != len(b):
            changes.append(f"{path} (len {len(a)} -> {len(b)})")
        n = min(len(a), len(b))
        scan = min(n, 200)
        for i in range(scan):
            changes.extend(deep_diff(a[i], b[i], f"{path}[{i}]"))
        if n > scan:
            changes.append(f"{path} (list truncated compare: first {scan} items)")
        return changes

    if a != b:
        changes.append(path or "<root>")
    return changes


def load_json(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    samples = REPO_ROOT / "reference" / "samples"
    out_dir = REPO_ROOT / "output" / "inspect"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "flat": samples / "FLAT_BRUSH.course",
        "raise": samples / "RAISE_BRUSH.course",
        "lower": samples / "LOWER_BRUSH.course",
    }

    # Validate files exist
    missing = [k for k, p in files.items() if not p.exists()]
    if missing:
        print("ERROR: Missing course files:")
        for k in missing:
            print(f"  {k}: {files[k]}")
        print("\nCheck filenames + location:")
        print(f"  {samples}")
        sys.exit(1)

    print("Using files:")
    for k, p in files.items():
        print(f"  {k}: {p.name}")

    # Dump and summarize
    dumped = {}
    summaries = {}

    for k, p in files.items():
        dump_path = export_course_json(p, out_dir)
        dumped[k] = dump_path
        data = load_json(dump_path)
        summaries[k] = summarize(data, k)

    print("\n=== SUMMARY (key fields) ===")
    for k in ["flat", "raise", "lower"]:
        s = summaries[k]
        print(f"\n[{k}] {files[k].name}")
        print(f"  name: {s['name']}")
        print(f"  version: {s['version']}  legacyTerrain: {s['legacyTerrain']}")
        print(f"  height_len: {s['height_len']}  terrainHeight_len: {s['terrainHeight_len']}")

        hf = s["height_first"]
        thf = s["terrainHeight_first"]

        if hf:
            print("  height[0]:")
            print(f"    tool={hf.get('tool')} type={hf.get('type')} value={hf.get('value')}")
            sc = hf.get("scale", {})
            pos = hf.get("position", {})
            print(f"    scale=({sc.get('x')}, {sc.get('z')}) pos=({pos.get('x')}, {pos.get('z')})")
        else:
            print("  height[0]: <none>")

        if thf:
            print("  terrainHeight[0]:")
            print(f"    tool={thf.get('tool')} type={thf.get('type')} value={thf.get('value')}")
            sc = thf.get("scale", {})
            pos = thf.get("position", {})
            print(f"    scale=({sc.get('x')}, {sc.get('z')}) pos=({pos.get('x')}, {pos.get('z')})")
        else:
            print("  terrainHeight[0]: <none>")

        print(f"  dumped: {dumped[k]}")

    # Diffs: flat -> raise, flat -> lower
    flat_json = load_json(dumped["flat"])
    raise_json = load_json(dumped["raise"])
    lower_json = load_json(dumped["lower"])

    print("\n=== DIFF PATHS (flat -> raise) ===")
    diffs_fr = deep_diff(flat_json, raise_json)
    for p in diffs_fr[:200]:
        print(" ", p)
    if len(diffs_fr) > 200:
        print(f"  ... ({len(diffs_fr)-200} more)")

    print("\n=== DIFF PATHS (flat -> lower) ===")
    diffs_fl = deep_diff(flat_json, lower_json)
    for p in diffs_fl[:200]:
        print(" ", p)
    if len(diffs_fl) > 200:
        print(f"  ... ({len(diffs_fl)-200} more)")

    # Save a combined summary JSON (easy to share back here)
    summary_path = out_dir / "brush_tests_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "files": {k: str(v) for k, v in files.items()},
                "dumps": {k: str(v) for k, v in dumped.items()},
                "summaries": summaries,
                "diffs": {
                    "flat_to_raise": diffs_fr,
                    "flat_to_lower": diffs_fl,
                },
            },
            f,
            indent=2,
        )

    print(f"\nWrote combined summary to: {summary_path}")


if __name__ == "__main__":
    main()
