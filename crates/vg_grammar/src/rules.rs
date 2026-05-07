use bevy_math::Vec3;

use crate::{Claim, ClaimTree, Frame, GrammarContext};

pub trait Rule {
    fn emit(&self, ctx: &GrammarContext, tree: &mut ClaimTree);
}

#[derive(Clone, Debug, Default)]
pub struct RuleSet {
    rules: Vec<RuleNode>,
}

impl RuleSet {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn with(mut self, rule: impl Into<RuleNode>) -> Self {
        self.rules.push(rule.into());
        self
    }
}

impl Rule for RuleSet {
    fn emit(&self, ctx: &GrammarContext, tree: &mut ClaimTree) {
        for rule in &self.rules {
            rule.emit(ctx, tree);
        }
    }
}

#[derive(Clone, Debug)]
pub enum RuleNode {
    Room(RoomSpec),
    Corridor(CorridorSpec),
    Door(DoorSpec),
    GalleryChain(GalleryChainSpec),
}

impl Rule for RuleNode {
    fn emit(&self, ctx: &GrammarContext, tree: &mut ClaimTree) {
        match self {
            Self::Room(rule) => rule.emit(ctx, tree),
            Self::Corridor(rule) => rule.emit(ctx, tree),
            Self::Door(rule) => rule.emit(ctx, tree),
            Self::GalleryChain(rule) => rule.emit(ctx, tree),
        }
    }
}

impl From<RoomSpec> for RuleNode {
    fn from(value: RoomSpec) -> Self {
        Self::Room(value)
    }
}

impl From<CorridorSpec> for RuleNode {
    fn from(value: CorridorSpec) -> Self {
        Self::Corridor(value)
    }
}

impl From<DoorSpec> for RuleNode {
    fn from(value: DoorSpec) -> Self {
        Self::Door(value)
    }
}

impl From<GalleryChainSpec> for RuleNode {
    fn from(value: GalleryChainSpec) -> Self {
        Self::GalleryChain(value)
    }
}

#[derive(Clone, Debug)]
pub struct RoomSpec {
    pub name: String,
    pub center: Vec3,
    pub size: Vec3,
    pub frame: Frame,
    pub wall_thickness: f32,
}

impl RoomSpec {
    pub fn new(name: impl Into<String>, center: Vec3, size: Vec3) -> Self {
        Self {
            name: name.into(),
            center,
            size,
            frame: Frame::IDENTITY,
            wall_thickness: 0.25,
        }
    }

    pub fn in_frame(mut self, frame: Frame) -> Self {
        self.frame = frame;
        self
    }
}

impl Rule for RoomSpec {
    fn emit(&self, ctx: &GrammarContext, tree: &mut ClaimTree) {
        let half = self.size * 0.5;
        let t = self.wall_thickness;
        let wall_height = self.size.z;
        let wall_z = self.center.z + wall_height * 0.5;
        let frame = self.frame;

        tree.push(
            Claim::solid_box(
                format!("{} floor", self.name),
                self.center + Vec3::new(0.0, 0.0, -t * 0.5),
                Vec3::new(self.size.x, self.size.y, t),
                ctx.materials.floor,
            )
            .in_frame(frame)
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
            .in_frame(frame)
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
            .in_frame(frame)
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
            .in_frame(frame)
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
            .in_frame(frame)
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
            .in_frame(frame)
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
    pub frame: Frame,
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
            frame: Frame::IDENTITY,
            wall_thickness: 0.2,
        }
    }

    pub fn in_frame(mut self, frame: Frame) -> Self {
        self.frame = frame;
        self
    }
}

impl Rule for CorridorSpec {
    fn emit(&self, ctx: &GrammarContext, tree: &mut ClaimTree) {
        let t = self.wall_thickness;
        let z = self.center.z + self.height * 0.5;
        let frame = self.frame;
        tree.push(
            Claim::solid_box(
                format!("{} floor", self.name),
                self.center + Vec3::new(0.0, 0.0, -t * 0.5),
                Vec3::new(self.length, self.width, t),
                ctx.materials.floor,
            )
            .in_frame(frame)
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
            .in_frame(frame)
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
            .in_frame(frame)
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
            .in_frame(frame)
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
    pub frame: Frame,
}

impl DoorSpec {
    pub fn new(name: impl Into<String>, center: Vec3, size: Vec3) -> Self {
        Self {
            name: name.into(),
            center,
            size,
            frame: Frame::IDENTITY,
        }
    }

    pub fn in_frame(mut self, frame: Frame) -> Self {
        self.frame = frame;
        self
    }
}

impl Rule for DoorSpec {
    fn emit(&self, _ctx: &GrammarContext, tree: &mut ClaimTree) {
        tree.push(
            Claim::void_box(&self.name, self.center, self.size)
                .in_frame(self.frame)
                .tagged("door")
                .tagged("void"),
        );
    }
}

#[derive(Clone, Debug)]
pub struct GalleryChainSpec {
    pub name: String,
    pub frame: Frame,
    pub rooms: usize,
    pub base_room_size: Vec3,
    pub corridor_length: f32,
}

impl GalleryChainSpec {
    pub fn new(name: impl Into<String>, rooms: usize) -> Self {
        Self {
            name: name.into(),
            frame: Frame::IDENTITY,
            rooms: rooms.max(1),
            base_room_size: Vec3::new(5.0, 4.0, 3.0),
            corridor_length: 3.0,
        }
    }

    pub fn in_frame(mut self, frame: Frame) -> Self {
        self.frame = frame;
        self
    }
}

impl Rule for GalleryChainSpec {
    fn emit(&self, ctx: &GrammarContext, tree: &mut ClaimTree) {
        let mut cursor_x = 0.0;
        for index in 0..self.rooms {
            let width_jitter = ctx.range(format!("{}:{index}:width", self.name), -0.4, 0.6);
            let depth_jitter = ctx.range(format!("{}:{index}:depth", self.name), -0.25, 0.5);
            let room_size = self.base_room_size + Vec3::new(width_jitter, depth_jitter, 0.0);
            let room_center = Vec3::new(cursor_x, 0.0, 0.0);

            RoomSpec::new(
                format!("{} room {index}", self.name),
                room_center,
                room_size,
            )
            .in_frame(self.frame)
            .emit(ctx, tree);

            if index + 1 < self.rooms {
                let room_half = room_size.x * 0.5;
                let next_width = self.base_room_size.x
                    + ctx.range(format!("{}:{}:width", self.name, index + 1), -0.4, 0.6);
                let next_half = next_width * 0.5;
                let corridor_center_x = cursor_x + room_half + self.corridor_length * 0.5;
                let door_x = cursor_x + room_half;

                DoorSpec::new(
                    format!("{} doorway {index}", self.name),
                    Vec3::new(door_x, 0.0, 1.1),
                    Vec3::new(0.8, 1.5, 2.2),
                )
                .in_frame(self.frame)
                .emit(ctx, tree);

                CorridorSpec::along_x(
                    format!("{} corridor {index}", self.name),
                    Vec3::new(corridor_center_x, 0.0, 0.0),
                    self.corridor_length,
                )
                .in_frame(self.frame)
                .emit(ctx, tree);

                let next_door_x = cursor_x + room_half + self.corridor_length;
                DoorSpec::new(
                    format!("{} doorway {}b", self.name, index),
                    Vec3::new(next_door_x, 0.0, 1.1),
                    Vec3::new(0.8, 1.5, 2.2),
                )
                .in_frame(self.frame)
                .emit(ctx, tree);

                cursor_x += room_half + self.corridor_length + next_half;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use bevy_math::Quat;
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
        let tree_report = tree.compile_csg_tree().expect("claims compile to tree");
        let output = report.assembler.build();
        let door_void = Aabb::from_center_size(Vec3::new(3.0, 0.0, 1.1), Vec3::new(0.7, 1.4, 2.2));

        assert!(output.mesh.triangle_count() > 60);
        assert!(output.report.warnings.is_empty());
        assert!(tree_report.arena.nodes().len() > report.brush_ids.len());
        for tri in output.mesh.indices.chunks_exact(3) {
            let center = (output.mesh.positions[tri[0] as usize]
                + output.mesh.positions[tri[1] as usize]
                + output.mesh.positions[tri[2] as usize])
                / 3.0;
            assert!(!door_void.contains_point_strict(center, 1.0e-4));
        }
    }

    #[test]
    fn gallery_chain_uses_seeded_variation_and_frames() {
        let ctx = GrammarContext::new(99);
        let mut tree = ClaimTree::new();
        let frame = Frame::new(Vec3::new(10.0, 0.0, 0.0), Quat::from_rotation_z(0.4));
        GalleryChainSpec::new("chain", 3)
            .in_frame(frame)
            .emit(&ctx, &mut tree);

        assert_eq!(tree.count_kind(ClaimKind::Solid), 26);
        assert_eq!(tree.count_kind(ClaimKind::Void), 4);
        assert!(tree.claims().iter().any(|claim| !claim.is_axis_aligned()));

        let report = tree.compile();
        let tree_report = tree.compile_csg_tree().expect("claims compile to tree");
        let output = report.assembler.build();
        assert!(output.mesh.triangle_count() > 150);
        assert!(output.report.warnings.is_empty());
        assert!(tree_report.arena.nodes().len() > report.brush_ids.len());
    }

    #[test]
    fn ruleset_composes_rules_without_losing_claims() {
        let ctx = GrammarContext::new(5);
        let mut tree = ClaimTree::new();
        RuleSet::new()
            .with(RoomSpec::new("a", Vec3::ZERO, Vec3::new(4.0, 4.0, 3.0)))
            .with(DoorSpec::new(
                "a door",
                Vec3::new(2.0, 0.0, 1.0),
                Vec3::new(0.7, 1.2, 2.0),
            ))
            .emit(&ctx, &mut tree);

        assert_eq!(tree.count_kind(ClaimKind::Solid), 6);
        assert_eq!(tree.count_kind(ClaimKind::Void), 1);
    }
}
