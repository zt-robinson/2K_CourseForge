from pathlib import Path
import json
import sys

# Make repo imports work (same trick as your other scripts)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.course_file import CourseFile  # noqa: E402


def summarize_course(course_path: Path, out_dir: Path) -> dict:
    course = CourseFile.load(course_path)

    # Export full JSON (for deep inspection if needed)
    dump_path = out_dir / f"{course_path.stem}.json"
    course.export_json(dump_path)

    data = course.course_data

    # Quick stats about likely terrain containers
    height_len = len(data.get("height", [])) if isinstance(data.get("height", []), list) else None
    terrain_height_len = len(data.get("terrainHeight", [])) if isinstance(data.get("terrainHeight", []), list) else None

    all_map_edits = data.get("AllMapEdits", [])
    all_map_edits_summary = []
    if isinstance(all_map_edits, list):
        for i, entry in enumerate(all_map_edits):
            if isinstance(entry, dict):
                all_map_edits_summary.append({
                    "index": i,
                    "IsEmpty": entry.get("IsEmpty"),
                    "brushes_len": len(entry.get("brushes", [])) if isinstance(entry.get("brushes", []), list) else None,
                    "splines_len": len(entry.get("splines", [])) if isinstance(entry.get("splines", []), list) else None,
                })

    summary = {
        "file": str(course_path),
        "name": data.get("name"),
        "version": data.get("version"),
        "legacyTerrain": data.get("legacyTerrain"),
        "useV4Height": data.get("useV4Height"),
        "useV46HeightFieldDiscretization": data.get("useV46HeightFieldDiscretization"),
        "blurHeight": data.get("blurHeight"),
        "waterLevel": data.get("waterLevel"),
        "hillsAmount": data.get("hillsAmount"),
        "height_len": height_len,
        "terrainHeight_len": terrain_height_len,
        "surfaceBrushes2_len": len(data.get("surfaceBrushes2", [])) if isinstance(data.get("surfaceBrushes2", []), list) else None,
        "surfaceSplines2_len": len(data.get("surfaceSplines2", [])) if isinstance(data.get("surfaceSplines2", []), list) else None,
        "AllMapEdits_summary": all_map_edits_summary,
        "dump_json": str(dump_path),
    }
    return summary


def safe_read_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def deep_diff(a, b, path=""):
    """
    Minimal deep-diff that returns a list of changed "paths".
    Keeps it lightweight: only reports changed keys/indices, not huge values.
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
            # still try to compare overlap
        n = min(len(a), len(b))
        # only scan first chunk to avoid huge runtime on big arrays
        scan = min(n, 200)
        for i in range(scan):
            new_path = f"{path}[{i}]"
            changes.extend(deep_diff(a[i], b[i], new_path))
        if n > scan:
            changes.append(f"{path} (list truncated compare: first {scan} items)")
        return changes

    # primitives
    if a != b:
        changes.append(path or "<root>")
    return changes


def main():
    repo_root = Path(__file__).parent.parent
    samples = repo_root / "reference" / "samples"
    out_dir = repo_root / "output" / "inspect"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = {
    "min": samples / "terrain_min*.course",
    "max": samples / "terrain_max*.course",
    }

    # Resolve globs (you said filenames start with base_/terrain_/landscape_)
    resolved = {}
    for key, pattern in files.items():
        matches = sorted(samples.glob(pattern.name))
        if not matches:
            # fallback: just try prefix scan
            matches = sorted([p for p in samples.glob("*.course") if p.name.lower().startswith(f"terrain_{key}")])
        if not matches:
            raise FileNotFoundError(f"Could not find a .course file for '{key}' in {samples}")
        if len(matches) > 1:
            print(f"WARNING: multiple matches for {key}. Using first: {matches[0].name}")
        resolved[key] = matches[0]

    print("Using files:")
    for k, p in resolved.items():
        print(f"  {k}: {p.name}")

    # Summaries + dumps
    summaries = {}
    for k, p in resolved.items():
        summaries[k] = summarize_course(p, out_dir)

    # Print summaries
    print("\n=== SUMMARY ===")
    for k in ["min", "max"]:
        s = summaries[k]
        print(f"\n[{k}] {Path(s['file']).name}")
        print(f"  name: {s['name']}")
        print(f"  version: {s['version']}, legacyTerrain: {s['legacyTerrain']}")
        print(f"  height_len: {s['height_len']}, terrainHeight_len: {s['terrainHeight_len']}")
        print(f"  AllMapEdits: {[(e['IsEmpty'], e['brushes_len'], e['splines_len']) for e in s['AllMapEdits_summary']]}")
        print(f"  dump: {s['dump_json']}")

    # Load dumped JSONs for diffing
    min_json = safe_read_json(Path(summaries["min"]["dump_json"]))
    max_json = safe_read_json(Path(summaries["max"]["dump_json"]))

    print("\n=== DIFF PATHS (min -> max) ===")
    diffs = deep_diff(min_json, max_json)

    # Save a combined summary json
    summary_path = out_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2)
    print(f"\nWrote summary to: {summary_path}")


if __name__ == "__main__":
    main()
