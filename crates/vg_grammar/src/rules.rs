use bevy_math::Vec3;

use crate::{Claim, ClaimTree, GrammarContext};

pub trait Rule {
    fn emit(&self, ctx: &GrammarContext, tree: &mut ClaimTree);
}

#[derive(Clone, Debug)]
pub struct RoomSpec {
    pub name: String,
    pub center: Vec3,
    pub size: Vec3,
    pub wall_thickness: f32,
}

impl RoomSpec {
    pub fn new(name: impl Into<String>, center: Vec3, size: Vec3) -> Self {
        Self {
            name: name.into(),
            center,
            size,
            wall_thickness: 0.25,
        }
    }
}

impl Rule for RoomSpec {
    fn emit(&self, ctx: &GrammarContext, tree: &mut ClaimTree) {
        let half = self.size * 0.5;
        let t = self.wall_thickness;
        let wall_height = self.size.z;
        let wall_z = self.center.z + wall_height * 0.5;

        tree.push(
            Claim::solid_box(
                format!("{} floor", self.name),
                self.center + Vec3::new(0.0, 0.0, -t * 0.5),
                Vec3::new(self.size.x, self.size.y, t),
                ctx.materials.floor,
            )
            .tagged("room")
            .tagged("floor"),
        );
        tree.push(
            Claim::solid_box(
                format!("{} ceiling", self.name),
                self.center + Vec3::new(0.0, 0.0, wall_height + t * 0.5),
                Vec3::new(self.size.x, self.size.y, t),
                ctx.materials.ceiling,
            )
            .tagged("room")
            .tagged("ceiling"),
        );
        tree.push(
            Claim::solid_box(
                format!("{} north wall", self.name),
                Vec3::new(self.center.x, self.center.y + half.y, wall_z),
                Vec3::new(self.size.x, t, wall_height),
                ctx.materials.wall,
            )
            .tagged("room")
            .tagged("wall"),
        );
        tree.push(
            Claim::solid_box(
                format!("{} south wall", self.name),
                Vec3::new(self.center.x, self.center.y - half.y, wall_z),
                Vec3::new(self.size.x, t, wall_height),
                ctx.materials.wall,
            )
            .tagged("room")
            .tagged("wall"),
        );
        tree.push(
            Claim::solid_box(
                format!("{} east wall", self.name),
                Vec3::new(self.center.x + half.x, self.center.y, wall_z),
                Vec3::new(t, self.size.y, wall_height),
                ctx.materials.wall,
            )
            .tagged("room")
            .tagged("wall"),
        );
        tree.push(
            Claim::solid_box(
                format!("{} west wall", self.name),
                Vec3::new(self.center.x - half.x, self.center.y, wall_z),
                Vec3::new(t, self.size.y, wall_height),
                ctx.materials.wall,
            )
            .tagged("room")
            .tagged("wall"),
        );
    }
}

#[derive(Clone, Debug)]
pub struct CorridorSpec {
    pub name: String,
    pub center: Vec3,
    pub length: f32,
    pub width: f32,
    pub height: f32,
    pub wall_thickness: f32,
}

impl CorridorSpec {
    pub fn along_x(name: impl Into<String>, center: Vec3, length: f32) -> Self {
        Self {
            name: name.into(),
            center,
            length,
            width: 2.0,
            height: 2.6,
            wall_thickness: 0.2,
        }
    }
}

impl Rule for CorridorSpec {
    fn emit(&self, ctx: &GrammarContext, tree: &mut ClaimTree) {
        let t = self.wall_thickness;
        let z = self.center.z + self.height * 0.5;
        tree.push(
            Claim::solid_box(
                format!("{} floor", self.name),
                self.center + Vec3::new(0.0, 0.0, -t * 0.5),
                Vec3::new(self.length, self.width, t),
                ctx.materials.floor,
            )
            .tagged("corridor")
            .tagged("floor"),
        );
        tree.push(
            Claim::solid_box(
                format!("{} left wall", self.name),
                Vec3::new(self.center.x, self.center.y + self.width * 0.5, z),
                Vec3::new(self.length, t, self.height),
                ctx.materials.wall,
            )
            .tagged("corridor")
            .tagged("wall"),
        );
        tree.push(
            Claim::solid_box(
                format!("{} right wall", self.name),
                Vec3::new(self.center.x, self.center.y - self.width * 0.5, z),
                Vec3::new(self.length, t, self.height),
                ctx.materials.wall,
            )
            .tagged("corridor")
            .tagged("wall"),
        );
        tree.push(
            Claim::solid_box(
                format!("{} ceiling", self.name),
                self.center + Vec3::new(0.0, 0.0, self.height + t * 0.5),
                Vec3::new(self.length, self.width, t),
                ctx.materials.ceiling,
            )
            .tagged("corridor")
            .tagged("ceiling"),
        );
    }
}

#[derive(Clone, Debug)]
pub struct DoorSpec {
    pub name: String,
    pub center: Vec3,
    pub size: Vec3,
}

impl DoorSpec {
    pub fn new(name: impl Into<String>, center: Vec3, size: Vec3) -> Self {
        Self {
            name: name.into(),
            center,
            size,
        }
    }
}

impl Rule for DoorSpec {
    fn emit(&self, _ctx: &GrammarContext, tree: &mut ClaimTree) {
        tree.push(
            Claim::void_box(&self.name, self.center, self.size)
                .tagged("door")
                .tagged("void"),
        );
    }
}

#[cfg(test)]
mod tests {
    use vg_csg::Aabb;

    use super::*;
    use crate::ClaimKind;

    #[test]
    fn room_corridor_door_grammar_emits_semantic_claims_and_mesh() {
        let ctx = GrammarContext::new(42);
        let mut tree = ClaimTree::new();
        RoomSpec::new("gallery", Vec3::ZERO, Vec3::new(6.0, 5.0, 3.0)).emit(&ctx, &mut tree);
        CorridorSpec::along_x("artery", Vec3::new(5.0, 0.0, 0.0), 5.0).emit(&ctx, &mut tree);
        DoorSpec::new(
            "gallery east doorway",
            Vec3::new(3.0, 0.0, 1.1),
            Vec3::new(0.7, 1.4, 2.2),
        )
        .emit(&ctx, &mut tree);

        assert_eq!(tree.count_kind(ClaimKind::Solid), 10);
        assert_eq!(tree.count_kind(ClaimKind::Void), 1);
        assert!(
            tree.claims()
                .iter()
                .any(|claim| claim.tags.iter().any(|tag| tag.0 == "door"))
        );

        let report = tree.compile();
        let output = report.assembler.build();
        let door_void = Aabb::from_center_size(Vec3::new(3.0, 0.0, 1.1), Vec3::new(0.7, 1.4, 2.2));

        assert!(output.mesh.triangle_count() > 60);
        assert!(output.report.warnings.is_empty());
        for tri in output.mesh.indices.chunks_exact(3) {
            let center = (output.mesh.positions[tri[0] as usize]
                + output.mesh.positions[tri[1] as usize]
                + output.mesh.positions[tri[2] as usize])
                / 3.0;
            assert!(!door_void.contains_point_strict(center, 1.0e-4));
        }
    }
}
