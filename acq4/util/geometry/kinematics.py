"""Inverse kinematics and boundary calculation utilities."""
from __future__ import annotations

from functools import lru_cache
from typing import List

import numpy as np
from coorx import AffineTransform, Transform

from .lines_planes import Line, Plane


def greedy_axis_inverse_kinematics(
    point,
    device_to_global: Transform,
    bounds: list[tuple[float, float]],
    starting_position: list[float],
    axis: int | None = None,
) -> np.ndarray:
    """Calculate the global_to_device kinematics for a point given a device with more dimensions
    than the space in which it operates.

    Strategy
    --------
    Set the greedy axis to as close to point as possible, starting at the starting_point.
    Then solve for the other axes.

    Parameters
    ----------
    point : Mappable
        Target point in global coordinates.
    device_to_global : Transform
        Mapping from device coordinates to global. Assumed not to be invertible.
    bounds : list[tuple[float, float]]
        A list of (min, max) pairs for each dimension of the device in its own coordinate system.
        E.g. [(0, 20000), ...]
    starting_position : list[float]
        The starting position in device coordinates.
    axis : int | None
        The axis which should be preferred. Defaults to the axis most aligned with the displacement
        from device_to_global.map(starting_position) to point.

    Returns
    -------
    np.ndarray
        The calculated position in the device coordinate system.

    Raises
    ------
    ValueError
        If any of the arguments are invalid, or if no valid position could be found.
    """
    if np.allclose(device_to_global.map(starting_position), point):
        bounded = np.clip(starting_position, [b[0] for b in bounds], [b[1] for b in bounds])
        if not np.allclose(bounded, starting_position):
            raise ValueError("Invalid starting position nevertheless maps to target point")
        return np.array(bounded)
    if axis is None:
        local_direction = np.array(point) - device_to_global.map(starting_position)
        axis = 0
        max_dot = 0
        for i in range(len(bounds)):
            axis_vec = np.asarray(device_to_global.full_matrix[:3, i])
            axis_vec = axis_vec / np.linalg.norm(axis_vec)
            dot = abs(axis_vec.dot(np.asarray(local_direction)))
            if dot > max_dot:
                max_dot = dot
                axis = i
    origin_in_global = device_to_global.map(np.zeros(len(bounds)))
    axis_step = np.zeros(len(bounds))
    axis_step[axis] = 1
    axis_in_global = device_to_global.map(axis_step) - origin_in_global
    axis_scale = np.linalg.norm(axis_in_global)
    start_in_global = device_to_global.map(np.array(starting_position))
    displacement = np.asarray(point) - start_in_global
    raw_greedy_pos = (displacement.dot(axis_in_global / axis_scale) / axis_scale) + starting_position[axis]
    greedy_pos = max(bounds[axis][0], min(bounds[axis][1], raw_greedy_pos))
    neutral: list = [None] * len(bounds)
    neutral[axis] = greedy_pos
    try:
        return neutral_anchored_inverse_kinematics(
            point,
            device_to_global,
            bounds,
            neutral,
        )
    except np.linalg.LinAlgError:
        # how do we bottom out of this recursion if the destination is unreachable in the greedy
        # direction?
        starting_position = starting_position.copy()
        starting_position[axis] = raw_greedy_pos
        return greedy_axis_inverse_kinematics(
            point,
            device_to_global,
            bounds,
            starting_position,
        )


def neutral_anchored_inverse_kinematics(
    point,
    device_to_global: Transform,
    bounds: list[tuple[float, float]],
    neutral: list[float | None],
    tol: float = 1e-12,
) -> np.ndarray:
    """Calculate the global_to_device kinematics for a point given a device with more dimensions
    than the space in which it operates.

    Strategy
    --------
    Calculate the bounding planes in the neutral position. If the point is inside, we're done.
    Otherwise, draw a neutral_axis parallel to the neutral axis through the point and find the
    distance to bounding planes.

    Parameters
    ----------
    point : Mappable
        Target point in global coordinates.
    device_to_global : Transform
        Mapping from device coordinates to global. Assumed not to be invertible.
    bounds : list[tuple[float, float]]
        A list of (min, max) pairs for each dimension of the device in its own coordinate system.
        E.g. [(0, 20000), ...]
    neutral : list[float | None]
        A list containing the neutral position in device coordinates. Only one dimension can be so
        designated, with all the others set to None. E.g. [None, None, None, 0]
    tol : float
        Tolerance for floating point comparisons.

    Returns
    -------
    np.ndarray
        The calculated position in the device coordinate system.

    Raises
    ------
    ValueError
        If any of the arguments are invalid, or if no valid position could be found.
    """
    neutral_index = None
    for i, n in enumerate(neutral):
        if n is not None:
            if neutral_index is not None:
                raise ValueError("Only one neutral axis can be specified")
            neutral_index = i
    if neutral_index is None:
        raise ValueError("One neutral axis must be specified")

    origin_in_global = device_to_global.map(np.zeros(len(neutral)))
    neutral_in_global = device_to_global.map(np.array([0 if n is None else n for n in neutral]))
    neutral_axis_step = device_to_global.map(np.array([0 if n is None else 1 for n in neutral])) - origin_in_global
    neutral_axis = Line(direction=neutral_axis_step, point=point)

    # construct global_to_device transform, excluding neutral axis
    global_to_device = []
    for i in range(len(neutral)):
        if i == neutral_index:
            continue
        dev_axis = np.zeros(len(neutral))
        dev_axis[i] = 1
        global_axis = device_to_global.map(dev_axis) - origin_in_global
        global_to_device.append(global_axis)
    global_to_device = AffineTransform(np.asarray(global_to_device).T, neutral_in_global).inverse

    def _prep_device_pos(pt, neutral_pos) -> np.ndarray:
        pos = global_to_device.map(pt).tolist()
        pos.insert(neutral_index, neutral_pos)
        return np.array(pos)

    def clip(p):
        return np.clip(
            p,
            [b[0] for b in bounds],
            [b[1] for b in bounds],
        )

    nonneutral_bounds = [b for i, b in enumerate(bounds) if i != neutral_index]
    bound_planes_in_global = limits_to_boundaries(
        nonneutral_bounds, global_to_device.inverse, "dev"
    )

    if all(p.allows_point(point, tol) for p in bound_planes_in_global):
        # point is already in bounds; neutral position is fine
        return clip(_prep_device_pos(point, neutral[neutral_index]))

    intersections = []
    for plane in bound_planes_in_global:
        intersect_pt = plane.intersecting_point(neutral_axis, tol)
        if intersect_pt is not None:
            displacement = point - intersect_pt
            intersections.append((intersect_pt, displacement))

    # sort boundary intersections by distance to the point
    intersections.sort(key=lambda x: np.linalg.norm(x[1]))
    for intersect_pt, displacement in intersections:
        axial_dist = displacement.dot(neutral_axis.direction)
        # map this distance back to device coordinates
        axial_dist /= np.linalg.norm(neutral_axis_step)
        neutral_pos = axial_dist + neutral[neutral_index]
        candidate = _prep_device_pos(intersect_pt, neutral_pos)
        if all(bounds[i][0] - tol <= candidate[i] <= bounds[i][1] + tol for i in range(len(candidate))):
            return clip(candidate)

    raise ValueError("No valid position found within bounds")


def limits_to_boundaries(
    limits: list[tuple[float | None, float | None]], local_to_global: AffineTransform, name: str
) -> list[Plane]:
    """Convert coordinate limits to boundary planes in global coordinates.

    Parameters
    ----------
    limits : list[tuple[float | None, float | None]]
        A list of local (min, max) pairs for each dimension. None can be used to indicate no limit
        in that direction.
    local_to_global : AffineTransform
        Transform that maps from the local coordinate system of the limits to the global coordinate
        system. Nx3 mapping.
    name : str
        Name to use for the planes.

    Returns
    -------
    list[Plane]
        A list of Planes representing the global boundaries defined by the limits.
    """
    # TODO alternate algorithm: find all parallel planes at once, and remove the ones in the middle
    # fill in with appropriate nigh-infinities
    limits = [
        (-1e18 if min_val is None else min_val, 1e18 if max_val is None else max_val)
        for min_val, max_val in limits
    ]
    ndim = len(limits)

    @lru_cache(maxsize=None)
    def corner(*axes):
        return local_to_global.map(np.asarray([limits[i][ax] for i, ax in enumerate(axes)]))

    if ndim <= 3:
        center = (corner(0, 0, 0) + corner(1, 1, 1)) / 2
        planes = [
            Plane.from_3_points(corner(0, 0, 0), corner(0, 1, 0), corner(0, 0, 1), f"{name}'s min x"),
            Plane.from_3_points(corner(1, 0, 0), corner(1, 1, 0), corner(1, 0, 1), f"{name}'s max x"),
            Plane.from_3_points(corner(0, 0, 0), corner(1, 0, 0), corner(0, 0, 1), f"{name}'s min y"),
            Plane.from_3_points(corner(0, 1, 0), corner(1, 1, 0), corner(0, 1, 1), f"{name}'s max y"),
            Plane.from_3_points(corner(0, 0, 0), corner(1, 0, 0), corner(0, 1, 0), f"{name}'s min z"),
            Plane.from_3_points(corner(0, 0, 1), corner(1, 0, 1), corner(0, 1, 1), f"{name}'s max z"),
        ]
    else:  # 4 axes
        center = (corner(0, 0, 0, 0) + corner(1, 1, 1, 1)) / 2
        planes = [
            Plane.from_3_points(
                corner(0, 0, 0, 0), corner(0, 1, 0, 0), corner(0, 0, 1, 0), f"{name}'s min x, min d"
            ),
            Plane.from_3_points(
                corner(0, 0, 0, 0), corner(1, 0, 0, 0), corner(0, 0, 1, 0), f"{name}'s min y, min d"
            ),
            Plane.from_3_points(
                corner(0, 0, 0, 0), corner(1, 0, 0, 0), corner(0, 1, 0, 0), f"{name}'s min z, min d"
            ),
            Plane.from_3_points(
                corner(1, 0, 1, 0), corner(0, 0, 1, 0), corner(0, 0, 1, 1), f"{name}'s min y, diag 1"
            ),
            Plane.from_3_points(
                corner(1, 0, 1, 0), corner(1, 0, 0, 0), corner(1, 0, 0, 1), f"{name}'s min y, diag 2"
            ),
            Plane.from_3_points(
                corner(0, 1, 1, 0), corner(0, 0, 1, 0), corner(0, 0, 1, 1), f"{name}'s min x, diag 1"
            ),
            Plane.from_3_points(
                corner(0, 1, 1, 0), corner(0, 1, 0, 0), corner(0, 1, 0, 1), f"{name}'s min x, diag 2"
            ),
            Plane.from_3_points(
                corner(1, 1, 0, 0), corner(0, 1, 0, 0), corner(0, 1, 0, 1), f"{name}'s min z, diag 1"
            ),
            Plane.from_3_points(
                corner(1, 1, 0, 0), corner(1, 0, 0, 0), corner(1, 0, 0, 1), f"{name}'s min z, diag 2"
            ),
            Plane.from_3_points(
                corner(1, 1, 1, 1), corner(1, 0, 1, 1), corner(1, 1, 0, 1), f"{name}'s max x, max d"
            ),
            Plane.from_3_points(
                corner(1, 1, 1, 1), corner(0, 1, 1, 1), corner(1, 1, 0, 1), f"{name}'s max y, max d"
            ),
            Plane.from_3_points(
                corner(1, 1, 1, 1), corner(0, 1, 1, 1), corner(1, 0, 1, 1), f"{name}'s max z, max d"
            ),
        ]
        # remove any coplanar planes in case D is orthogonal to some other axis
        unique_planes = []
        for p in planes:
            if not any(p.coplanar_with(other) for other in unique_planes):
                unique_planes.append(p)
        planes = unique_planes
    # flip normals to point inward
    for p in planes:
        if p.distance_to_point(center) < 0:
            p.normal = -p.normal

    return planes
