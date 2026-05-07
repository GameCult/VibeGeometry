//! Procedural grammar for emitting semantic CSG claims.
//!
//! `vg_grammar` is the authoring layer above `vg_csg`: rules describe why
//! space exists, then compile into solid and void brush claims.

mod claim;
mod context;
mod frame;
mod rules;

pub use claim::{Claim, ClaimKind, ClaimTag, ClaimTree, CompileReport};
pub use context::{GrammarContext, Materials};
pub use frame::Frame;
pub use rules::{CorridorSpec, DoorSpec, GalleryChainSpec, RoomSpec, Rule, RuleSet};
