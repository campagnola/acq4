"""Primitive 3D shape generation functions."""
from __future__ import annotations

import numpy as np


def truncated_cone(
    bottom_radius: float,
    top_radius: float,
    height: float,
    close_top: bool = False,
    close_bottom: bool = False,
    segments: int = 32,
) -> (np.ndarray, np.ndarray):
    """Generate vertices and faces for a truncated cone (frustum).

    Parameters
    ----------
    bottom_radius : float
        Radius of the bottom circle.
    top_radius : float
        Radius of the top circle.
    height : float
        Height of the cone.
    close_top : bool
        Whether to close the top with a cap.
    close_bottom : bool
        Whether to close the bottom with a cap.
    segments : int
        Number of segments around the circumference.

    Returns
    -------
    vertices : np.ndarray
        Array of vertex positions.
    faces : np.ndarray
        Array of face indices.
    """
    theta = np.linspace(0, 2 * np.pi, segments, endpoint=False)
    bottom_circle = np.column_stack(
        (bottom_radius * np.cos(theta), bottom_radius * np.sin(theta), np.zeros(segments))
    )
    top_circle = np.column_stack(
        (top_radius * np.cos(theta), top_radius * np.sin(theta), np.full(segments, height))
    )

    vertices = np.vstack((bottom_circle, top_circle))

    faces = []
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.extend(
            (
                [i, next_i, segments + next_i],
                [i, segments + next_i, segments + i],
            )
        )

    if close_bottom:
        bottom_center = len(vertices)
        vertices = np.vstack((vertices, [[0, 0, 0], [0, 0, height]]))
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([i, next_i, bottom_center])
    if close_top:
        top_center = len(vertices)
        vertices = np.vstack((vertices, [[0, 0, height]]))
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([segments + i, segments + next_i, top_center])

    return vertices, np.array(faces)
