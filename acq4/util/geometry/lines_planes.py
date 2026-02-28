"""Line and plane geometry classes and operations."""
from __future__ import annotations

import itertools
from typing import List

import numpy as np

from acq4.util.approx import ApproxDict, ApproxSet


class Line:
    """A line in 3D space defined by a direction and a point.

    Parameters
    ----------
    direction : np.ndarray
        Direction vector of the line (will be normalized).
    point : np.ndarray
        A point on the line.
    """

    def __init__(self, direction, point):
        self.direction = direction / np.linalg.norm(direction)
        if np.isnan(self.direction).any():
            raise ValueError(f"Direction vector {direction} is invalid")
        self.point = point

    def __eq__(self, other: "Line") -> bool:
        epsilon = 1e-12
        cross_product = np.cross(self.direction, other.direction)
        return (
            np.linalg.norm(cross_product) < epsilon
            and np.linalg.norm(np.cross(self.direction, other.point - self.point)) < epsilon
        )

    def __hash__(self):
        # Normalize the direction vector
        direction_norm = np.linalg.norm(self.direction)
        if direction_norm < 1e-10:
            raise ValueError("Direction vector cannot be zero")
        unit_direction = self.direction / direction_norm

        # Compute the moment vector
        moment = np.cross(self.point, unit_direction)

        # Make the representation canonical by ensuring the
        # first non-zero component of direction is positive
        for i in range(3):
            if abs(unit_direction[i]) > 1e-10:
                if unit_direction[i] < 0:
                    unit_direction = -unit_direction
                    moment = -moment
                break

        return hash((tuple(unit_direction), tuple(moment)))

    def intersecting_point(self, other: "Line", epsilon: float = 1e-12) -> np.ndarray | None:
        """
        Find the intersection point of two 3D lines, accounting for floating point precision.

        Parameters
        ----------
        other : Line
            The other line to intersect with.
        epsilon : float
            Tolerance for determining if lines intersect.

        Returns
        -------
        np.ndarray | None
            The closest point between the two lines, if that's within epsilon of the lines
            intersecting. None, otherwise.
        """
        # Check if lines are parallel
        cross_product = np.cross(self.direction, other.direction)
        if np.linalg.norm(cross_product) < epsilon:
            if np.linalg.norm(np.cross(self.direction, other.point - self.point)) < epsilon:
                return self.point
            return None

        w0 = self.point - other.point

        # Coefficients for the system of equations
        a = np.dot(self.direction, self.direction)
        b = np.dot(self.direction, other.direction)
        c = np.dot(other.direction, other.direction)
        d = np.dot(self.direction, w0)
        e = np.dot(other.direction, w0)

        # Parameters for points of closest approach
        denominator = a * c - b * b
        if abs(denominator) < epsilon:
            return None

        sc = (b * e - c * d) / denominator
        tc = (a * e - b * d) / denominator

        # Find closest points on each line
        closest_point1 = self.point + sc * self.direction
        closest_point2 = other.point + tc * other.direction

        # Calculate distance between lines
        distance = np.linalg.norm(closest_point1 - closest_point2)

        # If distance is within epsilon, lines intersect
        if distance < epsilon:
            return closest_point1
        return None

    def __str__(self):
        return f"Line({self.point} -> {self.point + self.direction})"

    def __repr__(self):
        return str(self)


def are_colinear(l1, l2):
    """Check if two line segments are colinear.

    Parameters
    ----------
    l1 : tuple[np.ndarray, np.ndarray]
        First line segment as (start, end) points.
    l2 : tuple[np.ndarray, np.ndarray]
        Second line segment as (start, end) points.

    Returns
    -------
    bool
        True if the line segments are colinear.
    """
    a, b = l1
    c, d = l2
    return np.allclose(np.cross(b - a, d - c), 0, atol=1e-10) and np.allclose(
        np.cross(a - c, b - c), 0, atol=1e-10
    )


class Plane:
    """A plane in 3D space defined by a normal vector and a point.

    Parameters
    ----------
    normal : np.ndarray
        Normal vector of the plane (will be normalized).
    point : np.ndarray
        A point on the plane.
    name : str, optional
        Name for this plane (used in string representation).
    """

    @classmethod
    def wireframe(cls, *planes: "Plane", innermost=True) -> List[tuple[np.ndarray, np.ndarray]]:
        """Given a set of intersecting planes, assumed to form a closed volume with side-length
        greater than 1e-9, make a wireframe of that volume.

        Parameters
        ----------
        *planes : Plane
            The planes defining the volume.
        innermost : bool
            If True, only return edges that are inside all planes.

        Returns
        -------
        List[tuple[np.ndarray, np.ndarray]]
            List of segment endpoints.
        """
        lines = set()
        segments = ApproxDict()
        for i, plane in enumerate(planes):
            for other in planes[i + 1 :]:
                line = plane.intersecting_line(other)
                if line is not None:
                    lines.add(line)

        for a, b, c in itertools.product(lines, lines, lines):
            if a == b or b == c or a == c:
                continue
            if (start := a.intersecting_point(b)) is not None and (
                end := a.intersecting_point(c)
            ) is not None:
                if np.allclose(start, end, atol=1e-9):
                    continue
                if innermost and any(
                    not p.allows_point(start) or not p.allows_point(end) for p in planes
                ):
                    continue
                start = tuple(start)  # tuples so we can key a dict
                end = tuple(end)
                if start not in segments.get(end, ApproxSet()):
                    segments.setdefault(start, ApproxSet()).add(end)
        return [
            (np.array(start), np.array(end)) for start, ends in segments.items() for end in ends
        ]

    @classmethod
    def from_3_points(
        cls, a: np.ndarray, b: np.ndarray, c: np.ndarray, name=None, tolerance=1e-9
    ) -> "Plane":
        """Create a plane from three points.

        The normal will be determined by the right-hand rule on the points.

        Parameters
        ----------
        a, b, c : np.ndarray
            Three points defining the plane.
        name : str, optional
            Name for the plane.
        tolerance : float
            Tolerance for determining if points are colinear.

        Returns
        -------
        Plane
            The plane defined by the three points.

        Raises
        ------
        ValueError
            If the points are colinear.
        """
        normal = np.cross(b - a, c - a)
        if np.linalg.norm(normal) < tolerance:
            raise ValueError("We cannot find a single plane from colinear points")
        return cls(normal, a, name)

    def __init__(self, normal, point, name=None):
        self.normal = normal / np.linalg.norm(normal)
        self.point = point
        self.name = name

    def intersecting_point(self, line: Line, tolerance=1e-9) -> np.ndarray | None:
        """Find the intersection point of this plane with a line.

        Parameters
        ----------
        line : Line
            The line to intersect with.
        tolerance : float
            Tolerance for determining if line is parallel to plane.

        Returns
        -------
        np.ndarray | None
            The intersection point, or None if line is parallel to plane.
        """
        denom = np.dot(self.normal, line.direction)
        if abs(denom) < tolerance:
            # parallel or even coplanar
            return None
        t = np.dot(self.normal, self.point - line.point) / denom
        return line.point + t * line.direction

    def contains_point(self, pt: np.ndarray, tolerance: float = 1e-9) -> bool:
        """Check if a point lies on this plane.

        Parameters
        ----------
        pt : np.ndarray
            Point to check.
        tolerance : float
            Tolerance for the check.

        Returns
        -------
        bool
            True if point is on the plane.
        """
        # If the dot product is close to zero, the point is on the plane
        dot_product = np.dot(pt - self.point, self.normal)
        return abs(dot_product) < tolerance

    def coplanar_with(self, other: "Plane", tolerance=1e-9) -> bool:
        """Return whether this plane is coplanar with another, within the given tolerance.

        Parameters
        ----------
        other : Plane
            The other plane.
        tolerance : float
            Tolerance for the check.

        Returns
        -------
        bool
            True if planes are coplanar.
        """
        if not np.allclose(np.cross(self.normal, other.normal), 0, atol=tolerance):
            return False
        return abs(self.distance_to_point(other.point)) < tolerance

    def distance_to_point(self, pt: np.ndarray) -> float:
        """Return the signed distance from the plane to a point.

        Positive distances are in the direction of the normal.

        Parameters
        ----------
        pt : np.ndarray
            Point to measure distance to.

        Returns
        -------
        float
            Signed distance from plane to point.
        """
        return np.dot(self.normal, pt - self.point)

    def allows_point(self, pt: np.ndarray, tolerance=1e-9):
        """Return whether a point is on the correct side of the boundary.

        Parameters
        ----------
        pt : np.ndarray
            Point to check.
        tolerance : float
            Tolerance for the check.

        Returns
        -------
        bool
            True if point is on the positive side of the plane (or on it).
        """
        return self.distance_to_point(pt) > -abs(tolerance)

    def intersecting_line(self, other: "Plane") -> Line | None:
        """Find the line of intersection between this plane and another.

        Parameters
        ----------
        other : Plane
            The other plane.

        Returns
        -------
        Line | None
            The line of intersection, or None if planes are parallel.
        """
        direction = np.cross(self.normal, other.normal)
        if np.allclose(direction, 0):
            return None

        # Normalize the direction vector
        direction = direction / np.linalg.norm(direction)

        # Calculate a point on the intersection line
        n1n2 = np.dot(self.normal, other.normal)
        n1n1 = np.dot(self.normal, self.normal)
        n2n2 = np.dot(other.normal, other.normal)
        c1 = np.dot(self.normal, self.point)
        c2 = np.dot(other.normal, other.point)

        det = n1n1 * n2n2 - n1n2 * n1n2
        c1n2 = c1 * n2n2 - c2 * n1n2
        c2n1 = c2 * n1n1 - c1 * n1n2

        point = (c1n2 * self.normal + c2n1 * other.normal) / det
        return Line(direction, point)

    @property
    def coefficients(self):
        """Get the plane equation coefficients (a, b, c, d) for ax + by + cz + d = 0.

        Returns
        -------
        tuple[float, float, float, float]
            The coefficients (a, b, c, d).
        """
        a, b, c = self.normal
        d = -np.dot(self.normal, self.point)
        return a, b, c, d

    def __str__(self):
        if self.name is not None:
            return self.name
        a, b, c, d = self.coefficients
        return f"Plane({a}x + {b}y + {c}z + {d} = 0)"

    def __repr__(self):
        return str(self)
