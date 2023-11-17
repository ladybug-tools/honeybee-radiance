# coding=utf-8
"""Model Radiance Properties."""
from honeybee.extensionutil import model_extension_dicts
from honeybee.checkdup import check_duplicate_identifiers
from honeybee.boundarycondition import Surface
from honeybee.typing import invalid_dict_error, clean_rad_string, clean_and_id_rad_string
from honeybee.model import Model

from ..sensorgrid import SensorGrid
from ..view import View
from ..dynamic.group import DynamicShadeGroup, DynamicSubFaceGroup
from ..modifierset import ModifierSet
from ..mutil import dict_to_modifier  # imports all modifiers classes
from ..modifier.material import aBSDF, BSDF
from ..lib.modifiers import black, generic_context
from ..lib.modifiersets import generic_modifier_set_visible

try:
    from itertools import izip as zip  # python 2
except ImportError:
    pass   # python 3


class ModelRadianceProperties(object):
    """Radiance Properties for Honeybee Model.

    Args:
        host: A honeybee_core Model object that hosts these properties.

    Properties:
        * host
        * sensor_grids
        * views
        * modifiers
        * blk_modifiers
        * room_modifiers
        * face_modifiers
        * shade_modifiers
        * bsdf_modifiers
        * modifier_sets
        * global_modifier_set
        * dynamic_shade_groups
        * dynamic_subface_groups
        * shade_group_identifiers
        * subface_group_identifiers
        * has_sensor_grids
        * has_views
    """

    def __init__(self, host, sensor_grids=None, views=None):
        """Initialize Model radiance properties."""
        self._host = host
        self.sensor_grids = sensor_grids
        self.views = views

    @property
    def host(self):
        """Get the Model object hosting these properties."""
        return self._host

    @property
    def sensor_grids(self):
        """Get or set an array of SensorGrids that are associated with the model."""
        return tuple(self._sensor_grids)

    @sensor_grids.setter
    def sensor_grids(self, value):
        if value:
            try:
                self._sensor_grids = list(value)
                for obj in self._sensor_grids:
                    assert isinstance(obj, SensorGrid), 'Expected SensorGrid for Model' \
                        ' sensor_grids. Got {}.'.format(type(value))
            except (ValueError, TypeError):
                raise TypeError(
                    'Model sensor_grids must be an array. Got {}.'.format(type(value)))
        else:
            self._sensor_grids = []

    @property
    def views(self):
        """Get or set an array of Views that are associated with the model."""
        return tuple(self._views)

    @views.setter
    def views(self, value):
        if value:
            try:
                self._views = list(value)
                for obj in self._views:
                    assert isinstance(obj, View), 'Expected View for Model' \
                        ' views. Got {}.'.format(type(value))
            except (ValueError, TypeError):
                raise TypeError(
                    'Model views must be an array. Got {}.'.format(type(value)))
        else:
            self._views = []

    @property
    def modifiers(self):
        """A list of all unique modifiers in the model.

        This includes modifiers across all Faces, Apertures, Doors, Shades, Room
        ModifierSets, and modifiers for any dynamic states assigned to these objects.

        However, it excludes modifiers in the default modifier set. It also excludes
        blk_modifiers and the modifier_direct of any states, which can be obtained
        separately from the blk_modifiers property.
        """
        all_mods = self.room_modifiers + self.face_modifiers + self.shade_modifiers
        return list(set(all_mods))

    @property
    def blk_modifiers(self):
        """A list of all unique modifier_blk in the model.

        This includes modifier_blk across all Faces, Apertures, Doors, and Shades.
        It also includes modifier_direct for any dynamic states assigned to
        these objects.
        """
        modifiers = [black]
        for face in self.host.faces:  # check all orphaned Face modifiers
            self._check_and_add_face_modifier_blk(face, modifiers)
        for ap in self.host.orphaned_apertures:  # check all Aperture modifiers
            self._check_and_add_dynamic_obj_modifier_blk(ap, modifiers)
        for dr in self.host.orphaned_doors:  # check all Door modifiers
            self._check_and_add_dynamic_obj_modifier_blk(dr, modifiers)
        for shade in self.host.shades:
            self._check_and_add_dynamic_obj_modifier_blk(shade, modifiers)
        for sm in self.host.shade_meshes:  # check all ShadeMesh modifiers
            self._check_and_add_obj_modifier_blk(sm, modifiers)
        return list(set(modifiers))

    @property
    def room_modifiers(self):
        """A list of all unique modifiers assigned to Room ModifierSets."""
        room_mods = []
        for cnstr_set in self.modifier_sets:
            room_mods.extend(cnstr_set.modified_modifiers_unique)
        return list(set(room_mods))

    @property
    def face_modifiers(self):
        """A list of all unique modifiers assigned to Faces, Apertures and Doors.

        This includes both objects that are a part of Rooms as well as orphaned
        objects. It does not include the modifiers of any shades assigned to these
        objects. Nor does it include any blk modifiers.
        """
        modifiers = []
        for face in self.host.faces:  # check all orphaned Face modifiers
            self._check_and_add_face_modifier(face, modifiers)
        for ap in self.host.orphaned_apertures:  # check all Aperture modifiers
            self._check_and_add_dynamic_obj_modifier(ap, modifiers)
        for dr in self.host.orphaned_doors:  # check all Door modifiers
            self._check_and_add_dynamic_obj_modifier(dr, modifiers)
        return list(set(modifiers))

    @property
    def shade_modifiers(self):
        """A list of all unique modifiers assigned to Shade and ShadeMeshes in the model.
        """
        modifiers = []
        for room in self.host.rooms:
            self._check_and_add_room_modifier_shade(room, modifiers)
        for face in self.host.orphaned_faces:
            self._check_and_add_face_modifier_shade(face, modifiers)
        for ap in self.host.orphaned_apertures:
            self._check_and_add_obj_modifier_shade(ap, modifiers)
        for dr in self.host.orphaned_doors:
            self._check_and_add_obj_modifier_shade(dr, modifiers)
        for shade in self.host.orphaned_shades:
            self._check_and_add_orphaned_shade_modifier(shade, modifiers)
        for shade_mesh in self.host.shade_meshes:
            self._check_and_add_shade_mesh_modifier(shade_mesh, modifiers)
        return list(set(modifiers))

    @property
    def bsdf_modifiers(self):
        """A list of all unique BSDF modifiers in the model.

        This includes any BSDF modifiers in both the Model.modifiers and the
        Model.blk_modifiers.
        """
        all_mods = self.modifiers + self.blk_modifiers
        return list(set(mod for mod in all_mods if isinstance(mod, (aBSDF, BSDF))))

    @property
    def modifier_sets(self):
        """A list of all unique Room-Assigned ModifierSets in the Model."""
        modifier_sets = []
        for room in self.host.rooms:
            if room.properties.radiance._modifier_set is not None:
                if not self._instance_in_array(room.properties.radiance._modifier_set,
                                               modifier_sets):
                    modifier_sets.append(room.properties.radiance._modifier_set)
        return list(set(modifier_sets))  # catch equivalent modifier sets

    @property
    def global_modifier_set(self):
        """The global radiance modifier set.

        This is what is used whenever no modifier has been assigned to a given
        Face/Aperture/Door/Shade and there is no modifier_set assigned to the
        parent Room.
        """
        return generic_modifier_set_visible

    @property
    def dynamic_shade_groups(self):
        """Get a list of DynamicShadeGroups in the model.

        These can be used to write dynamic shades into radiance files.
        """
        # gather all of the shades with a common identifier into groups
        group_dict = {}
        for shade in self.host.shades:
            if shade.properties.radiance._dynamic_group_identifier:
                group_id = shade.properties.radiance._dynamic_group_identifier
                try:
                    group_dict[group_id].append(shade)
                except KeyError:
                    group_dict[group_id] = [shade]
        # return DynamicShadeGroup objects
        return [DynamicShadeGroup(ident, shades)for ident, shades in group_dict.items()]

    @property
    def dynamic_subface_groups(self):
        """Get a list of DynamicSubFaceGroups in the model.

        These can be used to write dynamic Apertures and Doors into radiance files.
        """
        # gather all of the subfaces with a common identifier into groups
        group_dict = {}
        for subface in self.host.apertures + self.host.doors:
            if subface.properties.radiance._dynamic_group_identifier:
                group_id = subface.properties.radiance._dynamic_group_identifier
                try:
                    group_dict[group_id].append(subface)
                except KeyError:
                    group_dict[group_id] = [subface]
        # return DynamicSubFaceGroup objects
        return [DynamicSubFaceGroup(ident, subf)for ident, subf in group_dict.items()]

    @property
    def shade_group_identifiers(self):
        """Get a list of identifiers for all the DynamicShadeGroups in the model."""
        group_ids = set()
        for shade in self.host.shades:
            if shade.properties.radiance._dynamic_group_identifier:
                group_ids.add(shade.properties.radiance._dynamic_group_identifier)
        return list(group_ids)

    @property
    def subface_group_identifiers(self):
        """Get a list of identifiers for all the DynamicSubFaceGroups in the model."""
        group_ids = set()
        for subface in self.host.apertures + self.host.doors:
            if subface.properties.radiance._dynamic_group_identifier:
                group_ids.add(subface.properties.radiance._dynamic_group_identifier)
        return list(group_ids)

    @property
    def has_sensor_grids(self):
        """Get a boolean for whether there are sensor grids assigned to the model."""
        return len(self._sensor_grids) != 0

    @property
    def has_views(self):
        """Get a boolean for whether there are views assigned to the model."""
        return len(self._views) != 0

    def remove_sensor_grids(self):
        """Remove all sensor grids from the model."""
        self._sensor_grids = []

    def remove_views(self):
        """Remove all views from the model."""
        self._views = []

    def add_sensor_grid(self, sensor_grid):
        """Add a SensorGrid to this model.

        Args:
            sensor_grid: A SensorGrid to add to this model.
        """
        assert isinstance(sensor_grid, SensorGrid), \
            'Expected SensorGrid. Got {}.'.format(type(sensor_grid))
        self._sensor_grids.append(sensor_grid)

    def add_view(self, view):
        """Add a View to this model.

        Args:
            view: A View to add to this model.
        """
        assert isinstance(view, View), 'Expected View. Got {}.'.format(type(view))
        self._views.append(view)

    def add_sensor_grids(self, sensor_grids):
        """Add a list of SensorGrids to this model."""
        for grid in sensor_grids:
            self.add_sensor_grid(grid)

    def add_views(self, views):
        """Add a list of Views to this model."""
        for view in views:
            self.add_view(view)

    def faces_by_blk(self):
        """Get all Faces in the model separated by their blk property.

        This method will also ensure that any faces with Surface boundary condition
        are not duplicated in the result but are rather offset from the base face
        to ensure modifiers on opposite sides of interior Faces are accounted for.
        Furthermore, this method also ensures that any static interior sub-faces
        (with Surface
        boundary condition) only have one of such objects in the output lists.

        Returns:
            A tuple with 2 lists:

            -   faces: A list of all faces without a unique modifier_blk.

            -   faces_blk: A list of all opaque faces that have a unique modifier_blk.
        """
        faces, faces_blk = [], []
        interior_faces, offset = set(), self.host.tolerance * -2
        for face in self.host.faces:
            if isinstance(face.boundary_condition, Surface):
                if face.identifier in interior_faces:
                    face = face.duplicate()
                    face.move(face.normal * offset)
                else:
                    interior_faces.add(face.boundary_condition.boundary_condition_object)
                    for subf in face.apertures + face.doors:
                        if subf.properties.radiance.dynamic_group_identifier is None:
                            if subf.properties.radiance._modifier_blk:
                                faces_blk.append(subf)
                            else:
                                faces.append(subf)
            if face.properties.radiance._modifier_blk:
                faces_blk.append(face)
            else:
                faces.append(face)
        return faces, faces_blk

    def subfaces_by_blk(self):
        """Get model exterior sub-faces (Apertures, Doors) grouped by their blk property.

        Dynamic sub-faces will be excluded from the output lists.

        Returns:
            A tuple with 2 lists:

            -   subfaces: A list of all sub-faces without a unique modifier_blk
                (just using the default black).

            -   subfaces_blk: A list of all sub-faces that have a unique modifier_blk.
        """
        subfaces, subfaces_blk = [], []
        for subf in self.host.apertures + self.host.doors:
            if subf.properties.radiance.dynamic_group_identifier:
                continue  # sub-face will be accounted for in the dynamic objects
            if isinstance(subf.boundary_condition, Surface):
                continue  # static interior apertures are part of the scene
            if subf.properties.radiance._modifier_blk:
                subfaces_blk.append(subf)
            else:
                subfaces.append(subf)
        return subfaces, subfaces_blk

    def shades_by_blk(self):
        """Get all Shades in the model separated by their blk property.

        Dynamic shades will be excluded from the output lists.

        Returns:
            A tuple with 2 lists:

            -   shades: A list of all opaque shades without a unique modifier_blk
                (just using the default black or transparent modifier).

            -   shades_blk: A list of all opaque shades that have a unique modifier_blk.
        """
        shades, shades_blk = [], []
        for shade in self.host.shades:
            if shade.properties.radiance.dynamic_group_identifier:
                continue  # shade will be accounted for in the dynamic objects
            if shade.properties.radiance._modifier_blk:
                shades_blk.append(shade)
            else:
                shades.append(shade)
        return shades, shades_blk

    def shade_meshes_by_blk(self):
        """Get all ShadeMeshes in the model separated by their blk property.

        Returns:
            A tuple with 2 lists:

            -   shade_meshes: A list of all shade meshes without a unique
                modifier_blk (just using the default black or transparent modifier).

            -   shade_meshes_blk: A list of all shade meshes that have a unique modifier_blk.
        """
        shade_meshes, shade_meshes_blk = [], []
        for shade in self.host.shade_meshes:
            if shade.properties.radiance._modifier_blk:
                shade_meshes_blk.append(shade)
            else:
                shade_meshes.append(shade)
        return shade_meshes, shade_meshes_blk

    def move(self, moving_vec):
        """Move all sensor_grid and view geometry along a vector.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the objects.
        """
        for grid in self._sensor_grids:
            grid.move(moving_vec)
        for view in self._views:
            view.move(moving_vec)

    def rotate(self, axis, angle, origin):
        """Rotate all sensor_grid and view geometry.

        Args:
            axis: A ladybug_geometry Vector3D axis representing the axis of rotation.
            angle: An angle for rotation in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for grid in self._sensor_grids:
            grid.rotate(axis, angle, origin)
        for view in self._views:
            view.rotate(axis, angle, origin)

    def rotate_xy(self, angle, origin):
        """Rotate all sensor_grids and views counterclockwise in the world XY plane.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for grid in self._sensor_grids:
            grid.rotate_xy(angle, origin)
        for view in self._views:
            view.rotate_xy(angle, origin)

    def reflect(self, plane):
        """Reflect all sensor_grid and view geometry across a plane.

        Args:
            plane: A ladybug_geometry Plane across which the object will
                be reflected.
        """
        for grid in self._sensor_grids:
            grid.reflect(plane)
        for view in self._views:
            view.reflect(plane)

    def scale(self, factor, origin=None):
        """Scale all sensor_grid and view geometry by a factor.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from the World origin (0, 0, 0).
        """
        for grid in self._sensor_grids:
            grid.scale(factor, origin)
        for view in self._views:
            view.scale(factor, origin)

    def generate_exterior_face_sensor_grid(
            self, dimension, offset=0.1, face_type='Wall', punched_geometry=False):
        """Get a radiance SensorGrid generated from all exterior Faces of this Model.

        The Face geometry without windows punched into it will be used. This
        will be None if the Model has no exterior Faces.

        Args:
            dimension: The dimension of the grid cells as a number.
            offset: A number for how far to offset the grid from the base face.
                Positive numbers indicate an offset towards the exterior. (Default
                is 0.1, which will offset the grid to be 0.1 unit from the faces).
            face_type: Text to specify the type of face that will be used to
                generate grids. Note that only Faces with Outdoors boundary
                conditions will be used, meaning that most Floors will typically
                be excluded unless they represent the underside of a cantilever.
                Choose from the following. (Default: Wall).

                * Wall
                * Roof
                * Floor
                * All

            punched_geometry: Boolean to note whether the punched_geometry of the faces
                should be used (True) with the areas of sub-faces removed from the grid
                or the full geometry should be used (False). (Default:False).

        Returns:
            A honeybee_radiance SensorGrid generated from the exterior Faces
            of the model. Will be None if the Model has no exterior Faces.
        """
        # generate the mesh grid from the exterior Faces
        face_grid = self.host.generate_exterior_face_grid(
            dimension, offset, face_type, punched_geometry)
        if face_grid is None:  # no valid mesh could be generated
            return None
        # create the sensor grid from the mesh
        f_nm = 'Faces' if face_type.title() == 'All' else face_type.title()
        grid_name = '{}_Exterior{}'.format(self.host.display_name, f_nm)
        sensor_grid = SensorGrid.from_mesh3d(clean_rad_string(grid_name), face_grid)
        sensor_grid.display_name = grid_name
        return sensor_grid

    def generate_exterior_aperture_sensor_grid(
            self, dimension, offset=0.1, aperture_type='All'):
        """Get a radiance SensorGrid generated from all exterior Apertures of this Model.

        This will be None if the Model has no exterior Apertures.

        Args:
            dimension: The dimension of the grid cells as a number.
            offset: A number for how far to offset the grid from the base aperture.
                Positive numbers indicate an offset towards the exterior while
                negative numbers indicate an offset towards the interior, essentially
                modeling the value of sun on the building interior. (Default
                is 0.1, which will offset the grid to be 0.1 unit from the aperture).
            aperture_type: Text to specify the type of Aperture that will be used to
                generate grids. Window indicates Apertures in Walls. Choose from
                the following. (Default: All).

                * Window
                * Skylight
                * All

        Returns:
            A honeybee_radiance SensorGrid generated from the exterior Apertures
            of the model. Will be None if the Model has no exterior Apertures.
        """
        # generate the mesh grid from the exterior Apertures
        ap_grid = self.host.generate_exterior_aperture_grid(
            dimension, offset, aperture_type)
        if ap_grid is None:  # no valid mesh could be generated
            return None
        # create the sensor grid from the mesh
        f_nm = 'Apertures' if aperture_type.title() == 'All' else aperture_type.title()
        grid_name = '{}_Exterior{}'.format(self.host.display_name, f_nm)
        sensor_grid = SensorGrid.from_mesh3d(clean_rad_string(grid_name), ap_grid)
        sensor_grid.display_name = grid_name
        return sensor_grid

    def check_all(self, raise_exception=True, detailed=False):
        """Check all of the aspects of the Model radiance properties.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised
                if any errors are found. If False, this method will simply
                return a text string with all errors that were found. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A text string with all errors that were found or a list if detailed is True.
            This string (or list) will be empty if no errors were found.
        """
        # set up defaults to ensure the method runs correctly
        detailed = False if raise_exception else detailed
        msgs = []
        # perform checks for key honeybee model schema rules
        msgs.append(self.check_duplicate_modifier_identifiers(False, detailed))
        msgs.append(self.check_duplicate_modifier_set_identifiers(False, detailed))
        msgs.append(self.check_duplicate_sensor_grid_identifiers(False, detailed))
        msgs.append(self.check_duplicate_view_identifiers(False, detailed))
        msgs.append(self.check_sensor_grid_rooms_in_model(False, detailed))
        msgs.append(self.check_view_rooms_in_model(False, detailed))
        # output a final report of errors or raise an exception
        full_msgs = [msg for msg in msgs if msg]
        if detailed:
            return [m for msg in full_msgs for m in msg]
        full_msg = '\n'.join(full_msgs)
        if raise_exception and len(full_msgs) != 0:
            raise ValueError(full_msg)
        return full_msg

    def check_duplicate_modifier_identifiers(self, raise_exception=True, detailed=False):
        """Check that there are no duplicate Modifier identifiers in the model.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised
                if duplicate identifiers are found. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        return check_duplicate_identifiers(
            self.modifiers, raise_exception, 'Radiance Modifier',
            detailed, '010001', 'Radiance', error_type='Duplicate Modifier Identifier')

    def check_duplicate_modifier_set_identifiers(
            self, raise_exception=True, detailed=False):
        """Check that there are no duplicate ModifierSet identifiers in the model.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised
                if duplicate identifiers are found. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        return check_duplicate_identifiers(
            self.modifier_sets, raise_exception, 'ModifierSet',
            detailed, '010002', 'Radiance',
            error_type='Duplicate ModifierSet Identifier')

    def check_duplicate_sensor_grid_identifiers(
            self, raise_exception=True, detailed=False):
        """Check that there are no duplicate SensorGrid identifiers in the model.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised
                if duplicate identifiers are found. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        return check_duplicate_identifiers(
            self.sensor_grids, raise_exception, 'SensorGrid',
            detailed, '010003', 'Radiance', error_type='Duplicate SensorGrid Identifier')

    def check_duplicate_view_identifiers(self, raise_exception=True, detailed=False):
        """Check that there are no duplicate View identifiers in the model.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised
                if duplicate identifiers are found. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        return check_duplicate_identifiers(
            self.views, raise_exception, 'View', detailed, '010004', 'Radiance',
            error_type='Duplicate View Identifier')

    def check_sensor_grid_rooms_in_model(self, raise_exception=True, detailed=False):
        """Check that the room_identifiers of SenorGrids are in the model.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised if
                SensorGrids reference Rooms that are not in the Model. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        detailed = False if raise_exception else detailed
        # gather a list of all the missing rooms
        grid_ids = [(grid, grid.room_identifier) for grid in self.sensor_grids
                    if grid.room_identifier is not None]
        room_ids = set(room.identifier for room in self.host.rooms)
        missing_rooms = [] if detailed else set()
        for grid in grid_ids:
            if grid[1] not in room_ids:
                if detailed:
                    missing_rooms.append(grid[0])
                else:
                    missing_rooms.add(grid[1])
        # if missing rooms were found, then report the issue
        if len(missing_rooms) != 0:
            if detailed:
                all_err = []
                for grid in missing_rooms:
                    msg = 'SensorGrid "{}" has a room_identifier that is not in the ' \
                        'Model: "{}"'.format(grid.identifier, grid.room_identifier)
                    error_dict = {
                        'type': 'ValidationError',
                        'code': '010005',
                        'error_type': 'SensorGrid Room Not In Model',
                        'extension_type': 'Radiance',
                        'element_type': 'SensorGrid',
                        'element_id': [grid.identifier],
                        'element_name': [grid.display_name],
                        'message': msg
                    }
                    all_err.append(error_dict)
                return all_err
            else:
                msg = 'The model has the following missing rooms referenced by sensor ' \
                    'grids:\n{}'.format('\n'.join(missing_rooms))
                if raise_exception:
                    raise ValueError(msg)
                return msg
        return [] if detailed else ''

    def check_view_rooms_in_model(self, raise_exception=True, detailed=False):
        """Check that the room_identifiers of Views are in the model.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised if
                Views reference Rooms that are not in the Model. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        detailed = False if raise_exception else detailed
        # gather a list of all the missing rooms
        view_ids = [(view, view.room_identifier) for view in self.views
                    if view.room_identifier is not None]
        room_ids = set(room.identifier for room in self.host.rooms)
        missing_rooms = [] if detailed else set()
        for view in view_ids:
            if view[1] not in room_ids:
                if detailed:
                    missing_rooms.append(view[0])
                else:
                    missing_rooms.add(view[1])
        if len(missing_rooms) != 0:
            if detailed:
                all_err = []
                for view in missing_rooms:
                    msg = 'View "{}" has a room_identifier that is not in the ' \
                        'Model: "{}"'.format(view.identifier, view.room_identifier)
                    error_dict = {
                        'type': 'ValidationError',
                        'code': '010006',
                        'error_type': 'View Room Not In Model',
                        'extension_type': 'Radiance',
                        'element_type': 'View',
                        'element_id': [view.identifier],
                        'element_name': [view.display_name],
                        'message': msg
                    }
                    all_err.append(error_dict)
                return all_err
            else:
                msg = 'The model has the following missing rooms referenced by ' \
                    'views:\n{}'.format('\n'.join(missing_rooms))
                if raise_exception:
                    raise ValueError(msg)
                return msg
        return [] if detailed else ''

    def apply_properties_from_dict(self, data):
        """Apply the radiance properties of a dictionary to the host Model of this object.

        Args:
            data: A dictionary representation of an entire honeybee-core Model.
                Note that this dictionary must have ModelRadianceProperties in order
                for this method to successfully apply the radiance properties.
        """
        assert 'radiance' in data['properties'], \
            'Dictionary possesses no ModelRadianceProperties.'

        modifiers, modifier_sets = self.load_properties_from_dict(data)

        # collect lists of radiance property dictionaries
        room_e_dicts, face_e_dicts, shd_e_dicts, ap_e_dicts, dr_e_dicts = \
            model_extension_dicts(data, 'radiance', [], [], [], [], [])

        # apply radiance properties to objects using the radiance property dictionaries
        for room, r_dict in zip(self.host.rooms, room_e_dicts):
            if r_dict is not None:
                room.properties.radiance.apply_properties_from_dict(
                    r_dict, modifier_sets)
        for face, f_dict in zip(self.host.faces, face_e_dicts):
            if f_dict is not None:
                face.properties.radiance.apply_properties_from_dict(
                    f_dict, modifiers)
        for aperture, a_dict in zip(self.host.apertures, ap_e_dicts):
            if a_dict is not None:
                aperture.properties.radiance.apply_properties_from_dict(
                    a_dict, modifiers)
        for door, d_dict in zip(self.host.doors, dr_e_dicts):
            if d_dict is not None:
                door.properties.radiance.apply_properties_from_dict(
                    d_dict, modifiers)
        # apply properties to the Shades with separation of Shades from ShadeMesh
        all_shades = self.host.shades + self.host._shade_meshes
        for shade, s_dict in zip(all_shades, shd_e_dicts):
            if s_dict is not None:
                shade.properties.radiance.apply_properties_from_dict(
                    s_dict, modifiers)

        # apply the sensor grids and views if they are in the data.
        rad_data = data['properties']['radiance']
        if 'sensor_grids' in rad_data and rad_data['sensor_grids'] is not None:
            self.sensor_grids = \
                [SensorGrid.from_dict(grid) for grid in rad_data['sensor_grids']]
        if 'views' in rad_data and rad_data['views'] is not None:
            self.views = [View.from_dict(view) for view in rad_data['views']]

    def to_dict(self):
        """Return Model radiance properties as a dictionary."""
        base = {'radiance': {'type': 'ModelRadianceProperties'}}

        # add the global modifier set to the dictionary
        gs = self.global_modifier_set.to_dict(abridged=True, none_for_defaults=False)
        gs['type'] = 'GlobalModifierSet'
        del gs['identifier']
        g_mods = self.global_modifier_set.modifiers_unique
        gs['modifiers'] = [mod.to_dict() for mod in g_mods]
        gs['context_modifier'] = generic_context.identifier
        gs['modifiers'].append(generic_context.to_dict())
        base['radiance']['global_modifier_set'] = gs

        # add all ModifierSets to the dictionary
        base['radiance']['modifier_sets'] = []
        modifier_sets = self.modifier_sets
        for mod_set in modifier_sets:
            base['radiance']['modifier_sets'].append(mod_set.to_dict(abridged=True))

        # add all unique Modifiers to the dictionary
        room_mods = []
        for mod_set in modifier_sets:
            room_mods.extend(mod_set.modified_modifiers_unique)
        all_mods = room_mods + self.face_modifiers + self.shade_modifiers
        modifiers = list(set(all_mods))
        base['radiance']['modifiers'] = []
        for mod in modifiers:
            base['radiance']['modifiers'].append(mod.to_dict())

        # add the sensor grids and views to the dictionary
        if len(self._sensor_grids) != 0:
            base['radiance']['sensor_grids'] = \
                [grid.to_dict() for grid in self._sensor_grids]
        if len(self._views) != 0:
            base['radiance']['views'] = [view.to_dict() for view in self._views]

        return base

    def duplicate(self, new_host=None):
        """Get a copy of this object.

        new_host: A new Model object that hosts these properties.
            If None, the properties will be duplicated with the same host.
        """
        _host = new_host or self._host
        new_grids = [sg.duplicate() for sg in self._sensor_grids]
        new_views = [vw.duplicate() for vw in self._views]
        return ModelRadianceProperties(_host, new_grids, new_views)

    @staticmethod
    def load_properties_from_dict(data):
        """Load model radiance properties of a dictionary to Python objects.

        Loaded objects include Modifiers and ModifierSets.

        The function is called when re-serializing a Model object from a dictionary
        to load honeybee_radiance objects into their Python object form before
        applying them to the Model geometry.

        Args:
            data: A dictionary representation of an entire honeybee-core Model.
                Note that this dictionary must have ModelRadianceProperties in order
                for this method to successfully load the radiance properties.

        Returns:
            A tuple with two elements

            -   modifiers: A dictionary with identifiers of modifiers as keys and Python
                modifier objects as values.

            -   modifier_sets: A dictionary with identifiers of modifier sets as keys
                and Python modifier set objects as values.
        """
        assert 'radiance' in data['properties'], \
            'Dictionary possesses no ModelRadianceProperties.'

        # process all modifiers in the ModelRadianceProperties dictionary
        modifiers = {}
        if 'modifiers' in data['properties']['radiance'] and \
                data['properties']['radiance']['modifiers'] is not None:
            for mod in data['properties']['radiance']['modifiers']:
                try:
                    modifiers[mod['identifier']] = dict_to_modifier(mod)
                except Exception as e:
                    invalid_dict_error(mod, e)

        # process all modifier sets in the ModelRadianceProperties dictionary
        modifier_sets = {}
        if 'modifier_sets' in data['properties']['radiance'] and \
                data['properties']['radiance']['modifier_sets'] is not None:
            if 'modifier_sets' in data['properties']['radiance'] and \
                    data['properties']['radiance']['modifier_sets'] is not None:
                for m_set in data['properties']['radiance']['modifier_sets']:
                    try:
                        if m_set['type'] == 'ModifierSet':
                            modifier_sets[m_set['identifier']] = \
                                ModifierSet.from_dict(m_set)
                        else:
                            modifier_sets[m_set['identifier']] = \
                                ModifierSet.from_dict_abridged(m_set, modifiers)
                    except Exception as e:
                        invalid_dict_error(m_set, e)

        return modifiers, modifier_sets

    @staticmethod
    def dump_properties_to_dict(modifiers=None, modifier_sets=None):
        """Get a ModelRadianceProperties dictionary from arrays of Python objects.

        Args:
            modifiers: A list or tuple of radiance modifier objects.
            modifier_sets: A list or tuple of modifier set objects.

        Returns:
            data: A dictionary representation of ModelRadianceProperties. Note that
                all objects in this dictionary will follow the abridged schema.
        """
        # process the modifiers and modifier sets
        all_m = [] if modifiers is None else list(modifiers)
        all_mod_sets = [] if modifier_sets is None else list(modifier_sets)
        for mod_set in all_mod_sets:
            all_m.extend(mod_set.modified_modifiers)

        # get sets of unique objects
        all_mods = set(all_m)

        # add all object dictionaries into one object
        data = {'type': 'ModelRadianceProperties'}
        data['modifiers'] = [m.to_dict() for m in all_mods]
        data['modifier_sets'] = [ms.to_dict(abridged=True) for ms in all_mod_sets]
        return data

    @staticmethod
    def reset_resource_ids_in_dict(
            data, add_uuid=False, reset_modifiers=True, reset_modifier_sets=True):
        """Reset the identifiers of radiance resource objects in a Model dictionary.

        This is useful when human-readable names are needed when the model is
        exported to other formats like Rad and the uniqueness of the
        identifiers is less of a concern.

        Args:
            data: A dictionary representation of an entire honeybee-core Model.
                Note that this dictionary must have ModelRadianceProperties in order
                for this method to successfully edit the radiance properties.
            add_uuid: Boolean to note whether newly-generated resource object IDs
                should be derived only from a cleaned display_name (False) or
                whether this new ID should also have a unique set of 8 characters
                appended to it to guarantee uniqueness. (Default: False).
            reset_modifiers: Boolean to note whether the IDs of all modifiers in
                the model should be reset or kept. (Default: True).
            reset_modifier_sets: Boolean to note whether the IDs of all modifier
                sets in the model should be reset or kept. (Default: True).

        Returns:
            A new Model dictionary with the resource identifiers reset. All references
            to the reset resources will be correct and valid in the resulting dictionary,
            assuming that the input is valid.
        """
        model = Model.from_dict(data)
        modifiers, modifier_sets = \
            model.properties.radiance.load_properties_from_dict(data)
        res_func = clean_and_id_rad_string if add_uuid else clean_rad_string

        # change the identifiers of the modifiers
        if reset_modifiers:
            model_mods = set()
            for mod in model.properties.radiance.modifiers:
                mod.unlock()
                old_id, new_id = mod.identifier, res_func(mod.display_name)
                mod.identifier = new_id
                modifiers[old_id].unlock()
                modifiers[old_id].identifier = new_id
                model_mods.add(old_id)
            for old_id, mod in modifiers.items():
                if old_id not in model_mods:
                    mod.unlock()
                    mod.identifier = res_func(mod.display_name)

        # change the identifiers of the modifier_sets
        if reset_modifier_sets:
            model_ms = set()
            for ms in model.properties.radiance.modifier_sets:
                ms.unlock()
                old_id, new_id = ms.identifier, res_func(ms.display_name)
                ms.identifier = new_id
                modifier_sets[old_id].unlock()
                modifier_sets[old_id].identifier = new_id
                model_ms.add(old_id)
            for old_id, ms in modifier_sets.items():
                if old_id not in model_ms:
                    ms.unlock()
                    ms.identifier = res_func(ms.display_name)

        # create the model dictionary and update any unreferenced resources
        model_dict = model.to_dict()
        mr_props = model_dict['properties']['radiance']
        mr_props['modifiers'] = [mod.to_dict() for mod in modifiers.values()]
        mr_props['modifier_sets'] = \
            [ms.to_dict(abridged=True) for ms in modifier_sets.values()]
        return model_dict

    def _check_and_add_room_modifier_shade(self, room, modifiers):
        """Check if a modifier is assigned to a Room's shades and add it to a list."""
        self._check_and_add_obj_modifier_shade(room, modifiers)
        for face in room.faces:  # check all Face modifiers
            self._check_and_add_face_modifier_shade(face, modifiers)

    def _check_and_add_face_modifier_shade(self, face, modifiers):
        """Check if a modifier is assigned to a Face's shades and add it to a list."""
        self._check_and_add_obj_modifier_shade(face, modifiers)
        for ap in face.apertures:  # check all Aperture modifiers
            self._check_and_add_obj_modifier_shade(ap, modifiers)
        for dr in face.doors:  # check all Door Shade modifiers
            self._check_and_add_obj_modifier_shade(dr, modifiers)

    def _check_and_add_obj_modifier_shade(self, subf, modifiers):
        """Check if a modifier is assigned to an object's shades and add it to a list."""
        for shade in subf.shades:
            self._check_and_add_dynamic_obj_modifier(shade, modifiers)

    def _check_and_add_face_modifier(self, face, modifiers):
        """Check if a modifier is assigned to a face and add it to a list."""
        self._check_and_add_obj_modifier(face, modifiers)
        for ap in face.apertures:  # check all Aperture modifiers
            self._check_and_add_dynamic_obj_modifier(ap, modifiers)
        for dr in face.doors:  # check all Door modifiers
            self._check_and_add_dynamic_obj_modifier(dr, modifiers)

    def _check_and_add_face_modifier_blk(self, face, modifiers):
        """Check if a modifier_blk is assigned to a face and add it to a list."""
        self._check_and_add_obj_modifier_blk(face, modifiers)
        for ap in face.apertures:  # check all Aperture modifiers
            self._check_and_add_dynamic_obj_modifier_blk(ap, modifiers)
        for dr in face.doors:  # check all Door modifiers
            self._check_and_add_dynamic_obj_modifier_blk(dr, modifiers)

    def _check_and_add_obj_modifier(self, obj, modifiers):
        """Check if a modifier is assigned to an object and add it to a list."""
        mod = obj.properties.radiance._modifier
        if mod is not None:
            if not self._instance_in_array(mod, modifiers):
                modifiers.append(mod)

    def _check_and_add_dynamic_obj_modifier(self, obj, modifiers):
        """Check if a modifier is assigned to a dynamic object and add it to a list."""
        mod = obj.properties.radiance._modifier
        if mod is not None:
            if not self._instance_in_array(mod, modifiers):
                modifiers.append(mod)
        for st in obj.properties.radiance._states:
            stm = (st._modifier, st._modifier_direct) + \
                tuple(s.modifier for s in st._shades)
            for mod in stm:
                if mod is not None:
                    if not self._instance_in_array(mod, modifiers):
                        modifiers.append(mod)

    def _check_and_add_obj_modifier_blk(self, obj, modifiers):
        """Check if a modifier_blk is assigned to an object and add it to a list."""
        mod = obj.properties.radiance._modifier_blk
        if mod is not None:
            if not self._instance_in_array(mod, modifiers):
                modifiers.append(mod)

    def _check_and_add_dynamic_obj_modifier_blk(self, obj, modifiers):
        """Check if a modifier_blk is assigned to a dynamic object and add it to a list.
        """
        mod = obj.properties.radiance._modifier_blk
        if mod is not None:
            if not self._instance_in_array(mod, modifiers):
                modifiers.append(mod)
        for st in obj.properties.radiance._states:
            for s in st._shades:
                mod = s.modifier
                if mod is not None:
                    if not self._instance_in_array(mod, modifiers):
                        modifiers.append(mod)

    def _check_and_add_orphaned_shade_modifier(self, obj, modifiers):
        """Check if a modifier is assigned to an object and add it to a list."""
        mod = obj.properties.radiance._modifier
        if mod is not None:
            if not self._instance_in_array(mod, modifiers):
                modifiers.append(mod)
        else:
            def_mod = generic_context if obj.is_detached else \
                generic_modifier_set_visible.shade_set.exterior_modifier
            if not self._instance_in_array(def_mod, modifiers):
                modifiers.append(def_mod)
        for st in obj.properties.radiance._states:
            stm = (st._modifier, st._modifier_direct) + \
                tuple(s.modifier for s in st._shades)
            for mod in stm:
                if mod is not None:
                    if not self._instance_in_array(mod, modifiers):
                        modifiers.append(mod)

    def _check_and_add_shade_mesh_modifier(self, obj, modifiers):
        """Check if a modifier is assigned to an object and add it to a list."""
        mod = obj.properties.radiance._modifier
        if mod is not None:
            if not self._instance_in_array(mod, modifiers):
                modifiers.append(mod)
        else:
            def_mod = generic_context if obj.is_detached else \
                generic_modifier_set_visible.shade_set.exterior_modifier
            if not self._instance_in_array(def_mod, modifiers):
                modifiers.append(def_mod)

    @staticmethod
    def _instance_in_array(object_instance, object_array):
        """Check if a specific object instance is already in an array.

        This can be much faster than  `if object_instance in object_array`
        when you expect to be testing a lot of the same instance of an object for
        inclusion in an array since the builtin method uses an == operator to
        test inclusion.
        """
        for val in object_array:
            if val is object_instance:
                return True
        return False

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Model Radiance Properties: [host: {}]'.format(self.host.display_name)
