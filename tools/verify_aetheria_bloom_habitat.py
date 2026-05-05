"""Verify the generated Aetheria Bloom habitat study scene."""

from __future__ import annotations

from pathlib import Path
import sys

import bpy


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from vibegeometry import assert_objects_exist, assert_render_artifacts, assert_scene_density

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
    "hubward_endcap_pressure_face",
    "capward_endcap_pressure_face",
    "hubward_endcap_terrace_ring_00",
    "capward_endcap_terrace_ring_00",
    "hubward_docking_hub_office_complex_ring_office_mesh",
    "hubward_docking_hub_office_complex_office_spoke_bridge_00",
    "hubward_endcap_rice_paddy_slums_annular_shelf_mesh",
    "hubward_endcap_rice_paddy_slums_rickety_shack_mesh",
    "hubward_endcap_rice_paddy_slums_midrise_housing_mesh",
    "hubward_endcap_rice_paddy_slums_surface_urban_crown_mesh",
    "hubward_endcap_rice_paddy_slums_patched_roof_mesh",
    "hubward_endcap_rice_paddy_slums_ladders_nets_handlines",
    "capward_endcap_beach_service_00_00",
    "spiral_cargo_spoke_00",
    "spiral_passenger_spoke_01",
    "spiral_atmospheric_utility_rib_00",
    "spun_to_despun_transfer_loop_00",
    "spiral_spoke_shell_collar_00",
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
    "hubward_low_g_transition_band",
    "hyperurban_favela_city_belt",
    "prestige_urban_luxury_spoke_belt",
    "urban_mixed_suburban_industrial_belt",
    "industrial_agricultural_belt",
    "beach_resort_rim",
    "cylindrical_sea_after_beach",
    "wrapped_road_graph_0",
    "wrapped_river_0",
    "airflow_cloud_patch_0",
    "hubward_spoke_access_market_stack_00_00",
    "hyperurban_nested_town_nested_house_mesh",
    "hyperurban_nested_town_lane_network",
    "luxury_spoke_plaza_-5.0_-3.14",
    "luxury_spoke_plaza_detail_-5.0_00_plaza_ring",
    "luxury_spoke_plaza_detail_-5.0_00_kiosk_00",
    "luxury_spoke_plaza_detail_-5.0_00_feeder_walk_00",
    "mixed_belt_nested_town_nested_house_mesh",
    "factory_yard_block_00_00",
    "axial_surface_service_lane_00",
    "circumferential_market_seam_00",
    "Camera_Bloom_Cutaway",
    "Camera_Interior_World",
    "Camera_Hubward_Endcap_Terraces",
}


def assert_true(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def verify_scene():
    assert_objects_exist(bpy, REQUIRED_OBJECTS)

    group = bpy.data.node_groups.get("VG Bloom Light Spine")
    assert_true(group is not None, "Missing Geometry Script node group VG Bloom Light Spine")
    assert_true(len(group.nodes) >= 20, f"Unexpectedly small light-spine graph: {len(group.nodes)} nodes")
    assert_true(len(group.links) >= 25, f"Unexpectedly sparse light-spine graph: {len(group.links)} links")

    carrier = bpy.data.objects["GN_Light_Spine_Modifier_Carrier"]
    assert_true(any(mod.type == "NODES" and mod.node_group == group for mod in carrier.modifiers), "Light-spine carrier lacks expected geometry-nodes modifier")

    assert_render_artifacts(
        ARTIFACT_DIR / filename
        for filename in (
            "aetheria_bloom_habitat.png",
            "aetheria_bloom_interior_world.png",
            "aetheria_bloom_hubward_endcap_terraces.png",
            "aetheria_bloom_habitat.blend",
        )
    )

    mesh_objects = assert_scene_density(bpy, 930)

    slum_mesh = bpy.data.objects["hubward_endcap_rice_paddy_slums_rickety_shack_mesh"].data
    mid_mesh = bpy.data.objects["hubward_endcap_rice_paddy_slums_midrise_housing_mesh"].data
    crown_mesh = bpy.data.objects["hubward_endcap_rice_paddy_slums_surface_urban_crown_mesh"].data
    assert_true(len(slum_mesh.polygons) >= 1200, f"Endcap slum mesh is too sparse: {len(slum_mesh.polygons)} faces")
    assert_true(len(mid_mesh.polygons) >= 600, f"Endcap midrise mesh is too sparse: {len(mid_mesh.polygons)} faces")
    assert_true(len(crown_mesh.polygons) >= 250, f"Endcap urban crown mesh is too sparse: {len(crown_mesh.polygons)} faces")

    print("AETHERIA_BLOOM_VERIFY ok")
    print("AETHERIA_BLOOM_VERIFY group", group.name, len(group.nodes), len(group.links))
    print("AETHERIA_BLOOM_VERIFY objects", len(mesh_objects))


if __name__ == "__main__":
    verify_scene()
