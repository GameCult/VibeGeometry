use bevy_math::Vec3;
use vg_csg::{Assembler, BrushId, MaterialId};

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
            material: MaterialId::default(),
            tags: Vec::new(),
        }
    }

    pub fn tagged(mut self, tag: impl Into<String>) -> Self {
        self.tags.push(ClaimTag::new(tag));
        self
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
                ClaimKind::Solid => assembler.solid_box(
                    &claim.name,
                    vg_csg::Aabb::from_center_size(claim.center, claim.size),
                    claim.material,
                ),
                ClaimKind::Void => assembler.cut_box(
                    &claim.name,
                    vg_csg::Aabb::from_center_size(claim.center, claim.size),
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
}

#[derive(Clone, Debug)]
pub struct CompileReport {
    pub assembler: Assembler,
    pub brush_ids: Vec<BrushId>,
    pub solid_claims: usize,
    pub void_claims: usize,
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
}
