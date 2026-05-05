"""Verify the Lucent tether habitat study scene."""

from pathlib import Path

import bpy

try:
    from vibegeometry import assert_objects_exist, assert_render_artifacts, assert_scene_density
except ModuleNotFoundError:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from vibegeometry import assert_objects_exist, assert_render_artifacts, assert_scene_density


OUT_DIR = Path("experiments/generated/lucent_tether_habitat")


REQUIRED_OBJECTS = [
    "lucent_tether_main_cable",
    "lucent_tether_spin_reference_core",
    "city_bubble_sealed_aquarium",
    "city_bubble_miniature_skyscraper_mesh",
    "city_bubble_attention_lit_tower_mesh",
    "media_eye_transfer_lounge_glass_shell",
    "media_eye_public_camera_eye",
    "transfer_lounge_curved_floor_slab",
    "elevator_gate_threshold",
    "waist_high_glass_rail",
    "safe_line_white_arc",
    "moderation_overlay_wall_public_status",
    "feed_ops_prompt_panels",
    "sponsor_risk_color_stack",
    "audience_heat_meter",
    "mara_private_control_rail",
    "pippa_delayed_side_panel",
    "brant_delayed_side_panel",
    "security_lounge_doors",
    "GN_Lucent_Feed_Ribbon_Carrier",
    "Camera_Lucent_Tether_Overview",
    "Camera_Media_Eye_Lounge",
    "Camera_City_Bubble_Aquarium",
]


def verify_geometry_script_group():
    group = bpy.data.node_groups.get("VG Lucent Feed Ribbon")
    if group is None:
        raise AssertionError("Missing Geometry Script group: VG Lucent Feed Ribbon")
    if len(group.nodes) < 18 or len(group.links) < 25:
        raise AssertionError(f"VG Lucent Feed Ribbon looks underbuilt: {len(group.nodes)} nodes, {len(group.links)} links")
    carrier = bpy.data.objects["GN_Lucent_Feed_Ribbon_Carrier"]
    modifiers = [modifier for modifier in carrier.modifiers if modifier.type == "NODES" and modifier.node_group == group]
    if not modifiers:
        raise AssertionError("Feed ribbon carrier lacks the VG Lucent Feed Ribbon nodes modifier")


def verify_artifacts():
    assert_render_artifacts(
        [
            OUT_DIR / "lucent_tether_habitat.blend",
            OUT_DIR / "lucent_tether_overview.png",
            OUT_DIR / "lucent_media_eye_lounge.png",
            OUT_DIR / "lucent_city_bubble_aquarium.png",
        ],
        min_size=10_000,
    )


def main():
    assert_objects_exist(bpy, REQUIRED_OBJECTS)
    geometry_objects = assert_scene_density(bpy, min_geometry_objects=55)
    verify_geometry_script_group()
    verify_artifacts()
    print(f"LUCENT_TETHER_VERIFY ok objects={len(geometry_objects)}")


if __name__ == "__main__":
    main()
