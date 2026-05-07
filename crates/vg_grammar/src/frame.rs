use bevy_math::{Quat, Vec3};

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Frame {
    pub origin: Vec3,
    pub rotation: Quat,
}

impl Frame {
    pub const IDENTITY: Self = Self {
        origin: Vec3::ZERO,
        rotation: Quat::IDENTITY,
    };

    pub fn new(origin: Vec3, rotation: Quat) -> Self {
        Self { origin, rotation }
    }

    pub fn translated(self, local_offset: Vec3) -> Self {
        Self {
            origin: self.point(local_offset),
            rotation: self.rotation,
        }
    }

    pub fn rotated(self, local_rotation: Quat) -> Self {
        Self {
            origin: self.origin,
            rotation: self.rotation * local_rotation,
        }
    }

    pub fn point(self, local: Vec3) -> Vec3 {
        self.origin + self.rotation * local
    }

    pub fn vector(self, local: Vec3) -> Vec3 {
        self.rotation * local
    }
}
