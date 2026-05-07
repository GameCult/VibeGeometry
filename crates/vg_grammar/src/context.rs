use vg_csg::MaterialId;

#[derive(Clone, Copy, Debug)]
pub struct Materials {
    pub wall: MaterialId,
    pub floor: MaterialId,
    pub ceiling: MaterialId,
    pub trim: MaterialId,
}

impl Default for Materials {
    fn default() -> Self {
        Self {
            wall: MaterialId(1),
            floor: MaterialId(2),
            ceiling: MaterialId(3),
            trim: MaterialId(4),
        }
    }
}

#[derive(Clone, Debug)]
pub struct GrammarContext {
    pub seed: u64,
    pub materials: Materials,
    pub world_scale: f32,
}

impl GrammarContext {
    pub fn new(seed: u64) -> Self {
        Self {
            seed,
            materials: Materials::default(),
            world_scale: 1.0,
        }
    }

    pub fn unit(&self, salt: impl AsRef<str>) -> f32 {
        let mut hash = self.seed ^ 0x9E37_79B9_7F4A_7C15;
        for byte in salt.as_ref().bytes() {
            hash ^= u64::from(byte);
            hash = hash.wrapping_mul(0x1000_0000_01B3);
            hash ^= hash >> 32;
        }
        let bits = (hash >> 40) as u32;
        bits as f32 / 0x00FF_FFFFu32 as f32
    }

    pub fn range(&self, salt: impl AsRef<str>, min: f32, max: f32) -> f32 {
        min + (max - min) * self.unit(salt)
    }
}

impl Default for GrammarContext {
    fn default() -> Self {
        Self::new(0)
    }
}
