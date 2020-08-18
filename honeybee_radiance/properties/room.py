# coding=utf-8
"""Room Radiance Properties."""
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

    def generate_sensor_grid(self, x_dim, y_dim=None, offset=1.0):
        """Get a radiance SensorGrid generated from this Room's floors.

        The output grid will have this room referenced in their room_identifier
        property. It will also include a Mesh3D object with faces that align
        with the grid positions under the grid's mesh property.

        Note that the x_dim and y_dim refer to dimensions within the XY coordinate
        system of the floor faces's planes. So rotating the planes of the floor faces
        will result in rotated grid cells.

        Args:
            x_dim: The x dimension of the grid cells as a number.
            y_dim: The y dimension of the grid cells as a number. Default is None,
                which will assume the same cell dimension for y as is set for x.
            offset: A number for how far to offset the grid from the base face.
                Default is 1.0, which will not offset the grid to be 1 unit above
                the floor.

        Returns:
            A honeybee_radiance SensorGrid generated from the floors of the room.
            Will be None if the Room has no floors

        Usage:

        .. code-block:: python

            from honeybee.room import Room
            room = Room.from_box(3.0, 6.0, 3.2, 180)
            south_face = room[3]
            south_face.apertures_by_ratio(0.4, 0.01)
            sensor_grid = room.properties.radiance.generate_grid(0.5, 0.5, 1)
        """
        floor_grid = self.host.generate_grid(x_dim, y_dim, offset)
        if floor_grid is None:
            return None
        sensor_grid = SensorGrid.from_mesh3d(self.host.identifier, floor_grid)
        sensor_grid.room_identifier = self.host.identifier
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

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Room Radiance Properties:\n host: {}'.format(self.host.identifier)
