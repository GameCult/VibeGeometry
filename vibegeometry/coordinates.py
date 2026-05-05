"""Coordinate-frame helpers for procedural Blender scenes."""

from __future__ import annotations

import math
from dataclasses import dataclass


TAU = math.tau


@dataclass(frozen=True)
class CylinderFrame:
    """Shared cylindrical frame: x is axial, angle is azimuth, radius is spin radius."""

    inner_radius: float

    @staticmethod
    def radial(angle: float) -> tuple[float, float, float]:
        return (0.0, math.cos(angle), math.sin(angle))

    @staticmethod
    def tangent(angle: float) -> tuple[float, float, float]:
        return (0.0, -math.sin(angle), math.cos(angle))

    @staticmethod
    def cyl_point(x: float, angle: float, radius: float) -> tuple[float, float, float]:
        return (x, radius * math.cos(angle), radius * math.sin(angle))

    def surface_point(self, x: float, angle: float, radius: float | None = None, lift: float = -0.04) -> tuple[float, float, float]:
        r = (self.inner_radius if radius is None else radius) + lift
        return self.cyl_point(x, angle, r)

