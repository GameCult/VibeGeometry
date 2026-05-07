use bevy_math::Vec3;
use vg_grammar::{ClaimTree, Frame, GalleryChainSpec, GrammarContext, Rule};

fn main() {
    let ctx = GrammarContext::new(7);
    let mut tree = ClaimTree::new();

    GalleryChainSpec::new("dream gallery", 4)
        .in_frame(Frame::new(
            Vec3::ZERO,
            bevy_math::Quat::from_rotation_z(0.2),
        ))
        .emit(&ctx, &mut tree);

    let compiled = tree.compile();
    let tree_compiled = tree.compile_csg_tree().expect("example emits claims");
    let output = compiled.assembler.build();

    println!(
        "claims={} solids={} voids={} brushes={} tree_nodes={} vertices={} triangles={} warnings={}",
        tree.claims().len(),
        compiled.solid_claims,
        compiled.void_claims,
        compiled.brush_ids.len(),
        tree_compiled.arena.nodes().len(),
        output.mesh.vertex_count(),
        output.mesh.triangle_count(),
        output.report.warnings.len()
    );
}
