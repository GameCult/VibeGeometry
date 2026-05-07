use bevy_math::Vec3;
use vg_grammar::{ClaimTree, CorridorSpec, DoorSpec, GrammarContext, RoomSpec, Rule};

fn main() {
    let ctx = GrammarContext::new(7);
    let mut tree = ClaimTree::new();

    RoomSpec::new("dream gallery", Vec3::ZERO, Vec3::new(6.0, 5.0, 3.0)).emit(&ctx, &mut tree);
    CorridorSpec::along_x("east artery", Vec3::new(5.0, 0.0, 0.0), 5.0).emit(&ctx, &mut tree);
    DoorSpec::new(
        "gallery to artery",
        Vec3::new(3.0, 0.0, 1.1),
        Vec3::new(0.7, 1.4, 2.2),
    )
    .emit(&ctx, &mut tree);

    let compiled = tree.compile();
    let output = compiled.assembler.build();

    println!(
        "claims={} solids={} voids={} brushes={} vertices={} triangles={} warnings={}",
        tree.claims().len(),
        compiled.solid_claims,
        compiled.void_claims,
        compiled.brush_ids.len(),
        output.mesh.vertex_count(),
        output.mesh.triangle_count(),
        output.report.warnings.len()
    );
}
