"""Tests for Geometry shape creation and mesh operations."""
import numpy as np

from coorx import NullTransform

from acq4.util.geometry import Geometry


def test_mesh(geometry):
    mesh = geometry.mesh
    assert mesh is not None
    assert np.allclose(mesh.bounds, [[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]])


def test_cross_geometry_transform():
    geom_a = Geometry(
        {
            "type": "box",
            "size": [1.0, 1.0, 1.0],
            "transform": {"pos": (-10, 2, 100), "angle": 45, "axis": (0, 0, 1)},
        },
        "a_mesh",
        "a",
    )
    geom_b = Geometry(
        {"type": "box", "size": [1.0, 1.0, 1.0], "transform": {"pos": (50, 50, 50)}}, "b_mesh", "b"
    )
    from_a_to_global = NullTransform(3, from_cs=geom_a.parent_name, to_cs="global")
    from_b_to_global = NullTransform(3, from_cs=geom_b.parent_name, to_cs="global")
    from_a_to_b = (
        geom_b.transform.inverse * from_b_to_global.inverse * from_a_to_global * geom_a.transform
    )
    geom_c = geom_a.transformed_to(geom_b.transform, from_a_to_b)
    # geom_c's transform should be the same as geom_b's
    assert np.all(geom_c.transform.map((0, 0, 0)) == np.array([50, 50, 50]))
    # geom_c's mesh should be rotated and therefore the voxels should be wholly unique
    assert geom_c.voxel_template(0.1).volume.shape != geom_a.voxel_template(0.1).volume.shape
    assert geom_c.voxel_template(0.1).volume.shape != geom_b.voxel_template(0.1).volume.shape
    # TODO it would be nice to positively assert something about the transformed voxelization
    # TODO would they have about the same volume?
