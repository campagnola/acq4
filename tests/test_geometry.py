






class FakeDevice(Qt.QObject):
    sigGeometryChanged = Qt.pyqtSignal(str, str)
    sigGlobalTransformChanged = Qt.pyqtSignal(str, str)

    def __init__(self, name, geom, bounds=None):
        super().__init__()
        self._name = name
        self._bounds = bounds
        self.transform = NullTransform(3, from_cs=name, to_cs="global").as_pyqtgraph()
        self.geom = geom

    def name(self):
        return self._name

    def getGeometry(self, name=None):
        return self.geom

    def globalPhysicalTransform(self):
        return self.transform

    def getBoundaries(self):
        return self._bounds


if __name__ == "__main__":
    avg_time, avg_path_length, path = test_cylinder_pathfinding_performance()
    print(f"\nTarget performance: 0.2s or less (current: {avg_time:.4f}s)")

    import pyqtgraph as pg
    import pyqtgraph.opengl as gl

    pg.mkQApp()
    visualizer = VisualizerWindow(testing=True)
    visualizer.show()
    # geom = Geometry(
    #     {
    #         "type": "box",
    #         "size": [0.2, 0.2, 0.2],
    #         # "transform": {"angle": 45, "axis": (1, 1, 0)},
    #         "children": {
    #             "more rotated": {
    #                 "type": "box",
    #                 "size": [0.5, 0.5, 0.5],
    #                 "transform": {"pos": (1.5, 0, 0), "angle": 45, "axis": (0, 0, 1)},
    #             }
    #         },
    #     },
    #     "test_mesh",
    #     "test",
    # )
    geom = Geometry({"type": "box", "size": [1.0, 1.0, 1.0]}, "test_mesh", "test")
    some_bounds = [
        Plane(np.array([1, 0, 0]), np.array([0, 0, 0])),
        Plane(np.array([0, 1, 0]), np.array([0, 0, 0])),
        Plane(np.array([0, 0, 1]), np.array([0, 0, 0])),
        Plane(np.array([1, 0, 0]), np.array([1, 1, 1])),
        Plane(np.array([0, 1, 0]), np.array([1, 1, 1])),
        Plane(np.array([0, 0, 1]), np.array([1, 1, 1])),
    ]

    dev = FakeDevice("test", geom)  # , bounds=some_bounds)
    visualizer.addDevice(dev)
    viz = visualizer.pathPlanVisualizer(dev)
    # test_paths_stay_inside_bounds(geom, viz)
    # test_grazing_paths((0.6, 0.6, 0.6), viz)
    # test_bounds_prevent_path(geom, some_bounds, viz)
    # test_path_with_funner_traveler(geom, viz)
    # test_single_voxel_voxelization(geom, viz)
    # test_find_path(geom, viz)
    # test_no_path(viz)
    test_no_path_because_of_offset_shadow(geom, viz)
