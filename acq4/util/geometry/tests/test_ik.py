import numpy as np
import pytest
from acq4.util.geometry import (
    Geometry,
    Volume,
    Plane,
    Line,
    point_in_bounds,
    neutral_anchored_inverse_kinematics,
    greedy_axis_inverse_kinematics,
)
from coorx.linear import AffineTransform


def test_neutral_anchored_inverse_kinematics_neutral():
    bounds, transform = overspecified()

    neutral_pt = [-1, 0, 0]
    neutral_pos = neutral_anchored_inverse_kinematics(
        neutral_pt, transform, bounds, [1, None, None, None]
    )
    assert np.allclose(neutral_pos, [1, 0, 0, 0])


def test_neutral_anchored_inverse_kinematics_in_bounds():
    bounds, transform = overspecified()

    in_bounds_pt = [-2, -2, -2]
    in_bounds_pos = neutral_anchored_inverse_kinematics(
        in_bounds_pt, transform, bounds, [1, None, None, None]
    )
    # x should be pinned at 1, d should be (2 - x) / half, z should be 2 - (d * half)
    assert np.allclose(in_bounds_pos, [1, 2, 1, 1 / HALF])
    # now a bunch of random in-bounds points
    for _ in range(100):
        rand_pos = [
            n if n is not None else np.random.uniform(b[0], b[1])
            for n, b in zip([1, None, None, None], bounds)
        ]
        rand_pt = transform.map(rand_pos)[:3]
        solved_pos = neutral_anchored_inverse_kinematics(
            rand_pt, transform, bounds, [1, None, None, None]
        )
        assert np.allclose(solved_pos, rand_pos)


def test_neutral_anchored_inverse_kinematics_with_zero_neutral():
    bounds, transform = overspecified()
    neutral = [0, None, None, None]

    pt = [-2, -2, -2]
    pos = neutral_anchored_inverse_kinematics(pt, transform, bounds, neutral)
    assert np.allclose(pos, [0, 2, 0, 2 / HALF])

    pt = [0, 0, 0]
    pos = neutral_anchored_inverse_kinematics(pt, transform, bounds, neutral)
    assert np.allclose(pos, [0, 0, 0, 0])

    pt = [-5 * HALF, -5, -5 * HALF]
    pos = neutral_anchored_inverse_kinematics(pt, transform, bounds, neutral)
    assert np.allclose(pos, [0, 5, 0, 5])

    pt = [-7, -2, -2]
    pos = neutral_anchored_inverse_kinematics(pt, transform, bounds, neutral)
    assert np.allclose(pos, [5, 2, 0, 2 / HALF])

    pt = [-5, -5, -5]
    pos = neutral_anchored_inverse_kinematics(pt, transform, bounds, neutral)
    assert np.allclose(pos, [5 - 5 * HALF, 5, 5 - 5 * HALF, 5])

    pt = [1, 1, 1]
    with pytest.raises(ValueError):
        neutral_anchored_inverse_kinematics(pt, transform, bounds, neutral)


def test_neutral_anchored_inverse_kinematics_with_diagonal_neutral():
    bounds, transform = overspecified()
    neutral = [None, None, None, 1]

    pt = [-2, -2, -2]
    pos = neutral_anchored_inverse_kinematics(pt, transform, bounds, neutral)
    assert np.allclose(pos, [2 - HALF, 2, 2 - HALF, 1])

    pt = [0, 0, 0]
    pos = neutral_anchored_inverse_kinematics(pt, transform, bounds, neutral)
    assert np.allclose(pos, [0, 0, 0, 0])

    pt = [-5 * HALF, -2, -5 * HALF]
    pos = neutral_anchored_inverse_kinematics(pt, transform, bounds, neutral)
    assert np.allclose(pos, [4 * HALF, 2, 4 * HALF, 1])

    pt = [-5 - 5 * HALF, -3, -5 - 5 * HALF]
    pos = neutral_anchored_inverse_kinematics(pt, transform, bounds, neutral)
    assert np.allclose(pos, [5, 3, 5, 5])

    pt = [-7, -2, -2]
    pos = neutral_anchored_inverse_kinematics(pt, transform, bounds, neutral)
    assert np.allclose(pos, [5, 2, 0, 2 / HALF])

    pt = [1, 1, 1]
    with pytest.raises(ValueError):
        neutral_anchored_inverse_kinematics(pt, transform, bounds, neutral)


def test_neutral_anchored_inverse_kinematics_extremes():
    bounds, transform = overspecified()

    origin_pt = [0, 0, 0]
    origin_pos = neutral_anchored_inverse_kinematics(
        origin_pt, transform, bounds, [1, None, None, None]
    )
    assert np.allclose(origin_pos, [0, 0, 0, 0])

    max_pt = [-5 - 5 * HALF, -5, -5 - 5 * HALF]
    max_pos = neutral_anchored_inverse_kinematics(max_pt, transform, bounds, [1, None, None, None])
    assert np.allclose(max_pos, [5, 5, 5, 5])


def test_neutral_anchored_inverse_kinematics_with_x():
    bounds, transform = overspecified()

    only_possible_with_x_pt = [-7, -2, -2]
    only_possible_with_x_pos = neutral_anchored_inverse_kinematics(
        only_possible_with_x_pt, transform, bounds, [1, None, None, None]
    )
    assert np.allclose(only_possible_with_x_pos, [5, 2, 0, 2 / HALF])
    # and a bunch more random points across the whole space
    bounds = np.asarray(bounds)
    for _ in range(100):
        rand_pos = np.random.uniform(bounds[:, 0], bounds[:, 1])
        rand_pos[0] = 1  # x is fixed at 1
        rand_pt = transform.map(rand_pos)[:3]
        solved_pos = neutral_anchored_inverse_kinematics(
            rand_pt, transform, bounds, [1, None, None, None]
        )
        assert np.allclose(solved_pos, rand_pos)


def test_neutral_anchored_inverse_kinematics_impossible():
    bounds, transform = overspecified()

    impossible = [
        [-2, -20, -2],
        [-2, -2, 10],
        [10, -2, -2],
        [-20, -2, -2],
        [-2, -2, -20],
        [0, 1, 0],
    ]
    for impossible_pt in impossible:
        with pytest.raises(ValueError):
            neutral_anchored_inverse_kinematics(
                impossible_pt, transform, bounds, [1, None, None, None]
            )
        with pytest.raises(ValueError):
            neutral_anchored_inverse_kinematics(
                impossible_pt, transform, bounds, [0, None, None, None]
            )


def test_greedy_axis_inverse_kinematics():
    bounds, transform = overspecified()

    point = [-3 * HALF, 0, -3 * HALF]
    start = [0, 0, 0, 0]
    preferred_axis_pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 3)
    assert np.allclose(preferred_axis_pos, [0, 0, 0, 3])

    point = [-2, 0, -4]
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 3)
    assert np.allclose(pos, [0, 0, 2, 2 / HALF])


def test_greedy_axis_inverse_kinematics_all_axes():
    bounds, transform = overspecified()
    point = [-3, -3, -3]
    start = [0, 0, 0, 0]

    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 0)
    assert np.allclose(pos, [3, 3, 3, 0])

    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 2)
    assert np.allclose(pos, [3, 3, 3, 0])

    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 3)
    assert np.allclose(pos, [0, 3, 0, 3 / HALF])


def test_greedy_axis_inverse_kinematics_along_each_axis():
    bounds, transform = overspecified()
    start = [0, 0, 0, 0]

    point = [-5, -1, 0]
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 0)
    assert np.allclose(pos, [5, 1, 0, 0])

    point = [-1, -5, -1]
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 1)
    # TODO should this recursively pick which axis to be greedy along?
    assert np.allclose(pos, [0, 5, 0, 1 / HALF])

    point = [-1, 0, -5]
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 2)
    assert np.allclose(pos, [1, 0, 5, 0])

    point = [-5 * HALF, -1, -5 * HALF]
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 3)
    assert np.allclose(pos, [0, 1, 0, 5])


def test_greedy_axis_inverse_kinematics_auto_axis():
    bounds, transform = overspecified()
    start = [0, 0, 0, 0]

    point = [-5, -1, 0]
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start)
    assert np.allclose(pos, [5, 1, 0, 0])

    point = [-1, -5, -1]
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start)
    assert np.allclose(pos, [0, 5, 0, 1 / HALF])

    point = [-3, -5, -1]  # y then x
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start)
    assert np.allclose(pos, [3, 5, 1, 0])

    point = [-1, 0, -5]
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start)
    assert np.allclose(pos, [1, 0, 5, 0])

    point = [-5 * HALF, -1, -5 * HALF]
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start)
    assert np.allclose(pos, [0, 1, 0, 5])


def test_greedy_axis_inverse_kinematics_impossible():
    bounds, transform = overspecified()
    impossible = [
        [-2, -20, -2],
        [-2, -2, 10],
        [10, -2, -2],
        [-20, -2, -2],
        [-2, -2, -20],
        [0, 1, 0],
    ]
    start = [0, 0, 0, 0]
    for impossible_pt in impossible:
        with pytest.raises(ValueError):
            greedy_axis_inverse_kinematics(impossible_pt, transform, bounds, start)
        with pytest.raises(ValueError):
            greedy_axis_inverse_kinematics(impossible_pt, transform, bounds, start, 0)
        with pytest.raises(ValueError):
            greedy_axis_inverse_kinematics(impossible_pt, transform, bounds, start, 1)
        with pytest.raises(ValueError):
            greedy_axis_inverse_kinematics(impossible_pt, transform, bounds, start, 2)
        with pytest.raises(ValueError):
            greedy_axis_inverse_kinematics(impossible_pt, transform, bounds, start, 3)


def test_greedy_axis_inverse_kinematics_past_boundaries():
    bounds, transform = overspecified()
    start = [0, 0, 0, 0]

    point = [-5 - 2 * HALF, 0, -2]
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 0)
    assert np.allclose(pos, [5, 0, 2 - 2 * HALF, 2])

    point = [-2, 0, -5 - 2 * HALF]
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 2)
    assert np.allclose(pos, [2 - 2 * HALF, 0, 5, 2])


def test_greedy_axis_inverse_kinematics_starting_point_adherence():
    bounds, transform = overspecified()
    start = [1, 1, 1, 1]

    point = [-3, 0, -3]
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 0)
    assert np.allclose(pos, [3 - HALF, 0, 3 - HALF, 1])

    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 2)
    assert np.allclose(pos, [3 - HALF, 0, 3 - HALF, 1])

    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 3)
    assert np.allclose(pos, [1, 0, 1, 2 / HALF])


def test_greedy_axis_inverse_kinematics_with_scaled_axis():
    """Greedy IK must correctly project displacement onto axes with non-unit scale.
    When an axis maps 1 device unit to >1 global unit, the projection must divide
    by axis_scale twice: once to normalize direction, once to convert global→device units.
    Without the double-division, the greedy projection overshoots, causing the solver
    to redistribute displacement away from the greedy axis into x/z.
    """
    bounds, transform = scaled_overspecified()
    # d-axis is [-3*HALF, 0, -3*HALF] with ||d|| = 3
    # So 1 device unit on d = 3 global units along that direction

    # Non-zero starting position exposes the bug: the inflated greedy projection
    # causes neutral_anchored_IK to compensate by using x/z instead of d
    start = [0, 0, 0, 1]

    # target is at device position [0, 0.5, 0, 0.5]
    target_dev = np.array([0, 0.5, 0, 0.5])
    point = list(transform.map(target_dev))
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 3)
    assert np.allclose(pos, target_dev), f"expected {target_dev}, got {pos}"

    # target at [0.5, 0.5, 0, 0.5]
    target_dev = np.array([0.5, 0.5, 0, 0.5])
    point = list(transform.map(target_dev))
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 3)
    assert np.allclose(pos, target_dev), f"expected {target_dev}, got {pos}"

    # target at [1, 0.5, 0, 0.5]
    target_dev = np.array([1, 0.5, 0, 0.5])
    point = list(transform.map(target_dev))
    pos = greedy_axis_inverse_kinematics(point, transform, bounds, start, 3)
    assert np.allclose(pos, target_dev), f"expected {target_dev}, got {pos}"

HALF = 2**0.5 / 2


def scaled_overspecified():
    """Like overspecified(), but the diagonal axis has a non-unit scale factor (3x).
    This makes axis_scale != 1 for axis 3, exposing projection bugs that
    divide by axis_scale the wrong number of times.
    """
    scale = 3
    x = [-1, 0, 0]
    y = [0, -1, 0]
    z = [0, 0, -1]
    d = [-scale * HALF, 0, -scale * HALF]  # 45° in x-z plane, but 3x longer
    transform = AffineTransform(np.asarray([x, y, z, d]).T, offset=np.zeros(3))
    bounds = [(0, 5)] * 4
    return bounds, transform


def overspecified():
    # keep the math easy and distinguishable, but still get coverage
    x = [-1, 0, 0]
    y = [0, -1, 0]
    z = [0, 0, -1]
    d = [-HALF, 0, -HALF]  # 45° in x-z plane
    transform = AffineTransform(np.asarray([x, y, z, d]).T, offset=np.zeros(3))
    bounds = [(0, 5)] * 4
    return bounds, transform
