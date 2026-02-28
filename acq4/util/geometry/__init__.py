"""Geometry utilities for 3D spatial operations, motion planning, and collision detection.

This package provides:
- 3D shape primitives and mesh handling
- Voxel-based collision detection
- Line and plane geometry
- Motion planning with A* and RRT algorithms
- Inverse kinematics utilities
- Transform loading utilities
"""

# Primitives
from .primitives import truncated_cone

# Voxel operations
from .voxels import (
    Volume,
    convolve_kernel_onto_volume,
    convolve_kernel_onto_volume_numba,
    convolve_kernel_onto_volume_scipy,
    find_intersected_voxels_3ddda,
    find_intersected_voxels_axial,
    find_intersected_voxels_axial_numba,
    find_intersected_voxels_broadphase,
    find_intersected_voxels_exhaustive,
    find_intersected_voxels_numba,
    find_intersected_voxels_supercover,
    line_intersects_voxel,
)

# Pathfinding
from .pathfinding import (
    RRTNode,
    a_star_ish,
    generate_biased_sphere_points,
    generate_even_sphere_points,
    reconstruct_path,
    rrt_connect,
    simplify_path,
    simplify_path_dp,
)

# Motion planner
from .planner import GeometryMotionPlanner, point_in_bounds

# Shapes
from .shapes import Geometry

# Lines and planes
from .lines_planes import Line, Plane, are_colinear

# Transforms
from .transforms import load_transform_from_anything

# Kinematics
from .kinematics import (
    greedy_axis_inverse_kinematics,
    limits_to_boundaries,
    neutral_anchored_inverse_kinematics,
)

__all__ = [
    # Primitives
    "truncated_cone",
    # Voxels
    "Volume",
    "convolve_kernel_onto_volume",
    "convolve_kernel_onto_volume_numba",
    "convolve_kernel_onto_volume_scipy",
    "find_intersected_voxels_3ddda",
    "find_intersected_voxels_axial",
    "find_intersected_voxels_axial_numba",
    "find_intersected_voxels_broadphase",
    "find_intersected_voxels_exhaustive",
    "find_intersected_voxels_numba",
    "find_intersected_voxels_supercover",
    "line_intersects_voxel",
    # Pathfinding
    "RRTNode",
    "a_star_ish",
    "generate_biased_sphere_points",
    "generate_even_sphere_points",
    "reconstruct_path",
    "rrt_connect",
    "simplify_path",
    "simplify_path_dp",
    # Motion planner
    "GeometryMotionPlanner",
    "point_in_bounds",
    # Shapes
    "Geometry",
    # Lines and planes
    "Line",
    "Plane",
    "are_colinear",
    # Transforms
    "load_transform_from_anything",
    # Kinematics
    "greedy_axis_inverse_kinematics",
    "limits_to_boundaries",
    "neutral_anchored_inverse_kinematics",
]
