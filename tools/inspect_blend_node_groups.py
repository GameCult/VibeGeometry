"""Inspect Geometry Nodes node groups in the currently opened Blender file.

Run with Blender:

    blender --background source.blend --python tools/inspect_blend_node_groups.py -- --json out.json
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import bpy


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "to_tuple"):
        return list(value.to_tuple())
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return repr(value)


def _socket_summary(socket: Any) -> dict[str, Any]:
    summary = {
        "name": getattr(socket, "name", ""),
        "identifier": getattr(socket, "identifier", ""),
        "type": getattr(socket, "type", ""),
        "bl_socket_idname": getattr(socket, "bl_socket_idname", ""),
        "enabled": getattr(socket, "enabled", None),
        "is_linked": getattr(socket, "is_linked", None),
        "is_multi_input": getattr(socket, "is_multi_input", None),
    }
    if hasattr(socket, "default_value"):
        try:
            summary["default_value"] = _jsonable(socket.default_value)
        except Exception as exc:  # pragma: no cover - Blender API guardrail
            summary["default_value_error"] = str(exc)
    return summary


def _interface_item_summary(item: Any) -> dict[str, Any]:
    summary = {
        "name": getattr(item, "name", ""),
        "item_type": getattr(item, "item_type", ""),
        "in_out": getattr(item, "in_out", ""),
        "socket_type": getattr(item, "socket_type", ""),
        "identifier": getattr(item, "identifier", ""),
        "description": getattr(item, "description", ""),
    }
    for attr in ("default_value", "min_value", "max_value", "hide_value", "hide_in_modifier"):
        if hasattr(item, attr):
            try:
                summary[attr] = _jsonable(getattr(item, attr))
            except Exception as exc:  # pragma: no cover - Blender API guardrail
                summary[f"{attr}_error"] = str(exc)
    return summary


def _node_summary(node: Any) -> dict[str, Any]:
    ignored_props = {
        "rna_type",
        "name",
        "label",
        "location",
        "width",
        "height",
        "dimensions",
        "inputs",
        "outputs",
        "internal_links",
        "parent",
        "select",
        "show_options",
        "show_preview",
        "show_texture",
        "hide",
        "mute",
        "use_custom_color",
        "warning_propagation",
    }
    properties: dict[str, Any] = {}
    for prop in node.bl_rna.properties:
        if prop.identifier in ignored_props or prop.is_readonly:
            continue
        if prop.identifier.startswith("bl_"):
            continue
        try:
            value = getattr(node, prop.identifier)
        except Exception:
            continue
        if value is None or isinstance(value, (str, int, float, bool)):
            properties[prop.identifier] = value
    summary = {
        "name": node.name,
        "label": node.label,
        "bl_idname": node.bl_idname,
        "type": node.type,
        "properties": properties,
        "location": _jsonable(node.location),
        "inputs": [_socket_summary(socket) for socket in node.inputs],
        "outputs": [_socket_summary(socket) for socket in node.outputs],
    }
    node_tree = getattr(node, "node_tree", None)
    if node_tree is not None:
        summary["node_tree"] = getattr(node_tree, "name", "")
    return summary


def _link_summary(link: Any) -> dict[str, str]:
    return {
        "from_node": link.from_node.name,
        "from_socket": link.from_socket.name,
        "from_socket_identifier": getattr(link.from_socket, "identifier", ""),
        "to_node": link.to_node.name,
        "to_socket": link.to_socket.name,
        "to_socket_identifier": getattr(link.to_socket, "identifier", ""),
    }


def _modifier_users() -> list[dict[str, str]]:
    users: list[dict[str, str]] = []
    for obj in bpy.data.objects:
        for modifier in obj.modifiers:
            if modifier.type == "NODES" and getattr(modifier, "node_group", None):
                users.append(
                    {
                        "object": obj.name,
                        "modifier": modifier.name,
                        "node_group": modifier.node_group.name,
                    }
                )
    return users


def inspect_file() -> dict[str, Any]:
    node_groups = []
    for group in bpy.data.node_groups:
        if group.bl_idname != "GeometryNodeTree":
            continue
        interface_items = []
        if hasattr(group, "interface") and hasattr(group.interface, "items_tree"):
            interface_items = [_interface_item_summary(item) for item in group.interface.items_tree]
        node_groups.append(
            {
                "name": group.name,
                "bl_idname": group.bl_idname,
                "is_modifier": getattr(group, "is_modifier", None),
                "is_tool": getattr(group, "is_tool", None),
                "interface": interface_items,
                "node_count": len(group.nodes),
                "link_count": len(group.links),
                "nodes": [_node_summary(node) for node in group.nodes],
                "links": [_link_summary(link) for link in group.links],
            }
        )
    return {
        "blend_file": bpy.data.filepath,
        "blender_version": bpy.app.version_string,
        "node_groups": sorted(node_groups, key=lambda item: item["name"].lower()),
        "modifier_users": _modifier_users(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True, help="Path for the inspection JSON output.")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])

    data = inspect_file()
    with open(args.json, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
    print(f"Inspected {len(data['node_groups'])} geometry node groups -> {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
