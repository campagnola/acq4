"""Motion planning with collision avoidance."""
from __future__ import annotations

from threading import RLock
from typing import TYPE_CHECKING, Dict

import numpy as np
from coorx import Point, Transform
from pyqtgraph import debug
from pyqtgraph.debug import Profiler
from pyqtgraph.units import µm

from .pathfinding import a_star_ish, rrt_connect, simplify_path

if TYPE_CHECKING:
    from .lines_planes import Plane
    from .shapes import Geometry


def point_in_bounds(point, bounds):
    """Return True if the given point is inside the given bounds.

    Also return the first plane that the point is outside of, if any.

    Parameters
    ----------
    point : np.ndarray
        Point to check.
    bounds : list[Plane]
        List of planes defining the bounds.

    Returns
    -------
    tuple[bool, Plane | None]
        (True, None) if point is in bounds, (False, plane) if not.
    """
    for plane in bounds:
        if plane.distance_to_point(point) < 0:
            return False, plane
    return True, None


class GeometryMotionPlanner:
    """Motion planner that finds collision-free paths through a set of geometry obstacles."""

    _cache = {}
    _cache_lock = RLock()

    @classmethod
    def clear_cache(cls):
        """Clear the cached convolved obstacles."""
        with cls._cache_lock:
            cls._cache = {}

    def __init__(self, geometries: Dict["Geometry", Transform], voxel_size: float = 200 * µm):
        """
        Parameters
        ----------
        geometries : Dict[Geometry, Transform]
            Dictionary of Geometry instances representing all collision objects in the world
            and the transform that respectively takes them to the global coordinate system.
        voxel_size : float
            Resolution of the voxel grid used for path planning.
        """
        self._draw_n = 0
        self.geometries = geometries
        self.voxel_size = voxel_size

    def find_path(self, *args, **kwargs):
        """Find a path using the specified mode.

        Parameters
        ----------
        mode : str
            Either 'A*' or 'RRT Connect' (default).
        *args, **kwargs
            Passed to the underlying pathfinding method.

        Returns
        -------
        list
            List of global positions to get from start to stop.
        """
        if (mode := kwargs.pop("mode", "RRT Connect")) == "A*":
            return self.find_path_astar(*args, **kwargs)
        elif mode == "RRT Connect":
            return self.find_path_rrt(*args, **kwargs)
        else:
            raise ValueError(f"Invalid pathfinding mode: {mode}. Use 'A*' or 'RRT Connect'.")

    def find_path_astar(
        self,
        traveler: "Geometry",
        to_global_from_traveler: Transform,
        start,
        stop,
        bounds=None,
        callback=None,
        visualizer: "VisualizePathPlan" = None,
    ):
        """
        Return a path from *start* to *stop* in the global coordinate system that *traveling_object*
        can follow to avoid collisions.

        Method:
        1. Create voxelized representations of traveling_object in the coordinate systems of all
           other geometries:
           - traveling_object.voxelize (in coordinate system of traveling_object)
           - take mirror image of volume; this becomes the convolution kernel
           - the center of the kernel needs to be mirrored as well
        2. Create convolutions between all other geometries and traveling_object:
           - geometry.voxelize (in local coordinate system)
           - volume.convolve(geometry_voxels, traveling_kernel)
        3. Do a path-finding algorithm that, at each step, checks for collisions among all
           convolved volumes:
           - A* (ish)
           - volume.check_edge_collision

        Parameters
        ----------
        traveler : Geometry
            Geometry representing the object to be moved from *start* to *stop*.
        to_global_from_traveler : Transform
            Transform that maps from the traveling_object's local coordinate system to global.
        start : np.ndarray
            Global coordinates of the traveling object's origin when at initial location.
        stop : np.ndarray
            Global coordinates of the final location we want the traveling object's origin to be.
        callback : callable
            A function to be called at each step of the path planning process (mostly to aid in
            visualization and debugging).
        bounds : list[Plane]
            Planes that define the bounds of the space in which the path is to be found.
        visualizer : VisualizePathPlan or None
            If not None, a VisualizePathPlan to visualize the path planning process.

        Returns
        -------
        list
            List of global positions to get from start to stop.
        """
        profile = debug.Profiler()
        start = Point(start, "global")
        stop = Point(stop, "global")
        bounds = [] if bounds is None else bounds
        if visualizer is not None:
            visualizer.startPath([start.coordinates, stop.coordinates], bounds)
        in_bounds, bound_plane = point_in_bounds(start.coordinates, bounds)
        if not in_bounds:
            raise ValueError(
                f"Starting point {start} is on the wrong side of the {bound_plane} boundary"
            )
        profile.mark("basic setup")

        obstacles = self.make_convolved_obstacles(traveler, to_global_from_traveler, visualizer)
        profile.mark("made convolved obstacles")

        for i, _o in enumerate(obstacles):
            obst_volume, to_global_from_obst, obst_name = _o
            # obst = list(self.geometries.keys())[i]
            # users will sometimes drive the hardware to where the motion planner would consider
            # things impossible
            # TODO pull pipette out along its axis to start
            # if obst_volume.contains_point(to_global_from_obst.inverse.map(start)):
            #     raise ValueError(f"Start point {start} is inside obstacle {obst.name}")
            if obst_volume.contains_point(to_global_from_obst.inverse.map(stop)):
                raise ValueError(f"Destination point {stop} is inside obstacle {obst_name}")

        profile.mark("voxelized all obstacles")

        def edge_cost(a: np.ndarray, b: np.ndarray):
            prof = Profiler(disabled=False)
            if not point_in_bounds(b, bounds)[0]:
                prof.mark("bounds check")
                return np.inf
            prof.mark("bounds check")
            a = Point(a, start.system)
            b = Point(b, start.system)
            for vol, to_global, _ in obstacles:
                intersects = vol.intersects_line(to_global.inverse.map(a), to_global.inverse.map(b))
                prof.mark(f"intersection check {to_global.systems[0].name}")
                if intersects:
                    return np.inf
            return np.linalg.norm(b - a)

        path = a_star_ish(start.coordinates, stop.coordinates, edge_cost, callback=callback)
        profile.mark("A*")
        path = simplify_path(path, edge_cost)
        profile.mark("simplified path")
        if callback:
            callback(path, skip=1)
        profile.finish()
        return path[1:]

    def find_path_rrt(
        self,
        traveler: "Geometry",
        to_global_from_traveler: Transform,
        start,
        stop,
        bounds=None,
        callback=None,
        visualizer: "VisualizePathPlan" = None,
    ):
        """
        Return a path from *start* to *stop* in the global coordinate system that *traveling_object*
        can follow to avoid collisions.

        Method:
        1. Create voxelized representations of traveling_object in the coordinate systems of all
           other geometries:
           - traveling_object.voxelize (in coordinate system of traveling_object)
           - take mirror image of volume; this becomes the convolution kernel
           - the center of the kernel needs to be mirrored as well
        2. Create convolutions between all other geometries and traveling_object:
           - geometry.voxelize (in local coordinate system)
           - volume.convolve(geometry_voxels, traveling_kernel)
        3. Do a path-finding algorithm that, at each step, checks for collisions among all
           convolved volumes:
           - RRT-Connect (bidirectional rapidly-exploring random tree)
           - volume.check_edge_collision

        Parameters
        ----------
        traveler : Geometry
            Geometry representing the object to be moved from *start* to *stop*.
        to_global_from_traveler : Transform
            Transform that maps from the traveling_object's local coordinate system to global.
        start : np.ndarray
            Global coordinates of the traveling object's origin when at initial location.
        stop : np.ndarray
            Global coordinates of the final location we want the traveling object's origin to be.
        callback : callable
            A function to be called at each step of the path planning process (mostly to aid in
            visualization and debugging).
        bounds : list[Plane]
            Planes that define the bounds of the space in which the path is to be found.
        visualizer : VisualizePathPlan or None
            If not None, a VisualizePathPlan to visualize the path planning process.

        Returns
        -------
        list
            List of global positions to get from start to stop.
        """
        profile = debug.Profiler()
        start = Point(start, "global")
        stop = Point(stop, "global")
        bounds = [] if bounds is None else bounds
        if visualizer is not None:
            visualizer.startPath([start.coordinates, stop.coordinates], bounds)
        in_bounds, bound_plane = point_in_bounds(start.coordinates, bounds)
        if not in_bounds:
            raise ValueError(
                f"Starting point {start} is on the wrong side of the {bound_plane} boundary"
            )
        profile.mark("basic setup")

        obstacles = self.make_convolved_obstacles(traveler, to_global_from_traveler, visualizer)
        profile.mark("made convolved obstacles")

        for i, _o in enumerate(obstacles):
            obst_volume, to_global_from_obst, obst_name = _o
            # obst = list(self.geometries.keys())[i]
            # users will sometimes drive the hardware to where the motion planner would consider
            # things impossible
            # TODO pull pipette out along its axis to start
            # if obst_volume.contains_point(to_global_from_obst.inverse.map(start)):
            #     raise ValueError(f"Start point {start} is inside obstacle {obst.name}")
            if obst_volume.contains_point(to_global_from_obst.inverse.map(stop)):
                raise ValueError(f"Destination point {stop} is inside obstacle {obst_name}")

        profile.mark("voxelized all obstacles")

        def edge_cost_intersection(a: np.ndarray, b: np.ndarray):
            if not point_in_bounds(b, bounds)[0]:
                return np.inf
            a = Point(a, start.system)
            b = Point(b, start.system)
            for vol, to_global, _ in obstacles:
                if vol.intersects_line(to_global.inverse.map(a), to_global.inverse.map(b)):
                    return np.inf
            return np.linalg.norm(b - a)

        def edge_cost_walk(a: np.ndarray, b: np.ndarray):
            if not point_in_bounds(b, bounds)[0]:
                return np.inf
            a = Point(a, start.system)
            b = Point(b, start.system)
            edge_dist = np.linalg.norm(b - a)
            if edge_dist < self.voxel_size:
                step = b - a
                iterations = 1
            else:
                step = self.voxel_size * (b - a) / edge_dist
                iterations = int(np.ceil(edge_dist / self.voxel_size))

            curr = a
            for _ in range(iterations):
                for vol, to_global, _ in obstacles:
                    if vol.contains_point(to_global.inverse.map(curr)):
                        return np.inf
                curr = Point(curr.coordinates + step, start.system)
            return edge_dist

        # Calculate appropriate step size based on voxel size and distance
        distance = np.linalg.norm(stop.coordinates - start.coordinates)
        step_size = min(distance / 10, self.voxel_size * 5)
        step_size = max(step_size, self.voxel_size)

        # Use RRT-Connect for pathfinding
        path = rrt_connect(
            start.coordinates,
            stop.coordinates,
            edge_cost_intersection,
            max_iterations=4000,
            step_size=step_size,
            goal_sample_rate=0.2,
            callback=callback,
        )

        profile.mark("RRT-Connect")

        if callback:
            callback(path, skip=1)
        profile.finish()
        return path[1:] if len(path) > 1 else path

    def make_convolved_obstacles(self, traveler, to_global_from_traveler, visualizer=None):
        """Create convolved obstacle volumes for collision checking.

        Parameters
        ----------
        traveler : Geometry
            The geometry that will be moving through the space.
        to_global_from_traveler : Transform
            Transform from traveler coordinates to global.
        visualizer : VisualizePathPlan, optional
            Visualizer for debugging.

        Returns
        -------
        list[tuple[Volume, Transform, str]]
            List of (convolved volume, transform to global, obstacle name) tuples.
        """
        obstacles = []
        for obst, to_global_from_obst in self.geometries.items():
            if obst is traveler:
                continue
            cache_key = (obst.name, traveler.name)
            with self._cache_lock:
                if cache_key not in self._cache:
                    convolved_obst = obst.make_convolved_voxels(
                        traveler,
                        to_global_from_obst.inverse * to_global_from_traveler,
                        self.voxel_size,
                    )
                    # TODO is this bad? explicitly setting transforms frequently is...
                    convolved_obst.transform = obst.transform * convolved_obst.transform
                    self._cache[cache_key] = convolved_obst
                obst_volume = self._cache[cache_key]

            obstacles.append((obst_volume, to_global_from_obst, obst.name))
            if visualizer is not None:
                visualizer.addObstacle(obst.name, obst_volume, to_global_from_obst).raiseErrors(
                    "obstacle failed to render"
                )
        return obstacles
