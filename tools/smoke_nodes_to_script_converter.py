"""Smoke-test Geometry Script's node-tree-to-script converter in Blender."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GEOMETRY_SCRIPT = ROOT / "external" / "geometry-script"


def _load_converter():
    sys.path.insert(0, str(ROOT))
    from tools.geometry_script_loader import load_repo_geometry_script

    load_repo_geometry_script()
    from geometry_script.operators.convert_tree import convert_node_tree

    return convert_node_tree


def main() -> int:
    import bpy

    parser = argparse.ArgumentParser()
    parser.add_argument("--groups", nargs="+", required=True)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])

    convert_node_tree = _load_converter()
    results = []
    ok = True
    for name in args.groups:
        tree = bpy.data.node_groups[name]
        try:
            script = convert_node_tree(tree)
            compile(script, f"<nodes_to_script:{name}>", "exec")
            output_path = None
            if args.out_dir:
                args.out_dir.mkdir(parents=True, exist_ok=True)
                output_path = args.out_dir / f"{name.replace(' ', '_').lower()}.py"
                output_path.write_text(script, encoding="utf-8")
            result = {
                "group": name,
                "ok": True,
                "script_length": len(script),
                "line_count": len(script.splitlines()),
                "header": script.splitlines()[:8],
                "output_path": str(output_path) if output_path else None,
            }
        except Exception as exc:
            ok = False
            result = {
                "group": name,
                "ok": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        results.append(result)

    payload = {"ok": ok, "results": results}
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print("VG_NODES_TO_SCRIPT_SMOKE " + json.dumps(payload, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
