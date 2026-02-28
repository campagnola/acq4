"""3D geometry shapes and mesh handling."""
from __future__ import annotations

from typing import Dict, List, Optional, TYPE_CHECKING

import numpy as np
import pyqtgraph.opengl as gl
import trimesh
from coorx import AffineTransform, NullTransform, Point, TTransform, Transform
from trimesh.voxel import VoxelGrid

from .primitives import truncated_cone
from .voxels import Volume

if TYPE_CHECKING:
    from .transforms import load_transform_from_anything


class Geometry:
    """A 3D geometry composed of meshes with hierarchical transforms.

    Parameters
    ----------
    config : Dict | str, optional
        Configuration dictionary for creating the geometry (see parse_config).
    name : str, optional
        Name of this geometry.
    parent_name : str, optional
        Name of the parent coordinate system.
    mesh : trimesh.Trimesh, optional
        Pre-existing mesh to use.
    transform : Transform, optional
        Transform from this geometry's local coordinates to parent coordinates.
    color : tuple, optional
        RGBA color tuple for rendering.
    """

    def __init__(
        self,
        config: Dict | str = None,
        name: str = None,
        parent_name: str = None,
        mesh: trimesh.Trimesh = None,
        transform: Transform = None,
        color=None,
    ):
        """Create a geometry either from a configuration (see parse_config) or from a mesh
        and transform."""
        self.color = color
        self.name = name
        self.parent_name = parent_name
        if parent_name is None and transform is not None:
            self.parent_name = str(transform.systems[1])
        if name is None and transform is not None:
            self.name = str(transform.systems[0])
        self._config = config
        self._children: List[Geometry] = []
        if mesh is None:
            self._mesh: trimesh.Trimesh = trimesh.Trimesh()
            self._total_mesh: Optional[trimesh.Trimesh] = None
        else:
            self._mesh = self._total_mesh = mesh
        # maps from local coordinate system of geometry (the coordinates in which mesh vertices
        # are specified) to parent
        if config is not None:
            self.parse_config()
        if getattr(self, "_transform", None) is None:
            self._transform: Transform = transform or NullTransform(
                3, **self._default_transform_args()
            )

    def parse_config(self):
        """Create 3D mesh from a configuration.

        Format example::

            geometry:
                color: (1, 0.7, 0.1, 1)    # color will be inherited by children
                type: "cone"               # type must be "cone", "cylinder" or "box"
                top_radius: 20 * mm
                bottom_radius: 4 * mm
                children:
                    component_1:               # names for children are in their key
                        type: "cone"
                        height: 3 * mm
                        top_radius: 40 * mm    # overrides top-level defaults
                        transform:
                            pos: 0, 0, -10 * um
                        children:              # nested components compound their transforms
                            halo:
                                type: "cylinder"
                                height: 1 * mm
                                radius: 50 * mm
                                color: (1, 1, 1, 0.1)
                                transform:
                                    pos: 0, 0, 3 * mm
                    fuse:                      # some devices may expect specific component names
                        type: "box"
                        size: (80 * mm, 80 * mm, 10 * mm)
                        transform:
                            pos: 0, 0, -83 * mm
        """
        # Import here to avoid circular import
        from .transforms import load_transform_from_anything

        config = self._config.copy()

        self.color = config.pop("color", None)

        self._transform = load_transform_from_anything(config.pop("transform", {}))

        self._children = []
        for name, child_config in config.pop("children", {}).items():
            if "color" not in child_config:
                child_config["color"] = self.color
            child = Geometry(child_config, name, self.name)
            self._children.append(child)

        geom_type = config.pop("type", None)
        if geom_type == "box":
            self._mesh = self.make_box(config)
        elif geom_type == "cone":
            self._mesh = self.make_cone(config)
        elif geom_type == "cylinder":
            self._mesh = self.make_cylinder(config)
        elif geom_type is not None:
            raise ValueError(f"Unsupported geometry type: {geom_type}")

        if len(config) > 0:
            raise ValueError(f"Invalid geometry config: {config}")

    @property
    def mesh(self) -> trimesh.Trimesh:
        """Get the concatenated mesh containing all geometry from this object and its children.

        Returns
        -------
        trimesh.Trimesh
            Concatenated mesh expressed in the local coordinate system of this object.
        """
        if self._total_mesh is None:
            self._total_mesh = self._mesh
            for child in self._children:
                kid = child.mesh.copy()
                kid.apply_transform(child.transform.full_matrix)
                self._total_mesh += kid
        return self._total_mesh

    def glMesh(self) -> gl.GLMeshItem:
        """Create a PyQtGraph OpenGL mesh item for rendering.

        Returns
        -------
        gl.GLMeshItem
            OpenGL mesh item ready for rendering.
        """
        # TODO get children to have separate colors
        mesh = gl.MeshData(vertexes=self.mesh.vertices, faces=self.mesh.faces)
        if self.color is None:
            color = (1, 1, 1, 1)
        else:
            color = np.array(self.color)
        return gl.GLMeshItem(meshdata=mesh, smooth=False, color=color, shader="shaded")

    @property
    def transform(self):
        """Transform that maps from the local coordinate system of this geometry to the parent
        geometry's coordinate."""
        return self._transform

    def voxel_template(self, voxel_size: float) -> Volume:
        """Create a voxelized representation of this geometry.

        Parameters
        ----------
        voxel_size : float
            Size of each voxel.

        Returns
        -------
        Volume
            Voxelized representation of the geometry.
        """
        voxels: VoxelGrid = self.mesh.voxelized(voxel_size)
        matrix = voxels.transform
        from_voxels_to_mesh = AffineTransform(
            matrix=matrix[:3, :3],
            offset=matrix[:3, 3],
            from_cs=f"Voxel centers of {self.transform.systems[0]}",
            to_cs=self.transform.systems[0],
        ) * TTransform(
            offset=(-0.5, -0.5, -0.5),
            to_cs=f"Voxel centers of {self.transform.systems[0]}",
            from_cs=f"Voxels of {self.transform.systems[0]}",
        )

        return Volume(voxels.encoding.dense.T, from_voxels_to_mesh)

    # old code, but we might use urdf again someday
    # def _urdf_visuals(self):
    #     from pymp import Planner
    #     import hppfcl
    #
    #     urdf: str = self.config
    #     srdf = f"{urdf[:-5]}.srdf"
    #     end_effector = ET.parse(srdf).getroot().find("end_effector").attrib["name"]
    #     joints = [j.attrib["name"] for j in ET.parse(urdf).getroot().findall("joint") if
    #               j.attrib["type"] != "fixed"]
    #     planner = Planner(urdf, joints, end_effector, srdf)
    #     objects = []
    #     for obj in planner.scene.collision_model.geometryObjects:
    #         geom = obj.geometry
    #         if isinstance(geom, hppfcl.Cylinder):
    #             conf = {
    #                 "type": "cylinder",
    #                 "radius": geom.radius,
    #                 "height": 2.0 * geom.halfLength,
    #                 "close_top": True,
    #                 "close_bottom": True,
    #             }
    #         elif isinstance(geom, hppfcl.Cone):
    #             conf = {
    #                 "type": "cone",
    #                 "bottom_radius": geom.radius,
    #                 "top_radius": 0,
    #                 "height": 2.0 * geom.halfLength,
    #                 "close_bottom": True,
    #             }
    #         elif isinstance(geom, hppfcl.Box):
    #             conf = {"type": "box", "size": 2.0 * geom.halfSide}
    #         else:
    #             raise ValueError(f"Unsupported geometry type: {type(geom)}")
    #         xform = np.dot(
    #             np.array(planner.scene.model.jointPlacements[obj.parentJoint]),
    #             np.array(obj.placement),
    #         )
    #         conf["transform"] = Qt.QtGui.QMatrix4x4(xform.reshape((-1,)))
    #         objects.append({obj.name: conf})
    #
    #     root = objects.pop(0)
    #     last = root
    #     while objects:
    #         obj = objects.pop(0)
    #         list(last.values())[0].setdefault("children", {}).update(obj)
    #         last = obj
    #     return []

    @staticmethod
    def make_box(args) -> trimesh.Trimesh:
        """Create a box mesh.

        Parameters
        ----------
        args : dict
            Must contain 'size' key with (x, y, z) dimensions.

        Returns
        -------
        trimesh.Trimesh
            Box mesh.
        """
        return trimesh.creation.box(args.pop("size"))

    @staticmethod
    def make_cone(args) -> trimesh.Trimesh:
        """Create a truncated cone mesh.

        Parameters
        ----------
        args : dict
            Must contain 'bottom_radius', 'top_radius', 'height' keys.
            Optional: 'close_top', 'close_bottom', 'segments'.

        Returns
        -------
        trimesh.Trimesh
            Cone mesh.
        """
        points, faces = truncated_cone(
            bottom_radius=args.pop("bottom_radius"),
            top_radius=args.pop("top_radius"),
            height=args.pop("height"),
            close_top=args.pop("close_top", False),
            close_bottom=args.pop("close_bottom", False),
            segments=args.pop("segments", 32),
        )
        return trimesh.Trimesh(points, faces)

    def make_cylinder(self, args):
        """Create a cylinder mesh.

        Parameters
        ----------
        args : dict
            Must contain 'radius', 'height' keys.
            Optional: 'close_top', 'close_bottom', 'segments'.

        Returns
        -------
        trimesh.Trimesh
            Cylinder mesh.
        """
        args["bottom_radius"] = args["top_radius"] = args.pop("radius")
        return self.make_cone(args)

    def contains(self, point, padding=None) -> bool:
        """Check if a point is contained within this geometry's bounding box.

        Parameters
        ----------
        point : np.ndarray
            Point to check.
        padding : float, optional
            If provided, also check points offset by this amount along each axis.

        Returns
        -------
        bool
            True if point is contained.
        """
        if padding is not None:
            for ax in range(3):
                for sign in (-1, 1):
                    adjustment = np.zeros(3)
                    adjustment[ax] = sign * padding
                    if self.contains(point + adjustment):
                        return True
        bounds = self.mesh.bounds
        return np.all(bounds[0] <= point) and np.all(point <= bounds[1])

    def transformed_to(self, other_transform, from_self_to_other):
        """
        Return a new Geometry that is a transformed version of this one.

        The mesh will be transformed by the from_self_to_other transform, while the new
        geometry itself will have the other_transform.

        Parameters
        ----------
        other_transform : Transform
            Transform for the new geometry.
        from_self_to_other : Transform
            Transform to apply to the mesh vertices.

        Returns
        -------
        Geometry
            New transformed geometry.
        """
        vertices = from_self_to_other.map(self.mesh.vertices)
        mesh = trimesh.Trimesh(vertices=vertices, faces=self.mesh.faces)
        return Geometry(
            mesh=mesh,
            transform=other_transform,
            color=self.color,
            name=f"[{self.name} in {other_transform.systems[0]}]",
        )

    def _default_transform_args(self):
        return dict(from_cs=self.name, to_cs=self.parent_name)

    def make_convolved_voxels(
        self, other: "Geometry", to_my_parent_from_other_parent: Transform, voxel_size: float
    ) -> Volume:
        """Return a Volume that represents the accessible space the other geometry could move
        through without a collision.

        Parameters
        ----------
        other : Geometry
            The other geometry to convolve with.
        to_my_parent_from_other_parent : Transform
            Transform from other's parent coordinate system to this geometry's parent.
        voxel_size : float
            Size of each voxel.

        Returns
        -------
        Volume
            Convolved volume representing collision space.
        """
        to_self_from_other = (
            self.transform.inverse * to_my_parent_from_other_parent * other.transform
        )
        xformed = other.transformed_to(self.transform, to_self_from_other)
        xformed_voxels = xformed.voxel_template(voxel_size)
        # this prevents two pipette tips from smashing into each other, but it makes it harder
        # to deal with larger objects. we can leave this commented until we start needing to
        # handle 2 pipettes.
        # xformed_voxels.volume = np.pad(xformed_voxels.volume, 1, mode="constant")[1:, 1:, 1:]
        # xformed_voxels.volume = scipy.ndimage.binary_dilation(xformed_voxels.volume, iterations=1)
        # TODO this is adding a scale=-1, but none of the transforms reflect this
        shadow = xformed_voxels.volume[::-1, ::-1, ::-1]
        other_origin = Point((0, 0, 0), other.parent_name)
        other_origin_in_my_parent = to_my_parent_from_other_parent.map(other_origin)
        other_origin_in_self = self.transform.inverse.map(other_origin_in_my_parent)
        other_origin_in_xformed_voxels = xformed_voxels.transform.inverse.map(other_origin_in_self)
        center = (
            np.array(shadow.T.shape) - other_origin_in_xformed_voxels - (0.5, 0.5, 0.5)
        ).round()
        self_voxels = self.voxel_template(voxel_size)
        return self_voxels.convolve(shadow, center, f"[shadow of {xformed.name}]")
