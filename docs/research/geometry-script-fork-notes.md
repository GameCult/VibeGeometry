# Geometry Script Fork Notes

VibeGeometry uses a repo-local Geometry Script clone at:

```text
external/geometry-script
```

The clone currently tracks upstream:

```text
https://github.com/carson-katri/geometry-script.git
```

The GameCult fork remote is:

```text
https://github.com/GameCult/geometry-script.git
```

Patch work belongs in this clone first, then in a fork branch/PR. Do not patch
the installed AppData add-on directly. That path is live installation state, not
source control, and it will quietly become a stupid little archaeological layer
if indulged.

## Setup

Run from the VibeGeometry repo root:

```powershell
.\tools\setup_geometry_script_clone.ps1
```

This clones upstream into `external/geometry-script`, creates or switches to the
patch branch, and applies the patch stored in:

```text
patches/geometry-script/0001-fix-nested-tree-group-references-on-blender-4.patch
```

`external/` is intentionally ignored by the VibeGeometry repository. The clone
is source-controlled as its own repo, not smuggled into this repo as a pile of
vendor files.

## Active Patch Branch

Branch:

```text
vibegeometry/blender-5-nested-tree-groups
```

Problem:

- Geometry Script's `@tree` decorator returns a Python function intended to
  create a nested node-group node when called inside another `@tree`.
- Under Blender 5.1, that returned function tries to call
  `geometrynodegroup(...)`, but no such generated DSL symbol exists.
- Manually calling the generated `group(node_tree=...)` wrapper returned
  `None` in the nested path, so callers could not access group outputs.

Patch:

- In Blender 4/5, create `GeometryNodeGroup` directly.
- Assign `result.node_tree = node_group`.
- Wire positional and keyword arguments into enabled group inputs with
  Geometry Script's existing `set_or_create_link(...)` helper.
- Return `Type(...)` wrappers for each enabled group output.

Verification:

- `examples/geometry_script/shriinivas_cartesian_helper.py` loads
  `external/geometry-script` through `tools/geometry_script_loader.py`.
- `VG Cartesian Circle` calls `vg_cartesian_helper(...)` twice inside its own
  `@tree` body.
- Generated circle graph contains nested `GeometryNodeGroup` nodes.
- `tools/verify_cartesian_translations.py` verifies helper, line, parabola, and
  circle behavior against the source `cartesian.blend` groups in Blender 5.1.1.

## Fork/PR Todo

- Upstream PR: https://github.com/carson-katri/geometry-script/pull/69
- Keep `external/geometry-script` on
  `vibegeometry/blender-5-nested-tree-groups` until that PR is merged or a
  better maintained fork replaces it.
