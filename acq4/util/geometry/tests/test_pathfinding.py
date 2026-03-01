"""Tests for pathfinding and motion planning."""
import time

import numpy as np
import pytest

from coorx import NullTransform, TTransform, SRT3DTransform, Point

from acq4.util.geometry import Geometry, GeometryMotionPlanner, Plane, point_in_bounds

def test_find_path(geometry, viz):
    voxel_size = 0.1
    geometry_to_global = NullTransform(3, from_cs=geometry.parent_name, to_cs="global")
    planner = GeometryMotionPlanner({geometry: geometry_to_global}, voxel_size)
    traveler = Geometry(
        {"type": "box", "size": [voxel_size, voxel_size, voxel_size]}, "traveler_mesh", "traveler"
    )
    dest = Point(np.array([0, 0, 3]), "global")
    start = Point(np.array([0, 0, -2]), "global")
    traveler_to_global = NullTransform(3, from_cs=traveler.parent_name, to_cs="global")
    path = planner.find_path(traveler, traveler_to_global, start, dest, visualizer=viz)
    do_viz(viz, {traveler: traveler_to_global, geometry: geometry_to_global})

    assert path is not None
    assert len(path) >= 2
    assert not np.all(path[0] == start.coordinates)
    assert not np.all(path[0] == dest.coordinates)
    assert np.all(path[-1] == dest.coordinates)
    # walk along the path at voxel_size steps and assert that we haven't touched the box
    last_point = start
    geometry_vol = geometry.voxel_template(voxel_size)
    global_to_geom_mesh = geometry.transform.inverse * geometry_to_global.inverse
    for waypoint in path:
        assert not geometry.contains(
            waypoint, padding=voxel_size
        ), f"waypoint {waypoint} is within {voxel_size} of {geometry.mesh.bounds}"
        # TODO ugh! this line is intermittently failing....
        # assert not geometry_vol.intersects_line(global_to_geom_mesh.map(last_point), global_to_geom_mesh.map(waypoint)), f"line from {last_point} to {waypoint} intersects {geometry.mesh.bounds}"
        last_point = waypoint


@pytest.mark.xfail(reason="we aren't currently building for multi-pipette planning")
@pytest.mark.parametrize("offset", [(0, 0, 0), (1, 1, 1), (0.2, 0.2, 0.2), (0.6, 0.6, 0.6)])
def test_grazing_paths(offset, viz):
    vx = 1.0
    trav = Geometry({"type": "box", "size": [vx / 2, vx / 2, vx / 2]}, "trav", "trav_mesh")
    obst = Geometry(
        {
            "type": "box",
            "size": [vx * 0.9, vx * 0.9, vx * 0.9],
            "transform": {"pos": (0.05, 0.05, 0.05)},
        },
        "obst",
        "obst_mesh",
    )
    trav_to_global = SRT3DTransform(
        angle=90, axis=(1, 0, 1), offset=offset, from_cs=trav.parent_name, to_cs="global"
    )
    obst_to_global = TTransform(offset=(1, 1, 1.5), from_cs=obst.parent_name, to_cs="global")
    to_obst_parent_from_trav_parent = obst_to_global.inverse * trav_to_global
    conv_obst = obst.make_convolved_voxels(trav, to_obst_parent_from_trav_parent, vx)
    if viz:
        trav_mesh = trav.glMesh()
        viz.view.addItem(trav_mesh)
        viz.setMeshTransform(trav.name, trav_to_global.as_pyqtgraph())
        obst_mesh = obst.glMesh()
        viz.view.addItem(obst_mesh)
        viz.setMeshTransform(obst.name, obst_to_global.as_pyqtgraph())
        # viz.startPath(
        #     Point(np.array([0, 0, 0]), "trav").mapped_to("global"),
        #     Point(np.array([1.1, 2, 2]), "global"),
        #     [],
        # )
        viz.startPath(
            Point(np.array(offset), "global"),
            Point(np.array([2, 0, 2]), "global"),
            [],
        )
        viz.addObstacle(trav.voxel_template(vx), trav_to_global * trav.transform).wait()
        # viz.addObstacleVolumeOutline(obst.voxel_template(vx), obst_to_global * obst.transform).wait()
        viz.addObstacle(conv_obst, obst_to_global * obst.transform).wait()
        # to_obst_from_trav = obst.transform.inverse * to_obst_parent_from_trav_parent * trav.transform
        # xformed = trav.transformed_to(obst.transform, to_obst_from_trav)
        # xformed_voxels = xformed.voxel_template(vx)
        # viz.addObstacleVolumeOutline(xformed_voxels, obst_to_global * obst.transform)

        pg.exec()

    assert conv_obst.intersects_line(
        Point(np.array([0, 0, 0]), "trav").mapped_to("obst"),
        Point(np.array([1.1, 2, 2]), "global").mapped_to("obst"),
    )
    assert conv_obst.intersects_line(
        Point(np.array(offset), "global").mapped_to("obst"),
        Point(np.array([2, 0, 2]), "global").mapped_to("obst"),
    )
    for pt in obst.mesh.vertices:
        pt = Point(pt, "obst_mesh").mapped_to("obst")
        assert conv_obst.contains_point(pt), f"point {pt} is not in the convolved obstacle"


def test_z_and_x_are_not_swapped(viz):
    geometry = Geometry({"type": "box", "size": [10.0, 1.0, 1.0]}, "test_mesh", "test")
    voxel_size = 0.1
    from_geom_to_global = NullTransform(3, from_cs=geometry.parent_name, to_cs="global")
    start = Point(np.array([0, 0, 3]), "global")
    dest = Point(np.array([0, -4, 0]), "global")
    planner = GeometryMotionPlanner({geometry: from_geom_to_global}, voxel_size)
    traveler = Geometry(
        {"type": "box", "size": [voxel_size, voxel_size, voxel_size]}, "traveler_mesh", "traveler"
    )

    traveler_to_global = NullTransform(3, from_cs=traveler.parent_name, to_cs="global")
    path = planner.find_path(traveler, traveler_to_global, start, dest, visualizer=viz)
    do_viz(viz, {geometry: from_geom_to_global, traveler: traveler_to_global})
    assert path is not None

    with pytest.raises(ValueError):
        planner.find_path(
            traveler,
            NullTransform(3, from_cs=traveler.parent_name, to_cs="global"),
            start[::-1],
            dest,
            visualizer=viz,
        )
    do_viz(viz, {geometry: from_geom_to_global, traveler: traveler_to_global})


def test_path_with_funner_traveler(geometry, viz):
    voxel_size = 0.1
    traveler = Geometry(
        {
            "type": "cylinder",
            "radius": voxel_size,
            "height": 10 * voxel_size,
            "transform": {"angle": 45, "axis": (0, 1, 0)},
        },
        "traveler_mesh",
        "traveler",
    )
    start = Point(np.array([-0.4, -0.4, -1.2]), "global")
    dest = Point(np.array([0.2, 0.2, 3]), "global")
    to_global_from_geometry = NullTransform(3, from_cs="test", to_cs="global")
    planner = GeometryMotionPlanner({geometry: to_global_from_geometry}, voxel_size)
    to_global_from_traveler = TTransform(offset=start, from_cs="traveler", to_cs="global")
    path = planner.find_path(traveler, to_global_from_traveler, start, dest, visualizer=viz)
    do_viz(viz, {traveler: to_global_from_traveler, geometry: to_global_from_geometry})
    assert path is not None
    assert len(path) >= 2
    assert not np.all(path[0] == start)
    assert not np.all(path[0] == dest)


def test_bounds_prevent_path(geometry, cube, viz):
    voxel_size = 0.1
    traveler = Geometry(
        {
            "type": "cylinder",
            "radius": voxel_size,
            "height": 10 * voxel_size,
            "transform": {"angle": 45, "axis": (0, 1, 0)},
        },
        "traveler_mesh",
        "traveler",
    )
    start = Point(np.array([-0.4, -0.4, -1.2]), "global")
    dest = Point(np.array([0.2, 0.2, 3]), "global")
    planner = GeometryMotionPlanner(
        {geometry: NullTransform(3, from_cs="test", to_cs="global")}, voxel_size
    )
    traveler_to_global = TTransform(offset=start, from_cs="traveler", to_cs="global")
    with pytest.raises(ValueError):
        planner.find_path(traveler, traveler_to_global, start, dest, cube, visualizer=viz)
    do_viz(viz, {traveler: traveler_to_global})


@pytest.mark.xfail(reason="This scenario is highly unlikely, but we may fix it at some point")
def test_paths_stay_inside_bounds(geometry, viz):
    voxel_size = 1
    sqrt3 = 3**0.5
    sqrt6 = 6**0.5
    tetrahedron = [
        Plane(np.array([sqrt3 / 3, 0, -1 / 3]), np.array([0, 0, 10])),
        Plane(np.array([-sqrt3 / 6, -1 / 2, -1 / 3]), np.array([0, 0, 10])),
        Plane(np.array([-sqrt3 / 6, 1 / 2, -1 / 3]), np.array([0, 0, 10])),
        Plane(np.array([0, 0, 1]), np.array([0, 0, 0])),
    ]
    edges = Plane.wireframe(*tetrahedron)
    bottom_corners = {tuple(pt) for edge in edges for pt in edge if pt[2] == 0}
    start = bottom_corners.pop()
    start = Point(start, "global")
    stop = np.sum([np.array(c) for c in bottom_corners], axis=0) / 2
    stop = Point(stop, "global")

    edge_length = 10 * 4 / (6**0.5)
    transecting_obst = Geometry(
        {"type": "cylinder", "radius": voxel_size * 0.49, "height": edge_length},
        "blocker_mesh",
        "blocker",
    )
    obst_to_global = SRT3DTransform(
        offset=(0, -edge_length / 2, 0), angle=90, axis=(1, 0, 0), from_cs="blocker", to_cs="global"
    )
    trav_to_global = TTransform(offset=start, from_cs="test", to_cs="global")
    if viz:
        viz.startPath(start, stop, tetrahedron)
    planner = GeometryMotionPlanner({transecting_obst: obst_to_global}, voxel_size)
    try:
        for _ in range(1):
            path = planner.find_path(
                geometry, trav_to_global, start, stop, tetrahedron, visualizer=viz
            )
            for point in path:
                assert point_in_bounds(point, tetrahedron)
    finally:
        if viz:
            pg.exec()


def test_no_path(viz):
    geometry = Geometry({"type": "box", "size": [1.0, 1.0, 1.0]}, "test_mesh", "test")
    voxel_size = 0.1
    geometry_to_global = NullTransform(3, from_cs=geometry.parent_name, to_cs="global")
    planner = GeometryMotionPlanner({geometry: geometry_to_global}, voxel_size)
    traveler = Geometry(
        {
            "type": "box",
            "size": [voxel_size, voxel_size, 6 * voxel_size],
            "transform": {"pos": (0, 0, -0.3)},
        },
        "traveler_mesh",
        "traveler",
    )
    from_traveler_to_global = TTransform(offset=(0, 2, 3), from_cs="traveler", to_cs="global")
    start = from_traveler_to_global.map(Point(np.array([0, 0, 0]), "traveler"))
    dest = Point(np.array([voxel_size, voxel_size, voxel_size]) * 2, "global")  # inside the box
    with pytest.raises(ValueError):
        planner.find_path(traveler, from_traveler_to_global, start, dest, visualizer=viz)
    do_viz(viz, {geometry: geometry_to_global, traveler: from_traveler_to_global})


def test_no_path_because_of_shadow(geometry):
    voxel_size = 0.1
    traveler = Geometry(
        {
            "type": "cylinder",
            "radius": voxel_size,
            "height": 10 * voxel_size,
            "transform": {"angle": 45, "axis": (0, 1, 0)},
        },
        "traveler_mesh",
        "traveler",
    )
    point = Geometry(
        {"type": "box", "size": [voxel_size, voxel_size, voxel_size]}, "point_mesh", "point"
    )
    start = Point(np.array([0.7, 0, -0.7]), "global")
    dest = Point(np.array([0.2, 0.2, 5]), "global")
    planner = GeometryMotionPlanner(
        {geometry: NullTransform(3, from_cs=geometry.parent_name, to_cs="global")}, voxel_size
    )
    point_to_global = NullTransform(3, from_cs=point.parent_name, to_cs="global")
    path = planner.find_path(point, point_to_global, start, dest)
    assert path is not None
    traveler_to_global = NullTransform(3, from_cs=traveler.parent_name, to_cs="global")
    with pytest.raises(ValueError):
        planner.find_path(traveler, traveler_to_global, start, dest)


def test_no_path_because_of_offset_shadow(geometry, viz):
    voxel_size = 0.1
    traveler = Geometry(
        {
            "type": "cylinder",
            "radius": voxel_size,
            "height": 50 * voxel_size,
            "transform": {"angle": 45, "axis": (0, 1, 0)},
        },
        "traveler_mesh",
        "traveler",
    )
    point = Geometry(
        {"type": "box", "size": [voxel_size, voxel_size, voxel_size]}, "point_mesh", "point"
    )
    to_the_side = TTransform(offset=(1, 2, 3), from_cs="test", to_cs="global")
    from_geom_to_global = SRT3DTransform(
        offset=(1, 2, 3),
        angle=45,
        axis=(1, 0, 0),
        from_cs="test",
        to_cs="global",
    )
    dest = to_the_side.map(Point(np.array([0.7, 0, -0.7]), "test"))
    start = to_the_side.map(Point(np.array([0.2, 0.2, 5]), "test"))
    planner = GeometryMotionPlanner({geometry: from_geom_to_global}, voxel_size)
    point_to_global = TTransform(offset=start, from_cs="point", to_cs="global")
    path = planner.find_path(point, point_to_global, start, dest, visualizer=viz)
    do_viz(viz, {geometry: from_geom_to_global, point: point_to_global})
    assert path is not None
    traveler_to_global = TTransform(offset=start, from_cs="traveler", to_cs="global")
    with pytest.raises(ValueError):
        planner.find_path(traveler, traveler_to_global, start, dest, visualizer=viz)
    do_viz(viz, {geometry: from_geom_to_global, traveler: traveler_to_global})



def test_cylinder_pathfinding_performance():
    """
    Performance test for pathfinding in a challenging scenario:
    - Navigating from under a half-closed cylinder to a position just inside the top lip
    """
    voxel_size = 0.1
    height = 10.0
    radius = 5.0
    cylinder = Geometry(
        {
            "type": "cylinder",
            "radius": radius,
            "height": height,
            "close_bottom": True,
            "close_top": False,
        },
        "cylinder_mesh",
        "cylinder",
    )

    # Create a small traveler
    traveler = Geometry({"type": "box", "size": [0.5, 0.5, 0.5]}, "traveler_mesh", "traveler")

    cylinder_to_global = NullTransform(3, from_cs="cylinder", to_cs="global")
    planner = GeometryMotionPlanner({cylinder: cylinder_to_global}, voxel_size)
    traveler_to_global = NullTransform(3, from_cs="traveler", to_cs="global")

    # Start inside/under the cylinder
    start = Point(np.array([0.0, 0, -1.0]), "global")

    # End just inside the top lip - requires navigating around the edge
    end = Point(np.array([0, 0, height - 0.2]), "global")

    # Timing variables
    times = []
    path_lengths = []
    iterations = 5  # Number of iterations to run

    # First run (warm-up)
    print("\nRunning initial warm-up iteration...")
    start_time = time.time()
    path = planner.find_path(traveler, traveler_to_global, start, end)
    first_run_time = time.time() - start_time
    print(f"Initial run: {first_run_time:.4f}s, path length: {len(path)}")

    # Benchmark runs
    print(f"Running {iterations} benchmark iterations...")
    for i in range(iterations):
        start_time = time.time()
        path = planner.find_path(traveler, traveler_to_global, start, end)
        elapsed = time.time() - start_time
        times.append(elapsed)
        path_lengths.append(len(path))
        print(f"Iteration {i + 1}: {elapsed:.4f}s, path length: {len(path)}")

    # Report results
    avg_time = sum(times) / len(times)
    avg_path_length = sum(path_lengths) / len(path_lengths)

    print("\nResults:")
    print(f"Average execution time: {avg_time:.4f}s")
    print(f"Average path length: {avg_path_length:.1f} waypoints")
    print(f"Time range: {min(times):.4f}s - {max(times):.4f}s")

    return avg_time, avg_path_length, path



