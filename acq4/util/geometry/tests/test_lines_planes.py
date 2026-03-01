"""Tests for Line, Plane, and wireframe operations."""
import numpy as np
import pytest

from acq4.util.geometry import Line, Plane


def assert_all_intersect_at(pt, *lines):
    for a in lines:
        for b in lines:
            if a == b:
                # point can be arbitrary
                assert a.intersecting_point(b) is not None
                assert b.intersecting_point(a) is not None
            else:
                assert np.allclose(
                    x := a.intersecting_point(b), pt
                ), f"{a} and {b} intersect at {x}, not {pt}"
                assert np.allclose(
                    x := b.intersecting_point(a), pt
                ), f"{b} and {a} intersect at {x}, not {pt}"


def test_line_intersections():
    a = Line(np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, 0.0]))

    assert_all_intersect_at(
        np.array([0.0, 0.0, 0.0]),
        a,
        Line(np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 0.0])),
        Line(np.array([0.0, 0.0, 1.0]), np.array([0.0, 0.0, 0.0])),
        Line(np.array([0.0, 0.0, 1.0]), np.array([0.0, 0.0, 10.0])),
        Line(np.array([0.0, 0.0, -1.0]), np.array([0.0, 0.0, 10.0])),
        Line(np.array([0.0, -1.0, 1.0]), np.array([0.0, 1.0, -1.0])),
        Line(np.array([1.0, 1.0, 1.0]), np.array([3.14159, 3.14159, 3.14159])),
    )

    b = Line(np.array([0.0, 1.0, 0.0]), np.array([1.0, 1.0, 1.0]))
    assert a.intersecting_point(b) is None
    assert b.intersecting_point(a) is None


def test_wireframe(cube):
    wireframe = Plane.wireframe(*cube)
    assert len(wireframe) == 12
    wireframe = np.array(wireframe)
    assert wireframe.shape == (12, 2, 3)

    assert np.any(np.all(wireframe == np.array([[0, 0, 0], [1, 0, 0]]), axis=1))
    assert np.any(np.all(wireframe == np.array([[0, 0, 0], [0, 1, 0]]), axis=1))
    assert np.any(np.all(wireframe == np.array([[0, 0, 0], [0, 0, 1]]), axis=1))
    assert np.any(np.all(wireframe == np.array([[1, 1, 1], [0, 1, 1]]), axis=1))
    assert np.any(np.all(wireframe == np.array([[1, 1, 1], [1, 0, 1]]), axis=1))
    assert np.any(np.all(wireframe == np.array([[1, 1, 1], [1, 1, 0]]), axis=1))


def test_allows_point():
    plane = Plane(np.array((0, 0, 1)), np.array((0, 0, 0)))
    assert plane.allows_point(np.array((0, 0, 0)))
    assert plane.allows_point(np.array((0, 0, 1)))
    assert plane.allows_point(np.array((0, 0, 1e-9)))
    assert plane.allows_point(np.array((0, 0, -1e-10)))
    assert not plane.allows_point(np.array((0, 0, -1e-9)))
    assert not plane.allows_point(np.array((0, 0, -1)))


def test_wireframe_acq4():
    bounds = [
        Plane(
            np.array([9.99999971e-01, -2.41127827e-04, -4.41750099e-07]),
            np.array([0.00012748, -0.00034118, -0.00010044]),
        ),
        Plane(
            np.array([-9.99999971e-01, -2.41237557e-04, -4.41951126e-07]),
            np.array([0.14022748, 0.13975882, 0.13999956]),
        ),
        Plane(
            np.array([2.27538386e-04, 9.99999974e-01, -4.41957183e-07]),
            np.array([0.00012748, -0.00034118, -0.00010044]),
        ),
        Plane(
            np.array([2.27428656e-04, -9.99999974e-01, -4.41744050e-07]),
            np.array([0.14022748, 0.13975882, 0.13999956]),
        ),
        Plane(
            np.array([2.27483601e-04, -2.41182780e-04, 9.99999945e-01]),
            np.array([0.00012748, -0.00034118, -0.00010044]),
        ),
        Plane(
            np.array([2.27483400e-04, -2.41182566e-04, -9.99999945e-01]),
            np.array([0.14022748, 0.13975882, 0.13999956]),
        ),
    ]
    wireframe = Plane.wireframe(*bounds)
    assert len(wireframe) == 12
    wireframe = np.array(wireframe)
    assert wireframe.shape == (12, 2, 3)


def test_nested_wireframes_only_show_the_innermost(cube):
    inner_cube = [Plane(p.normal, p.point / 2) for p in cube]
    edges = Plane.wireframe(*cube, *inner_cube)
    assert len(edges) == 12
    for e in edges:
        for pt in e:
            for val in pt:
                assert val in [0, 0.5]


def test_wireframe_rhomboid():
    rhomboid = [
        Plane(np.array([1, 0, 1]), np.array([0, 0, 0])),
        Plane(np.array([0, 1, 1]), np.array([0, 0, 0])),
        Plane(np.array([0, 0, 1]), np.array([0, 0, 0])),
        Plane(np.array([-1, 0, -1]), np.array([1, 1, 1])),
        Plane(np.array([0, -1, -1]), np.array([1, 1, 1])),
        Plane(np.array([0, 0, -1]), np.array([1, 1, 1])),
    ]
    wireframe = Plane.wireframe(*rhomboid)
    assert len(wireframe) == 12
    wireframe = np.array(wireframe)
    assert wireframe.shape == (12, 2, 3)

    assert np.any(np.all(wireframe == np.array([[-1, 0, 0], [1, 0, 0]]), axis=1))
    assert np.any(np.all(wireframe == np.array([[1, 1, 1], [0, 1, 0]]), axis=1))

