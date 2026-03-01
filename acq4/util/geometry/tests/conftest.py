"""Shared fixtures for geometry tests."""
import numpy as np
import pytest

from acq4.util.geometry import Geometry, GeometryMotionPlanner, Plane


@pytest.fixture(autouse=True)
def clear_planner_cache():
    """Clear the motion planner cache before each test."""
    GeometryMotionPlanner.clear_cache()


@pytest.fixture
def geometry():
    """A simple 1x1x1 box geometry centered at the origin."""
    return Geometry({"type": "box", "size": [1.0, 1.0, 1.0]}, "test_mesh", "test")


@pytest.fixture
def cube():
    """Six planes forming a unit cube from (0,0,0) to (1,1,1)."""
    return [
        Plane(np.array([1, 0, 0]), np.array([0, 0, 0])),
        Plane(np.array([0, 1, 0]), np.array([0, 0, 0])),
        Plane(np.array([0, 0, 1]), np.array([0, 0, 0])),
        Plane(np.array([-1, 0, 0]), np.array([1, 1, 1])),
        Plane(np.array([0, -1, 0]), np.array([1, 1, 1])),
        Plane(np.array([0, 0, -1]), np.array([1, 1, 1])),
    ]
