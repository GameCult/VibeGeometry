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

The fork is intentionally kept small. As of 2026-05-04, its live branches are:

```text
main
vibegeometry/blender-5-nested-tree-groups
vibegeometry/blender-5-nodes-to-script
```

Upstream may still have historical branches such as `gh-pages` or
`nodes_to_script`; those are upstream history, not GameCult fork policy.

## Upstream `nodes_to_script` Branch

Upstream's historical `nodes_to_script` branch is real and potentially useful,
but should be treated as prototype material rather than a drop-in dependency.

Observed on 2026-05-04:

- Branch head: `b78ec37` (`Improve dot access handling`, 2023-03-01).
- Merge base with current `main`: `5fbc7d1`.
- Main has substantial later work not present on the branch, including Blender
  4 `NodeTree.interface` migration, nested tree checks, repeat-zone support,
  and Blender 3/4 compatibility fixes.
- The branch adds `operators/convert_tree.py` and registers a
  `geometry_script.convert_tree` node editor operator.

The operator walks the active node tree, creates one assignment per node, reads
enabled input defaults and node-specific properties, follows links into
arguments, topologically sorts from `Group Output`, then writes a generated
`@tree(...)` script into a Blender text datablock.

That makes it useful as a translation assistant or bootstrap oracle. It does
not replace manual doctrine-building yet: output quality, Blender 5.1
compatibility, interface sockets, zones, nested groups, multi-input sockets,
and current Geometry Script API drift all need testing before VibeGeometry
leans on it.

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
current VibeGeometry toolchain branch, and applies the patches stored in:

```text
patches/geometry-script/0001-fix-nested-tree-group-references-on-blender-4.patch
patches/geometry-script/0002-Port-node-tree-conversion-operator.patch
```

`external/` is intentionally ignored by the VibeGeometry repository. The clone
is source-controlled as its own repo, not smuggled into this repo as a pile of
vendor files.

## Toolchain Branch

Branch:

```text
vibegeometry/blender-5-nodes-to-script
```

This is the branch VibeGeometry should use locally. It contains:

- the nested `@tree` group fix from
  `vibegeometry/blender-5-nested-tree-groups`
- a Blender 5.1 port of the historical `nodes_to_script` converter prototype

The converter adds:

- `operators/convert_tree.py`
- a callable `convert_node_tree(tree)` function for headless tests
- a `geometry_script.convert_tree` node editor operator that writes a generated
  script into a Blender text datablock

Smoke test:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\source-blends\shriinivas-fieldvalue.blend' --python '.\tools\smoke_nodes_to_script_converter.py' -- --groups 'Create Decimal' 'Digit At' 'Next Digit' 'Seven Segments' 'Delete Segments' 'Field Value' --json '.\experiments\inspection\nodes-to-script-smoke.json' --out-dir '.\experiments\inspection\nodes-to-script-output'
```

Current acceptance:

- Converter runs in Blender 5.1.1.
- Generated drafts compile as Python for the tested groups.
- The full 176-node `Field Value` source group emits a 179-line draft script.
- Generated text is a bootstrap draft, not doctrine-quality final code or style
  guidance.

Known limits:

- Nested source group calls are emitted by source group name, so dependency
  groups must be converted or replaced by hand-authored equivalents.
- The generated script preserves node-level wiring and therefore can be noisy.
- Generated names and ordering reflect extraction mechanics, not spatial intent.
- Behavioral equivalence still needs the same evaluated-geometry or scalar
  harness verification used by the hand translations.

## Upstream PR Branch

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
- Keep PR #69 limited to the nested `@tree` fix. Converter work belongs on
  `vibegeometry/blender-5-nodes-to-script` unless it is intentionally prepared
  as a separate upstream PR.
