"""Load the repo-local Geometry Script clone for Blender scripts."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GEOMETRY_SCRIPT_DIR = ROOT / "external" / "geometry-script"
GEOMETRY_SCRIPT_INIT = GEOMETRY_SCRIPT_DIR / "__init__.py"


def load_repo_geometry_script():
    """Import the repo-local Geometry Script clone as ``geometry_script``."""
    if not GEOMETRY_SCRIPT_INIT.exists():
        raise FileNotFoundError(
            f"Geometry Script clone not found: {GEOMETRY_SCRIPT_INIT}. "
            "Run tools/setup_geometry_script_clone.ps1 from the repo root."
        )

    existing = sys.modules.get("geometry_script")
    if existing is not None and getattr(existing, "__file__", None) == str(GEOMETRY_SCRIPT_INIT):
        return existing

    for name in list(sys.modules):
        if name == "geometry_script" or name.startswith("geometry_script."):
            del sys.modules[name]

    spec = importlib.util.spec_from_file_location(
        "geometry_script",
        GEOMETRY_SCRIPT_INIT,
        submodule_search_locations=[str(GEOMETRY_SCRIPT_DIR)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load Geometry Script from {GEOMETRY_SCRIPT_INIT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["geometry_script"] = module
    spec.loader.exec_module(module)
    return module
