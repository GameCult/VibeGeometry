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
}

impl Default for GrammarContext {
    fn default() -> Self {
        Self::new(0)
    }
}
