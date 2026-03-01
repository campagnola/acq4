"""Tests for voxelization, line intersection, and convolution operations."""
import numpy as np
import pytest

from coorx import NullTransform, TTransform, SRT3DTransform, Point

from acq4.util.geometry import Geometry, Volume


@pytest.mark.parametrize(
    "to_parent",
    [
        NullTransform(3),
        TTransform(offset=(-3, -3, -3)),
        TTransform(offset=(4.5, 4.5, 4.5)),
        SRT3DTransform(offset=(8.2, 8.2, -8.2), angle=30, axis=(0, 1, 0)),
        SRT3DTransform(offset=(-8.2, 8.2, 8.2), angle=30, axis=(0, 1, 0)),
        SRT3DTransform(offset=(-8.2, 8.2, -8.2), scale=(0.1, 0.1, 0.1), angle=30, axis=(0, 1, 0)),
    ],
)
def test_line_intersects_voxel(to_parent):
    to_parent.set_systems("global", "parent")

    def point(coords):
        # points are written relative to the volume origin, so we need to move them, but we need to pretend they were
        # always in parent
        return Point(to_parent.map(np.array(coords)), "parent")

    voxel = Volume(np.ones((3, 3, 3), dtype=bool), to_parent)
    assert voxel.intersects_line(point([-1, -1, -1]), point([4, 4, 4]))
    assert voxel.intersects_line(point([-1, -1, -1]), point([5, 5, 1]))
    assert not voxel.intersects_line(point([-1, -1, -1]), point([5, 5, 0]))
    assert not voxel.intersects_line(point([-1, -1, -1]), point([5, 5, -1]))
    a_bit = np.array([0, 0, 1e-6])
    assert not voxel.intersects_line(point([-1, 1.1, 2]), point([1, 1.1, 4] + a_bit))
    assert voxel.intersects_line(point([-1, 1.1, 2]), point([1, 1.1, 4] - a_bit))


def test_identity_convolve(geometry):
    kernel_array = np.ones((1, 1, 1), dtype=bool)
    orig = geometry.voxel_template(0.1)
    center = np.array((0, 0, 0))
    convolved = orig.convolve(kernel_array, center=center, name=geometry.name)
    assert np.all(convolved.volume == orig.volume)
    assert np.all(convolved.transform.map((0, 0, 0)) == orig.transform.map((0, 0, 0)))




def test_translated_convolve(geometry):
    kernel_array = np.ones((1, 1, 1), dtype=bool)
    voxel_size = 0.1
    orig = geometry.voxel_template(voxel_size)
    center = np.array([-10, 0, 100])  # off the grid centers are allowed
    convolved = orig.convolve(kernel_array, center=center, name="fake")
    assert np.all(convolved.volume == orig.volume)
    assert np.allclose(
        convolved.inverse_transform.map((0, 0, 0)) - center,
        orig.inverse_transform.map((0, 0, 0)),
    )


def test_offcenter_convolve(geometry):
    kernel_array = np.zeros((3, 3, 3), dtype=bool)
    kernel_array[1, 1, 1] = True
    orig = geometry.voxel_template(0.1)
    center = np.array((1, 1, 1))
    convolved = orig.convolve(kernel_array, center=center, name="fake")
    # we usually won't have kernels with empty edges, so this 1:-1 step is only needed for this test
    assert np.allclose(convolved.volume[1:-1, 1:-1, 1:-1], orig.volume)
    assert np.allclose(
        convolved.inverse_transform.map((0, 0, 0)) - center, orig.inverse_transform.map((0, 0, 0))
    )


def test_convolve_growth(geometry):
    dot = Geometry({"type": "box", "size": [0.1, 0.1, 0.1]}, "dot_mesh", "dot").voxel_template(0.1)
    kernel_array = geometry.voxel_template(0.1).volume
    center = np.array((0, 0, 0))
    convolved = dot.convolve(kernel_array, center=center, name=geometry.name)
    assert np.all(convolved.volume == kernel_array)


def test_single_voxel_voxelization(geometry, visualize):
    voxel_size = 1.0
    template = geometry.voxel_template(voxel_size)
    if visualize:
        import pyqtgraph as pg
        import pyqtgraph.opengl as gl

        w = gl.GLViewWidget()
        w.show()
        w.setCameraPosition(distance=20)
        g = gl.GLGridItem()
        g.scale(1, 1, 1)
        w.addItem(g)

        mesh = gl.MeshData(vertexes=geometry.mesh.vertices, faces=geometry.mesh.faces)
        m = gl.GLMeshItem(meshdata=mesh, smooth=False, color=(1, 0, 0, 0.5))
        m.setTransform(geometry.transform.as_pyqtgraph())
        w.addItem(m)

        vol = np.zeros(template.volume.T.shape + (4,), dtype=np.ubyte)
        vol[..., :3] = (30, 30, 100)
        vol[..., 3] = template.volume.T * 20
        v = gl.GLVolumeItem(vol, sliceDensity=10, smooth=False)
        v.setTransform((geometry.transform * template.transform).as_pyqtgraph())
        w.addItem(v)

        pg.exec()
    assert isinstance(template, Volume)
    assert template.volume.shape == (1, 1, 1)
    assert np.all(template.volume)
    assert np.all(template.inverse_transform.map((0, 0, 0)) == np.array([0.5, 0.5, 0.5]))


def test_coarse_voxelization(geometry):
    voxel_size = 0.25  # units per vx
    template = geometry.voxel_template(voxel_size)
    assert isinstance(template, Volume)
    assert template.volume.shape == (5, 5, 5)  # not 4; the edge is in the next voxel over
    expected = np.ones((5, 5, 5), dtype=bool)
    expected[1:-1, 1:-1, 1:-1] = False
    assert np.all(template.volume == expected)
    assert np.all(template.inverse_transform.map((0, 0, 0)) == np.array([5 / 2, 5 / 2, 5 / 2]))
    corner = np.array([0.5, 0.5, 0.5])
    assert np.all(template.inverse_transform.map(corner) == np.array([4.5, 4.5, 4.5]))
    assert np.all(template.transform.map(np.array([0, 3, 0]) == np.array([-0.5, 0.25, -0.5])))


def test_voxelized(geometry):
    voxel_size = 0.1
    template = geometry.voxel_template(voxel_size)
    assert isinstance(template, Volume)
    assert template.volume.shape == (11, 11, 11)
    expected = np.ones((11, 11, 11), dtype=bool)
    expected[1:-1, 1:-1, 1:-1] = False
    assert np.all(template.volume == expected)
    origin = template.inverse_transform.map(np.array([0, 0, 0]))
    assert np.all(origin[:3] == np.array([11 / 2, 11 / 2, 11 / 2]))


def test_translated_voxels_have_no_knowledge_of_such():
    voxel_size = 0.1
    offset = np.array([1.0, -0.1, 10.0])
    config = {"type": "box", "size": [1.0, 1.0, 1.0], "transform": {"pos": offset}}
    geometry = Geometry(config, "test_mesh", "test")
    template = geometry.voxel_template(voxel_size)
    assert isinstance(template, Volume)
    assert template.volume.shape == (11, 11, 11)
    # inverse goes from geometry to voxel
    origin = template.inverse_transform.map(np.array([0, 0, 0]))
    assert np.all(origin[:3] == np.array([11 / 2, 11 / 2, 11 / 2]))


def test_cached_voxels_behave_well(geometry):
    voxel_size = 0.1
    template = geometry.voxel_template(voxel_size)

    template2 = geometry.voxel_template(voxel_size)
    assert np.all(template.volume == template2.volume)


def test_cached_convolutions_behave_well(geometry):
    kernel_array = np.ones((1, 1, 1), dtype=bool)
    voxel_size = 0.1
    orig = geometry.voxel_template(voxel_size)
    center = np.array([-10, 0, 100])
    convolved = orig.convolve(kernel_array, center=center, name="fake")
    convolved2 = orig.convolve(kernel_array, center=center, name="fake")
    assert np.all(convolved.volume == convolved2.volume)
