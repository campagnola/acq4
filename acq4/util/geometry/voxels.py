"""Voxel-based geometry operations and intersection algorithms."""
from __future__ import annotations

from functools import cached_property
from typing import Any, Generator, List, Tuple

import numba
import numpy as np
import pyqtgraph as pg
from coorx import Point, TTransform, Transform


@numba.jit(nopython=True, nogil=True)
def line_intersects_voxel(start: np.ndarray, end: np.ndarray, vox: np.ndarray):
    """
    Check if a line segment intersects with a voxel (using Numba optimization)
    """
    diff = end - start
    norm = np.sqrt(diff[0] ** 2 + diff[1] ** 2 + diff[2] ** 2)  # Faster than np.linalg.norm
    direction = diff / norm

    # Check each axis
    for ax in range(3):
        if abs(direction[ax]) < 1e-10:  # Avoid division by zero
            continue

        ax2 = (ax + 1) % 3
        ax3 = (ax + 2) % 3

        # Calculate min and max for x_steps
        min_val = min(start[ax], end[ax])
        max_val = max(start[ax], end[ax])

        # Create steps array manually since np.arange isn't supported in nopython mode
        start_step = int(np.ceil(min_val))
        end_step = int(np.floor(max_val)) + 1

        for x in range(start_step, end_step):
            t = (x - start[ax]) / direction[ax]
            y = int(np.floor(start[ax2] + t * direction[ax2]))
            z = int(np.floor(start[ax3] + t * direction[ax3]))

            # Create index array
            index = np.zeros(3, dtype=np.int64)
            index[ax] = x
            index[ax2] = y
            index[ax3] = z

            # Check both current and previous voxel
            if index[0] == vox[0] and index[1] == vox[1] and index[2] == vox[2]:
                return True

            index[ax] -= 1
            if index[0] == vox[0] and index[1] == vox[1] and index[2] == vox[2]:
                return True

    return False


def find_intersected_voxels_broadphase(line_start, line_end, voxel_space_max):
    """Find voxels intersected by a line using broadphase culling."""
    # Create an axis-aligned bounding box for the line
    min_point = np.minimum(line_start, line_end)
    max_point = np.maximum(line_start, line_end)

    # Determine total bounds
    start_voxel = np.maximum(np.floor(min_point).astype(int), 0)
    end_voxel = np.minimum(np.ceil(max_point).astype(int), voxel_space_max)

    # Calculate simplified line equation: p = start + t * (end - start)
    direction = line_end - line_start

    # Use plane-sweeping technique:
    # For each plane perpendicular to longest axis, find intersecting voxels
    main_axis = np.argmax(np.abs(direction))

    # If the line is nearly vertical along the axis
    if abs(direction[main_axis]) < 1e-10:
        # Just check voxels along the line
        for x in range(start_voxel[0], end_voxel[0] + 1):
            for y in range(start_voxel[1], end_voxel[1] + 1):
                for z in range(start_voxel[2], end_voxel[2] + 1):
                    if line_intersects_voxel(line_start, line_end, np.array([x, y, z])):
                        yield (x, y, z)
        return

    # For each slice along main axis
    for slice_pos in range(start_voxel[main_axis], end_voxel[main_axis] + 1):
        # Find where line intersects this slice
        t = (slice_pos - line_start[main_axis]) / direction[main_axis]

        # Skip if this slice is outside line segment
        if t < 0 or t > 1:
            continue

        # Find intersection point with this slice
        intersection = line_start + t * direction

        # Only check voxels near the intersection point
        intersection_voxel = np.floor(intersection).astype(int)

        # Check a small neighborhood (3x3) around intersection point
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    voxel = intersection_voxel + np.array([dx, dy, dz])

                    # Skip out-of-bounds voxels
                    if np.any(voxel < 0) or np.any(voxel > voxel_space_max):
                        continue

                    # Use existing intersection test for correctness
                    if line_intersects_voxel(line_start, line_end, voxel):
                        yield tuple(voxel)


def find_intersected_voxels_3ddda(line_start, line_end, voxel_space_max):
    """Find voxels intersected by a line using 3D DDA algorithm."""
    # Initialize current voxel at start position
    current_voxel = np.floor(line_start).astype(int)

    # Direction and delta distances
    direction = line_end - line_start
    length = np.linalg.norm(direction)

    # Normalized direction
    if length > 1e-10:
        direction = direction / length
    else:
        # Just yield the start voxel if line is very short
        yield tuple(np.clip(current_voxel, 0, voxel_space_max))
        return

    # Step direction for each axis
    step = np.sign(direction).astype(int)

    # Calculate t values for next voxel boundaries
    next_boundary = current_voxel + np.maximum(step, 0)
    t_max = np.divide(
        next_boundary - line_start, direction, where=abs(direction) > 1e-10, out=np.full(3, np.inf)
    )

    # Delta t for moving one voxel along each axis
    delta_t = np.divide(step, direction, where=abs(direction) > 1e-10, out=np.full(3, np.inf))

    # Traverse voxels until we reach end
    remaining_length = length

    while remaining_length > 0:
        # Yield current voxel if in bounds
        if np.all(current_voxel >= 0) and np.all(current_voxel <= voxel_space_max):
            # Verify intersection with existing function for correctness
            if line_intersects_voxel(line_start, line_end, current_voxel):
                yield tuple(current_voxel)

        # Find closest axis boundary
        axis = np.argmin(t_max)

        # Move to next voxel
        remaining_length -= abs(delta_t[axis]) * abs(direction[axis])
        current_voxel[axis] += step[axis]
        t_max[axis] += abs(delta_t[axis])


@numba.jit(nopython=True, nogil=True)
def _compute_intersected_voxels(
    line_start: np.ndarray, line_end: np.ndarray, voxel_space_max: np.ndarray
) -> List[Tuple[int, int, int]]:
    """
    Compute all voxels intersected by a line segment with optimized bounds.
    Internal function optimized with Numba.

    Returns a list of (x, y, z) tuples representing intersected voxels.
    """
    # Compute bounding box of the line
    min_point = np.minimum(line_start, line_end)
    max_point = np.maximum(line_start, line_end)

    # Determine voxel range
    start_voxel = np.floor(min_point).astype(np.int64)
    start_voxel = np.maximum(start_voxel, 0)
    end_voxel = np.floor(max_point).astype(np.int64)
    end_voxel = np.minimum(end_voxel, voxel_space_max)

    # Direction and length
    direction = line_end - line_start
    line_length = np.sqrt(direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2)

    result = []

    # If the line is very short, use simplified approach
    if line_length < 1.0:
        for x in range(start_voxel[0], end_voxel[0] + 1):
            for y in range(start_voxel[1], end_voxel[1] + 1):
                for z in range(start_voxel[2], end_voxel[2] + 1):
                    if line_intersects_voxel(line_start, line_end, np.array([x, y, z])):
                        result.append((x, y, z))
        return result

    # Find dominant axis for optimization (axis with greatest change)
    abs_dir = np.abs(direction)
    dominant_axis = 0
    if abs_dir[1] > abs_dir[0] and abs_dir[1] > abs_dir[2]:
        dominant_axis = 1
    elif abs_dir[2] > abs_dir[0] and abs_dir[2] > abs_dir[1]:
        dominant_axis = 2

    # Other axes
    second_axis = (dominant_axis + 1) % 3
    third_axis = (dominant_axis + 2) % 3

    # For each primary position along dominant axis
    for primary in range(start_voxel[dominant_axis], end_voxel[dominant_axis] + 1):
        # Calculate where line enters and exits this slice
        if abs(direction[dominant_axis]) > 1e-10:
            # Calculate t-values where line enters/exits this slice
            t_min = (primary - line_start[dominant_axis]) / direction[dominant_axis]
            t_max = (primary + 1 - line_start[dominant_axis]) / direction[dominant_axis]

            # Ensure t_min <= t_max
            if t_min > t_max:
                t_min, t_max = t_max, t_min

            # Clip to line segment bounds
            t_min = max(0.0, t_min)
            t_max = min(1.0, t_max)

            # Calculate the points where the line enters and exits this slice
            point_min = line_start + t_min * direction
            point_max = line_start + t_max * direction

            # Calculate tighter bounds for secondary and tertiary axes in this slice
            secondary_min = int(np.floor(min(point_min[second_axis], point_max[second_axis])))
            secondary_max = int(np.floor(max(point_min[second_axis], point_max[second_axis])))
            tertiary_min = int(np.floor(min(point_min[third_axis], point_max[third_axis])))
            tertiary_max = int(np.floor(max(point_min[third_axis], point_max[third_axis])))

            # Apply global bounds constraints
            secondary_min = max(secondary_min, start_voxel[second_axis])
            secondary_max = min(secondary_max, end_voxel[second_axis])
            tertiary_min = max(tertiary_min, start_voxel[third_axis])
            tertiary_max = min(tertiary_max, end_voxel[third_axis])
        else:
            # Line is nearly parallel to the secondary-tertiary plane
            secondary_min = start_voxel[second_axis]
            secondary_max = end_voxel[second_axis]
            tertiary_min = start_voxel[third_axis]
            tertiary_max = end_voxel[third_axis]

        # Loop through the optimized secondary and tertiary bounds
        for secondary in range(secondary_min, secondary_max + 1):
            for tertiary in range(tertiary_min, tertiary_max + 1):
                # Construct voxel coordinates
                voxel = np.zeros(3, dtype=np.int64)
                voxel[dominant_axis] = primary
                voxel[second_axis] = secondary
                voxel[third_axis] = tertiary

                # Check if line intersects this voxel
                if line_intersects_voxel(line_start, line_end, voxel):
                    result.append((int(voxel[0]), int(voxel[1]), int(voxel[2])))

    return result


def find_intersected_voxels_numba(
    line_start: np.ndarray, line_end: np.ndarray, voxel_space_max: np.ndarray
) -> Generator[tuple[int, int, int], Any, None]:
    """
    Find all voxels intersected by a line segment with optimized search space.
    Uses Numba for acceleration and pre-computed bounds for secondary axes.

    Parameters
    ----------
    line_start : np.ndarray
        Start point of the line segment.
    line_end : np.ndarray
        End point of the line segment.
    voxel_space_max : np.ndarray
        Maximum voxel coordinates in the space (assumes minimum is 0).

    Yields
    ------
    tuple[int, int, int]
        Voxel coordinates intersected by the line.
    """
    # Ensure inputs are the right type for Numba
    line_start_array = np.asarray(line_start, dtype=np.float64)
    line_end_array = np.asarray(line_end, dtype=np.float64)
    voxel_space_max_array = np.asarray(voxel_space_max, dtype=np.int64)

    # Call the internal Numba-optimized function
    intersected_voxels = _compute_intersected_voxels(
        line_start_array, line_end_array, voxel_space_max_array
    )

    # Yield the results
    for voxel in intersected_voxels:
        yield voxel


def find_intersected_voxels_supercover(
    line_start: np.ndarray, line_end: np.ndarray, voxel_space_max: np.ndarray
) -> Generator[tuple[int, int, int], Any, None]:
    """
    Find all voxels intersected by a line segment using the 3D Supercover algorithm.

    Parameters
    ----------
    line_start : np.ndarray
        Start point of the line segment.
    line_end : np.ndarray
        End point of the line segment.
    voxel_space_max : np.ndarray
        Maximum voxel coordinates in the space (assumes minimum is 0).

    Yields
    ------
    tuple[int, int, int]
        Voxel coordinates intersected by the line.
    """
    # Initialize variables
    start = np.copy(line_start)
    end = np.copy(line_end)

    # Calculate direction and step
    direction = end - start
    step = np.sign(direction).astype(int)

    # Find absolute distances
    abs_direction = np.abs(direction)

    # Track current position
    current_voxel = np.floor(start).astype(int)

    # Handle special case: very short lines
    if np.allclose(start, end, rtol=1e-10, atol=1e-10):
        if np.all(current_voxel >= 0) and np.all(current_voxel <= voxel_space_max):
            yield tuple(current_voxel)
        return

    # Yield the starting voxel if valid
    if np.all(current_voxel >= 0) and np.all(current_voxel <= voxel_space_max):
        yield tuple(current_voxel)

    # Compute step sizes for each dimension
    # For supercover, we need to track both the voxel boundary and diagonal crossings
    tx = ty = tz = 0

    # Calculate initial tx, ty, tz values (time to next voxel boundary)
    if step[0] != 0:
        tx = (np.floor(start[0]) + max(0, step[0]) - start[0]) / direction[0]
    if step[1] != 0:
        ty = (np.floor(start[1]) + max(0, step[1]) - start[1]) / direction[1]
    if step[2] != 0:
        tz = (np.floor(start[2]) + max(0, step[2]) - start[2]) / direction[2]

    # Delta values (time to cross a whole voxel)
    delta_tx = abs(1.0 / direction[0]) if direction[0] != 0 else float("inf")
    delta_ty = abs(1.0 / direction[1]) if direction[1] != 0 else float("inf")
    delta_tz = abs(1.0 / direction[2]) if direction[2] != 0 else float("inf")

    # Length of the line segment
    line_length = np.linalg.norm(direction)
    traveled = 0

    # Main loop
    while traveled < line_length:
        # Determine which axis to step along (smallest tx, ty, or tz)
        if tx <= ty and tx <= tz:
            # Step along x axis
            current_voxel[0] += step[0]
            traveled = tx * line_length
            tx += delta_tx
        elif ty <= tx and ty <= tz:
            # Step along y axis
            current_voxel[1] += step[1]
            traveled = ty * line_length
            ty += delta_ty
        else:
            # Step along z axis
            current_voxel[2] += step[2]
            traveled = tz * line_length
            tz += delta_tz

        # If the current voxel is within bounds, yield it
        if (
            np.all(current_voxel >= 0)
            and np.all(current_voxel <= voxel_space_max)
            and traveled <= line_length
        ):
            # Verify with your existing function for correctness
            if line_intersects_voxel(line_start, line_end, current_voxel):
                yield tuple(current_voxel)

        # Supercover modification: Also check diagonal neighbors at boundaries
        # This ensures we don't miss any voxels the line passes through
        if np.isclose(tx, ty) or np.isclose(tx, tz) or np.isclose(ty, tz):
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        if dx == 0 and dy == 0 and dz == 0:
                            continue  # Skip the current voxel

                        neighbor = current_voxel + np.array([dx, dy, dz])
                        if np.all(neighbor >= 0) and np.all(neighbor <= voxel_space_max):
                            if line_intersects_voxel(line_start, line_end, neighbor):
                                yield tuple(neighbor)


def find_intersected_voxels_axial(
    line_start: np.ndarray, line_end: np.ndarray, voxel_space_max: np.ndarray
) -> Generator[tuple[int, int, int], Any, None]:
    """
    Find all voxels intersected by a line segment with optimized search space.

    Parameters
    ----------
    line_start : np.ndarray
        Start point of the line segment.
    line_end : np.ndarray
        End point of the line segment.
    voxel_space_max : np.ndarray
        Maximum voxel coordinates in the space (assumes minimum is 0).

    Yields
    ------
    tuple[int, int, int]
        Voxel coordinates intersected by the line.
    """
    # Compute bounding box of the line
    min_point = np.minimum(line_start, line_end)
    max_point = np.maximum(line_start, line_end)

    # Determine voxel range
    start_voxel = np.floor(min_point).astype(int)
    start_voxel = np.maximum(start_voxel, 0)
    end_voxel = np.floor(max_point).astype(int)
    end_voxel = np.minimum(end_voxel, voxel_space_max)

    # Get line direction for optimization
    direction = line_end - line_start
    line_length = np.linalg.norm(direction)

    # If the line is very short, just check immediate voxels
    if line_length < 1.0:
        for x in range(start_voxel[0], end_voxel[0] + 1):
            for y in range(start_voxel[1], end_voxel[1] + 1):
                for z in range(start_voxel[2], end_voxel[2] + 1):
                    if line_intersects_voxel(line_start, line_end, np.array([x, y, z])):
                        yield x, y, z
        return

    # Find dominant axis for optimization
    dominant_axis = np.argmax(np.abs(direction))
    second_axis = (dominant_axis + 1) % 3
    third_axis = (dominant_axis + 2) % 3

    # Sort voxels by distance along dominant axis for early termination possibilities
    for primary in range(start_voxel[dominant_axis], end_voxel[dominant_axis] + 1):
        # Calculate bounds for other axes at this primary position
        # This could be further optimized with more complex math
        for secondary in range(start_voxel[second_axis], end_voxel[second_axis] + 1):
            for tertiary in range(start_voxel[third_axis], end_voxel[third_axis] + 1):
                # Construct voxel coordinates based on axis ordering
                voxel = np.zeros(3, dtype=int)
                voxel[dominant_axis] = primary
                voxel[second_axis] = secondary
                voxel[third_axis] = tertiary

                # Use existing intersection test that's known to work correctly
                if line_intersects_voxel(line_start, line_end, voxel):
                    yield tuple(voxel)


@numba.njit(nogil=True)
def _line_intersects_voxel(
    line_start: np.ndarray, line_end: np.ndarray, voxel: np.ndarray, epsilon: float = 1e-6
) -> bool:
    """
    Tests if a line segment intersects with a voxel using the slab method.
    """
    # Voxel min and max bounds
    voxel_min = voxel.astype(np.float64)
    voxel_max = voxel_min + 1.0

    # Direction vector of the line
    direction = line_end - line_start

    # Initialize intersection interval to entire line
    t_enter = 0.0
    t_exit = 1.0

    # For each axis
    for i in range(3):
        # Check if line is parallel to the axis
        if np.abs(direction[i]) < epsilon:
            # Line is parallel to this axis, so check if it's within the voxel bounds
            if line_start[i] < voxel_min[i] - epsilon or line_start[i] > voxel_max[i] + epsilon:
                return False
            continue

        # Calculate intersection times with the two planes perpendicular to this axis
        t1 = (voxel_min[i] - line_start[i]) / direction[i]
        t2 = (voxel_max[i] - line_start[i]) / direction[i]

        # Ensure t1 <= t2
        if t1 > t2:
            t1, t2 = t2, t1

        # Update the overall intersection interval
        t_enter = max(t_enter, t1)
        t_exit = min(t_exit, t2)

        # If intervals don't overlap, no intersection
        if t_enter > t_exit + epsilon:
            return False

    # Check if the intersection interval is valid
    return t_exit >= 0 and t_enter <= 1


@numba.njit(nogil=True)
def _find_intersected_voxels_axial_core(
    line_start: np.ndarray, line_end: np.ndarray, voxel_space_max: np.ndarray
) -> List[Tuple[int, int, int]]:
    """
    Numba-optimized core function that returns a list of tuples.
    This maintains most of the original algorithm structure.
    """
    # Compute bounding box of the line
    min_point = np.minimum(line_start, line_end)
    max_point = np.maximum(line_start, line_end)

    # Determine voxel range - keeping your original type handling
    start_voxel = np.floor(min_point).astype(np.int64)
    start_voxel = np.maximum(start_voxel, 0)
    end_voxel = np.floor(max_point).astype(np.int64)
    end_voxel = np.minimum(end_voxel, voxel_space_max)

    # Pre-allocate a list for Numba
    result = numba.typed.List()

    # Get line direction for optimization
    direction = line_end - line_start
    line_length = np.linalg.norm(direction)

    # If the line is very short, just check immediate voxels
    if line_length < 1.0:
        for x in range(start_voxel[0], end_voxel[0] + 1):
            for y in range(start_voxel[1], end_voxel[1] + 1):
                for z in range(start_voxel[2], end_voxel[2] + 1):
                    voxel = np.array([x, y, z], dtype=np.int64)
                    if line_intersects_voxel(line_start, line_end, voxel):
                        result.append((x, y, z))
        return result

    # Find dominant axis for optimization
    dominant_axis = np.argmax(np.abs(direction))
    second_axis = (dominant_axis + 1) % 3
    third_axis = (dominant_axis + 2) % 3

    # Sort voxels by distance along dominant axis - preserving original algorithm
    for primary in range(start_voxel[dominant_axis], end_voxel[dominant_axis] + 1):
        for secondary in range(start_voxel[second_axis], end_voxel[second_axis] + 1):
            for tertiary in range(start_voxel[third_axis], end_voxel[third_axis] + 1):
                # Construct voxel coordinates based on axis ordering
                voxel = np.zeros(3, dtype=np.int64)
                voxel[dominant_axis] = primary
                voxel[second_axis] = secondary
                voxel[third_axis] = tertiary

                # Use existing intersection test
                if line_intersects_voxel(line_start, line_end, voxel):
                    result.append((int(voxel[0]), int(voxel[1]), int(voxel[2])))

    return result


def find_intersected_voxels_axial_numba(
    line_start: np.ndarray, line_end: np.ndarray, voxel_space_max: np.ndarray
) -> Generator[tuple[int, int, int], Any, None]:
    """
    Find all voxels intersected by a line segment with optimized search space.
    This maintains your original function interface.
    """
    # Call the JIT-optimized core function
    voxel_list = _find_intersected_voxels_axial_core(line_start, line_end, voxel_space_max)

    # Yield each voxel coordinate
    for voxel in voxel_list:
        yield voxel


def find_intersected_voxels_exhaustive(
    line_start: np.ndarray, line_end: np.ndarray, voxel_space_max: np.ndarray
) -> Generator[tuple[int, int, int], Any, None]:
    """
    Find all voxels intersected by a line segment.

    Parameters
    ----------
    line_start : np.ndarray
        Start point of the line segment.
    line_end : np.ndarray
        End point of the line segment.
    voxel_space_max : np.ndarray
        Maximum voxel coordinates in the space (assumes minimum is 0).

    Yields
    ------
    tuple[int, int, int]
        Voxel coordinates intersected by the line.
    """
    # Compute bounding box of the line
    min_point = np.minimum(line_start, line_end)
    max_point = np.maximum(line_start, line_end)

    # Determine voxel range
    start_voxel = np.floor(min_point).astype(int)
    start_voxel = np.maximum(start_voxel, 0)
    end_voxel = np.floor(max_point).astype(int)
    end_voxel = np.minimum(end_voxel, voxel_space_max)

    return (
        (x, y, z)
        for x in range(start_voxel[0], end_voxel[0] + 1)
        for y in range(start_voxel[1], end_voxel[1] + 1)
        for z in range(start_voxel[2], end_voxel[2] + 1)
        if line_intersects_voxel(line_start, line_end, np.array([x, y, z]))
    )


def convolve_kernel_onto_volume(volume: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Convolve a kernel onto a volume using coordinate-based approach."""
    # Convert to proper types if needed
    volume_bool = volume.astype(bool)
    kernel_bool = kernel.astype(bool)

    # Get coordinates of True values
    volume_coords = np.array(np.where(volume_bool)).T
    kernel_coords = np.array(np.where(kernel_bool)).T

    # Output shape
    v_shape = volume.shape
    k_shape = kernel.shape
    out_shape = (
        v_shape[0] + k_shape[0] - 1,
        v_shape[1] + k_shape[1] - 1,
        v_shape[2] + k_shape[2] - 1,
    )

    # Initialize output array
    result = np.zeros(out_shape, dtype=np.bool_)

    # For each True kernel position, add it to all True volume positions
    for kx, ky, kz in kernel_coords:
        # This creates an array of coordinates where the kernel's True position
        # is added to all True positions in the volume
        new_coords = volume_coords + np.array([kx, ky, kz])

        # Filter valid coordinates (those within bounds)
        valid_mask = np.all((new_coords >= 0) & (new_coords < out_shape), axis=1)
        valid_coords = new_coords[valid_mask]

        # Set those positions to True
        if len(valid_coords) > 0:
            result[valid_coords[:, 0], valid_coords[:, 1], valid_coords[:, 2]] = True

    return result


def convolve_kernel_onto_volume_scipy(volume: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Convolve a kernel onto a volume using scipy."""
    import scipy.signal

    return scipy.signal.convolve(volume.astype(int), kernel.astype(int), mode="full").astype(bool)


@numba.jit(nopython=True, nogil=True)
def convolve_kernel_onto_volume_numba(volume: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Convolve a kernel onto a volume using Numba optimization."""
    v_shape = volume.shape
    k_shape = kernel.shape
    shape = (v_shape[0] + k_shape[0] - 1, v_shape[1] + k_shape[1] - 1, v_shape[2] + k_shape[2] - 1)

    dest = np.zeros(shape, dtype=np.bool_)

    for x in range(v_shape[0]):
        for y in range(v_shape[1]):
            for z in range(v_shape[2]):
                if volume[x, y, z]:
                    for kx in range(k_shape[0]):
                        for ky in range(k_shape[1]):
                            for kz in range(k_shape[2]):
                                if kernel[kx, ky, kz]:
                                    dest[x + kx, y + ky, z + kz] = True
    return dest


class Volume(object):
    """
    A volumetric representation of Geometry.

    Parameters
    ----------
    volume : np.ndarray
        3D boolean array containing voxelized geometry.
    transform : Transform
        Transform that maps from the local coordinate system of this volume (i.e. voxel coordinates)
        to the parent geometry's coordinate system.
    """

    def __init__(self, volume: np.ndarray, transform: Transform):
        self.volume = volume
        self.transform: Transform = transform

    @property
    def inverse_transform(self):
        """The transform that maps from the parent geometry's coordinate system to the local coordinate system."""
        return self.transform.inverse

    @property
    def parent_origin(self):
        """The origin of the mesh CS in the voxel's CS."""
        origin = Point(np.array([0, 0, 0]), self.transform.systems[1])
        return self.transform.inverse.map(origin)

    def convolve(self, kernel_array: np.ndarray, center: np.ndarray, name: str) -> "Volume":
        """
        Return a new Volume that contains the convolution of self with *kernel_array*.

        Parameters
        ----------
        kernel_array : np.ndarray
            Voxel array to convolve with, already transformed to match the rotation of self.
        center : np.ndarray
            Position of the "center" point relative to the kernel. This is added to the resulting
            Volume's transform.
        name : str
            Name of the kernel.

        Returns
        -------
        Volume
            A new Volume containing the convolution result.
        """
        dest = convolve_kernel_onto_volume_numba(self.volume, kernel_array)
        draw_xform = TTransform(
            offset=-center,
            to_cs=self.transform.systems[0],
            from_cs=f"[convolved {name} in {self.transform.systems[1]}]",
        )
        return Volume(dest, self.transform * draw_xform)

    def intersects_line(self, a, b):
        """Return True if the line segment between *a* and *b* intersects with this volume.

        Points should be in the parent coordinate system of the volume.
        """
        line_voxels = find_intersected_voxels_axial(
            self.transform.inverse.map(a)[::-1],
            self.transform.inverse.map(b)[::-1],
            np.array(self.volume.shape) - 1,
        )
        return next((True for x, y, z in line_voxels if self.volume[x, y, z]), False)

    def contains_point(self, point: np.ndarray):
        """Return True if the given point is inside this volume.

        Point should be in the parent coordinate system of the volume.
        """
        # TODO turn [::-1] into a part of the transform
        coords = np.floor(self.transform.inverse.map(point)).astype(int)[::-1]
        if np.any(coords < 0) or np.any(coords >= self.volume.shape):
            return False
        return self.volume[tuple(coords)]

    @cached_property
    def surface_mesh(self):
        """Get the surface mesh representation of this volume."""
        return pg.isosurface(np.ascontiguousarray(self.volume.T.astype(int)), 1)
