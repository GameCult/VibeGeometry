# Pipeline Overview

VibeGeometry's intended pipeline turns visual intent into Blender geometry-node
machinery, then uses rendered evidence to decide what actually worked.

```text
reference images + instructions
-> scene brief
-> visual trait extraction
-> geometry strategy
-> node graph manifest
-> Blender Python builder
-> generated scene and render
-> render review
```

## Scene Brief

The scene brief is the target contract. It should say what the scene needs to
look like before it says how to build it.

Expected contents:

- reference image paths or URLs
- user instructions
- target visual traits
- constraints and exclusions
- camera and composition notes
- material and lighting expectations
- acceptance criteria
- open questions

## Geometry Strategy

The geometry strategy is plain-language reasoning about how the target can be
made procedurally. It should explain primitives, distributions, curves,
surfaces, instances, attributes, material variation, and scale relationships.

This is where the agent proves it knows what machine it is about to build.

## Node Graph Manifest

The node graph manifest is the inspectable design for Blender. It should name:

- geometry node groups
- exposed sockets and default values
- attribute names and where they flow
- modifiers and object targets
- materials and shader parameters
- reusable graph idioms
- performance risks or version-sensitive API assumptions

## Python Builder

The Python builder turns the manifest into a Blender scene. Python owns
construction, orchestration, render setup, and file output. It should not hide
the procedural design in ad hoc mesh mutation unless the scene brief explicitly
requires that escape hatch.

## Render Review

Render review compares output to the target. It should identify visual hits,
misses, graph problems, material issues, camera/lighting errors, and the next
single hypothesis to test.
