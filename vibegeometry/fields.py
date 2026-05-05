"""Deterministic scalar fields for procedural distribution."""

from __future__ import annotations

import math


def smoothstep(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def hash01(ix: int, iy: int = 0, seed: int = 0) -> float:
    n = ix * 374761393 + iy * 668265263 + seed * 1442695041
    n = (n ^ (n >> 13)) * 1274126177
    n = n ^ (n >> 16)
    return (n & 0xFFFFFFFF) / 0xFFFFFFFF


def value_noise_2d(x: float, y: float, seed: int = 0) -> float:
    ix = math.floor(x)
    iy = math.floor(y)
    fx = smoothstep(x - ix)
    fy = smoothstep(y - iy)
    a = hash01(ix, iy, seed)
    b = hash01(ix + 1, iy, seed)
    c = hash01(ix, iy + 1, seed)
    d = hash01(ix + 1, iy + 1, seed)
    ab = a + (b - a) * fx
    cd = c + (d - c) * fx
    return ab + (cd - ab) * fy


def fbm_2d(x: float, y: float, seed: int = 0, octaves: int = 4) -> float:
    value = 0.0
    amplitude = 0.5
    frequency = 1.0
    total = 0.0
    for octave in range(octaves):
        value += value_noise_2d(x * frequency, y * frequency, seed + octave * 19) * amplitude
        total += amplitude
        amplitude *= 0.5
        frequency *= 2.03
    return value / total if total else 0.0

