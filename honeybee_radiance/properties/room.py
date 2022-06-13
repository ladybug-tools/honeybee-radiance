# coding=utf-8
"""Room Radiance Properties."""
import math

from ladybug_geometry.geometry3d.pointvector import Vector3D
from honeybee.facetype import Floor, Wall
from honeybee.typing import clean_rad_string

from ..sensorgrid import SensorGrid
from ..view import View
from ..modifierset import ModifierSet
from ..lib.modifiersets import generic_modifier_set_visible


class RoomRadianceProperties(object):
    """Radiance Properties for Honeybee Room.

    Args:
        host: A honeybee_core Room object that hosts these properties.
        modifier_set: A honeybee ModifierSet object to specify all default
            modifiers for the Faces of the Room. If None, the Room will use
            the honeybee default modifier set, which is only representative
            of typical indoor conditions in the visible spectrum. Default: None.

    Properties:
        * host
        * modifier_set
    """

    __slots__ = ('_host', '_modifier_set')

    def __init__(self, host, modifier_set=None):
        """Initialize Room radiance properties."""
        # set the main properties of the Room
        self._host = host
        self.modifier_set = modifier_set

    @property
    def host(self):
        """Get the Room object hosting these properties."""
        return self._host

    @property
    def modifier_set(self):
        """Get or set the Room ModifierSet object.

        If not set, it will be the Honeybee default generic ModifierSet.
        """
        if self._modifier_set is not None:  # set by the user
            return self._modifier_set
        else:
            return generic_modifier_set_visible

    @modifier_set.setter
    def modifier_set(self, value):
        if value is not None:
            assert isinstance(value, ModifierSet), \
                'Expected ModifierSet. Got {}'.format(type(value))
            value.lock()   # lock in case modifier set has multiple references
        self._modifier_set = value

    def generate_sensor_grid(
            self, x_dim, y_dim=None, offset=1.0, remove_out=False, wall_offset=0):
        """Get a radiance SensorGrid generated from this Room's floors.

        The output grid will have this room referenced in its room_identifier
        property. It will also include a Mesh3D object with faces that align
        with the grid positions under the grid's mesh property.

        Note that the x_dim and y_dim refer to dimensions within the XY coordinate
        system of the floor faces's planes. So rotating the planes of the floor faces
        will result in rotated grid cells.

        Args:
            x_dim: The x dimension of the grid cells as a number.
            y_dim: The y dimension of the grid cells as a number. If None,
                the y dimension will be assumed to be the same as the x
                dimension. (Default: None).
            offset: A number for how far to offset the grid from the base face.
                (Default is 1.0, which will not offset the grid to be 1 unit above
                the floor).
            remove_out: Boolean to note whether an extra check should be run to remove
                sensor points that lie outside the Room volume. Note that this can
                add significantly to runtime and this check is not necessary
                in the case that all walls are vertical and all floors are
                horizontal (Default: False).
            wall_offset: A number for the distance at which sensors close to walls
                should be removed. Note that this option has no effect unless the
                value is more than half of the x_dim or y_dim. (Default: 0).

        Returns:
            A honeybee_radiance SensorGrid generated from the floors of the room.
            Will be None if the Room has no floors or the criteria for wall_offset
            and/or remove_out results in all sensors being removed.

        Usage:

        .. code-block:: python

            from honeybee.room import Room
            room = Room.from_box(3.0, 6.0, 3.2, 180)
            south_face = room[3]
            south_face.apertures_by_ratio(0.4, 0.01)
            sensor_grid = room.properties.radiance.generate_grid(0.5, 0.5, 1)
        """
        # generate the mesh grid from the floor Faces
        floor_grid = self._base_sensor_mesh(
            x_dim, y_dim, offset, remove_out, wall_offset)
        if floor_grid is None:  # no valid mesh could be generated
            return None

        # create the sensor grid from the mesh
        sensor_grid = SensorGrid.from_mesh3d(
            clean_rad_string(self.host.display_name), floor_grid)
        sensor_grid.room_identifier = self.host.identifier
        sensor_grid.display_name = self.host.display_name
        sensor_grid.base_geometry = \
            tuple(face.geometry.move(face.normal.reverse() * offset)
                  for face in self.host.faces if isinstance(face.type, Floor))
        return sensor_grid

    def generate_sensor_grid_radial(
            self, x_dim, y_dim=None, offset=1.0, remove_out=False, wall_offset=0,
            dir_count=8, start_vector=Vector3D(0, -1, 0), mesh_radius=None):
        """Get a SensorGrid of radial directions around positions from the floors.

        This type of sensor grid is particularly helpful for studies of multiple view
        directions, such as imageless glare studies.

        The output grid will have this room referenced in its room_identifier
        property. It will also include a Mesh3D of radial faces around each position
        under the grid's mesh property. Note that the x_dim and y_dim refer to
        dimensions within the XY coordinate system of the floor faces's planes.
        So rotating the planes of the floor faces will result in rotated grid cells.

        Args:
            x_dim: The x dimension of the grid cells as a number.
            y_dim: The y dimension of the grid cells as a number. If None,
                the y dimension will be assumed to be the same as the x
                dimension. (Default: None).
            offset: A number for how far to offset the grid from the base face.
                (Default: 1.0, which will not offset the grid to be 1 unit above
                the floor).
            remove_out: Boolean to note whether an extra check should be run to remove
                sensor points that lie outside the Room volume. Note that this can
                add significantly to runtime and this check is not necessary
                in the case that all walls are vertical and all floors are
                horizontal (Default: False).
            wall_offset: A number for the distance at which sensors close to walls
                should be removed. Note that this option has no effect unless the
                value is more than half of the x_dim or y_dim. (Default: 0).
            dir_count: A positive integer for the number of radial directions
                to be generated around each position. (Default: 8).
            start_vector: A Vector3D to set the start direction of the generated
                directions. This can be used to orient the resulting sensors to
                specific parts of the scene. It can also change the elevation of the
                resulting directions since this start vector will always be rotated in
                the XY plane to generate the resulting directions. (Default: (0, -1, 0)).
            mesh_radius: An optional number to override the radius of the meshes
                generated around each sensor. If None, it will be equal to 45%
                of the x_dim or y_dim (whichever is smaller). Set to zero to ensure
                no mesh is added to the resulting sensor grids. (Default: None).

        Returns:
            A honeybee_radiance SensorGrid generated from the floors of the room.
            Will be None if the Room has no floors or the criteria for wall_offset
            and/or remove_out results in all sensors being removed.
        """
        # generate the mesh grid from the floor Faces
        floor_grid = self._base_sensor_mesh(
            x_dim, y_dim, offset, remove_out, wall_offset)
        if floor_grid is None:  # no valid mesh could be generated
            return None

        # create the sensor grid from the mesh
        if mesh_radius is None:
            small_dim = x_dim if y_dim is None else min((x_dim, y_dim))
            mesh_radius = small_dim * 0.45
        sensor_grid = SensorGrid.from_mesh3d_radial(
            clean_rad_string(self.host.display_name), floor_grid, dir_count,
            start_vector, mesh_radius)
        sensor_grid.room_identifier = self.host.identifier
        sensor_grid.display_name = self.host.display_name
        sensor_grid.base_geometry = \
            tuple(face.geometry.move(face.normal.reverse() * offset)
                  for face in self.host.faces if isinstance(face.type, Floor))
        return sensor_grid

    def generate_view(self, direction, up_vector=(0, 0, 1), type='v', h_size=60,
                      v_size=60, shift=None, lift=None):
        """Get a single view in the center of the room facing a given direction.

        Note that the view will be located at the center of the bounding box
        around the room geometry and not the volume centroid. Also note that
        the view may not lie inside the room if the room is highly concave.

        The output view will have this room referenced in their room_identifier
        property.

        Args:
            direction: Set the view direction (-vd) vector to (x, y, z). The
                length of this vector indicates the focal distance as needed by
                the pixel depth of field (-pd) in rpict.
            up_vector: Set the view up (-vu) vector (vertical direction) to
                (x, y, z) default: (0, 0, 1).
            type: A single character for the view type (-vt). Choose from the following.

                * v - Perspective
                * h - Hemispherical fisheye
                * l - Parallel
                * c - Cylindrical panorama
                * a - Angular fisheye
                * s - Planisphere [stereographic] projection

                For more detailed description about view types check rpict manual
                page: (http://radsite.lbl.gov/radiance/man_html/rpict.1.html)
            h_size: Set the view horizontal size (-vh). For a perspective
                projection (including fisheye views), val is the horizontal field
                of view (in degrees). For a parallel projection, val is the view
                width in world coordinates.
            v_size: Set the view vertical size (-vv). For a perspective
                projection (including fisheye views), val is the horizontal field
                of view (in degrees). For a parallel projection, val is the view
                width in world coordinates.
            shift: Set the view shift (-vs). This is the amount the actual
                image will be shifted to the right of the specified view. This
                option is useful for generating skewed perspectives or rendering
                an image a piece at a time. A value of 1 means that the rendered
                image starts just to the right of the normal view. A value of -1
                would be to the left. Larger or fractional values are permitted
                as well.
            lift: Set the view lift (-vl) to a value. This is the amount the
                actual image will be lifted up from the specified view.

        Returns:
            A honeybee_radiance View generated in the center of the Room.

        Usage:

        .. code-block:: python

            from honeybee.room import Room
            room = Room.from_box(3.0, 6.0, 3.2, 180)
            south_face = room[3]
            south_face.apertures_by_ratio(0.4, 0.01)
            view = room.properties.radiance.generate_view((0, -1, 0))
        """
        pos = (self.host.center.x, self.host.center.y, self.host.center.z)
        view = View(self.host.identifier, pos, direction, up_vector, type,
                    h_size, v_size, shift, lift)
        view.room_identifier = self.host.identifier
        view.display_name = self.host.display_name
        return view

    @classmethod
    def from_dict(cls, data, host):
        """Create RoomRadianceProperties from a dictionary.

        Note that the dictionary must be a non-abridged version for this
        classmethod to work.

        Args:
            data: A dictionary representation of RoomRadianceProperties with the
                format below.
            host: A Room object that hosts these properties.

        .. code-block:: python

            {
            'type': 'RoomRadianceProperties',
            'modifier_set': {},  # ModifierSet dictionary
            }
        """
        assert data['type'] == 'RoomRadianceProperties', \
            'Expected RoomRadianceProperties. Got {}.'.format(data['type'])

        new_prop = cls(host)
        if 'modifier_set' in data and data['modifier_set'] is not None:
            new_prop.modifier_set = ModifierSet.from_dict(data['modifier_set'])
        return new_prop

    def apply_properties_from_dict(self, abridged_data, modifier_sets):
        """Apply properties from a RoomRadiancePropertiesAbridged dictionary.

        Args:
            abridged_data: A RoomRadiancePropertiesAbridged dictionary (typically
                coming from a Model) with the format below.
            modifier_sets: A dictionary of ModifierSets with identifiers of the sets
                as keys, which will be used to re-assign modifier_sets.

        .. code-block:: python

            {
            'type': 'RoomRadiancePropertiesAbridged',
            'modifier_set': str,  # ModifierSet identifier
            }
        """
        if 'modifier_set' in abridged_data and abridged_data['modifier_set'] is not None:
            self.modifier_set = modifier_sets[abridged_data['modifier_set']]

    def to_dict(self, abridged=False):
        """Return Room radiance properties as a dictionary.

        Args:
            abridged: Boolean for whether the full dictionary of the Room should
                be written (False) or just the identifier of the the individual
                properties (True). Default: False.
        """
        base = {'radiance': {}}
        base['radiance']['type'] = 'RoomRadianceProperties' if not \
            abridged else 'RoomRadiancePropertiesAbridged'

        # write the ModifierSet into the dictionary
        if self._modifier_set is not None:
            base['radiance']['modifier_set'] = \
                self._modifier_set.identifier if abridged else \
                self._modifier_set.to_dict()

        return base

    def duplicate(self, new_host=None):
        """Get a copy of this object.

        Args:
            new_host: A new Room object that hosts these properties.
                If None, the properties will be duplicated with the same host.
        """
        _host = new_host or self._host
        new_room = RoomRadianceProperties(_host, self._modifier_set)
        return new_room

    def _base_sensor_mesh(self, x_dim, y_dim, offset, remove_out, wall_offset):
        """Get a base Mesh3D from the Room floors to be used for sensor girds."""
        # generate the mesh grid from the floor Faces
        floor_grid = self.host.generate_grid(x_dim, y_dim, offset)
        if floor_grid is None:  # no floors in the host Room
            return None

        # remove any outdoor sensors if this has been requested
        if remove_out:
            geo = self.host.geometry
            pattern = [geo.is_point_inside(pt) for pt in floor_grid.face_centroids]
            try:
                floor_grid, vertex_pattern = floor_grid.remove_faces(pattern)
            except AssertionError:  # the grid lies completely outside of the room
                return None

        # remove any sensors within a certain distance of the walls, if requested
        if wall_offset >= x_dim / 2 or (y_dim is not None and wall_offset >= y_dim / 2):
            wall_geos = [f.geometry for f in self.host.faces if isinstance(f.type, Wall)]
            pattern = []
            for pt in floor_grid.face_centroids:
                for wg in wall_geos:
                    close_pt = wg.plane.closest_point(pt)
                    p_dist = pt.distance_to_point(close_pt)
                    if p_dist <= wall_offset:
                        close_pt_2d = wg.plane.xyz_to_xy(close_pt)
                        g_dist = wg.polygon2d.distance_to_point(close_pt_2d)
                        f_dist = math.sqrt(p_dist ** 2 + g_dist ** 2)
                        if f_dist <= wall_offset:
                            pattern.append(False)
                            break
                else:
                    pattern.append(True)
            try:
                floor_grid, vertex_pattern = floor_grid.remove_faces(pattern)
            except AssertionError:  # the grid lies completely outside of the room
                return None
        return floor_grid

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Room Radiance Properties: [host: {}]'.format(self.host.display_name)
