"""Verify the generated Aetheria Bloom habitat study scene."""

from __future__ import annotations

from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "experiments" / "generated" / "aetheria_bloom"


REQUIRED_OBJECTS = {
    "01_open_civic_inner_surface_full_bloom",
    "02_utility_mat_service_interlayer_full_bloom",
    "03_pressure_structural_shell_full_bloom",
    "04_outer_aggregate_shielding_full_bloom",
    "despun_center_axis_core",
    "despun_hub_cap_docking_axis",
    "docking_port_on_despun_hub_cap",
    "spun_spire_sheath_outer_frame",
    "traffic_light_spire_core",
    "GN_Light_Spine_Modifier_Carrier",
    "major_rotating_spoke_00_00",
    "thin_utility_spoke_00_-150",
    "frame_transfer_artery_00_00",
    "spoke_base_transfer_collar_00_00",
    "service_ring_kappa_human_gallery",
    "kappa_operations_gallery_badge_route",
    "octopoid_support_rig_prep_station",
    "kappa_crawl_throat_1",
    "kappa_crawl_throat_2",
    "kappa_crawl_throat_3",
    "kappa_seal_lung_1",
    "kappa_air_return_to_filters",
    "kappa_coolant_heat_exchanger",
    "kappa_condensate_drain",
    "hubcap_terrace_slum_band",
    "hyperurban_favela_city_belt",
    "prestige_urban_luxury_spoke_belt",
    "urban_mixed_suburban_industrial_belt",
    "industrial_agricultural_belt",
    "beach_resort_rim",
    "cylindrical_sea_after_beach",
    "wrapped_road_graph_0",
    "wrapped_river_0",
    "airflow_cloud_patch_0",
    "layered_hubcap_slum_stack_00_00",
    "luxury_spoke_plaza_-5.0_-2.09",
    "factory_yard_block_00_00",
    "Camera_Bloom_Cutaway",
    "Camera_Interior_World",
}


def assert_true(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def verify_scene():
    missing = sorted(name for name in REQUIRED_OBJECTS if name not in bpy.data.objects)
    assert_true(not missing, f"Missing required objects: {missing}")

    group = bpy.data.node_groups.get("VG Bloom Light Spine")
    assert_true(group is not None, "Missing Geometry Script node group VG Bloom Light Spine")
    assert_true(len(group.nodes) >= 20, f"Unexpectedly small light-spine graph: {len(group.nodes)} nodes")
    assert_true(len(group.links) >= 25, f"Unexpectedly sparse light-spine graph: {len(group.links)} links")

    carrier = bpy.data.objects["GN_Light_Spine_Modifier_Carrier"]
    assert_true(any(mod.type == "NODES" and mod.node_group == group for mod in carrier.modifiers), "Light-spine carrier lacks expected geometry-nodes modifier")

    for filename in ("aetheria_bloom_habitat.png", "aetheria_bloom_interior_world.png", "aetheria_bloom_habitat.blend"):
        path = ARTIFACT_DIR / filename
        assert_true(path.exists(), f"Missing generated artifact {path}")
        assert_true(path.stat().st_size > 10_000, f"Generated artifact is suspiciously small: {path}")

    mesh_objects = [obj for obj in bpy.data.objects if obj.type in {"MESH", "CURVE", "FONT"}]
    assert_true(len(mesh_objects) >= 250, f"Expected a populated whole-Bloom study scene, found {len(mesh_objects)} geometry/text objects")

    print("AETHERIA_BLOOM_VERIFY ok")
    print("AETHERIA_BLOOM_VERIFY group", group.name, len(group.nodes), len(group.links))
    print("AETHERIA_BLOOM_VERIFY objects", len(mesh_objects))


if __name__ == "__main__":
    verify_scene()
