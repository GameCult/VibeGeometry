use bevy_math::{Quat, Vec3};
use vg_csg::{
    Assembler, BrushId, CsgBranchOp, CsgNodeId, CsgOperationType, CsgTree, CsgTreeArena,
    CsgTreeBranch, MaterialId, Primitive,
};

use crate::Frame;

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct ClaimTag(pub String);

impl ClaimTag {
    pub fn new(value: impl Into<String>) -> Self {
        Self(value.into())
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ClaimKind {
    Solid,
    Void,
}

#[derive(Clone, Debug)]
pub struct Claim {
    pub name: String,
    pub kind: ClaimKind,
    pub center: Vec3,
    pub size: Vec3,
    pub rotation: Quat,
    pub material: MaterialId,
    pub tags: Vec<ClaimTag>,
}

impl Claim {
    pub fn solid_box(
        name: impl Into<String>,
        center: Vec3,
        size: Vec3,
        material: MaterialId,
    ) -> Self {
        Self {
            name: name.into(),
            kind: ClaimKind::Solid,
            center,
            size,
            rotation: Quat::IDENTITY,
            material,
            tags: Vec::new(),
        }
    }

    pub fn solid_oriented_box(
        name: impl Into<String>,
        center: Vec3,
        size: Vec3,
        rotation: Quat,
        material: MaterialId,
    ) -> Self {
        Self {
            name: name.into(),
            kind: ClaimKind::Solid,
            center,
            size,
            rotation,
            material,
            tags: Vec::new(),
        }
    }

    pub fn void_box(name: impl Into<String>, center: Vec3, size: Vec3) -> Self {
        Self {
            name: name.into(),
            kind: ClaimKind::Void,
            center,
            size,
            rotation: Quat::IDENTITY,
            material: MaterialId::default(),
            tags: Vec::new(),
        }
    }

    pub fn void_oriented_box(
        name: impl Into<String>,
        center: Vec3,
        size: Vec3,
        rotation: Quat,
    ) -> Self {
        Self {
            name: name.into(),
            kind: ClaimKind::Void,
            center,
            size,
            rotation,
            material: MaterialId::default(),
            tags: Vec::new(),
        }
    }

    pub fn tagged(mut self, tag: impl Into<String>) -> Self {
        self.tags.push(ClaimTag::new(tag));
        self
    }

    pub fn in_frame(mut self, frame: Frame) -> Self {
        self.center = frame.point(self.center);
        self.rotation = frame.rotation * self.rotation;
        self
    }

    pub fn is_axis_aligned(&self) -> bool {
        self.rotation.abs_diff_eq(Quat::IDENTITY, 1.0e-6)
    }
}

#[derive(Clone, Debug, Default)]
pub struct ClaimTree {
    claims: Vec<Claim>,
}

impl ClaimTree {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn push(&mut self, claim: Claim) {
        self.claims.push(claim);
    }

    pub fn extend(&mut self, claims: impl IntoIterator<Item = Claim>) {
        self.claims.extend(claims);
    }

    pub fn claims(&self) -> &[Claim] {
        &self.claims
    }

    pub fn count_kind(&self, kind: ClaimKind) -> usize {
        self.claims
            .iter()
            .filter(|claim| claim.kind == kind)
            .count()
    }

    pub fn compile(&self) -> CompileReport {
        let mut assembler = Assembler::new();
        let mut brush_ids = Vec::with_capacity(self.claims.len());
        for claim in &self.claims {
            let brush_id = match claim.kind {
                ClaimKind::Solid if claim.is_axis_aligned() => assembler.solid_box(
                    &claim.name,
                    vg_csg::Aabb::from_center_size(claim.center, claim.size),
                    claim.material,
                ),
                ClaimKind::Solid => assembler.solid_oriented_box(
                    &claim.name,
                    claim.center,
                    claim.size,
                    claim.rotation,
                    claim.material,
                ),
                ClaimKind::Void if claim.is_axis_aligned() => assembler.cut_box(
                    &claim.name,
                    vg_csg::Aabb::from_center_size(claim.center, claim.size),
                ),
                ClaimKind::Void => assembler.cut_oriented_box(
                    &claim.name,
                    claim.center,
                    claim.size,
                    claim.rotation,
                ),
            };
            brush_ids.push(brush_id);
        }

        CompileReport {
            assembler,
            brush_ids,
            solid_claims: self.count_kind(ClaimKind::Solid),
            void_claims: self.count_kind(ClaimKind::Void),
        }
    }

    pub fn compile_csg_tree(&self) -> Option<TreeCompileReport> {
        if self.claims.is_empty() {
            return None;
        }

        let mut arena = CsgTreeArena::new();
        let mut solid_nodes = Vec::new();
        let mut void_nodes = Vec::new();

        for claim in &self.claims {
            let primitive = claim.primitive();
            let brush = arena.generate_brush(
                &claim.name,
                CsgOperationType::Additive,
                primitive,
                claim.material,
            );

            match claim.kind {
                ClaimKind::Solid => solid_nodes.push(brush.node),
                ClaimKind::Void => void_nodes.push(brush.node),
            }
        }

        let solid_root = branch_or_single(&mut arena, "solids", CsgBranchOp::Addition, solid_nodes);
        let root = if void_nodes.is_empty() {
            solid_root
        } else {
            let void_root =
                branch_or_single(&mut arena, "voids", CsgBranchOp::Addition, void_nodes);
            arena
                .generate_branch(
                    "grammar result",
                    CsgBranchOp::Subtraction,
                    [solid_root, void_root],
                )
                .node
        };

        Some(TreeCompileReport {
            tree: arena.generate_tree(root),
            arena,
            solid_claims: self.count_kind(ClaimKind::Solid),
            void_claims: self.count_kind(ClaimKind::Void),
        })
    }
}

#[derive(Clone, Debug)]
pub struct CompileReport {
    pub assembler: Assembler,
    pub brush_ids: Vec<BrushId>,
    pub solid_claims: usize,
    pub void_claims: usize,
}

#[derive(Clone, Debug)]
pub struct TreeCompileReport {
    pub arena: CsgTreeArena,
    pub tree: CsgTree,
    pub solid_claims: usize,
    pub void_claims: usize,
}

impl TreeCompileReport {
    pub fn compile_to_assembler(&self) -> Assembler {
        self.arena.compile_tree_to_assembler(self.tree)
    }
}

fn branch_or_single(
    arena: &mut CsgTreeArena,
    name: &str,
    op: CsgBranchOp,
    nodes: Vec<CsgNodeId>,
) -> CsgNodeId {
    if nodes.len() == 1 {
        nodes[0]
    } else {
        CsgTreeBranch {
            node: arena.generate_branch(name, op, nodes).node,
        }
        .node
    }
}

impl Claim {
    fn primitive(&self) -> Primitive {
        if self.is_axis_aligned() {
            Primitive::Box {
                bounds: vg_csg::Aabb::from_center_size(self.center, self.size),
            }
        } else {
            Primitive::OrientedBox {
                center: self.center,
                size: self.size,
                rotation: self.rotation,
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use bevy_math::Vec3;

    use super::*;

    #[test]
    fn claim_tree_compiles_solids_and_voids_to_brushes() {
        let mut tree = ClaimTree::new();
        tree.push(Claim::solid_box(
            "wall",
            Vec3::ZERO,
            Vec3::new(4.0, 0.25, 3.0),
            MaterialId(1),
        ));
        tree.push(Claim::void_box(
            "door",
            Vec3::new(0.0, 0.0, -0.25),
            Vec3::new(1.0, 0.5, 1.5),
        ));

        let report = tree.compile();
        assert_eq!(report.solid_claims, 1);
        assert_eq!(report.void_claims, 1);
        assert_eq!(report.brush_ids.len(), 2);
        assert_eq!(report.assembler.brushes().len(), 2);
    }

    #[test]
    fn claim_tree_compiles_nested_csg_tree_intent() {
        let mut tree = ClaimTree::new();
        tree.push(Claim::solid_box(
            "wall",
            Vec3::ZERO,
            Vec3::new(4.0, 0.25, 3.0),
            MaterialId(1),
        ));
        tree.push(Claim::void_box(
            "door",
            Vec3::new(0.0, 0.0, -0.25),
            Vec3::new(1.0, 0.5, 1.5),
        ));

        let report = tree.compile_csg_tree().expect("non-empty tree");
        assert_eq!(report.solid_claims, 1);
        assert_eq!(report.void_claims, 1);
        assert_eq!(report.compile_to_assembler().brushes().len(), 2);
    }

    #[test]
    fn oriented_claims_compile_to_oriented_brushes() {
        let mut tree = ClaimTree::new();
        tree.push(Claim::solid_oriented_box(
            "angled wall",
            Vec3::ZERO,
            Vec3::new(4.0, 0.25, 3.0),
            Quat::from_rotation_z(0.25),
            MaterialId(1),
        ));
        tree.push(Claim::void_oriented_box(
            "angled door",
            Vec3::ZERO,
            Vec3::new(1.0, 0.5, 1.5),
            Quat::from_rotation_z(0.25),
        ));

        let report = tree.compile();
        assert_eq!(report.assembler.brushes().len(), 2);
    }
}
